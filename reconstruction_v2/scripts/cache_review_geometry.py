"""Cache expensive live construction output only in a disposable render session."""
import bpy

def cache_review_assembly(scene):
 o=scene.objects.get('Body_NoseAssembly')
 if not o or not any(m.type=='NODES' for m in o.modifiers):return
 bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
 me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
 o.modifiers.clear();o.data=me
