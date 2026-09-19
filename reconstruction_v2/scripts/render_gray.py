"""Neutral gray, fixed photo-camera renders. No model file is saved here."""
from pathlib import Path
import bpy,json,math,re,sys
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_Reconstruction_V2_Gray'));bpy.context.window.scene=s
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ids=[int(x) for x in args if x.isdigit()] or [62,63]
tag=next((x for x in args if re.fullmatch(r'r\d+',x)),s.get('revision','r01'))
subdir=next((x[4:] for x in args if x.startswith('out=')),'')
if subdir and (Path(subdir).name!=subdir or subdir in ('.','..')):raise ValueError('Output subdirectory must be a local name')
render_dir=V2/'renders'/subdir;render_dir.mkdir(exist_ok=True)
sys.path.insert(0,str(V2/'scripts'))
from cache_review_geometry import cache_review_assembly
cache_review_assembly(s)
percentage=60
samples=int(next((x.split('=',1)[1] for x in args if x.startswith('samples=')),'24'))
if not 8<=samples<=128:raise ValueError('Review samples must be 8..128')
s.render.resolution_percentage=percentage;s.cycles.samples=samples;s.render.film_transparent=True
s.render.use_border=False;s.render.use_crop_to_border=False
# GPU use re-checked in the actual rendering process.
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
 for device in p.devices:device.use=device.type=='CUDA'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
steer_prefix=('Tire_Front','Wheel_Front','Spoke_Front','Hub_Front','Axle_Front','BrakeDisc_Front','Caliper_Front','RotorCarrier_Front','Fork_','Fender_Front')
steering=[o for o in s.objects if o.name.startswith(steer_prefix) or o.get('steer_with_front',False)];original={o:o.matrix_world.copy() for o in steering}
visibility={o:o.hide_render for o in s.objects if o.name.startswith(('GuardBar','GuardMount'))}
for k in ids:
 for o,original_hide in visibility.items():o.hide_render=original_hide
 c=json.loads((V2/f'calibration/camera_{k}.json').read_text());s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.get('image_id')==k)
 s.render.resolution_x=c['image_size'][0];s.render.resolution_y=c['image_size'][1]
 if c.get('steering_model')=='raked_axis_25_6_trail104':
  rake=math.radians(25.6);axis=Vector((0,-math.sin(rake),math.cos(rake)));pivot=Vector((0,.819,0))
 else:axis=Vector((0,0,1));pivot=Vector((0,.715,.3039))
 T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(c['front_steer_deg']),4,axis)@Matrix.Translation(-pivot)
 for o in steering:o.matrix_world=T@original[o]
 s.render.filepath=str(render_dir/f'gray_{tag}_{k}.png');bpy.ops.render.render(write_still=True)
 for o in steering:o.matrix_world=original[o]
 print('GRAY_RENDER_COMPLETE',k,flush=True)
for o,original_hide in visibility.items():o.hide_render=original_hide
