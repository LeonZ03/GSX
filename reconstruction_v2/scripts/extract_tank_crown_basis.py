"""Extract tank subdivision response for fixed-camera shape refinement, r13 only.
The shell/seat Boolean is excluded ONLY from the linear proposal model; final
candidates are evaluated with the full modifier stack before they can be kept.
"""
from pathlib import Path
import bpy,json,hashlib,shutil,numpy as np
ROOT=Path(__file__).resolve().parents[2]; V2=ROOT/'reconstruction_v2';s=bpy.context.scene
if s.get('revision')!='r13':raise RuntimeError('Expected r13 source')
out=V2/'qa/tank_crown_basis_r14.npz'
if out.exists():raise FileExistsError(out)
frozen=V2/'calibration/r13_tank_frozen';frozen.mkdir(exist_ok=True)
inputs=list((V2/'data/control_cages').glob('*.json'))+list((V2/'calibration').glob('camera_*.json'))+list((V2/'annotations').glob('*.json'))+[Path(bpy.data.filepath)]
for p in (V2/'data/control_cages').glob('*.json'):
 if not (frozen/p.name).exists():shutil.copy2(p,frozen/p.name)
manifest=frozen/'manifest.json'
if not manifest.exists():manifest.write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2),encoding='utf8')
a=json.loads((frozen/'Body_Tank.json').read_text());g=np.array(a['grid']);o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Body_Tank.json'))
if np.max(abs(np.array([list(v.co) for v in o.data.vertices])*1000-g.reshape(-1,3)))>.01:raise RuntimeError('Cage mismatch')

import bmesh
a['cap_ends']=True;a['thickness_mm']=0
ns={'__name__':'gsx_api','__file__':str(V2/'scripts/build_gray.py')};exec(compile(Path(ns['__file__']).read_text(encoding='utf8'),ns['__file__'],'exec'),ns)
old=o.data;m=bpy.data.meshes.new('Tank_Closed_Crown_Basis');m.from_pydata((g.reshape(-1,3)*.001).tolist(),[],ns['cage_faces'](a));m.update()
for mat in old.materials:m.materials.append(mat)
o.data=m;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();ns['apply_creases'](o,a)

for m in o.modifiers:
 if m.type not in ('MIRROR','SUBSURF'):m.show_viewport=False;m.show_render=False
basis=[];names=[];lower=[];upper=[]
for row in range(9):
 for kind,axis,profile,lo,hi in [('width',0,g[row,:,0]/max(g[row,:,0]),-35,35),('upper_y',1,np.array([1,1,.85,.4,0,0,0,0]),-65,25),('lower_y',1,np.array([0,0,.15,.6,1,1,1,1]),-40,40),('height',2,np.array([1,1,.9,.7,.35,0,0,0]),-30,30)]:
  b=np.zeros_like(g);b[row,:,axis]=profile;basis.append(b);names.append(f'{row}_{kind}');lower.append(lo);upper.append(hi)
d=np.array(basis)
def sample(q):
 pts=(g+np.einsum('k,kijc->ijc',q,d)).reshape(-1,3)*.001
 for v,co in zip(o.data.vertices,pts):v.co=co
 o.data.update();bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();me.calc_loop_triangles();v=np.array([list(e.matrix_world@p.co) for p in me.vertices]);f=np.array([list(t.vertices) for t in me.loop_triangles]);e.to_mesh_clear();return v,f
q=np.zeros(len(names));v,f=sample(q);delta=[]
for i in range(len(names)):
 p=q.copy();p[i]=10;vi,fi=sample(p);assert np.array_equal(fi,f);delta.append((vi-v)/10)
b=np.array(delta);p=np.linspace(-6,6,len(names));check,_=sample(p);err=float(abs(check-v-np.einsum('k,kvc->vc',p,b)).max());assert err<2e-6,err
np.savez_compressed(out,vertices=v,triangles=f,basis=b,control_grid=g,control_basis=d,lower=lower,upper=upper)
(V2/'qa/tank_crown_basis_r14.json').write_text(json.dumps({'parameters':names,'cage_template':a,'linearity_error_m':err,'scope':'proposal outer skin only; final full stack required'},indent=2),encoding='utf8')
result={'parameters':len(names),'vertices':len(v),'linearity_error_m':err,'saved_scene':False}
