"""Non-destructive seat clearance on two adjoining tail shells.
The hidden operand shares the rider control mesh; source cages remain editable.
3 mm is a construction allowance, not a measured real-world gap.
"""
from pathlib import Path
import bpy,sys
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
name=args[0] if args else '10_seat_clearance_candidate.blend'
if Path(name).name!=name or not name.endswith('.blend'):raise ValueError('Local blend filename required')
out=V2/'blends'/name
if out.exists():raise FileExistsError(out)
if s.get('revision')!='r10':raise RuntimeError('Expected r10 seat candidate')
seat=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'))
if any(o.get('construction_role')=='rider_clearance_operand' for o in s.objects):raise RuntimeError('Clearance already installed; do not duplicate')
col=next(c for c in s.collection.children if c.name.startswith('Collection_Blockout'))
helper=seat.copy();helper.data=seat.data;helper.name='Tool_SeatClearance';col.objects.link(helper)
for k in list(helper.keys()):del helper[k]
helper['construction_role']='rider_clearance_operand';helper['clearance_mm']=3.;helper['export_exclude']=True;helper.hide_render=True;helper.hide_select=True;helper.display_type='WIRE'
con=helper.constraints.new('COPY_TRANSFORMS');con.target=seat
expand=helper.modifiers.new('Construction_Clearance_3mm','DISPLACE');expand.direction='NORMAL';expand.strength=.003;expand.mid_level=0.
for part in ['Body_SeatSide','Body_PillionBase']:
 o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/'+part+'.json'))
 mod=o.modifiers.new('Editable_SeatClearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=helper
 o['clearance_note']='3mm construction allowance; preserve editable cage and boolean; not actual measured fit.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out));print('SEAT_CLEARANCE_SAVED',out.name)