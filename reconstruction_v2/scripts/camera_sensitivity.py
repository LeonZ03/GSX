"""Read-only camera69 assumption profiles against frozen wheel observations.
Candidates are diagnostic only: never replace camera_69.json or change geometry.
Low wheel residual is not an appearance or metric acceptance criterion.
"""
from pathlib import Path
import sys,json,math,hashlib,copy
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from fit_cameras import wheel,CENTERS,project
A=json.loads((V2/'annotations/photo_69.json').read_text());BASE=json.loads((V2/'calibration/camera_69.json').read_text());W,H=A['image_size'];Q0=np.array(BASE['q']);MODEL=BASE['steering_model']

def camera(q,cx,cy):
 r=Rotation.from_rotvec(q[:3]).as_matrix();t=q[3:6];f=math.exp(q[6]);k=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
 return r,t,k

def errors(q,case):
 r,t,k=camera(q,case['cx'],case['cy']);out=[]
 for name,ann in A['wheels'].items():
  c,u,v=wheel(name,q[7],-1,MODEL);radius=case['radius_mm']/1000
  hom=k@np.column_stack([r@u*radius,r@v*radius,r@c+t]);ih=np.linalg.inv(hom);conic=ih.T@np.diag([1.,1.,-1.])@ih
  p=np.column_stack([ann['rim_points'],np.ones(len(ann['rim_points']))]);cp=(conic@p.T).T
  out.extend(np.sum(p*cp,axis=1)/(2*np.linalg.norm(cp[:,:2],axis=1)))
 return np.asarray(out)

def evaluate(q,case):
 r,t,k=camera(q,case['cx'],case['cy']);eye=-r.T@t;err=errors(q,case)
 at=[]
 if abs(q[7])>=.699:at.append('steering')
 if case.get('fixed_f_px') is None and (k[0,0]<=W*.551 or k[0,0]>=W*4.999):at.append('focal')
 physical=bool(eye[0]<0 and eye[1]>0 and eye[2]>-.5 and np.all(((r@np.array(list(CENTERS.values())).T).T+t)[:,2]>0))
 return dict(case, q=q.tolist(),R_cv=r.tolist(),t_cv_m=t.tolist(),K_px=k.tolist(),camera_position_m=eye.tolist(),front_steer_deg=math.degrees(q[7]),wheel_rms_px=float(np.sqrt(np.mean(err**2))),wheel_p95_px=float(np.percentile(abs(err),95)),boundary_hits=at,physical=physical)

def solve(case,extra_seeds=()):
 fixed=case.get('fixed_f_px');free=np.array([i for i in range(8) if i!=6 or fixed is None]);qbase=Q0.copy()
 if fixed is not None:qbase[6]=math.log(fixed)
 def unpack(x):
  q=qbase.copy();q[free]=x;return q
 def fun(x):
  q=unpack(x);return np.r_[errors(q,case),q[7]/.6]
 lower=np.array([-np.inf]*6+[math.log(W*.55),-.7])[free];upper=np.array([np.inf]*6+[math.log(W*5),.7])[free]
 starts=[qbase.copy()]
 for seed in extra_seeds:
  z=np.asarray(seed).copy()
  if fixed is not None:
   ratio=fixed/math.exp(z[6]);z[3:6]*=ratio;z[6]=math.log(fixed)
  starts.append(z)
 if fixed is not None:
  alt=qbase.copy();alt[3:6]*=fixed/math.exp(Q0[6]);starts.append(alt)
 best=None
 for q in starts:
  opt=least_squares(fun,q[free],bounds=(lower,upper),loss='soft_l1',f_scale=1.,max_nfev=500)
  out=evaluate(unpack(opt.x),case);out['optimizer_success']=bool(opt.success);out['nfev']=opt.nfev;out['robust_objective']=float(opt.cost)
  if best is None or (out['physical'], -opt.cost)>(best['physical'],-best['robust_objective']):best=out
 best['low_residual_diagnostic']=bool(best['physical'] and best['optimizer_success'] and not best['boundary_hits'] and best['wheel_rms_px']<=1 and best['wheel_p95_px']<=2)
 return best

def main():
 inputs=[V2/'calibration/camera_69.json',V2/'annotations/photo_69.json',V2/'annotations/seat_tail_r09.json',V2/'qa/tail_mesh_r11.json']+list((V2/'data/control_cages').glob('*.json'))
 hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
 filename=sys.argv[1] if len(sys.argv)>1 else 'camera69_sensitivity_r12.json'
 if Path(filename).name!=filename or not filename.endswith('.json'):raise ValueError('Local JSON filename required')
 outpath=V2/'calibration'/filename
 if outpath.exists():raise FileExistsError('Diagnostic output exists; preserve it before starting a new revision.')
 default={'radius_mm':220.,'cx':W/2,'cy':H/2,'fixed_f_px':None}
 cases=[dict(default,name='baseline_refit',family='baseline')]
 for fac in [.55,.60,.65,.80,1.,1.3,1.8,2.5,3.5,5.]:cases.append(dict(default,name=f'focal_{fac:.2f}w',family='focal_profile',fixed_f_px=W*fac))
 for radius in [215.,225.]:cases.append(dict(default,name=f'radius_{radius:.0f}',family='radius',radius_mm=radius))
 for axis in ['x','y']:
  for direction in [-1,1]:cases.append(dict(default,name=f'principal_{axis}_{direction:+d}',family='principal_point',**{('cx' if axis=='x' else 'cy'):(W/2+direction*.03*W if axis=='x' else H/2+direction*.03*H)}))
 for radius in [215.,225.]:
  for dx,dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:cases.append(dict(default,name=f'joint_r{radius:.0f}_{dx:+d}_{dy:+d}',family='joint_envelope',radius_mm=radius,cx=W/2+dx*.03*W,cy=H/2+dy*.03*H))
 results=[];previous_focal=None
 for case in cases:
  extras=[previous_focal] if case['family']=='focal_profile' and previous_focal is not None else []
  res=solve(case,extras)
  if case['family']=='focal_profile':previous_focal=res['q']
  results.append(res);print(res['name'],round(res['K_px'][0][0],1),round(res['wheel_rms_px'],3),res['low_residual_diagnostic'],flush=True)
 report={'status':'DIAGNOSTIC_ONLY_NOT_ACCEPTED','photo':69,'geometry_revision':'r11_unchanged','fitting_data':'68 observed wheel stripe samples plus original steer prior; no body contour used in camera fit','low_residual_screen':'RMS<=1px and P95<=2px, physical quadrant, optimizer successful, no optimized parameter on bound; diagnostic screen only, not acceptance or confidence interval','assumption_ranges':{'radius_mm':[215,225],'principal_offset_fraction_width_height':.03,'fixed_focal_fraction_width':[.55,5.]},'not_examined':['lens distortion','wheel stripe side-plane offsets','rake/trail family specification uncertainty','correlated annotation errors','independent body landmarks'],'input_sha256':hashes,'frozen_camera':evaluate(Q0,dict(default,name='frozen_baseline',family='baseline')),'candidates':results}
 assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
 outpath.write_text(json.dumps(report,indent=2),encoding='utf8');print('Saved isolated assumption profiles; production camera unchanged.',flush=True)
if __name__=='__main__':main()