"""Resolve the local r10 tank/seat overlap without moving reviewed control cages.
Uses the existing shared seat-clearance operand; no new photo camera; one hidden triangulated operand.
3 mm is a construction allowance, never a claim of measured motorcycle clearance.
The rejected direct-control-point experiment is archived locally in qa/blends.
"""
from pathlib import Path
import bpy,json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
name=args[0] if args else '11_tank_triangulated_candidate.blend'
if Path(name).name!=name or not name.endswith('.blend'):raise ValueError('New local blend filename required')
out=V2/'blends'/name
if out.exists():raise FileExistsError(out)
if s.get('revision')!='r10':raise RuntimeError('Expected isolated r10 source')
frozen=V2/'calibration/r10_interface_frozen';frozen.mkdir(exist_ok=True)
inputs=list((V2/'data/control_cages').glob('*.json'))+list((V2/'calibration').glob('camera_*.json'))+list((V2/'annotations').glob('*.json'))
for p in (V2/'data/control_cages').glob('*.json'):
 if not (frozen/p.name).exists():shutil.copy2(p,frozen/p.name)
p=frozen/'manifest.json'
if not p.exists():p.write_text(json.dumps({str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in inputs},indent=2),encoding='utf8')
seat=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'));tank=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Body_Tank.json'));helper=next(o for o in s.objects if o.get('construction_role')=='rider_clearance_operand')
if helper.data!=seat.data:raise RuntimeError('Clearance operand is stale; synchronize rider mesh first')
if any(o.get('construction_role')=='tank_seat_clearance_operand' for o in s.objects):raise RuntimeError('Tank interface already installed')
# Triangulate both operands before the exact cut: warped quads otherwise
# yielded seven nonadjacent self-intersection candidates along the cut rim.
operand=helper.copy();operand.data=seat.data;operand.name='Tool_TankSeatClearance'
next(c for c in s.collection.children if c.name.startswith('Collection_Blockout')).objects.link(operand)
operand['construction_role']='tank_seat_clearance_operand';operand['export_exclude']=True;operand.hide_render=True;operand.hide_select=True
tri=operand.modifiers.new('Stable_Operand_Triangles','TRIANGULATE');tri.quad_method='FIXED';tri.ngon_method='BEAUTY'
tri=tank.modifiers.new('Stable_Interface_Triangles','TRIANGULATE');tri.quad_method='FIXED';tri.ngon_method='BEAUTY'
mod=tank.modifiers.new('Editable_RiderSeatInterface','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=operand
# Preserve the full editable cage; cut only its evaluated intersection envelope.
tank['interface_note']='Existing 3mm seat-clearance envelope; modeled allowance, photo shape acceptance pending.'
tank['acceptance']='pending_interface_photo_review';s['revision']='r11';s.name='GSX250R_Reconstruction_V2_Gray_r11';s['visual_acceptance']='NOT_PASSED'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out))
result={'candidate':out.name,'blender_version':bpy.app.version_string,'control_vertices_moved':0,'new_objects':1,'existing_clearance_mm':helper.get('clearance_mm'),'status':'NOT_PASSED'}
print(json.dumps(result,indent=2))