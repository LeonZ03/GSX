"""Fit a mirror rim plane to local, manually traced photo silhouettes.

Private pixel annotations remain in qa; output is a provisional derived 3-D
control, never a calibrated measurement. Camera files are read-only.
"""
from pathlib import Path
import json,sys
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V.parent/'.tools/calibration'))
import numpy as np
from scipy.optimize import least_squares
from scipy.interpolate import CubicSpline
from scipy.spatial import cKDTree

def dense(p,n=180):
 p=np.array(p,float);p=np.vstack([p,p[0]])
 t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];t/=t[-1]
 return CubicSpline(t,p,bc_type='periodic')(np.arange(n)/n)

def run(annotation,output):
 a=json.loads(Path(annotation).read_text());cams={}
 for k in (62,63):
  c=json.loads((V/f'calibration/camera_{k}.json').read_text());cams[k]=[np.array(c[z]) for z in ('R_cv','t_cv_m','K_px')]
 def project(p,k):
  R,t,K=cams[k];v=(R@p.T).T+t;h=(K@v.T).T;return h[:,:2]/h[:,2:]
 uv=dense(a['63']);R,t,K=cams[63];eye=-R.T@t;rays=(R.T@np.linalg.inv(K)@np.c_[uv,np.ones(len(uv))].T).T
 target=dense(a['62']);tree=cKDTree(target)
 n0=np.array([.55,.83,.08]);n0/=np.linalg.norm(n0);c0=np.array([.310,.610,1.049]);d0=n0@c0
 def shape(q):
  n=np.array([np.sin(q[0])*np.cos(q[1]),np.cos(q[0])*np.cos(q[1]),np.sin(q[1])]);d=q[2]
  return eye+rays*((d-n@eye)/(rays@n))[:,None],n
 q0=[np.arctan2(n0[0],n0[1]),np.arcsin(n0[2]),d0]
 def fun(q):
  p,n=shape(q);u=project(p,62);back=cKDTree(u).query(target)[0]
  return np.r_[tree.query(u)[0],back,(q-np.array(q0))*[5,5,80]]
 sol=least_squares(fun,q0,bounds=([-.4,-.6,d0-.16],[1.4,.6,d0+.16]),loss='soft_l1',f_scale=3,max_nfev=350)
 p,n=shape(sol.x);cen=p.mean(axis=0)
 result={'revision':'r21','status':'TWO_USED_VIEW_SILHOUETTE_FIT_NOT_ACCEPTED','units':'mm','evidence':['owner_photo_62','owner_photo_63'],'normal_right':n.tolist(),'center_right':(cen*1000).tolist(),'rim_right_mm':(p[::6]*1000).round(4).tolist(),'shell_depth_mm':25,'shell_depth_status':'unmeasured_photo_led_estimate','notes':'Rim plane fitted to open-scene silhouettes in two previously used images. Rounded housing depth and left pose remain provisional; poses in earlier photo 69 may differ.'}
 Path(output).write_text(json.dumps(result,indent=2),encoding='utf8')
 metric={str(k):{'median_px':float(np.median(cKDTree(dense(a[str(k)])).query(project(p,k))[0])),'p95_px':float(np.percentile(cKDTree(dense(a[str(k)])).query(project(p,k))[0],95))} for k in (62,63)}
 (Path(output).parent/'mirror_fit_report.json').write_text(json.dumps({'used_view_diagnostic_only':metric,'solution':sol.x.tolist(),'parameter_bounds_hit':bool(np.any(sol.active_mask))},indent=2))
 return result,metric
if __name__=='__main__':
 r,m=run(sys.argv[1],sys.argv[2]);print(m)
