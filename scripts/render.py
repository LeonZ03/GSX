"""Render named cameras; use -- --preview for small Cycles QA images."""
import bpy,sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
preview='--preview' in args
scene=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
bpy.context.window.scene=scene
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX'; prefs.get_devices()
    for dev in prefs.devices: dev.use=(dev.type=='OPTIX')
    scene.cycles.device='GPU'
except Exception: scene.cycles.device='CPU'
scene.render.engine='CYCLES';scene.cycles.use_denoising=True
scene.cycles.samples=24 if preview else 160
scene.cycles.adaptive_threshold=.04 if preview else .01
scene.render.resolution_x=1400 if preview else 3840
scene.render.resolution_y=1000 if preview else 2160
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
cams=[a for a in args if a.startswith('Camera_')] or ['Camera_Front_3Q','Camera_Right_Ortho','Camera_Rear_3Q']
if preview:
    bpy.data.objects['LicensePlate_Region'].data.body='LOCAL'
    bpy.data.objects['LicensePlate_Number'].data.body='GSX250'
report=[]
for cam in cams:
    scene.camera=bpy.data.objects[cam]
    path=ROOT/'renders'/('checks' if preview else 'final')/(cam.replace('Camera_','')+'.png')
    path.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(path)
    start=time.time();bpy.ops.render.render(write_still=True)
    report.append({'camera':cam,'path':str(path.relative_to(ROOT)),'seconds':round(time.time()-start,2),'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':scene.cycles.samples,'device':scene.cycles.device})
    (ROOT/'qa'/('preview_render.json' if preview else 'final_render.json')).write_text(json.dumps(report,indent=2))
print('GSX_RENDER_COMPLETE')
