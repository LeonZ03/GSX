"""Apply a reviewed rider-seat proposal to a new isolated Blender file.
Only writes qa/blend artifacts; canonical control JSON is promoted separately.
"""
from pathlib import Path
import bpy,bmesh,json,sys
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
name=args[0] if args else '10_rider_candidate.blend'
if Path(name).name!=name or not name.endswith('.blend'):raise ValueError('New local blend filename required')
out=V2/'blends'/name
if out.exists():raise FileExistsError(out)
if s.get('revision')!='r09':raise RuntimeError('Expected isolated r09')
a=json.loads((V2/'qa/Seat_Rider_r10_candidate.json').read_text())
ns={'__name__':'gsx_api','__file__':str(V2/'scripts/build_gray.py')};exec(compile(Path(ns['__file__']).read_text(encoding='utf8'),ns['__file__'],'exec'),ns)
o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'));old=o.data
m=bpy.data.meshes.new('Seat_Rider_r10_Control');m.from_pydata([[v*.001 for v in p] for row in a['grid'] for p in row],[],ns['cage_faces'](a));m.update()
for mat in old.materials:m.materials.append(mat)
o.data=m;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
for f in m.polygons:f.use_smooth=True
ns['apply_creases'](o,a);o['acceptance']='pending_three_view_review'
if '--include-joins' in args:
 for part in ['Body_SeatSide','Body_PillionBase']:
  a=json.loads((V2/f'qa/{part}_r10_candidate.json').read_text());o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/'+part+'.json'))
  points=[p for row in a['grid'] for p in row]
  expected={tuple(sorted(f)) for f in ns['cage_faces'](a)}
  if len(points)!=len(o.data.vertices) or expected!={tuple(sorted(f.vertices)) for f in o.data.polygons}:raise RuntimeError('Unexpected join topology')
  for v,p in zip(o.data.vertices,points):v.co=[c*.001 for c in p]
  o.data.update();ns['apply_creases'](o,a);o['acceptance']='pending_interface_review'
s.name='GSX250R_Reconstruction_V2_Gray_r10';s['revision']='r10';s['visual_acceptance']='NOT_PASSED';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out));print('ISOLATED_RIDER_CANDIDATE',name)