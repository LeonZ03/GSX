"""Three frozen-camera native tank crops for r14 review; never save scene."""
from pathlib import Path
import bpy,json,math,sys
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene;tag=s.get('revision');out=V2/'renders/interface_r14';out.mkdir(exist_ok=True);ann=json.loads((V2/'annotations/tank_crown_r14.json').read_text())
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.film_transparent=True;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='CUDA'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
ids='--ids' in sys.argv or '--ids-full' in sys.argv
full='--ids-full' in sys.argv
if ids:
 s.cycles.samples=1;s.cycles.use_denoising=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
 def emission(name,color):
  mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.node_tree.nodes.clear();node=mat.node_tree.nodes.new('ShaderNodeEmission');node.inputs['Color'].default_value=(*color,1);node.inputs['Strength'].default_value=1;outnode=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(node.outputs[0],outnode.inputs['Surface']);return mat
 black=emission('DIAG_Occluder',(0,0,0));colors={key:emission('DIAG_'+key,rgb) for key,rgb in [('Body_Tank',(1,0,0)),('Seat_Rider',(0,1,0)),('Body_TankSideTrim',(0,0,1))]}
 for o in s.objects:
  if o.type not in ['MESH','CURVE','FONT']:continue
  part=Path(o.get('control_cage_source','')).stem;mat=colors.get(part,black)
  if not o.material_slots:o.data.materials.append(black)
  for slot in o.material_slots:slot.link='OBJECT';slot.material=mat
 tag+=('_ids_full' if full else '_ids')
metadata={}
for key,a in ann['views'].items():
 k=int(key);c=json.loads((V2/f'calibration/camera_{k}.json').read_text());w,h=c['image_size'];x0,y0,x1,y1=a['crop'];s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.get('image_id')==k);s.render.resolution_x=w;s.render.resolution_y=h
 s.render.border_min_x=x0/w;s.render.border_max_x=x1/w;s.render.border_min_y=1-y1/h;s.render.border_max_y=1-y0/h
 s.render.use_border=not full;s.render.use_crop_to_border=not full
 s.render.filepath=str(out/f'crop_{tag}_{k}.png');bpy.ops.render.render(write_still=True)
 metadata[key]={'requested_crop':a['crop'],'blender_border_fractions':[s.render.border_min_x,s.render.border_max_x,s.render.border_min_y,s.render.border_max_y]}
(out/f'crop_{tag}_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8');print('INTERFACE_NATIVE_CROPS',tag,flush=True)