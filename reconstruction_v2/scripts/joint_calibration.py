"""Joint two-view diagnostic constrained by observed wheel arcs and real SIFT ties.

No silhouette/model render is used to adjust a camera. Existing cameras are never
overwritten. Feature holdout evaluates epipolar agreement, NOT model accuracy.
"""
from pathlib import Path
import sys, json, hashlib, math
ROOT=Path(__file__).resolve().parents[2]; V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'))
import numpy as np, cv2
from scipy.optimize import least_squares
import fit_cameras as fc

def skew(t):
 x,y,z=t;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])

def fundamental(q):
 R1,t1,K1=fc.camera(q[:8],1280,1706);R2,t2,K2=fc.camera(q[8:],1280,1706)
 R=R2@R1.T;t=t2-R@t1
 return np.linalg.inv(K2).T@skew(t)@R@np.linalg.inv(K1)

def sampson(q,points):
 F=fundamental(q);a=np.c_[points[:,:2],np.ones(len(points))];b=np.c_[points[:,2:],np.ones(len(points))]
 fa=a@F.T;fb=b@F
 return np.sum(b*fa,axis=1)/np.sqrt(np.sum(fa[:,:2]**2,axis=1)+np.sum(fb[:,:2]**2,axis=1))

def triangulate(q,points):
 R1,t1,K1=fc.camera(q[:8],1280,1706);R2,t2,K2=fc.camera(q[8:],1280,1706)
 P1=K1@np.c_[R1,t1];P2=K2@np.c_[R2,t2]
 X=cv2.triangulatePoints(P1,P2,points[:,:2].T.copy(),points[:,2:].T.copy());X=(X[:3]/X[3]).T
 err=np.c_[fc.project(X,R1,t1,K1)-points[:,:2],fc.project(X,R2,t2,K2)-points[:,2:]]
 depths=np.c_[(X@R1.T+t1)[:,2],(X@R2.T+t2)[:,2]]
 return X,err,depths

def stats(x):
 x=np.abs(x);return {'median_px':float(np.median(x)),'p95_px':float(np.percentile(x,95)),'rms_px':float(np.sqrt(np.mean(x*x)))}

def main():
 dest=V2/'calibration/joint_candidate';dest.mkdir(exist_ok=True)
 ids=[62,63];base=V2/'calibration/r04_frozen' if (V2/'calibration/r04_frozen/camera_62.json').exists() else V2/'calibration';cams=[json.loads((base/f'camera_{k}.json').read_text()) for k in ids]
 anns=[json.loads((V2/f'annotations/photo_{k}.json').read_text()) for k in ids]
 source=V2/'calibration/feature_matches_62_63.json';data=json.loads(source.read_text(encoding='utf8'))
 # SIFT can provide multiple descriptors at one pixel: retain one physical tie.
 ties=[]
 for m in sorted(data['matches'],key=lambda m:m['descriptor_distance']):
  p=np.array(m['point'])
  if not any(np.linalg.norm(p[:2]-z[:2])<3 or np.linalg.norm(p[2:]-z[2:])<3 for z in ties):ties.append(p)
 ties=np.array(ties);bad=np.array([[418.188,1225.399,910.432,1253.834],[546.077,639.056,1180.765,723.035]]);keep=np.min(np.linalg.norm(ties[:,None,:]-bad[None,:,:],axis=2),axis=1)>4;rejected=ties[~keep].tolist();ties=ties[keep]
 # Visual review: exhaust-to-front-spoke repeat and two different plant regions.
 cells=np.floor(ties[:,:2]/55).astype(int);weights=np.array([1/math.sqrt(max(1,np.sum(np.all(cells==c,axis=1))/2)) for c in cells])
 rng=np.random.default_rng(42);order=rng.permutation(len(ties));test=order[::5];train=np.setdiff1d(order,test)
 q0=np.r_[cams[0]['q'],cams[1]['q']]
 def fun(q):
  return np.r_[fc.residual(q[:8],anns[0]),fc.residual(q[8:],anns[1]),sampson(q,ties[train])*weights[train]*2]
 low=np.full(16,-np.inf);high=-low
 for i in [0,8]:low[i+6]=math.log(750);high[i+6]=math.log(6400);low[i+7]=-.5;high[i+7]=.5
 opt=least_squares(fun,q0,bounds=(low,high),loss='soft_l1',f_scale=1.,max_nfev=2500,xtol=1e-12,ftol=1e-12,gtol=1e-10)
 q=opt.x;X,err,dep=triangulate(q,ties)
 report={'status':'CANDIDATE_NOT_METRIC_CERTIFIED','source_match_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rejected_visual_mismatches':rejected,'unique_ties':len(ties),'training_ties':train.tolist(),'holdout_ties':test.tolist(),'optimizer_success':bool(opt.success),'nfev':opt.nfev,'before':{'all_epipolar':stats(sampson(q0,ties)),'holdout_epipolar':stats(sampson(q0,ties[test]))},'after':{'all_epipolar':stats(sampson(q,ties)),'holdout_epipolar':stats(sampson(q,ties[test]))},'notes':['Holdout ties are not independent photographs and do not satisfy the independent-view gate.','Two-view features may still contain outliers and view-dependent highlights.','Wheel stripe radius/offsets and principal point are assumptions. Absolute accuracy is not certified.','No model silhouette or model-derived points used in this optimization.']}
 report['points']=[{'index':i,'pixels':p.tolist(),'xyz_mm':(x*1000).tolist(),'reprojection_error_px':e.tolist(),'depth_m':d.tolist(),'role':'holdout' if i in test else 'fit'} for i,(p,x,e,d) in enumerate(zip(ties,X,err,dep))]
 for j,k in enumerate(ids):
  old=cams[j];z=q[j*8:j*8+8];R,t,K=fc.camera(z,1280,1706);c=dict(old)
  c.update({'status':'joint_feature_candidate_not_metric_certified','method':'observed_rim_conics_plus_real_feature_epipolar_constraints','q':z.tolist(),'R_cv':R.tolist(),'t_cv_m':t.tolist(),'K_px':K.tolist(),'camera_position_m':(-R.T@t).tolist(),'front_steer_deg':math.degrees(z[7]),'rms_px':float(np.sqrt(np.mean(fc.residual(z,anns[j])**2))),'joint_report':'calibration/joint_candidate/report.json'})
  c['rim_residual_stats_px']=stats(fc.residual(z,anns[j]));c['previous_camera_sha256']=hashlib.sha256((V2/f'calibration/camera_{k}.json').read_bytes()).hexdigest()
  (dest/f'camera_{k}.json').write_text(json.dumps(c,indent=2));report[f'camera_{k}']={'eye_m':c['camera_position_m'],'focal_px':float(K[0,0]),'steer_deg':c['front_steer_deg'],'wheel_residual':c['rim_residual_stats_px']}
 (dest/'report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='points'},indent=2))
if __name__=='__main__':main()
