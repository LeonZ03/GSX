"""Extract an exact linear subdivision basis for a small rider-seat candidate.
Read a saved r09 in an isolated process. No source file or JSON is modified.
"""
from pathlib import Path
import json,sys,bpy,bmesh,numpy as np,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path.insert(0,str(V2/'scripts'))
from seat_parameters import basis,NAMES,LOWER,UPPER
s=bpy.context.scene
if s.get('revision')!='r09':raise RuntimeError('Expected isolated r09 source')
frozen=V2/'calibration/r09_tail_frozen';frozen.mkdir(exist_ok=True)
inputs=list((V2/'data/control_cages').glob('*.json'))+list((V2/'calibration').glob('camera_*.json'))+list((V2/'annotations').glob('*.json'))
for p in (V2/'data/control_cages').glob('*.json'):
 if not (frozen/p.name).exists():shutil.copy2(p,frozen/p.name)
p=frozen/'manifest.json'
if not p.exists():p.write_text(json.dumps({str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in inputs},indent=2),encoding='utf8')
a=json.loads((frozen/'Seat_Rider.json').read_text());a['cap_ends']=True;a['crease_boundary']=0.;a['crease_columns']={'3':.35,'4':.45}
ns={'__name__':'gsx_api','__file__':str(V2/'scripts/build_gray.py')};exec(compile(Path(ns['__file__']).read_text(encoding='utf8'),ns['__file__'],'exec'),ns)
o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'));g=np.asarray(a['grid'],float);d=basis(g);old=o.data
m=bpy.data.meshes.new('Seat_Rider_Basis');m.from_pydata((g.reshape(-1,3)*.001).tolist(),[],ns['cage_faces'](a));m.update()
for mat in old.materials:m.materials.append(mat)
o.data=m
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();ns['apply_creases'](o,a)
def sample(q):
 pts=(g+np.einsum('k,kijc->ijc',q,d)).reshape(-1,3)*.001
 for v,co in zip(m.vertices,pts):v.co=co
 m.update();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();v=np.array([list(e.matrix_world@v.co) for v in me.vertices]);f=np.array([list(t.vertices) for t in me.loop_triangles]);e.to_mesh_clear();return v,f
zero=np.zeros(len(NAMES));v,f=sample(zero);delta=[]
for k in range(len(NAMES)):
 q=zero.copy();q[k]=1;vk,fk=sample(q);assert np.array_equal(fk,f);delta.append(vk-v)
b=np.array(delta);q=np.linspace(-3,3,len(NAMES));check,_=sample(q);err=float(np.max(np.abs(check-v-np.einsum('k,kvc->vc',q,b))))
assert err<2e-6,err
np.savez_compressed(V2/'qa/seat_basis_r10.npz',vertices=v,triangles=f,basis=b,control_grid=g,control_basis=d,lower=LOWER,upper=UPPER)
(V2/'qa/seat_basis_r10.json').write_text(json.dumps({'parameters':NAMES,'cage_template':a,'linearity_error_m':err,'status':'candidate_only'},indent=2),encoding='utf8')
print('SEAT_BASIS',len(v),'vertices',len(NAMES),'parameters; linearity error m',err)