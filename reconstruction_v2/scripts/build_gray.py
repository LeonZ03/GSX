"""Build an independent editable gray reconstruction through Blender 5.2/MCP.
Does not touch r6.2. Main surfaces come from protected JSON control cages.
Mechanical pieces remain explicitly provisional until their dedicated review.
"""
from pathlib import Path
import bpy,sys,json,math,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'scripts'))
import build_motorcycle as b
C={};M={}

def empty(name,p,col):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.location=Vector(p)*.001;o.empty_display_size=.018;return o

def setup():
 # Always create an isolated scene; never clear existing objects or collections.
 base='GSX250R_Reconstruction_V2_Gray';name=base
 if name in bpy.data.scenes:
  i=2
  while f'{base}_{i}' in bpy.data.scenes:i+=1
  name=f'{base}_{i}'
 s=bpy.data.scenes.new(name);bpy.context.window.scene=s;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
 s['milestone']='M1 gray shape verification';s['visual_acceptance']='NOT_PASSED';s['unit_convention']='+X right +Y forward +Z up; metres'
 for n in ['Reference','Blockout','Wheels','FrontEnd','Engine','Body','Details','Materials','Lights','Cameras']:
  c=bpy.data.collections.new('Collection_'+n);s.collection.children.link(c);C[n]=c
 b.SC=s;b.C=C;b.COL=C['Body'];b.save=lambda *args:None
 b.materials()
 for m in b.M.values():
  n=next((x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');n.inputs['Base Color'].default_value=(.27,.27,.27,1);n.inputs['Metallic'].default_value=0;n.inputs['Roughness'].default_value=.65
  n.inputs['Transmission Weight'].default_value=0;n.inputs['Coat Weight'].default_value=0;n.inputs['Emission Strength'].default_value=0;m.diffuse_color=(.27,.27,.27,1)
 for key,g in [('shell',.48),('tank',.48),('trim',.12),('seat',.15),('lamp',.62),('wind',.32)]:
  m=bpy.data.materials.new('MAT_Gray_'+key);m.diffuse_color=(g,g,g,1);m.use_nodes=True;n=next((x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');n.inputs['Base Color'].default_value=(g,g,g,1);n.inputs['Roughness'].default_value=.7;M[key]=m
 b.M['rubber'].diffuse_color=(.065,.065,.065,1);next(n for n in b.M['rubber'].node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.065,.065,.065,1)
 C['Reference'].hide_render=True;C['Blockout'].hide_render=True
 return s

def apply_creases(o,data):
 nr=len(data['grid']);nc=len(data['grid'][0]);values={};boundary=data.get('crease_boundary',0.0)
 for j in range(nr):
  for i in range(nc-1):
   if j in (0,nr-1):values[tuple(sorted((j*nc+i,j*nc+i+1)))]=boundary
 for j in range(nr-1):
  for i in range(nc):
   if i in (0,nc-1):values[tuple(sorted((j*nc+i,(j+1)*nc+i)))]=boundary
 for key,val in data.get('crease_columns',{}).items():
  i=int(key)
  for j in range(nr-1):values[tuple(sorted((j*nc+i,(j+1)*nc+i)))]=float(val)
 attr=o.data.attributes.get('crease_edge') or o.data.attributes.new('crease_edge','FLOAT','EDGE')
 for e in o.data.edges:attr.data[e.index].value=values.get(tuple(sorted((e.vertices[0],e.vertices[1]))),0.0)

def cage_faces(data):
 """Grid quads, optionally with explicit quad end caps for closed seat cushions."""
 nr=len(data['grid']);nc=len(data['grid'][0])
 faces=[(j*nc+i,j*nc+i+1,(j+1)*nc+i+1,(j+1)*nc+i) for j in range(nr-1) for i in range(nc-1)]
 if data.get('cap_ends'):
  if nc%2:raise ValueError('Seat end caps require an even transverse profile')
  for row in (0,nr-1):
   for i in range(nc//2-1):
    f=(row*nc+i,row*nc+i+1,row*nc+nc-2-i,row*nc+nc-1-i)
    faces.append(tuple(reversed(f)) if row==0 else f)
 return faces

def cage(data):
 rows=data['grid'];nr=len(rows);nc=len(rows[0]);v=[p for row in rows for p in row];faces=cage_faces(data)
 b.COL=C['Body'] if data['name'].startswith(('Body','Seat')) else C['FrontEnd']
 o=b.mesh(data['name'],v,faces,smo=True);o.data.materials.append(M[data['material']]);o['control_cage_source']='reconstruction_v2/data/control_cages/'+data['name']+'.json';o['acceptance']='pending';o['editable_quads']=True
 if data['mirror_x']:
  md=o.modifiers.new('Symmetry_X','MIRROR');md.use_clip=True;md.merge_threshold=.0001
 md=o.modifiers.new('Editable_Subdivision','SUBSURF');md.levels=data['subdivision'];md.render_levels=data['subdivision']
 if data['thickness_mm']:
  md=o.modifiers.new('Shell_Thickness','SOLIDIFY');md.thickness=data['thickness_mm']*.001;md.offset=-1
  md.solidify_mode=data.get('solidify_mode','EXTRUDE');md.use_even_offset=data.get('use_even_offset',False);md.thickness_clamp=data.get('thickness_clamp',0.0);md.use_thickness_angle_clamp=data.get('use_thickness_angle_clamp',False)
 apply_creases(o,data)
 return o

def wheels():
 b.COL=C['Wheels']
 for name,y,rad,width in [('Front',715,303.9,110),('Rear',-715,313.9,140)]:
  b.tire(name,y,rad,width)
  half=42 if name=='Front' else 55
  b.lathe('Wheel_'+name,y,rad,[(-half,214),(-half,225),(-half+4,225),(-half+7,216),(half-7,216),(half-4,225),(half,225),(half,214)],'gloss',128)
  b.cyl('Hub_'+name,(0,y,rad),35,half*1.55,'gun',(1,0,0))
  b.cyl('Axle_'+name,(0,y,rad),10,230 if name=='Front' else 250,'steel',(1,0,0))
  empty('Datum_Axle_'+name,(0,y,rad),C['Reference'])
  # Ten cast spokes have a swept centerline and tapered rectangular section.
  for k in range(10):
   vs=[]
   for rr,da,wid in [(31,-.17,15),(75,-.08,13),(125,0,11),(170,.06,10),(216,.09,9)]:
    a=k*math.tau/10+da
    for x,du in [(-half*.48,-wid/2),(half*.48,-wid/2),(half*.48,wid/2),(-half*.48,wid/2)]:
     vs.append((x,y+rr*math.sin(a)+du*math.cos(a),rad+rr*math.cos(a)-du*math.sin(a)))
   fs=[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(4) for i in range(4)]
   b.mesh('Spoke_'+name+f'_{k:02}',vs,fs,'gloss',bev=1.2,smo=True)
  x=-65 if name=='Front' else 83;rr=145 if name=='Front' else 120
  b.lathe('BrakeDisc_'+name,y,rad,[(x-2,rr*.62),(x-2,rr),(x+2,rr),(x+2,rr*.62)],'steel',192)
  b.cube('Caliper_'+name,(x,y-105,rad+72),(43,66,90),'gun',10)
  for a in range(6):
   th=a*math.tau/6;b.rod('RotorCarrier_'+name,(x,y+35*math.sin(th),rad+35*math.cos(th)),(x,y+rr*.7*math.sin(th+.08),rad+rr*.7*math.cos(th+.08)),6,'gun')

def mechanical():
 b.mechanical()
 for o in C['Engine'].objects:o['acceptance']='mechanical_proxy_recheck_required'
 # Avoid claiming the old generic castings as inspected parts.
 # Their neutral surfaces provide occlusion and layout context only.


def front():
 b.COL=C['FrontEnd']
 for s in [-1,1]:
  lab='R' if s>0 else 'L'
  b.rod('Fork_Lower_'+lab,(s*93,715,304),(s*93,570,608),22,'gloss')
  b.rod('Fork_Stanchion_'+lab,(s*93,570,608),(s*93,438,901),18.5,'chrome')
  b.rod('Fork_DustSeal_'+lab,(s*93,571,606),(s*93,584,579),25,'rubber')
  b.tube('Handlebar_'+lab,[(s*88,439,900),(s*152,402,913),(s*288,353,912)],12,'gun')
  b.rod('Grip_'+lab,(s*218,379,913),(s*327,340,911),16,'rubber')
  b.cube('SwitchHousing_'+lab,(s*197,386,924),(42,39,49),'black',8)
  b.tube('Lever_'+lab,[(s*192,425,927),(s*245,421,929),(s*326,376,924)],5,'silver')
  b.tube('Mirror_Stem_'+lab,[(s*139,604,915),(s*196,581,970),(s*275,546,1045)],8,'gloss')
  # Shaped six-point shell, not the old generic ellipsoid.
  poly=[(s*269,546,1026),(s*310,541,1029),(s*369,558,1084),(s*377,572,1120),(s*345,584,1110),(s*282,568,1062)]
  b.panel('Mirror_'+lab,poly,'black',21,12)
  b.rod('Indicator_Stem_'+lab,(s*212,654,792),(s*267,662,792),6,'rubber')
  b.sphere('Indicator_'+lab,(s*284,667,794),(28,29,17),'lamp' if 'lamp' in b.M else 'silver')
  b.tube('GuardBar_'+lab,[(s*185,-96,491),(s*314,-65,510),(s*335,167,529),(s*308,190,485),(s*308,86,373),(s*283,-45,402),(s*185,-96,491)],12.5,'guard',True)
  b.rod('GuardBar_Slider_'+lab,(s*319,169,529),(s*360,169,529),20,'rubber')
  b.rod('GuardMount_'+lab,(s*190,203,532),(s*327,170,530),11,'guard')
  b.rod('GuardMount_Lower_'+lab,(s*150,15,392),(s*294,31,399),10,'guard')
 b.cube('TripleClamp_Upper',(0,445,886),(249,87,25),'gun',12)
 b.cube('TripleClamp_Lower',(0,536,697),(240,72,29),'gun',10)
 # Cockpit remains a named coarse unit for this geometry milestone.
 o=b.cube('Dashboard',(0,526,971),(203,49,128),'black',22);o.rotation_euler.x=.4
 o=b.cube('Dashboard_LCD',(0,500,984),(154,7,72),'gun',10);o.rotation_euler.x=.4
 b.cyl('FuelCap',(0,188,953),57,6,'silver',(0,.12,1),64)
 b.cyl('FuelCap_Core',(0,188,957),40,4,'black',(0,.12,1),64)
 b.tube('PhoneMount_Arm',[(-151,410,929),(-180,408,974)],10,'black')
 o=b.cube('PhoneMount',(-188,399,989),(79,21,150),'black',12);o.rotation_euler.x=.30
 b.rod('SteeringDamper',(-103,366,925),(140,366,925),12,'gun')
 b.COL=C['Details']
 b.tube('LicensePlate_Bracket',[(0,-918,833),(0,-1046,676),(0,-1060,568)],12,'black')
 # No real registration needed for M1; locally maintained private config remains untouched.
 b.cube('LicensePlate',(0,-1054,611),(220,5,140),'plate',3)


def camera_from_fit(c):
 R=Matrix(c['R_cv']);t=Vector(c['t_cv_m']);d=bpy.data.cameras.new('Camera_Photo_'+str(c['image_id']));o=bpy.data.objects.new(d.name,d);C['Cameras'].objects.link(o)
 T=Matrix.Identity(4);rot=R.transposed()@Matrix.Diagonal(Vector((1,-1,-1)))
 T.col[0].xyz=rot.col[0];T.col[1].xyz=rot.col[1];T.col[2].xyz=rot.col[2];T.translation=-(R.transposed()@t);o.matrix_world=T
 w,h=c['image_size'];d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=c['K_px'][0][0]*36/w;d.clip_start=.05;d.clip_end=100
 o['image_id']=int(c['image_id']);o['fit_status']=c['status'];o['camera_evidence']='rim_conics';o.lock_location=(True,True,True);o.lock_rotation=(True,True,True);return o

def stage():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.film_transparent=True
 s.render.resolution_x=1280;s.render.resolution_y=1706;s.render.resolution_percentage=60;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='AgX'
 s.world=bpy.data.worlds.new('Gray_Studio');s.world.use_nodes=True;next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.4,.4,.4,1);next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.6
 for name,pos,power,size in [('Key',(3,2,5),900,4),('Fill',(-3,1,3),600,3),('Rim',(0,-4,4),800,3)]:
  d=bpy.data.lights.new('Light_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);C['Lights'].objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.55))-o.location).to_track_quat('-Z','Y').to_euler()
 try:
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='CUDA';p.get_devices()
  for device in p.devices:device.use=device.type=='CUDA'
  s.cycles.device='GPU'
 except Exception:s.cycles.device='CPU'
 for p in sorted((V2/'calibration').glob('camera_*.json')):
  if p.stem[7:].isdigit():camera_from_fit(json.loads(p.read_text()))
 s.camera=next(o for o in C['Cameras'].objects if o.get('image_id')==63)
 # Orthographic inspection is separate from the locked photo cameras.
 b.COL=C['Cameras'];b.camera('Camera_Right_Ortho',(3500,0,630),(0,0,630),ortho=2350)


def main():
 setup();wheels();mechanical();front()
 for p in sorted((V2/'data/control_cages').glob('*.json')):cage(json.loads(p.read_text()))
 stage()
 for o in C['Wheels'].objects:o['acceptance']='wheel_profile_provisional'
 bpy.context.view_layer.update()
 from datetime import datetime
 path=V2/'blends'/('working_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend');bpy.data.libraries.write(str(path),{bpy.context.scene},fake_user=True);print('Saved independent scene',path)
if __name__=='__main__':main()
