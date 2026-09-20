"""Finish r45 trim interfaces and save explicit editable assembly controls."""
from pathlib import Path
import bpy,bmesh,json,sys,hashlib
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_structure import init
from rebuild_owner_shapes import remove
from rebuild_clutch_r30 import loft

def run():
 s=bpy.context.scene
 if s.get('revision')!='r45':raise ValueError('Requires r45')
 b=init(s)
 from connect_owner_mounts import apply as connect
 connect(s)
 if 'Headlight_BrowSeal' not in s.objects:
  rows=[]
  for t in [0,.1,.9,1]:
   row=[]
   for x in [-91,-72,-42,0,42,72,91]:
    q=abs(x)/91;a=Vector((x,770-15*q*q,874+10*q*q));c=Vector((x,750-9*q*q,893+8*q*q));row.append(list(a.lerp(c,t)))
   rows.append(row)
  b.patch('Headlight_BrowSeal',rows,'black',2.5,1)
 # Stepped/octagonal cradle pad follows photo65, preserving all arm roots.
 c=Vector((-185,408,1001));u=Vector((1,0,0));v=Vector((0,.30,.953939));n=u.cross(v)
 for name,w,h,dep,th,mat in [('PhoneMount',62,82,0,12,'black'),('PhoneMount_RubberPad',51,67,7,3,'rubber')]:
  remove(s,name);outline=[(-w/2+9,-h/2),(-w/2,-h/2+12),(-w/2,h/2-12),(-w/2+9,h/2),(w/2-9,h/2),(w/2,h/2-12),(w/2,-h/2+12),(w/2-9,-h/2)]
  o=loft(s,name,[[list(c+u*x+v*y+n*d) for x,y in outline] for d in [dep-th/2,dep+th/2]],b.M[mat],.5);o['steer_with_front']=True
 # Save parameter/control geometry; no photos, pixel annotations, or cameras.
 controls={}
 prefixes=('PhoneMount','Cockpit_','Dashboard_','Lever_','SideStand','GuardBar','GuardMount','LicensePlate_','Exhaust_Header','Exhaust_Collector','Exhaust_LinkPipe','Exhaust_Chamber','Intake_','ThrottleBody','Airbox_','OxygenSensor','Indicator','Headlight_','Fairing_MountTab','Frame_SeatRail','Frame_HeadGusset','Frame_SteeringHead','SteeringStem_Column')
 for o in s.objects:
  if not o.name.startswith(prefixes) or o.type not in ('MESH','CURVE'):continue
  d={'type':o.type,'matrix_world':[list(r) for r in o.matrix_world],'materials':[m.name for m in o.data.materials],'hidden':o.hide_render,'steer_with_front':bool(o.get('steer_with_front'))}
  if o.type=='MESH':d.update(vertices_mm=[list(v.co*1000) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons])
  else:
   d['bevel_radius_mm']=o.data.bevel_depth*1000;d['fill_caps']=o.data.use_fill_caps;d['splines']=[]
   for sp in o.data.splines:
    z={'type':sp.type,'cyclic':sp.use_cyclic_u}
    if sp.type=='BEZIER':z['points']=[{'co_mm':list(p.co*1000),'left_mm':list(p.handle_left*1000),'right_mm':list(p.handle_right*1000),'left_type':p.handle_left_type,'right_type':p.handle_right_type} for p in sp.bezier_points]
    else:z['points']=[list(p.co) for p in sp.points]
    d['splines'].append(z)
  controls[o.name]=d
 out=V/'data/current_controls';(out/'assembly_r45.json').write_text(json.dumps({'revision':'r45','status':'NOT_PASSED','objects':controls},indent=2))
 for p in out.glob('*.json'):
  if p.name in ['manifest.json','assembly_r45.json','r39_shape_basis.json']:continue
  d=json.loads(p.read_text());d['current_snapshot']='r45';p.write_text(json.dumps(d,indent=2))
 for o in s.objects:
  if o.name in controls:o['current_control_snapshot']='reconstruction_v2/data/current_controls/assembly_r45.json'
 manifest={'revision':'r45','status':'NOT_PASSED','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.json') if p.name!='manifest.json'},'replay':'From committed r42: rebuild_owner_structure.run, rebuild_owner_front_underbody.run, repair_owner_integration.run, finish_owner_fifteen.run. Historical candidate steps have known defects fixed by the following migration; never run them on refined source. Current blend remains authoritative; independent full replay not yet verified.'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'snapshot_objects':len(controls),'status':'NOT_PASSED'}
