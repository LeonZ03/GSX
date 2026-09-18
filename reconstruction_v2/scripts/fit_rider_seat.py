"""Bounded rider-seat fit using frozen 62/69 cameras, never camera optimization.
Only proposes a cage into qa/. Actual mesh and photo63 must be checked before use.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from fit_cameras import project
z=np.load(V2/'qa/seat_basis_r10.npz');v0=z['vertices'];b=z['basis'];faces=z['triangles'];meta=json.loads((V2/'qa/seat_basis_r10.json').read_text())
edge_faces={}
for i,f in enumerate(faces):
 for a,c in zip(f,np.roll(f,-1)):edge_faces.setdefault(tuple(sorted((int(a),int(c)))),[]).append(i)
edges=np.array(list(edge_faces));adj=[edge_faces[tuple(e)] for e in edges]
left=np.array([a[0] for a in adj]);right=np.array([a[-1] for a in adj])
ann=json.loads((V2/'annotations/seat_tail_r09.json').read_text())
views=[]
def dense(poly,step=2):
 out=[]
 for a,c in zip(poly,np.roll(poly,-1,axis=0)):
  n=max(1,int(np.ceil(np.linalg.norm(c-a)/step)));out.extend(a+(c-a)*np.arange(n)[:,None]/n)
 return np.array(out)
for k,weight in [(62,1.),(69,.65)]:
 c=json.loads((V2/f'calibration/camera_{k}.json').read_text());a=next(x for x in ann['boundaries'] if x['image_id']==k and x['part']=='Seat_Rider');ref=dense(np.array(a['points'],float));R=np.array(c['R_cv']);t=np.array(c['t_cv_m'])
 views.append({'id':k,'R':R,'t':t,'K':np.array(c['K_px']),'eye':-R.T@t,'ref':ref,'tree':cKDTree(ref),'weight':weight})
def vertices(q):return v0+np.einsum('k,kvc->vc',q,b)
def support(q,view):
 v=vertices(q);tri=v[faces];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);front=np.einsum('ij,ij->i',normal,view['eye']-tri.mean(axis=1))>0
 chosen=edges[front[left]!=front[right]]
 if len(chosen)<5:raise RuntimeError('Cannot identify seat silhouette')
 uv=project(v,view['R'],view['t'],view['K']);aa=[];bb=[];tt=[]
 for a,c in chosen:
  n=max(1,int(np.ceil(np.linalg.norm(uv[c]-uv[a])/2)))
  aa.extend([a]*n);bb.extend([c]*n);tt.extend(np.arange(n)/n)
 aa=np.array(aa);bb=np.array(bb);tt=np.array(tt)[:,None]
 return v0[aa]*(1-tt)+v0[bb]*tt,b[:,aa]*(1-tt)+b[:,bb]*tt
q=np.zeros(b.shape[0]);passes=[]
for iteration in range(3):
 cached=[support(q,view) for view in views]
 def residual(x):
  res=[]
  for view,(v,delta) in zip(views,cached):
   points=v+np.einsum('k,kpc->pc',x,delta);uv=project(points,view['R'],view['t'],view['K']);r=view['tree'].query(uv)[0];back=cKDTree(uv).query(view['ref'])[0]
   res.extend(np.r_[r,back]*view['weight'])
  res.extend(x*.8)
  # Keep adjacent section offsets smooth; no arbitrary individual vertices.
  for first in [2,5,8]:res.append((x[first]-2*x[first+1]+x[first+2])*.6)
  return np.array(res)
 fit=least_squares(residual,q,bounds=(z['lower'],z['upper']),diff_step=.005,loss='soft_l1',f_scale=4,max_nfev=100,ftol=1e-5,xtol=1e-5)
 q=fit.x;passes.append({'pass':iteration,'cost':float(fit.cost),'evaluations':fit.nfev});print('BOUNDED_SEAT_FIT',passes[-1],flush=True)
new=meta['cage_template'];new['grid']=(z['control_grid']+np.einsum('k,kijc->ijc',q,z['control_basis'])).tolist();new['revision']='r10';new['acceptance']='pending_three_view_review';new['revision_note']='Small bounded rider-seat fit to frozen 62/69. Camera and pillion remain unchanged. No real-world dimensional acceptance.'
(V2/'qa/Seat_Rider_r10_candidate.json').write_text(json.dumps(new,indent=2),encoding='utf8')
report={'status':'CANDIDATE_NOT_APPLIED','fit_views':[62,69],'cross_check_view':63,'parameters_mm':dict(zip(meta['parameters'],q.tolist())),'passes':passes,'hit_bound':[meta['parameters'][i] for i in range(len(q)) if min(q[i]-z['lower'][i],z['upper'][i]-q[i])<.1],'warning':'Manual contours and provisional cameras; photo63 not in optimization. Independent model acceptance is still absent.'}
(V2/'qa/seat_fit_r10.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))