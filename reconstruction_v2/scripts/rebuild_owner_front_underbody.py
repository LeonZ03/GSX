"""r43 -> r44 front, lighting hardware, supported brackets, and M1 underside.
Visible paths are photo-led, hidden dimensions provisional. No final appearance claim.
"""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_structure import init,purge,solid_tube,ring,seal_visible
from rebuild_owner_shapes import get,put,remove,rounded_path
from rebuild_clutch_r30 import loft
CHANGES=[]

def front(s,b):
 d=get(s,'Headlight_Lens');g=[]
 for z,y,w in [(874,770,88),(867,785,107),(834,814,121),(798,836,104),(754,851,70),(720,852,21),(715,850,3)]:
  g.append([[w*t,y-15*t*t,z+10*t*t] for t in [0,.2,.45,.7,.88,.97,1]])
 d.update(grid=g,crease_boundary=.8,crease_columns={},thickness_mm=1.8);o=put(s,d)
 # True shield perimeter, matching housing and reflector rather than old rounded bowl.
 contour=[Vector(p) for p in reversed(g[0])]+[Vector((-p[0],p[1],p[2])) for p in g[0][1:]]
 contour += [Vector((-row[-1][0],row[-1][1],row[-1][2])) for row in g[1:]]
 contour += [Vector((-p[0],p[1],p[2])) for p in reversed(g[-1][:-1])]
 contour += [Vector(p) for p in g[-1][1:]]
 contour += [Vector(row[-1]) for row in reversed(g[1:-1])]
 center=Vector((0,790,812));outer=[]
 for p in contour:
  v=Vector((p.x,0,p.z-812)).normalized();outer.append(p+v*4+Vector((0,-1,0)))
 purge(s,('Headlight_Surround','Headlight_Reflector','Headlight_BulbSocket'))
 ring(s,b,'Headlight_Surround',outer,contour,(0,-7,0),'black')
 # The reflector is a closed thin bowl, open visually at the front with a socket.
 verts=[];N=len(contour)
 for t in [0,.08,.38,.68,.82]:
  for p in contour:
   q=p.lerp(center,t);q.y-=28*math.sin(math.pi*t);verts.append(q)
 fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(4) for j in range(N)]
 refl=b.mesh('Headlight_Reflector',verts,fs,'silver',smo=False);m=refl.modifiers.new('Reflector_wall','SOLIDIFY');m.thickness=.0015;m.offset=-1
 # Socket connects remaining inner opening to a bulb support, behind lens.
 b.cyl('Headlight_BulbSocket',(0,756,812),24,39,'black',(0,1,0),48,1)
 b.sphere('Headlight_Bulb',(0,793,817),(10,15,17),'glass')
 back=[p+Vector((0,-10,0)) for p in outer]
 loft(s,'Headlight_Housing',[[list(p) for p in back],[list(p.lerp(center,.55)+Vector((0,-52,0))) for p in back]],b.M['black'],1)
 for side,lab in [(-1,'L'),(1,'R')]:
  b.panel('Headlight_Mount_'+lab,[(side*86,769,856),(side*90,735,857),(side*80,702,868),(side*70,734,867)],'black',4,1)
 # Align shared nose margin with revised lamp; do not change calibrated cameras.
 d=get(s,'Body_NoseCheek');g=d['grid'];inner=[None,[92,756,894],[111,775,879],[125,802,845],[108,827,805],[73,841,759]]
 for i,row in enumerate(g):
  if i==0:continue
  a=Vector(inner[i]);c=Vector(row[-1])
  for j,t in enumerate([0,.035,.18,.5,.82,.965,1]):row[j]=list(a.lerp(c,t)+Vector((0,4*math.sin(math.pi*t),0)))
 d['crease_columns']={'3':.55};put(s,d)
 # Neutral transmissive inspection lens reveals real lamp depth; not final PBR.
 for name in ['Headlight_Lens','Windscreen']:
  ob=s.objects[name];mat=ob.data.materials[0].copy();mat.name='MAT_Inspection_Clear_'+name;mat.diffuse_color=(.3,.3,.3,.4)
  pr=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');pr.inputs['Base Color'].default_value=(.65,.65,.65,1);pr.inputs['Transmission Weight'].default_value=.9;pr.inputs['Roughness'].default_value=.13;pr.inputs['IOR'].default_value=1.49
  ob.data.materials.clear();ob.data.materials.append(mat)
 CHANGES.append('angular_headlamp_thick_housing_reflector_and_nose')

def indicators(s,b):
 # Lens follows the elongated clear capsule seen in owner72, not a sphere.
 for side,lab in [(-1,'L'),(1,'R')]:
  purge(s,('Indicator_Stem_'+lab,'Indicator_'+lab))
  a=Vector((side*208,680,809));c=Vector((side*268,680,809))
  b.rod('Indicator_Stem_'+lab,a,c,8,'rubber',32)
  pts=[]
  for j in range(32):
   t=j*math.tau/32;pts.append((31*math.copysign(abs(math.cos(t))**.65,math.cos(t)),17*math.copysign(abs(math.sin(t))**.8,math.sin(t))))
  # global X length, Y depth, Z height
  rings=[[[side*288+x,680+dy,809+z] for x,z in pts] for dy in [-13,0]]
  loft(s,'Indicator_Base_'+lab,rings,b.M['black'],1)
  lensrings=[[[side*288+x*sc,680+dy,809+z*sc] for x,z in pts] for dy,sc in [(0,1),(7,.97),(14,.78)]]
  lens=loft(s,'Indicator_'+lab,lensrings,b.M['glass'],1)
  b.sphere('Indicator_Bulb_'+lab,(side*288,685,809),(9,8,8),'silver')
  b.cyl('Indicator_MountNut_'+lab,a,12,8,'black',(side,0,0),6,.5)
  # Rear also has a capsule lens, retain its observed mount centers.
  old=s.objects.get('Indicator_Rear_'+lab)
  if old:
   mw=old.matrix_world.copy();center=mw.translation*1000
   remove(s,'Indicator_Rear_'+lab)
   p=[[(center.x+x,center.y+dy,center.z+z) for x,z in pts] for dy in [-9,9]]
   loft(s,'Indicator_Rear_'+lab,p,b.M['glass'],2)
 CHANGES.append('capsule_indicators')

def guards(s,b):
 # Owner72 exposes the LOWER return and three axial ends absent from old loop.
 # Retain accepted rear mount and symmetric geometry; rebuild continuous bends.
 purge(s,('GuardBar','GuardMount'))
 rear=Vector((150.75,-34.68,484.86));upper=Vector((282.63,275.66,544.3));lower=Vector((260,260,438));bottom=Vector((239,170,327))
 for side,lab in [(-1,'L'),(1,'R')]:
  q=lambda p:Vector((side*p[0],p[1],p[2]))
  # One descending outer rail with lower return, joined diagonal behind sliders.
  path=[rear,upper,lower,bottom,Vector((159,3,352))]
  o=solid_tube(b,'GuardBar_'+lab,[q(p) for p in path],10.5,'black',True)
  # Continuous curve through the observed bends; physical tube radius retained.
  for pt in o.data.splines[0].bezier_points:pt.handle_left_type=pt.handle_right_type='AUTO'
  solid_tube(b,'GuardBar_Brace_'+lab,[q(rear),q(lower)],9.5,'black',False)
  for n,p,end in [('Upper',upper,(143,276,544)),('Lower',bottom,(153,170,327)),('Rear',rear,(172.47,-201.34,441.41))]:
   if n=='Rear':
    a=q(end);c=q(p);ax=(c-a).normalized();u=Vector((0,-ax.z,ax.y)).normalized();v=ax.cross(u)
    loft(s,'GuardMount_'+n+'_'+lab,[[list(k+u*x+v*y) for x,y in [(-12,-4),(12,-4),(12,4),(-12,4)]] for k in [a,c]],b.M['black'],1)
   else:b.rod('GuardMount_'+n+'_'+lab,q(end),q(p),10,'black')
  for n,p,L,r in [('upper',upper,53,17),('middle',lower,36,16),('lower',bottom,31,15)]:
   a=q(p);b.rod('GuardBar_Slider_'+n+'_'+lab,a,a+Vector((side*L,0,0)),r,'rubber',40)
   b.rod('GuardBar_SliderCap_'+n+'_'+lab,a+Vector((side*(L-3),0,0)),a+Vector((side*(L+1),0,0)),r*.9,'black',32)
  # This lower end meets the engine-side bracket, not open in space.
  b.panel('GuardMount_EngineTab_'+lab,[q(p) for p in [(149,-9,340),(177,-9,340),(177,17,370),(149,17,370)]],'black',6,1)
 CHANGES.append('symmetric_guard_lower_return_and_three_sliders')

def plate(s,b):
 # Stamped/moulded broad tapered carrier under tail, not skeletal twin tubes.
 purge(s,('LicensePlate_Support','LicensePlate_Crossmember'))
 rows=[]
 for y,z,w in [(-936,880,52),(-974,843,48),(-1015,784,44),(-1060,720,37),(-1068,697,84)]:
  rows.append([[-w,y,z],[0,y-4,z+3],[w,y,z]])
 b.patch('LicensePlate_Carrier',rows,'black',4,1)
 # Bent flanges and cross bar physically meet plate backing plane.
 for side,lab in [(-1,'L'),(1,'R')]:
  b.panel('LicensePlate_EdgeFlange_'+lab,[(side*47,-958,855),(side*38,-1020,775),(side*32,-1068,704),(side*32,-1048,698),(side*38,-1001,772),(side*47,-940,850)],'black',3,1)
 b.cube('LicensePlate_Crossmember',(0,-1068,697),(182,9,22),'black',2)
 for side in [-1,1]:
  b.rod('LicensePlate_Bolt_'+str(side),(side*78,-1064,701),(side*78,-1075,701),4,'steel',24)
 b.panel('LicensePlate_LampBridge',[(-36,-1035,777),(36,-1035,777),(38,-1015,794),(-38,-1015,794)],'black',4,1)
 CHANGES.append('thick_plate_carrier_flanged_mount')

def underbody(s,b):
 b.COL=b.C['Engine'];purge(s,('Exhaust_Header','Exhaust_Collector','OxygenSensor','Intake_','ThrottleBody'))
 # M1 FIG163A shows a flattened chamber, not the existing round curved collector.
 for side,lab in [(-1,'L'),(1,'R')]:
  pts=[(side*64,343,618),(side*64,363,555),(side*63,297,391),(side*52,198,233),(side*32,52,205)]
  solid_tube(b,'Exhaust_Header_'+lab,pts,19,'gun')
  # Rubber intake stubs, shared throttle shaft, twin forward airbox outlets.
  b.rod('Intake_Manifold_'+lab,(side*51,145,646),(side*51,198,628),22,'rubber',40)
  b.rod('ThrottleBody_'+lab,(side*51,90,675),(side*51,151,646),22,'gun',40)
  solid_tube(b,'Intake_AirboxOutlet_'+lab,[(side*51,47,698),(side*51,73,690),(side*51,98,672)],24,'rubber')
  for k,p in enumerate([(side*51,104,669),(side*51,148,646)]):b.cyl('Intake_Clamp_'+lab+str(k),p,24,7,'silver',(0,1,-.45),40,.5)
 b.rod('ThrottleBody_SharedShaft',(-75,128,662),(75,128,662),5,'steel')
 # Flattened oval chamber under sump, welded upper/lower shells.
 shape=[(-1,-.4),(-.7,-1),(.7,-1),(1,-.4),(1,.4),(.7,1),(-.7,1),(-1,.4)]
 stations=[(55,6,202,48,26),(25,9,193,56,34),(-145,25,186,62,35),(-208,49,194,49,32),(-237,75,205,24,24)]
 rings=[[[cx+w*u,y,z+h*v] for u,v in shape] for y,cx,z,w,h in stations]
 loft(s,'Exhaust_Collector',rings,b.M['gun'],4)
 solid_tube(b,'Exhaust_LinkPipe',[(75,-237,205),(119,-265,216),(188,-301,242),(242,-340,278)],24,'gun')
 b.cyl('Exhaust_JointClamp',(234,-334,271),28,17,'silver',(1,-1,1),48,1)
 for side in [-1,1]:
  solid_tube(b,'Exhaust_ChamberSeam_'+str(side),[(cx+side*w,y,z) for y,cx,z,w,h in stations[1:-1]],1.2,'steel')
 # Sensor at the visible merged front section, position provisional not exact spec.
 b.rod('OxygenSensor_Boss',(14,74,224),(14,83,248),9,'gun')
 b.rod('OxygenSensor',(14,83,248),(14,95,281),7,'silver')
 solid_tube(b,'OxygenSensorWire',[(14,95,280),(28,128,309),(82,161,411),(96,151,510)],2.5,'black')
 b.cube('OxygenSensor_Connector',(96,151,510),(15,24,33),'black',2)
 solid_tube(b,'Airbox_Breather',[(91,-45,658),(103,-32,615),(92,2,570)],7,'rubber')
 for side in [-1,1]:
  b.panel('Exhaust_ChamberMount_'+str(side),[(side*46,-151,217),(side*46,-126,259),(side*46,-98,257),(side*46,-126,217)],'gun',5,1)
 # Actual filter enclosure already present; add lid gasket and fasteners only.
 b.cube('Airbox_Lid',(0,-40,753),(230,190,9),'black',12)
 for x,y in [(-95,-118),(95,-118),(-95,37),(95,37)]:b.cyl('Airbox_LidBolt_'+str(x)+'_'+str(y),(x,y,759),4,3,'steel',(0,0,1),16,.4)
 for n in ['Exhaust_Collector','Exhaust_LinkPipe','Intake_Manifold_L','Intake_Manifold_R']:
  s.objects[n]['evidence']='Suzuki M1 FIG103A/140A/155A/163A structure; hidden path and wall sizes provisional'
 CHANGES.append('M1_dual_intake_headers_flat_collector')

def frame_support(s,b):
 b.COL=b.C['Details']
 # Route overly wide upper main tubes within the tank/side-cowl envelope.
 for lab in ['L','R']:
  o=s.objects['Frame_Main_'+lab]
  for p in o.data.splines[0].bezier_points:
   if p.co.y>.1:p.co.x*=.82
  o['unverified']='Upper frame transverse routing constrained inside covers, hidden dimensions unmeasured'
 # Short mounting bosses connect fairing inner surfaces to nearest frame surface.
 dg=bpy.context.evaluated_depsgraph_get()
 for side,lab in [(-1,'L'),(1,'R')]:
  f=s.objects['Frame_Main_'+lab];ev=f.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co*1000 for v in me.vertices];ev.to_mesh_clear()
  # These cover points are chosen from the real side panel control, not free endpoints.
  ob=s.objects['Body_SideFairing'];verts=[ob.matrix_world@v.co*1000 for v in ob.data.vertices]
  for k,index in enumerate([10,24]):
   a=verts[min(index,len(verts)-1)].copy();a.x=side*abs(a.x);c=min(pts,key=lambda p:(p-a).length)
   b.rod('Fairing_InnerBoss_'+lab+str(k),a,c,6,'black')
   b.cyl('Fairing_RubberGrommet_'+lab+str(k),a,9,6,'rubber',(side,0,0),32,1)
 CHANGES.append('inboard_upper_frame_and_fairing_bosses')

def run():
 s=bpy.context.scene
 if s.get('revision')!='r43':raise ValueError('Requires checkpointed r43')
 b=init(s);front(s,b);indicators(s,b);guards(s,b);plate(s,b);underbody(s,b);frame_support(s,b);seal_visible(s)
 from attach_steering_controls import apply
 apply(s)
 s['revision']='r44';s.name='GSX250R_Reconstruction_V2_Gray_r44';s['stage_B']=s['stage_C']='NOT_PASSED'
 bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 report={'changes':CHANGES,'status':'REQUIRES_INTEGRATED_QA','camera_changes':False};(V/'qa/structural_r44.json').write_text(json.dumps(report,indent=2));return report
