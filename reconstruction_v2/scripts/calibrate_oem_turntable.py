"""Shared official turntable camera diagnostic; no owner camera is modified.
Training frames 01/05/23/28, rear 14/19 reserved for structural checking only.
"""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2];V=ROOT/'reconstruction_v2';sys.path.insert(0,str(ROOT/'.tools/calibration'))
import cv2,numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
Q=V/'calibration/official_turntable_diagnostic';Q.mkdir(exist_ok=True)
ROI={int(k):v for k,v in json.loads((Q/'roi.local.json').read_text()).items()}
obs={}
for k,rr in ROI.items():
 im=cv2.imread(str(ROOT/'references/public'/f'official_turntable_{k:02}.jpg'));h,s,v=cv2.split(cv2.cvtColor(im,cv2.COLOR_BGR2HSV));mask=(((h<12)|(h>170))&(s>110)&(v>55)&(im[:,:,2]>im[:,:,1]*1.5))
 for wheel,(x0,y0,x1,y1) in rr.items():
  y,x=np.where(mask[y0:y1,x0:x1]);p=np.stack([x+x0,y+y0],1).astype(float);obs[(k,wheel)]=p[::max(1,len(p)//300)]
angles=np.linspace(0,math.tau,720,endpoint=False)
def camera(q,k):
 distance,eye_z,f,cx,cy,offset=q[:6];az=math.radians(50-10*k+offset);eye=np.array([distance*np.cos(az),distance*np.sin(az),eye_z]);forward=np.array([0,0,.5])-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);down=np.cross(forward,right);R=np.stack([right,down,forward]);return R,-R@eye,np.array([[f,0,cx],[0,f,cy],[0,0,1]])
def project(w,q,k):
 R,t,K=camera(q,k);p=w@R.T+t;u=p@K.T;return u[:,:2]/u[:,2,None]
def rim(q,k,wheel):
 side=1 if math.cos(math.radians(50-10*k+q[5]))>=0 else -1
 y,z,x=(.715,.3039,.038) if wheel=='Front' else (-.715,.3139,.049)
 w=np.stack([np.full(720,side*x),y+q[6]*np.cos(angles),z+q[6]*np.sin(angles)],1);return project(w,q,k)
def residual(q):return np.concatenate([cKDTree(rim(q,k,w)).query(p)[0] for (k,w),p in obs.items()])
fit=least_squares(residual,[6,1.4,1600,300,295,0,.216],bounds=([2,.3,500,260,240,-8,.210],[20,6,6000,340,340,8,.225]),loss='soft_l1',f_scale=1,max_nfev=250)
r=residual(fit.x);report={'status':'DIAGNOSTIC_ONLY_NOT_OWNER_VALIDATION','fit_parameters':fit.x.tolist(),'median_px':float(np.median(r)),'p95_px':float(np.percentile(r,95)),'training_frames':[1,5,23,28],'structural_check_frames':[14,19],'fitted_stripe_radius_mm':float(fit.x[6]*1000),'cameras':{str(k):{'R_cv':camera(fit.x,k)[0].tolist(),'t_cv_m':camera(fit.x,k)[1].tolist(),'K_px':camera(fit.x,k)[2].tolist(),'image_size':[600,576]} for k in [1,5,14,19,23,28,32]}}
(Q/'camera_diagnostic.json').write_text(json.dumps(report,indent=2))
for k in ROI:
 im=cv2.imread(str(ROOT/'references/public'/f'official_turntable_{k:02}.jpg'))
 for w in ROI[k]:
  for x,y in obs[(k,w)]:cv2.circle(im,(round(x),round(y)),1,(0,180,255),-1)
  cv2.polylines(im,[rim(fit.x,k,w).astype(np.int32)],True,(255,255,0),1)
 cv2.imwrite(str(Q/f'rims_{k:02}.jpg'),im)
print({k:v for k,v in report.items() if k!='cameras'})
