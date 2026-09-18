"""Render requested construction-stage check views; all outputs stay local."""
from pathlib import Path
import bpy,sys,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
plan=[('01_reference',['Camera_Right_Ortho']),('02_blockout',['Camera_Right_Ortho','Camera_Front_3Q']),('03_wheels',['Camera_Wheel_Detail']),('04_front_end',['Camera_Cockpit']),('05_engine_frame_exhaust',['Camera_Engine_Detail']),('06_body',['Camera_Front_3Q','Camera_Right_Ortho','Camera_Rear_3Q']),('08_materials',['Camera_Front_3Q','Camera_Right_Ortho','Camera_Rear_3Q'])]
for stage,cameras in plan:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blends'/(stage+'.blend')))
    s=next(x for x in bpy.data.scenes if x.name.startswith('GSX250R_User_Reconstruction'));bpy.context.window_manager.windows[0].scene=s
    for name in ['LicensePlate_Region','LicensePlate_Number']:
        o=bpy.data.objects.get(name)
        if o:o.data.body='LOCAL' if name.endswith('Region') else 'GSX250'
    if stage=='01_reference':
        # A rendered image plane supplements the non-rendering reference empties.
        images=list((ROOT/'IMG').glob('*_62_97.jpg'))
        if images:
            im=bpy.data.images.load(str(images[0]));data=bpy.data.meshes.new('ReferenceRender_Mesh')
            data.from_pydata([(0,-1.096,-.53),(0,.83,-.53),(0,.83,2.037),(0,-1.096,2.037)],[],[(0,1,2,3)]);data.update();uv=data.uv_layers.new()
            for li,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
            o=bpy.data.objects.new('ReferenceRender',data);s.collection.objects.link(o)
            mat=bpy.data.materials.new('ReferenceRender');mat.use_nodes=True;mat.node_tree.nodes.clear();out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;em=mat.node_tree.nodes.new('ShaderNodeEmission');mat.node_tree.links.new(tex.outputs['Color'],em.inputs[0]);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);data.materials.append(mat)
            s['alignment_note']='Perspective source, approximate wheelbase alignment only'
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
    s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    for name in cameras:
        s.camera=bpy.data.objects[name];s.render.filepath=str(ROOT/'renders/checks'/f'{stage}_{name[7:]}.png');bpy.ops.render.render(write_still=True)
    print('STAGE_CHECK_COMPLETE',stage,flush=True)
print('GSX_STAGE_CHECKS_COMPLETE')
