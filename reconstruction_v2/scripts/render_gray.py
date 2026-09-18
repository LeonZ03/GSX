"""Neutral gray, fixed photo-camera renders. No model file is saved here."""
from pathlib import Path
import bpy,json,math,re,sys
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_Reconstruction_V2_Gray'));bpy.context.window.scene=s
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ids=[int(x) for x in args if x.isdigit()] or [62,63]
tag=next((x for x in args if x.startswith('r0')),'r01')
percentage=60
s.render.resolution_percentage=percentage;s.cycles.samples=24;s.render.film_transparent=True
# GPU use re-checked in the actual rendering process.
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
 for device in p.devices:device.use=device.type=='CUDA'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
steer_prefix=('Tire_Front','Wheel_Front','Spoke_Front','Hub_Front','Axle_Front','BrakeDisc_Front','Caliper_Front','RotorCarrier_Front','Fork_','Fender_Front')
steering=[o for o in s.objects if o.name.startswith(steer_prefix)];original={o:o.matrix_world.copy() for o in steering}
for k in ids:
 c=json.loads((V2/f'calibration/camera_{k}.json').read_text());s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.get('image_id')==k)
 s.render.resolution_x=c['image_size'][0];s.render.resolution_y=c['image_size'][1]
 pivot=Vector((0,.715,.3039));T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(c['front_steer_deg']),4,'Z')@Matrix.Translation(-pivot)
 for o in steering:o.matrix_world=T@original[o]
 s.render.filepath=str(V2/f'renders/gray_{tag}_{k}.png');bpy.ops.render.render(write_still=True)
 for o in steering:o.matrix_world=original[o]
 print('GRAY_RENDER_COMPLETE',k,flush=True)
