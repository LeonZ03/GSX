"""Render a diagnostic camera without changing a formal camera or saving source."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Matrix,Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from cache_review_geometry import cache_review_assembly
from rebuild_body_stage_b import setup_helpers
import build_gray as bg
args=sys.argv[sys.argv.index('--')+1:];c=json.loads(Path(args[0]).read_text());tag=args[1];s=bpy.context.scene;setup_helpers(s);cam=bg.camera_from_fit(c);s.camera=cam
cache_review_assembly(s)
a=math.radians(25.6);axis=Vector((0,-math.sin(a),math.cos(a)));pivot=Vector((0,.819,0));T=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(c['front_steer_deg']),4,axis)@Matrix.Translation(-pivot)
pre=('Tire_Front','Wheel_Front','Spoke_Front','Hub_Front','Axle_Front','BrakeDisc_Front','Caliper_Front','RotorCarrier_Front','Fork_','Fender_Front')
for o in s.objects:
 if o.name.startswith(pre) or o.get('steer_with_front'):o.matrix_world=T@o.matrix_world
s.render.resolution_x=c['image_size'][0];s.render.resolution_y=c['image_size'][1];s.render.resolution_percentage=60;s.cycles.samples=24;s.render.film_transparent=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
for d in p.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.render.filepath=str(V/f'renders/gray_{tag}_70_diagnostic.png');bpy.ops.render.render(write_still=True)
