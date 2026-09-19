"""Extract a bounded editable windscreen basis; never save the source."""
from pathlib import Path
import bpy,json,numpy as np
V=Path(__file__).resolve().parents[1];out=V/'qa/front_r21'
s=bpy.context.scene;o=s.objects['Windscreen'];g=np.array([list(v.co) for v in o.data.vertices]).reshape(6,4,3)*1000
for m in s.objects['Body_NoseAssembly'].modifiers:m.show_viewport=False
solid=o.modifiers.get('Shell_Thickness');solid.show_viewport=False
D=[];names=[]
for row in range(2,6):
 for axis in (0,1,2):
  d=np.zeros_like(g);d[row,:,axis]=g[row,:,0]/g[row,-1,0] if axis==0 else 1;D.append(d);names.append(f'row_{row}_axis_{axis}')
D=np.array(D)
def sample(q):
 v=(g+np.einsum('k,kijc->ijc',q,D)).reshape(-1,3)*.001
 for p,co in zip(o.data.vertices,v):p.co=co
 o.data.update();bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();verts=np.array([list(p.co) for p in me.vertices]);counts={}
 for f in me.polygons:
  for a,b in zip(f.vertices,list(f.vertices[1:])+[f.vertices[0]]):
   key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
 edges=np.array([k for k,v in counts.items() if v==1]);e.to_mesh_clear();return verts,edges
q=np.zeros(len(D));v,edges=sample(q);deltas=[]
for i in range(len(D)):
 q=np.zeros(len(D));q[i]=1;vv,_=sample(q);deltas.append(vv-v)
np.savez_compressed(out/'wind_basis.npz',vertices=v,edges=edges,basis=np.array(deltas),grid=g,control_basis=D)
(out/'wind_basis.json').write_text(json.dumps({'parameters':names,'note':'Solidify disabled for central sheet boundary; evaluated solid must be reviewed separately.'}))
print('WINDSCREEN_BASIS',len(v),len(edges),flush=True)
