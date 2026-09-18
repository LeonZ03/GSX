"""Explicit, isolated r08 -> r09 seat/tail migration; never replays over fine edits.
Run in background Blender with the frozen 08_gray_review.blend input.
Requires local r08_tail_frozen snapshots. Camera and unrelated geometry stay fixed.
The 69 camera is provisional: these shape changes remain unaccepted.
"""
from pathlib import Path
import json,sys,bpy,bmesh
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=V2/'blends'/(args[0] if args else '09_gray_review.blend')
if out.exists() or out.parent!=V2/'blends':raise FileExistsError('New local output name required')
s=bpy.context.scene
if s.get('revision')!='r08':raise RuntimeError('Migration only accepts frozen r08')
ns={'__name__':'gsx_api','__file__':str(V2/'scripts/build_gray.py')}
exec(compile(Path(ns['__file__']).read_text(encoding='utf8'),ns['__file__'],'exec'),ns)
source=V2/'calibration/r08_tail_frozen';changed=[]
for name in ['Seat_Pillion','Body_Tail']:
 a=json.loads((source/(name+'.json')).read_text());g=a['grid']
 if name=='Seat_Pillion':
  # Visible cushion step in 69; capped front replaces the old open wafer edge.
  for j,row in enumerate(g):
   upper=[87,87,88,90,94,96,96][j];lower=upper-15
   for i,p in enumerate(row):
    p[2]+=upper if i<4 else lower
    p[1]+=60
    if i in (3,4):p[0]*=1.06
  a['cap_ends']=True;a['crease_boundary']=0.45;a['crease_columns']={'3':0.35,'4':0.4}
 elif name=='Body_Tail':
  for j,row in enumerate(g):
   top=[91,91,90,78,35,0][j];bottom=[91,87,70,46,15,0][j]
   for i,p in enumerate(row):p[2]+=top if i<=2 else bottom
  a['crease_columns']={'2':0.4,'3':0.3}
 a['revision']='r09';a['acceptance']='pending_fixed_camera_review'
 a['revision_note']='Seat/tail-only candidate. r08 cameras frozen; 69 provisional; no dimensional acceptance.'
 p=V2/'data/control_cages'/(name+'.json');p.write_text(json.dumps(a,indent=2),encoding='utf8')
 o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/'+name+'.json'))
 old=o.data;mesh=bpy.data.meshes.new(name+'_r09_Control');mesh.from_pydata([[c*.001 for c in p] for row in g for p in row],[],ns['cage_faces'](a));mesh.update()
 for m in old.materials:mesh.materials.append(m)
 o.data=mesh
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 for p in mesh.polygons:p.use_smooth=True
 ns['apply_creases'](o,a);o['acceptance']='pending';changed.append(name)
# Keep failed rider-seat experiments out of the retained candidate.
for name in ['Seat_Rider','Body_SeatSide']:
 (V2/'data/control_cages'/(name+'.json')).write_bytes((source/(name+'.json')).read_bytes())
# Visible black transition below the pillion front in photo69, with hidden
# attachment depth explicitly provisional. It joins beneath the rider seat.
seat=json.loads((V2/'data/control_cages/Seat_Pillion.json').read_text())
rows=[]
for row in seat['grid']:
 center=row[5];outer=row[4]
 rows.append([[0,center[1],center[2]-3],[outer[0]*.58,outer[1],center[2]-2],[outer[0],outer[1],outer[2]-3]])
rows.extend([[[0,-468,847],[70,-468,840],[122,-468,827]],[[0,-438,815],[72,-438,809],[126,-438,799]]])
base={'name':'Body_PillionBase','grid':rows,'mirror_x':True,'subdivision':2,'thickness_mm':3,'material':'trim','crease_boundary':0.6,'revision':'r09','acceptance':'pending','revision_note':'Visible pillion-to-rider black ramp from photo69. Hidden brackets and depth remain unverified.'}
ns['C'].update({k:next(c for c in s.collection.children if c.name.startswith('Collection_'+k)) for k in ['Body','FrontEnd']})
ns['M']['trim']=next(o.data.materials[0] for o in s.objects if o.get('control_cage_source','').endswith('/Body_SeatSide.json'))
(V2/'data/control_cages/Body_PillionBase.json').write_text(json.dumps(base,indent=2),encoding='utf8')
ns['cage'](base);changed.append(base['name'])
s.name='GSX250R_Reconstruction_V2_Gray_r09';s['revision']='r09';s['visual_acceptance']='NOT_PASSED'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('SEAT_TAIL_CANDIDATE',out.name,changed,flush=True)