"""Finish nonfolding sidelight backing and conformal seat undertray."""
from pathlib import Path
import bpy,bmesh,sys,json
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_shapes import get,setup_helpers
import build_gray as bg

def run():
 s=bpy.context.scene
 if s.get('revision')!='r41':raise ValueError('Requires r41')
 setup_helpers(s)
 from refine_position_lamps_owner import build
 build(s)
 sd=get(s,'Seat_Pillion');grid=[]
 for row in sd['grid']:
  grid.append([[p[0]+(1.3 if j<2 else 0),p[1],p[2]-2.0] for j,p in enumerate(row[3:])])
 data={'name':'Seat_Pillion_Pan','grid':grid,'material':'trim','units':'mm','mirror_x':True,'subdivision':2,'thickness_mm':2,'crease_boundary':.3,'revision':'r42'}
 pan=bg.cage(data);pan['control_cage_source']='reconstruction_v2/data/current_controls/Seat_Pillion_Pan.json';(V/'data/current_controls/Seat_Pillion_Pan.json').write_text(json.dumps(data,indent=2))
 o=s.objects['Body_PillionBase'];m=o.modifiers.new('Interface_roundoff_weld','WELD');m.merge_threshold=.000003
 from close_pillion_sides import apply as close_sides
 close_sides(s)
 from finish_surface_checks import apply
 apply(s)
 from close_outer_seat_transition import apply as outer_panel
 outer_panel(s)
 from attach_steering_controls import apply as attach_controls
 attach_controls(s)
 s['revision']='r42';s.name='GSX250R_Reconstruction_V2_Gray_r42';bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'revision':'r42','changes':['closed position lamp bezel replaces folded backing','conformal pillion seat pan'],'objects':len(s.objects)}
