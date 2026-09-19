"""Replace the existing mid-side cover with the rebuilt candidate, never layer both."""
from pathlib import Path
import bpy
V=Path(__file__).resolve().parents[1]
def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if not scene.objects.get('Body_FrameSidePanel') or not scene.objects.get('Body_MidSideCover'):raise ValueError('Requires the explicit r24 migration state')
 old=scene.objects['Body_MidSideCover'];new=scene.objects['Body_FrameSidePanel'];bpy.data.objects.remove(old,do_unlink=True)
 new.name='Body_MidSideCover';new.data.name='Body_MidSideCover_RebuiltMesh';new['control_cage_source']='reconstruction_v2/data/control_cages/Body_MidSideCover.json';new['revision']='r25';new['replaces_old_mid_side_cover']=True
 scene['stage_b_mid_cover_replaced']=True;scene['revision']='r25';scene.name='GSX250R_Reconstruction_V2_Gray_r25';scene['stage_B']='NOT_PASSED';scene['stage_C']='NOT_PASSED';scene['scope_r25']='Windscreen, mirror shells, replacement mid-side covers, left sprocket cover, rear shock and compact mounts'
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(output));return {'saved':str(output),'objects':len(scene.objects),'cages':sum(bool(o.get('control_cage_source')) for o in scene.objects)}
