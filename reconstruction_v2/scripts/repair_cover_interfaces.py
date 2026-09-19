"""Retain editable panels and remove diagnosed local construction clashes."""
from pathlib import Path
import bpy,json,sys
V=Path(__file__).resolve().parents[1]
def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 a=json.loads((V/'data/revisions/r24/Body_FrameSidePanel.json').read_text());o=scene.objects['Body_FrameSidePanel']
 for v,p in zip(o.data.vertices,[p for row in a['grid'] for p in row]):v.co=[x*.001 for x in p]
 o.data.update()
 for name in ('Mirror_Stem_L','Mirror_Stem_R'):
  stem=scene.objects[name];stem.data.use_fill_caps=True;m=stem.modifiers.new('Join_Curve_Cap_Seams','WELD');m.merge_threshold=.000001
 src=scene.objects['Engine_AlternatorCover'];helper=src.copy();helper.name='Tool_SprocketCoverClearance';next(c for c in scene.collection.children if c.name.startswith('Collection_Blockout')).objects.link(helper)
 helper.hide_render=True;helper.hide_set(True);helper['export_exclude']=True;helper['clearance_mm']=1.0
 m=helper.modifiers.new('One_mm_Construction_Clearance','DISPLACE');m.strength=.001;m.mid_level=0;m.direction='NORMAL'
 o=scene.objects['Engine_SprocketCover'];m=o.modifiers.new('Editable_AdjacentCase_Clearance','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=helper
 m=o.modifiers.new('Boolean_Vertex_Join','WELD');m.merge_threshold=.000003
 scene['revision']='r24';scene.name='GSX250R_Reconstruction_V2_Gray_r24';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(output));return {'saved':str(output),'objects':len(scene.objects)}
