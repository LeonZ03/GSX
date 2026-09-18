"""Physical-quadrant multistart review for added camera candidates; local only."""
from pathlib import Path
import sys,json,math
R0=Path(__file__).resolve().parents[2];V=R0/'reconstruction_v2';sys.path.insert(0,str(R0/'.tools/calibration'))
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from fit_cameras import look_at,residual,camera
for k in [69,70]:
 a=json.loads((V/f'annotations/photo_{k}.json').read_text(encoding='utf8'));a['steering_model']='raked_axis_25_6_trail104';w,h=a['image_size'];best=None
 for az in ([105,125,145,160] if k==69 else [-60,-45,-25,-10]):
  for foc in [1.2*w,2*w,3*w]:
   ang=math.radians(az);eye=np.array([3*math.cos(ang),3*math.sin(ang),1.2]);R=look_at(eye,np.array([0,0,.65]));q=np.r_[Rotation.from_matrix(R).as_rotvec(),-R@eye,math.log(foc),0.]
   opt=least_squares(residual,q,args=(a,),bounds=([-np.inf]*6+[math.log(w*.55),-.7],[np.inf]*6+[math.log(w*5),.7]),max_nfev=800,loss='soft_l1',f_scale=1)
   R,t,K=camera(opt.x,w,h);eye=-R.T@t;rr=residual(opt.x,a);score=float(np.mean(np.minimum(rr**2,25)))
   valid=(eye[0]<0 and eye[1]>0) if k==69 else (eye[0]>0 and eye[1]<0)
   if valid and eye[2]>-.5 and (best is None or score<best[0]):best=(score,opt.x)
 if best is None:print(k,'no physical solution');continue
 q=best[1];R,t,K=camera(q,w,h);rr=residual(q,a)
 c={'image_id':k,'image_size':[w,h],'role':'supplementary_reference','status':'provisional_added_photo_not_metric_certified','method':'visible_stripe_conics_physical_quadrant_multistart','R_cv':R.tolist(),'t_cv_m':t.tolist(),'K_px':K.tolist(),'camera_position_m':(-R.T@t).tolist(),'front_steer_deg':math.degrees(q[7]),'rim_radius_mm':220,'steering_model':a['steering_model'],'rms_px':float(np.sqrt(np.mean(rr**2))),'median_abs_px':float(np.median(abs(rr))),'p95_abs_px':float(np.percentile(abs(rr),95)),'q':q.tolist(),'assumptions':['Principal point at image center; zero distortion; no EXIF.','Stripe radius 220 +/- 5 mm and side offsets are assumptions.','No axle observation used because obscured/ambiguous.','Steering rake 25.6 degrees and trail 104 mm from family specification; exact owner-year confirmation pending.','This view is used for shape diagnosis, not a held-out acceptance view.']}
 c['eligible_for_shape_gate']=False;c['status']='REJECTED_HIGH_RESIDUAL_DIAGNOSTIC_ONLY' if c['rms_px']>2.5 or abs(q[7])>.69 or K[0,0]<w*.551 else 'provisional_raked_axis_candidate'
 (V/f'calibration/camera_{k}.json').write_text(json.dumps(c,indent=2));print(k,c['camera_position_m'],K[0,0],c['front_steer_deg'],c['rms_px'],c['p95_abs_px'])