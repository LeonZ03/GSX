"""Render-only polish: framing, clean background, and local privacy verification."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(os.environ.get('GSX_ROOT',Path(__file__).resolve().parents[1]))
s=next(x for x in bpy.data.scenes if x.name.startswith('GSX250R_User_Reconstruction'))
for name in ['Camera_Front_3Q','Camera_Rear_3Q','Camera_Left_3Q']:bpy.data.objects[name].data.lens=53
nodes=s.world.node_tree.nodes;links=s.world.node_tree.links
out=next(n for n in nodes if n.type=='OUTPUT_WORLD');envbg=next(n for n in nodes if n.type=='BACKGROUND')
flat=nodes.new('ShaderNodeBackground');flat.name='Camera_Background';flat.inputs[0].default_value=(.09,.115,.15,1);flat.inputs[1].default_value=.65
rays=nodes.new('ShaderNodeLightPath');mix=nodes.new('ShaderNodeMixShader');links.new(rays.outputs['Is Camera Ray'],mix.inputs[0]);links.new(envbg.outputs[0],mix.inputs[1]);links.new(flat.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs[0])
private=json.loads((ROOT/'config/user.local.json').read_text('utf-8')) if (ROOT/'config/user.local.json').exists() else {'plate_top':'LOCAL','plate_bottom':'GSX250'}
checks={'plate_text_matches_private_config':bpy.data.objects['LicensePlate_Region'].data.body==private['plate_top'] and bpy.data.objects['LicensePlate_Number'].data.body==private['plate_bottom'],'reference_objects_in_final':sum(o.name.startswith('Reference_') for o in s.objects),'blockout_objects_in_final':sum(o.name.startswith('Blockout_') for o in s.objects),'scene_count':len(bpy.data.scenes),'missing_images':[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]}
(ROOT/'qa/source_integrity.json').write_text(json.dumps(checks,indent=2))
s['revision']='r5.1: cleaned decals, optical corrections and final framing'
s.cycles.samples=160;s.cycles.adaptive_threshold=.01;s.render.resolution_x=3840;s.render.resolution_y=2160
for name in ['09_lighting_render','10_final']:bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blends'/(name+'.blend')),compress=True)
print(checks)
