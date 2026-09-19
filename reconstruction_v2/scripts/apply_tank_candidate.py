"""Apply one r14 tank candidate to an isolated r13 file, with explicit caps.
The original and canonical JSON remain untouched until the candidate is reviewed.
"""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene
if s.get('revision')!='r13':raise RuntimeError('Expected r13 source')
args=sys.argv[sys.argv.index('--')+1:];candidate=args[0];tag=args[1];width=float(args[2]) if len(args)>2 else 0
if any(Path(x).name!=x or x in ('.','..') for x in [candidate,tag]):raise ValueError('Local candidate names only')
out=V2/f'blends/{tag}.blend'
if out.exists():raise FileExistsError(out)
a=json.loads((V2/f'qa/{candidate}.json').read_text());a['cap_ends']=True;a['thickness_mm']=0
o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Body_Tank.json'));old=o.data
ns={'__name__':'gsx_api','__file__':str(V2/'scripts/build_gray.py')};exec(compile(Path(ns['__file__']).read_text(encoding='utf8'),ns['__file__'],'exec'),ns)
m=bpy.data.meshes.new('Body_Tank_ClosedQuadControl_'+tag);m.from_pydata([[x*.001 for x in p] for row in a['grid'] for p in row],[],ns['cage_faces'](a));m.update()
for mat in old.materials:m.materials.append(mat)
o.data=m;bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
for p in m.polygons:p.use_smooth=True
ns['apply_creases'](o,a);solid=o.modifiers.get('Shell_Thickness')
if solid:o.modifiers.remove(solid)
if width:
 bevel=o.modifiers.new('Editable_Interface_Rounding','BEVEL');bevel.width=width*.001;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.6;bevel.use_clamp_overlap=True
s['revision']=tag;s['visual_acceptance']='NOT_PASSED';bpy.context.view_layer.update()
# Keep filler assembly's existing XY and match the newly edited external skin.
e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());ok,hit,normal,index=e.ray_cast(Vector((0,.188,1.3)),Vector((0,0,-1)))
if not ok:raise RuntimeError('Tank crown ray failed')
cap=s.objects.get('FuelCap');core=s.objects.get('FuelCap_Core');change=hit.z+.003-cap.location.z
for obj in [cap,core]:obj.location.z+=change
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out));a['revision']=a.get('revision','candidate');a['revision_note']='Closed quad ends and independent tank rear/crown controls; shell removed from closed volume. Fixed 62/63/69 cameras; no real-world precision claim.';a['interface_rounding_mm']=width
(V2/f'qa/{tag}_cage.json').write_text(json.dumps(a,indent=2),encoding='utf8')
result={'source':str(out),'tank_quads':len(m.polygons),'rounding_mm':width,'fuel_cap_z_shift_mm':change*1000,'canonical_changed':False}
