"""Actual Blender geometry views; no generative images and no source saving."""
from pathlib import Path
import bpy
from mathutils import Vector
V=Path(__file__).resolve().parents[1]


def render(component='guard',tag='r46',keys=None):
    s=bpy.context.scene
    keep=lambda o: o.name.startswith(('GuardBar','GuardMount')) if component=='guard' else (o.name=='Body_Tank' or o.name.startswith('FuelCap'))
    for o in s.objects:
        if o.type in ('MESH','CURVE','FONT') and not keep(o):o.hide_render=True
    if component=='guard':
        # Single R assembly in all views makes the internal bracing legible.
        for o in s.objects:
            if keep(o) and o.name.endswith('_L'):o.hide_render=True
        configs={'Side':((2,.09,.44),(.24,.09,.44),.65),
                 'Front':((.24,2,.44),(.24,.09,.44),.65),
                 'Top':((.24,.09,2),(.24,.09,.44),.65),
                 'Oblique':((1.15,.83,.82),(.23,.09,.44),.67)}
    else:
        configs={'Side':((2,.08,.86),(0,.08,.86),.67),
                 'Top':((0,.08,2),(0,.08,.86),.68),
                 'Oblique':((.85,.76,1.50),(0,.08,.87),.69)}
    s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading
    sh.light='STUDIO';sh.studiolight_rotate_z=.5;sh.color_type='SINGLE';sh.single_color=(.35,.35,.35)
    sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1
    sh.background_type='WORLD';s.world.color=(.82,.82,.82);s.view_settings.view_transform='Standard'
    s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.use_border=False
    out=V/'renders/product_review';out.mkdir(exist_ok=True)
    col=next(c for c in s.collection.children if c.name.startswith('Collection_Cameras'))
    paths=[]
    for key in keys or configs:
        eye,target,scale=configs[key];data=bpy.data.cameras.new('Inspect_Product_'+key)
        cam=bpy.data.objects.new(data.name,data);col.objects.link(cam);cam.location=eye
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        data.type='ORTHO';data.ortho_scale=scale;s.camera=cam
        path=out/(tag+'_'+component+'_'+key+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);paths.append(str(path))
    return paths
