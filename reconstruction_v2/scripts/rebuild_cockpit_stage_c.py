"""Photo-supported GSX cockpit structure; blank LCD, no invented markings.
Apply only to an isolated review source. All sizes are reconstruction estimates.
"""
from pathlib import Path
import bpy,math,sys,json
from mathutils import Vector,Matrix
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
from rebuild_body_stage_b import setup_helpers

def apply(scene):
 b=setup_helpers(scene)
 # Reuse neutral materials by scene object, never assume un-suffixed datablocks.
 sources={'black':'Body_TankSideTrim','gun':'Body_TankSideTrim','rubber':'Seat_Rider','silver':'FuelCap','steel':'FuelCap','glass':'Headlight_Lens'}
 for key,n in sources.items():b.M[key]=scene.objects[n].data.materials[0]
 b.COL=b.C['FrontEnd'];created=[]
 def remove(names):
  for n in names:
   o=scene.objects.get(n)
   if o:bpy.data.objects.remove(o,do_unlink=True)
 def mesh(name,vs,fs,mat,bev=1):
  o=b.mesh(name,vs,fs,mat,bev=bev,smo=False);created.append(o);return o
 # Official LCD instrument casing has two upper shoulders and a shallow lower
 # arc. A simple rectangle or a tachometer dial is not this model's cluster.
 center=Vector((0,526,971));up=Vector((0,.40,.916515));normal=Vector((0,-.916515,.40))
 def q(u,v,dep=0):return list(center+Vector((u,0,0))+up*v+normal*dep)
 outline=[(-98,-35),(-98,36),(-83,53),(-67,59),(-56,49),(56,49),(67,59),(83,53),(98,36),(98,-35),(76,-47),(0,-51),(-76,-47)]
 remove(['Dashboard','Dashboard_LCD'])
 # Closed ruled casing, separate bezel/lens and two lower control buttons.
 vs=[q(u,v,dep) for dep in [-29,0] for u,v in outline];N=len(outline)
 fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 mesh('Dashboard',vs,fs,'black',3)
 bezel=[q(u*.93,v*.92,2) for u,v in outline];o=b.panel('Dashboard_Bezel',bezel,'black',4,2);created.append(o)
 display=[q(-62,-30,5),q(62,-30,5),q(62,31,5),q(-62,31,5)]
 o=b.panel('Dashboard_LCD',display,'glass',1,2);created.append(o)
 for s in [-1,1]:
  poly=[q(s*57,-40,4),q(s*80,-41,4),q(s*89,-33,4),q(s*59,-33,4)]
  o=b.panel('Dashboard_Button_'+('L' if s<0 else 'R'),poly,'rubber',4,1);created.append(o)
  for j in range(4):
   o=b.cyl('Dashboard_IndicatorWindow_'+str(s)+'_'+str(j),q(s*79,24-j*14,4),3.2,1,'glass',normal,16,.2);created.append(o)
 # Empty four-jaw clamp visible in photo 70; do not leave the old phone-sized slab.
 remove(['PhoneMount','PhoneMount_Arm'])
 phone=Vector((-188,399,997));pu=Vector((1,0,0));pv=Vector((0,.2955,.9553));pn=pu.cross(pv)
 def pq(x,z,dep=0):return phone+pu*x+pv*z+pn*dep
 pad=b.cube('PhoneMount',pq(0,0),(58,12,69),'black',5);pad.rotation_euler.x=-.30;created.append(pad)
 for sx in [-1,1]:
  for sz in [-1,1]:
   label=('L' if sx<0 else 'R')+('Lower' if sz<0 else 'Upper')
   pts=[pq(sx*19,sz*21),pq(sx*33,sz*40),pq(sx*33,sz*51),pq(sx*27,sz*51,8)]
   created.append(b.tube('PhoneMount_Jaw_'+label,pts,3.4,'black',False,False))
   o=b.cube('PhoneMount_Contact_'+label,pq(sx*31,sz*45,3),(8,9,15),'rubber',2);o.rotation_euler.x=-.30;created.append(o)
 created.append(b.rod('PhoneMount_Arm',(-151,410,929),(-180,408,965),8,'black'))
 created.append(b.sphere('PhoneMount_BallJoint',(-180,408,965),(13,13,13),'black'))
 created.append(b.cyl('PhoneMount_LockWheel',(-188,416,977),17,12,'black',(0,1,0),32,1))
 created.append(b.cube('PhoneMount_HandleClamp',(-150,410,929),(27,25,26),'black',4))
 # Steering damper is a body with a narrow sliding rod, clamp and two eyes.
 remove(['SteeringDamper'])
 created.append(b.rod('SteeringDamper',(-94,366,925),(53,366,925),12,'gun'))
 created.append(b.rod('SteeringDamper_Rod',(52,366,925),(146,366,925),4.8,'silver'))
 created.append(b.cyl('SteeringDamper_Adjuster',(-105,366,925),13,18,'black',(1,0,0),32,1))
 for name,pos in [('Body',(-5,366,925)),('End',(142,366,925))]:
  created.append(b.cyl('SteeringDamper_Eye_'+name,pos,11,14,'gun',(0,0,1),32,1))
  created.append(b.bolt('SteeringDamper_Bolt_'+name,(pos[0],pos[1],pos[2]+8),5,(0,0,1),'steel'))
 created.append(b.cube('SteeringDamper_Clamp',(-5,370,913),(37,28,15),'black',3))
 # Exposed upper clamp receives fork caps and key barrel, preserving the old
 # steering axis and all fork transforms (no silent geometry-based camera refit).
 for sx in [-1,1]:
  created.append(b.cyl('ForkCap_'+('L' if sx<0 else 'R'),(sx*93,445,904),18,8,'silver',(0,-.42,.9075),48,1))
  created.append(b.cyl('ForkCap_Hex_'+str(sx),(sx*93,443,908),10,5,'steel',(0,-.42,.9075),6,.5))
 created.append(b.cyl('Ignition_Barrel',(0,480,902),20,23,'black',(0,-.35,.9367),48,1))
 created.append(b.cyl('Ignition_Rim',(0,476,913),18,4,'silver',(0,-.35,.9367),48,1))
 key=b.cube('Ignition_KeySlot',(0,474,916),(2.7,13,1.5),'black',.6);created.append(key)
 # Lens perimeter stays from photo-led cage. Reflector is an independent
 # shallow concave bowl behind it, visible in dedicated exploded inspections.
 for o in list(scene.objects):
  if o.name.startswith('Headlight_Reflector'):bpy.data.objects.remove(o,do_unlink=True)
 ring=[(-83,755,874),(-98,782,847),(-80,814,802),(-53,828,764),(-24,826,741),(0,833,736),(24,826,741),(53,828,764),(80,814,802),(98,782,847),(83,755,874),(0,761,876)]
 vc=[];nc=len(ring)
 for t in [0,.16,.50,.75,.9]:
  for p in ring:
   a=Vector(p);c=Vector((0,755,816));pt=a.lerp(c,t);pt.y-=28*math.sin(math.pi*t);vc.append(pt)
 fs=[(j*nc+i,j*nc+(i+1)%nc,(j+1)*nc+(i+1)%nc,(j+1)*nc+i) for j in range(4) for i in range(nc)]
 mesh('Headlight_Reflector',vc,fs,'silver',0)
 created.append(b.cyl('Headlight_BulbSocket',(0,753,816),17,19,'black',(0,1,0),40,1))
 # Neutral lens/rim separation is a shape diagnostic, not final glass.
 lampmat=scene.objects['Headlight_Lens'].data.materials[0]
 lampmat=lampmat.copy();lampmat.name='MAT_Gray_HeadlightDiagnostic';lampmat.diffuse_color=(.44,.44,.44,1)
 next(n for n in lampmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.44,.44,.44,1)
 scene.objects['Headlight_Lens'].data.materials.clear();scene.objects['Headlight_Lens'].data.materials.append(lampmat)
 for o in created:
  o['stage_c_owner']='cockpit';o['acceptance']='PHOTO_SUPPORTED_FORM_DIMENSIONS_UNVERIFIED'
 bpy.context.view_layer.update()
 return {'objects_created':len(created),'names':[o.name for o in created],'source':'owner photos 62/63/66/70 and official GSX250R-A dashboard','stage_C':'NOT_PASSED'}
