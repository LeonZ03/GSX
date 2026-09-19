"""Bounded fixed-camera windscreen proposal from reviewed open edge traces."""
from pathlib import Path
import sys,json,os
os.environ['OPENBLAS_NUM_THREADS']='1'
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V.parent/'.tools/calibration'))
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
z=np.load(V/'qa/front_r21/wind_basis.npz');v=z['vertices'];b=z['basis'];edge=z['edges'];a=json.loads((V/'qa/front_r21/windscreen_root.local.json').read_text())
# Sample all actual subdivided boundary edges; only annotated visible points
# enter one-way distance, so hidden edges are never invented as observed.
t=np.linspace(0,1,6);samples=(v[edge[:,0],None]*(1-t[None,:,None])+v[edge[:,1],None]*t[None,:,None]).reshape(-1,3)
delta=(b[:,edge[:,0],None]*(1-t[None,None,:,None])+b[:,edge[:,1],None]*t[None,None,:,None]).reshape(len(b),-1,3)
views=[]
for k in [62,63,69]:
 c=json.loads((V/f'calibration/camera_{k}.json').read_text());points=[]
 for name,poly in a['photos'][str(k)].items():
  for aa,bb in zip(poly,poly[1:]):
   aa,bb=np.array(aa),np.array(bb);n=max(2,int(np.linalg.norm(bb-aa)/3));points.extend(aa+(bb-aa)*np.linspace(0,1,n)[:,None])
 views.append((k,np.array(c['R_cv']),np.array(c['t_cv_m']),np.array(c['K_px']),np.array(points)))
def errors(q):
 p=samples+np.einsum('k,kvc->vc',q,delta);out=[]
 for k,R,T,K,ref in views:
  vv=(R@p.T).T+T;uv=(K@vv.T).T;uv=uv[:,:2]/uv[:,2:];out.append(cKDTree(uv).query(ref)[0])
 return out
def fun(q):
 return np.r_[np.concatenate(errors(q)),q*.3,np.diff(q.reshape(4,3),n=2,axis=0).ravel()*.35]
q=np.zeros(len(b));limit=np.tile([24,28,34],4)
r=least_squares(fun,q,bounds=(-limit,limit),loss='soft_l1',f_scale=4,max_nfev=180,diff_step=.01)
a=json.loads((V/'data/control_cages/Windscreen.json').read_text());a['grid']=(z['grid']+np.einsum('k,kijc->ijc',r.x,z['control_basis'])).round(4).tolist();a['revision']='r21';a['notes']+=' Bounded upper rim/curvature fit; lower two rows preserved; root reviewed open traces only; shape and lens remain unaccepted.'
(V/'qa/front_r21/Windscreen_candidate.json').write_text(json.dumps(a,indent=2))
report={'status':'USED_VIEW_OPEN_BOUNDARY_DIAGNOSTIC_NOT_ACCEPTED','parameters':r.x.tolist(),'bounds_hit':r.active_mask.tolist(),'metrics':{str(view[0]):{'before_median':float(np.median(e0)),'after_median':float(np.median(e1)),'before_p95':float(np.percentile(e0,95)),'after_p95':float(np.percentile(e1,95))} for view,e0,e1 in zip(views,errors(q),errors(r.x))}}
(V/'qa/front_r21/wind_fit_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
