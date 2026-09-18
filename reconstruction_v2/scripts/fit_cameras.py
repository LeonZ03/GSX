"""Photo camera fit from rim conics and axle observations; no body pixels used.
Output is a calibration candidate until an annotated review accepts it.
Wheel rim lip radius is estimated, NOT the 17-inch bead-seat radius.
"""
from pathlib import Path
import sys,json,hashlib,math
ROOT=Path(__file__).resolve().parents[2]; V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'))
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
RIM_RADIUS=.220
CENTERS={'front':np.array([0,.715,.3039]),'rear':np.array([0,-.715,.3139])}

def look_at(eye,target):
 z=np.asarray(target)-eye;z=z/np.linalg.norm(z)
 x=np.cross(z,[0,0,1]);x/=np.linalg.norm(x);y=np.cross(z,x)
 return np.array([x,y,z])

def camera(q,w,h):
 R=Rotation.from_rotvec(q[:3]).as_matrix();t=np.array(q[3:6]);f=math.exp(q[6])
 K=np.array([[f,0,w/2],[0,f,h/2],[0,0,1]])
 return R,t,K

def wheel(k,steer=0,side=1):
 c=CENTERS[k].copy();x=side*(.042 if k=='front' else .055)
 Q=Rotation.from_rotvec(np.array([0,0,steer if k=='front' else 0])).as_matrix()
 return c+Q@np.array([x,0,0]),Q@np.array([0,1,0]),Q@np.array([0,0,1])

def project(p,R,t,K):
 v=(R@np.asarray(p).T).T+t;u=(K@v.T).T
 return u[...,:2]/u[...,2:3]

def residual(q,a):
 w,h=a['image_size'];R,t,K=camera(q,w,h);res=[]
 side=1 if a.get('side','right')=='right' else -1
 for k,ann in a['wheels'].items():
  if len(ann.get('rim_points',[]))<5:continue
  c,u,v=wheel(k,q[7],side)
  H=K@np.column_stack([R@u*RIM_RADIUS,R@v*RIM_RADIUS,R@c+t])
  ih=np.linalg.inv(H);C=ih.T@np.diag([1,1,-1])@ih
  p=np.column_stack([ann['rim_points'],np.ones(len(ann['rim_points']))]);cp=(C@p.T).T
  dist=np.sum(p*cp,axis=1)/(2*np.linalg.norm(cp[:,:2],axis=1))
  res.extend(dist)
  # Axle end sits outside rim plane; center observation must target the visible axle.
  if ann.get('center'):
   cc=CENTERS[k]+Rotation.from_rotvec([0,0,q[7] if k=='front' else 0]).as_matrix()@np.array([side*(.115 if k=='front' else .125),0,0])
   res.extend((project([cc],R,t,K)[0]-ann['center'])*.5)
 # Soft zero-steer prior prevents a one-wheel ellipse from absorbing camera error.
 res.append(q[7]/.6)
 return np.array(res)

def solve(a):
 w,h=a['image_size'];best=None
 for az in ([-10,5,15,30,45] if a.get('side','right')=='right' else [165,190,205,225]):
  for f in [w*.85,w*1.3,w*2.0,w*3.0]:
   el=.22;d=3.0;az=math.radians(az)
   eye=np.array([d*math.cos(az),d*math.sin(az),1.2]);R=look_at(eye,np.array([0,0,.65]));t=-R@eye
   q=np.r_[Rotation.from_matrix(R).as_rotvec(),t,math.log(f),0.]
   lower=[-np.inf]*6+[math.log(w*.55),-.8];upper=[np.inf]*6+[math.log(w*5),.8]
   opt=least_squares(residual,q,args=(a,),bounds=(lower,upper),loss='linear',max_nfev=1000)
   cost=float(np.mean(residual(opt.x,a)**2))
   R,t,K=camera(opt.x,w,h); eye=-R.T@t
   valid=eye[2]>-.5 and (eye[0]>0)==(a.get('side','right')=='right') and np.all((R@np.array(list(CENTERS.values())).T).T[:,2]+t[2]>0)
   if valid and (best is None or cost<best[0]):best=(cost,opt.x)
 if best is None:raise RuntimeError('No physically valid fit')
 q=best[1];R,t,K=camera(q,w,h);e=residual(q,a)
 return {'image_id':a['image_id'],'image_size':[w,h],'role':a.get('role','fit'),'status':'candidate_not_locked','method':'rim_conics_and_axle_centers_only','assumptions':['Estimated visible fluorescent stripe center diameter 440 +/- 10 mm; bead seat is 431.8 mm.','No EXIF; principal point fixed at image center; zero lens distortion.','Camera pose includes whole-bike lean; front steering fitted independently.','Low residual does not certify body shape or metric accuracy.'],'R_cv':R.tolist(),'t_cv_m':t.tolist(),'K_px':K.tolist(),'camera_position_m':(-R.T@t).tolist(),'front_steer_deg':math.degrees(q[7]),'rim_radius_mm':RIM_RADIUS*1000,'rms_px':float(np.sqrt(np.mean(e**2))),'median_abs_px':float(np.median(abs(e))),'p95_abs_px':float(np.percentile(abs(e),95)),'residuals_px':e.tolist(),'q':q.tolist()}

def main():
 for p in sorted((V2/'annotations').glob('photo_*.json')):
  a=json.loads(p.read_text(encoding='utf-8-sig'))
  existing=V2/'calibration'/f"camera_{a['image_id']}.json"
  if existing.exists() and '--refit' not in sys.argv:
   print(a['image_id'],'existing camera preserved; --refit required');continue
  if existing.exists():
   from datetime import datetime
   import shutil
   backup=V2/'calibration/history';backup.mkdir(exist_ok=True)
   shutil.copy2(existing,backup/(existing.stem+'_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json'))
  if len([k for k in a.get('wheels',{}) if len(a['wheels'][k].get('rim_points',[]))>=5])<2:continue
  out=solve(a);out['annotation_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
  dest=V2/'calibration'/f"camera_{a['image_id']}.json";dest.write_text(json.dumps(out,indent=2),encoding='utf8')
  print(a['image_id'],out['rms_px'],out['camera_position_m'],out['front_steer_deg'])
if __name__=='__main__':main()
