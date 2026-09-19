"""Fit a convex rear crown envelope, excluding invisible internal silhouettes.
A proposal tool only: full-stack depth renders and junction inspection are required.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import ConvexHull
from interface_projection import dense
from fit_cameras import project
z=np.load(V2/'qa/tank_crown_basis_r14.npz');v=z['vertices'];b=z['basis'];meta=json.loads((V2/'qa/tank_crown_basis_r14.json').read_text());ann=json.loads((V2/'annotations/tank_crown_r14.json').read_text());views=[]
for k in ['62','63','69']:
 c=json.loads((V2/f'calibration/camera_{k}.json').read_text());views.append(dict(id=k,R=np.array(c['R_cv']),t=np.array(c['t_cv_m']),K=np.array(c['K_px']),ref=dense(ann['views'][k]['boundaries']['rear_outline'])[::2],crown=dense(ann['views'][k]['boundaries']['crown'])[::2] if 'crown' in ann['views'][k]['boundaries'] else None))
def distances(uv,ref):
 hull=uv[ConvexHull(uv).vertices];a=hull;c=np.roll(hull,-1,axis=0);ac=c-a;delta=ref[:,None,:]-a;t=np.clip(np.einsum('rhc,hc->rh',delta,ac)/(ac*ac).sum(axis=1),0,1);d=ref[:,None,:]-(a[None,:,:]+t[:,:,None]*ac[None,:,:]);ix=(d*d).sum(axis=2).argmin(axis=1);return d[np.arange(len(ref)),ix]
if (V2/'qa/tank_crown_fit_r15.json').exists():raise FileExistsError('Preserve completed r14 candidate run; choose a new revision')
assert [view['id'] for view in views if view['crown'] is not None]==['62','69']
rows=[]
for side_weight in [2,3]:
 penalty=.12
 def residual(q):
  pts=v+np.einsum('k,kvc->vc',q,b);res=[];used_crown_views=[]
  for view in views:
   uv=project(pts,view['R'],view['t'],view['K']);res.extend((distances(uv,view['ref'])/np.sqrt(len(view['ref']))*8*(side_weight if view['id']=='69' else 1)).ravel())
   if view['crown'] is not None:
    used_crown_views.append(view['id']);res.extend((distances(uv,view['crown'])/np.sqrt(len(view['crown']))*12).ravel())
  assert used_crown_views==['62','69'], 'Every visible crown view must contribute to the objective'
  res.extend(q*penalty);res.extend((np.diff(q.reshape(9,4),n=2,axis=0)*.35).ravel());g=z['control_grid']+np.einsum('k,kijc->ijc',q,z['control_basis']);res.extend(np.minimum(np.diff(g[:,:,1],axis=0)-4,0).ravel()*2)
  return np.array(res)
 fit=least_squares(residual,np.zeros(len(b)),bounds=(z['lower'],z['upper']),diff_step=.005,loss='soft_l1',f_scale=4,max_nfev=180,ftol=1e-6,xtol=1e-6);q=fit.x;name=f'crown_joint_w{side_weight}_r15';cage=dict(meta['cage_template']);cage['grid']=(z['control_grid']+np.einsum('k,kijc->ijc',q,z['control_basis'])).tolist();cage['revision']='r15';cage['revision_note']='Separate rear crown/width/knee controls fitted with fixed camera rear envelopes; full-stack review required.'
 (V2/f'qa/{name}.json').write_text(json.dumps(cage,indent=2),encoding='utf8');metrics={view['id']:float(np.linalg.norm(distances(project(v+np.einsum('k,kvc->vc',q,b),view['R'],view['t'],view['K']),view['ref']),axis=1).mean()) for view in views};rows.append({'name':name,'crown_views':[view['id'] for view in views if view['crown'] is not None],'metrics':metrics,'params':dict(zip(meta['parameters'],q.tolist())),'cost':fit.cost,'evals':fit.nfev});print(name,metrics,flush=True)
(V2/'qa/tank_crown_fit_r15.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
