"""Candidate-only camera solve from explicitly reviewed, separate wheel ROIs.
No formal camera files are changed. ROI and plate masks are private local inputs.
"""
from pathlib import Path
import os,sys,json,math
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V.parent/'.tools/calibration'));sys.path.insert(0,str(V/'scripts'))
import numpy as np,cv2
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from fit_cameras import camera,residual,look_at
cfg=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
k=cfg['image_id'];im=Image.open(next((V.parent/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB');rgb=np.array(im);w,h=im.size
ann={'image_id':k,'image_size':[w,h],'side':'right','steering_model':'raked_axis_25_6_trail104','wheels':{}}
preview=im.copy();draw=ImageDraw.Draw(preview)
for box in cfg['redact']:draw.rectangle(box,fill=(35,35,35))
for name,box in cfg['boxes'].items():
 x0,y0,x1,y1=box;roi=rgb[y0:y1,x0:x1];hsv=cv2.cvtColor(roi,cv2.COLOR_RGB2HSV);mask=cv2.inRange(hsv,np.array([18,105,105]),np.array([48,255,255]));n,lab,stats,cent=cv2.connectedComponentsWithStats(mask)
 pp=[]
 for j in range(1,n):
  if stats[j,4]<35:continue
  yy,xx=np.where(lab==j);pp.extend(np.c_[xx+x0,yy+y0])
 pp=np.array(pp);center=pp.mean(axis=0);angles=np.arctan2(pp[:,1]-center[1],pp[:,0]-center[0]);sample=[]
 for th in np.arange(-np.pi,np.pi,.07):
  dist=np.arctan2(np.sin(angles-th),np.cos(angles-th));selected=pp[np.abs(dist)<.025]
  if len(selected)>2:sample.append(np.median(selected,axis=0).tolist())
 ann['wheels'][name]={'center':None,'rim_points':sample,'method':'observed stripe pixels; apparent centroid used only for angular subsampling, never an axle observation'}
 draw.rectangle(box,outline='orange',width=2)
 for x,y in sample:draw.ellipse((x-2,y-2,x+2,y+2),fill='red')
preview.save(out/'samples.jpg');(out/'samples.local.json').write_text(json.dumps(ann,indent=2))
best=None;candidates=[]
for az in (-65,-45,-25,0):
 for f in (w*.9,w*1.6,w*2.8):
  eye=np.array([3*np.cos(np.deg2rad(az)),3*np.sin(np.deg2rad(az)),1.6]);R=look_at(eye,np.array([0,0,.6]));t=-R@eye;q=np.r_[Rotation.from_matrix(R).as_rotvec(),t,np.log(f),.1]
  sol=least_squares(residual,q,args=(ann,),bounds=([-np.inf]*6+[np.log(w*.55),-.8],[np.inf]*6+[np.log(w*5),.8]),loss='soft_l1',f_scale=1.5,max_nfev=180)
  R,t,K=camera(sol.x,w,h);eye=-R.T@t;e=residual(sol.x,ann);valid=eye[0]>0 and eye[2]>0 and t[2]>1
  score=float(np.mean(e[:-1]**2));candidates.append({'rms':score**.5,'eye':eye.tolist(),'focal':float(K[0,0]),'steer':float(np.rad2deg(sol.x[7])),'valid':bool(valid)})
  if valid and (best is None or score<best[0]):best=(score,sol.x)
if best is None:raise ValueError('No physical candidate')
q=best[1];R,t,K=camera(q,w,h);e=residual(q,ann)[:-1]
r={'status':'ROOT_CANDIDATE_REQUIRES_ROI_AND_SENSITIVITY_REVIEW','image_id':k,'image_size':[w,h],'role':'diagnostic','steering_model':ann['steering_model'],'R_cv':R.tolist(),'t_cv_m':t.tolist(),'K_px':K.tolist(),'camera_position_m':(-R.T@t).tolist(),'front_steer_deg':float(np.rad2deg(q[7])),'q':q.tolist(),'rms_px':float(np.sqrt(np.mean(e**2))),'median_px':float(np.median(abs(e))),'p95_px':float(np.percentile(abs(e),95)),'candidate_search':candidates,'note':'Candidate conic fit is not metric certification or shape validation.'}
(out/'camera_candidate.json').write_text(json.dumps(r,indent=2));print({key:r[key] for key in ['rms_px','median_px','p95_px','camera_position_m','front_steer_deg']})
