"""Deterministic neutral inspection renders, independent of photo fitting."""
from pathlib import Path
import bpy,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1]

def cameras(scene):
 col=next(c for c in scene.collection.children if c.name.startswith('Collection_Cameras'))
 configs={'Front':((2.8,3.2,1.65),(0,.15,.64),2.5),
 'Rear':((-2.8,-3.2,1.6),(0,-.12,.65),2.45),
 'Nose':((1.4,2.7,1.1),(0,.61,.88),.90),
 'Cockpit':((.70,-1.4,2.15),(0,.40,.96),.82),
 'RightEngine':((3.1,-.2,.70),(0,-.10,.44),1.15),
 'LeftDrive':((-3.1,-.65,.8),(0,-.50,.40),1.2)}
 out={}
 for key,(eye,target,scale) in configs.items():
  name='Camera_Inspect_'+key;o=scene.objects.get(name)
  if not o:
   d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);col.objects.link(o)
  o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;out[key]=o
 return out

def render(scene,tag,keys):
 sys.path.insert(0,str(V/'scripts'))
 from cache_review_geometry import cache_review_assembly
 cache_review_assembly(scene)
 cams=cameras(scene);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
 scene.render.resolution_x=1440;scene.render.resolution_y=1080;scene.render.resolution_percentage=75
 scene.render.film_transparent=False;scene.render.use_border=False;scene.render.use_crop_to_border=False
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
 try:
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
  for d in p.devices:d.use=d.type=='CUDA'
  scene.cycles.device='GPU'
 except Exception:scene.cycles.device='CPU'
 out=V/'renders/stage_bc';out.mkdir(exist_ok=True)
 for key in keys:
  scene.camera=cams[key];scene.render.filepath=str(out/f'{tag}_{key}.png');bpy.ops.render.render(write_still=True)
 return {'renders':[str(out/f'{tag}_{key}.png') for key in keys]}
