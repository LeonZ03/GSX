"""Fixed-camera native-resolution interface crops; no source scene is saved."""
from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene;tag=s.get('revision');out=V2/'renders/interface_r11';out.mkdir(exist_ok=True)
BOXES={62:(555,740,720,880),63:(470,780,635,920),69:(925,540,1090,680)}
s.render.engine='CYCLES';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.resolution_percentage=100;s.cycles.samples=32;s.render.film_transparent=True;s.render.use_border=True;s.render.use_crop_to_border=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='CUDA'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
for k,(x0,y0,x1,y1) in BOXES.items():
 c=json.loads((V2/f'calibration/camera_{k}.json').read_text());w,h=c['image_size'];s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.get('image_id')==k)
 s.render.resolution_x=w;s.render.resolution_y=h;s.render.border_min_x=x0/w;s.render.border_max_x=x1/w;s.render.border_min_y=1-y1/h;s.render.border_max_y=1-y0/h
 s.render.filepath=str(out/f'crop_{tag}_{k}.png');bpy.ops.render.render(write_still=True)
print('NATIVE_INTERFACE_CROPS',tag)