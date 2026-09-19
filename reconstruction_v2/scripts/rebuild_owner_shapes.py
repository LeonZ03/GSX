"""Owner nine-point correction: editable photo-led shapes, one private working blend.
Run through Blender MCP only. Requires checkpointed r39. Dimensions not measured
from the real bike remain estimates, never a claim of completed 1:1 acceptance.
"""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector,Matrix
V=Path(__file__).resolve().parents[1];ROOT=V.parent
sys.path.insert(0,str(V/'scripts'))
import build_gray as bg
from rebuild_body_stage_b import setup_helpers
from rebuild_clutch_r30 import loft
OUT=V/'data/current_controls'
CHANGED=[]
def remove(s,n):
 o=s.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
def get(s,n):
 o=s.objects[n];d=json.loads((ROOT/o['control_cage_source']).read_text(encoding='utf8'));nc=len(d['grid'][0]);d['grid']=[[list(v.co*1000) for v in o.data.vertices[i:i+nc]] for i in range(0,len(o.data.vertices),nc)];return d

def put(s,d):
 o=s.objects[d['name']];old=o.data;me=bpy.data.meshes.new(d['name']+'_OwnerControl');me.from_pydata([[t*.001 for t in p] for r in d['grid'] for p in r],[],bg.cage_faces(d));me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for m in old.materials:me.materials.append(m)
 for f in me.polygons:f.use_smooth=True
 o.data=me;bg.apply_creases(o,d);d['revision']='r40';d['status']='PHOTO_LED_UNVERIFIED_DIMENSIONS';OUT.mkdir(exist_ok=True)
 (OUT/(d['name']+'.json')).write_text(json.dumps(d,indent=2));o['control_cage_source']='reconstruction_v2/data/current_controls/'+d['name']+'.json';o['acceptance']='NOT_PASSED';CHANGED.append(d['name'])
 if d['name']=='Seat_Rider':
  helper=s.objects.get('Tool_SeatClearance')
  if helper:helper.data=me
 return o

def rounded_path(points,r=13):
 out=[]
 for i,p in enumerate(points):
  p=Vector(p);a=Vector(points[(i-1)%len(points)]);c=Vector(points[(i+1)%len(points)]);ra=min(r,(a-p).length*.2,(c-p).length*.2);a=p+(a-p).normalized()*ra;c=p+(c-p).normalized()*ra
  for j in range(7):
   t=j/6;out.append(a*(1-t)**2+p*2*t*(1-t)+c*t*t)
 return out

def guards_stand(s,b):
 for o in list(s.objects):
  if o.name.startswith(('GuardBar','GuardMount','SideStand')):bpy.data.objects.remove(o,do_unlink=True)
 b.COL=b.C['Details'];nodes={'rear':[150.75,-34.68,484.86],'upper':[282.63,275.66,544.3],'lower':[250.47,225.15,437.79],'elbow':[231.72,141.42,413.08]}
 rear=Vector(nodes['rear']);upper=Vector(nodes['upper']);brace=rear.lerp(upper,.32)
 for sign,lab in [(-1,'L'),(1,'R')]:
  def q(p):return Vector((sign*p[0],p[1],p[2]))
  b.tube('GuardBar_'+lab,[q(p) for p in rounded_path([nodes[k] for k in ['rear','upper','lower','elbow']])],10.5,'black',True,False)
  b.tube('GuardBar_Brace_'+lab,[q(brace),q(nodes['elbow'])],9.5,'black',False,False)
  b.rod('GuardMount_Upper_'+lab,q([143,276,544]),q(nodes['upper']),10,'black')
  b.rod('GuardMount_Lower_'+lab,q([153,238,353]),q(nodes['lower']),9,'black')
  a=q([172.47,-201.34,441.41]);c=q(nodes['rear']);axis=(c-a).normalized();u=Vector((0,-axis.z,axis.y)).normalized();v=axis.cross(u).normalized()
  rings=[[list(p+u*x+v*y) for x,y in [(-12.5,-4),(12.5,-4),(12.5,4),(-12.5,4)]] for p in [a,c]]
  loft(s,'GuardMount_Rear_'+lab,rings,b.M['black'],1.5)
  for label,radius,length in [('upper',17,52),('lower',15,33)]:
   p=q(nodes[label]);b.rod('GuardBar_Slider_'+label+'_'+lab,p,p+Vector((sign*length,0,0)),radius,'rubber',48)
   b.rod('GuardBar_SliderCap_'+label+'_'+lab,p+Vector((sign*(length-3),0,0)),p+Vector((sign*(length+1),0,0)),radius*.85,'black')
  b.bolt('GuardMount_RearBolt_'+lab,a,6,(sign,0,0),'steel')
 # Fixed photo69 projection puts the deployed foot forward of the old stand.
 a=Vector((-145,-5.86,253.74));p=Vector((-227.40,17.28,14));el=a.lerp(p,.58)+Vector((-3,9,0))
 b.tube('SideStand',[a,el,p],10.5,'gun',False,False)
 b.cube('SideStand_Foot',p,(44,59,10),'gun',5)
 b.cyl('SideStand_Pivot',a,18,25,'gun',(1,0,0),40,2)
 b.bolt('SideStand_PivotBolt',a+Vector((-15,0,0)),7,(-1,0,0),'steel')
 b.rod('SideStand_FrameBracket',(-116,-6,271),a,14,'gun')
 b.tube('SideStand_DeployTab',[a.lerp(p,.55),(-256,40,110),(-264,37,84)],4.8,'gun',False,False)
 start=a+Vector((-13,4,9));end=a.lerp(p,.65)+Vector((-14,12,2));axis=(end-start).normalized();u=axis.cross(Vector((1,0,0))).normalized();v=axis.cross(u)
 coil=[start.lerp(end,i/180)+5*(u*math.cos(i/180*math.tau*18)+v*math.sin(i/180*math.tau*18)) for i in range(181)]
 b.tube('SideStand_Spring',coil,1.2,'steel',False,False)
 (OUT/'guard_stand.json').write_text(json.dumps({'guard_nodes_mm':nodes,'tube_radius_mm':10.5,'brace_fraction':.32,'stand_pivot_mm':list(a),'stand_foot_mm':list(p),'evidence':'62/63 tube junctions, 69 deployed stand; depths and tube diameters approximate'},indent=2))
 CHANGED.extend(['GuardBar_L','GuardBar_R','SideStand'])

def fender(s,b):
 d=get(s,'Fender_Front');g=[]
 # Broad crown, downturned side wings around fork mounts, tapered forward nose.
 for y,z,w,drop in [(425,515,59,22),(445,548,66,28),(505,600,75,43),(571,625,79,120),(609,637,80,169),(644,640,81,174),(672,640,81,136),(705,639,80,43),(772,632,77,27),(850,620,72,25),(916,601,62,23),(945,589,47,17),(952,587,37,14)]:
  row=[]
  for t in [0,.28,.56,.78,.89,.96,1]:
   dz=18*t*t+(drop-18)*max(0,(t-.78)/.22)**1.25
   row.append([w*t,y-(4*t if y>900 else 0),z-dz])
  g.append(row)
 d['grid']=g;d['crease_columns']={'3':.25,'4':.30};d['crease_boundary']=.4;d['thickness_mm']=2.5;put(s,d)
 for side,lab in [(-1,'L'),(1,'R')]:
  b.COL=b.C['FrontEnd'];b.cyl('Fender_Front_Mount_'+lab,(side*84,617,527),6,4,'steel',(side,0,0),32,.5)


def seats_tank(s,b):
 for n in ['Seat_Rider','Seat_Pillion']:
  d=get(s,n);g=d['grid'];N=len(g)
  for i,row in enumerate(g):
   if n=='Seat_Rider':
    # Convex transverse upholstery over longitudinal rider pocket.
    crown=[8,12,18,22,21,14,5,2][i]
    for j,w in enumerate([1,.8,.12,0,0,0]):row[j][2]+=crown*w
    if i in [0,1]:
     for j in range(4):row[j][2]+=8*(1-j/7)
   else:
    crown=[1,5,16,23,24,17,8][i]
    for j,w in enumerate([1,.75,.2,0,0,0]):row[j][2]+=crown*w
    # Round the previously planar front face and its upholstered shoulder.
    if i>=N-2:
     for j in [0,1,2]:row[j][1]+=7*(1-j/3)
  d['crease_boundary']=.20;d['crease_columns']={'3':.18,'4':.22};put(s,d)
 # Tank: retain center/cap mounting zone, create distinct shoulders and knee recess.
 d=get(s,'Body_Tank');g=d['grid']
 for i,row in enumerate(g):
  weight=[0,.08,.45,.85,1,1,.8,.4,.1,0][i]
  row[2][0]+=5*weight;row[2][2]-=7*weight
  row[3][0]+=10*weight;row[3][2]+=3*weight
  row[4][0]+=[0,0,-8,-14,5,9,5,0,0,0][i]
  row[5][0]-=[0,0,9,22,19,9,2,0,0,0][i]
  row[5][2]+=5*weight
 d['crease_columns']={'2':.38,'3':.55,'4':.25,'5':.4};put(s,d)
 # Re-seat the cap and its construction cutters after changing the tank shoulder.
 tank=s.objects['Body_Tank'];cuts=[m for m in tank.modifiers if m.type=='BOOLEAN' and m.object and m.object.name=='Tool_FuelCapRecess'];flags=[m.show_viewport for m in cuts]
 for m in cuts:m.show_viewport=False
 bpy.context.view_layer.update();ev=tank.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[]
 for y in [.178,.188,.198]:
  ok,p,normal,idx=ev.ray_cast(Vector((0,y,2)),Vector((0,0,-1)))
  if not ok:raise RuntimeError('Tank mount ray failed')
  pts.append(p)
 normal=Vector((1,0,0)).cross((pts[2]-pts[0]).normalized()).normalized();old=Vector((0,.188,.9554381));oldnormal=Vector((0,.377147,.926153)).normalized();rotation=oldnormal.rotation_difference(normal).to_matrix().to_4x4();T=Matrix.Translation(pts[1])@rotation@Matrix.Translation(-old)
 for o in s.objects:
  if o.name.startswith(('FuelCap','Tool_FuelCap')):o.matrix_world=T@o.matrix_world
 for m,f in zip(cuts,flags):m.show_viewport=f


def cockpit(s,b):
 b.COL=b.C['FrontEnd']
 prefixes=('Handlebar','Grip_','SwitchHousing','Lever_','TripleClamp_Upper','BrakeReservoir','ClutchPerch')
 for o in list(s.objects):
  if o.name.startswith(prefixes):bpy.data.objects.remove(o,do_unlink=True)
 outline=[(-116,458),(-113,432),(-96,418),(-67,422),(-36,410),(36,410),(67,422),(96,418),(113,432),(116,458),(96,476),(57,477),(33,508),(-33,508),(-57,477),(-96,476)]
 rings=[[[x,y,886-.46*(y-445)+dz] for x,y in outline] for dz in [-10,10]];clamp=loft(s,'TripleClamp_Upper',rings,b.M['black'],2.5)
 for side,lab in [(-1,'L'),(1,'R')]:
  axis=Vector((0,-.42,.9075));cut=b.cyl('Tool_TripleClampFork_'+lab,(side*93,445,886),19.1,80,'black',axis,64,0);cut.hide_render=True;cut.hide_set(True);cut['export_exclude']=True
  m=clamp.modifiers.new('Fork_bore_'+lab,'BOOLEAN');m.object=cut;m.operation='DIFFERENCE'
  b.cyl('Handlebar_ForkCollar_'+lab,(side*93,445,903),26,21,'black',axis,48,1.8)
  # Angled cast clip-on riser, distinct from the straight grip tube.
  a=Vector((side*102,433,910));c=Vector((side*180,402,927));u=Vector((0,1,0));v=(c-a).normalized().cross(u).normalized()
  riser=loft(s,'Handlebar_Riser_'+lab,[[list(p+u*x+v*y) for x,y in [(-14,-10),(14,-10),(16,8),(-14,12)]] for p in [a,c]],b.M['black'],3)
  start=Vector((side*173,404,925));end=Vector((side*331,337,918));axis=(end-start).normalized()
  b.rod('Handlebar_'+lab,start,end,11,'gun',40)
  ga=start.lerp(end,.30);gb=end-axis*7;b.rod('Grip_'+lab,ga,gb,16,'rubber',48)
  b.rod('Grip_Flange_'+lab,ga-axis*3,ga+axis*2,20,'rubber',48)
  b.rod('Grip_BarEnd_'+lab,end-axis*3,end+axis*22,18,'black',48)
  for j in range(1,10):
   p=ga.lerp(gb,j/10);b.rod('Grip_Rib_'+lab+'_'+str(j),p-axis*.45,p+axis*.45,16.4,'rubber',40)
  housing=b.cube('SwitchHousing_'+lab,start.lerp(end,.18),(39,47,47),'black',6);housing.rotation_euler.z=side*math.radians(-22)
  switch=b.cube('SwitchHousing_Rocker_'+lab,(side*207,391,950),(16,19,10),'trim',3);switch.rotation_euler.z=side*math.radians(-22)
  b.cyl('Lever_Pivot_'+lab,(side*187,426,932),10,16,'gun',(0,0,1),40,1)
  pts=[(side*186,427,935),(side*218,430,934),(side*255,414,930),(side*305,381,921),(side*338,369,916)]
  # Flattened lever cross section, not a round wire.
  rings=[]
  for i,p in enumerate(pts):
   w=[8,8,6,5,4][i];rings.append([[p[0],p[1]+dy,p[2]+dz] for dy,dz in [(-w,-2.8),(w,-2.8),(w,2.8),(-w,2.8)]])
  loft(s,'Lever_'+lab,rings,b.M['silver'],1.6);b.sphere('Lever_End_'+lab,pts[-1],(6,6,5),'silver')
  if side>0:
   reservoir=b.cube('BrakeReservoir',(153,444,958),(65,43,31),'black',4);reservoir.rotation_euler.z=math.radians(-18)
   lid=b.cube('BrakeReservoir_Lid',(153,444,976),(69,46,5),'black',2);lid.rotation_euler.z=math.radians(-18)
   b.cyl('BrakeReservoir_LevelGlass',(162,420,958),7,2,'glass',(0,-1,0),32,.5)
   b.tube('BrakeReservoir_Hose',[(177,447,950),(206,451,945),(224,422,925),(186,410,899)],3.5,'rubber')
  else:b.cube('ClutchPerch',(-182,422,931),(34,30,25),'black',4)
 CHANGED.extend(['Handlebar_L','Handlebar_R','TripleClamp_Upper','Lever_L','Lever_R'])


def face(s,b):
 # Refine shared shell controls without breaking the live assembly links.
 for name in ['Body_NoseCheek','Body_NoseSideReturn']:
  d=get(s,name);g=d['grid']
  # Add a longitudinal fold between lamp-side face and side return, as on 66.
  for i,row in enumerate(g):
   factor=math.sin(math.pi*i/(len(g)-1))
   for j,p in enumerate(row):
    if j in [2,3,4]:p[1]+=factor*[0,0,2,6,3,0,0][j]
  d['crease_columns']={'3':.6};d['crease_boundary']=.65;put(s,d)
 d=get(s,'Headlight_Lens');g=d['grid'];widths=[80,101,120,112,85,46,12]
 for row,w in zip(g,widths):
  old=row[-1][0]
  for j,p in enumerate(row):p[0]*=w/old;p[1]-=4*(1-j/(len(row)-1))
 d['crease_boundary']=.32;put(s,d)
 # Wing-shaped sidelights: pointed outer end, broad inner lower lens beside lamp.
 pairs=[([184,751,881],[179,755,878]),([177,770,866],[146,786,840]),([154,800,827],[120,815,797]),([128,816,799],[117,817,795])]
 for name,pad,depth in [('Headlight_PositionLens',0,0),('Headlight_PositionSurround',3,-2.4)]:
  d=get(s,name);g=[]
  for a,c in pairs:
   a,c=Vector(a),Vector(c);u=(a-c).normalized();a+=u*pad;c-=u*pad
   g.append([list(a.lerp(c,t)+Vector((0,depth,0))) for t in [0,.05,.28,.72,.95,1]])
  d['grid']=g;d['crease_boundary']=.55;d['thickness_mm']=2;put(s,d)
 CHANGED.append('Headlight_PositionLens')


def run():
 s=bpy.context.scene
 if s.get('revision')!='r39':raise ValueError('Requires committed r39; do not repeat on refined output')
 if Path(bpy.data.filepath).resolve()!=(V/'model_history/GSX250R.blend').resolve():raise ValueError('Use single working source')
 OUT.mkdir(exist_ok=True);b=setup_helpers(s)
 for key,n in {'black':'Body_TankSideTrim','gun':'Engine_ClutchCover','rubber':'Seat_Rider','silver':'FuelCap','steel':'BrakeDisc_Front','glass':'Headlight_Lens','trim':'Body_TankSideTrim'}.items():b.M[key]=s.objects[n].data.materials[0]
 guards_stand(s,b);fender(s,b);seats_tank(s,b);cockpit(s,b);face(s,b)
 for o in s.objects:
  if o.name.startswith(('GuardBar','GuardMount')):o.hide_render=False
 s['revision']='r40';s.name='GSX250R_Reconstruction_V2_Gray_r40';s['visual_acceptance']='NOT_PASSED';s['stage_B']='NOT_PASSED';s['stage_C']='NOT_PASSED'
 bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 report={'revision':'r40','changed':CHANGED,'objects':len(s.objects),'camera_changes':False,'rear_wheel_hugger':False,'status':'CANDIDATE_REQUIRES_RENDER_AND_GEOMETRY_REVIEW'}
 (V/'qa/owner_corrections_r40.json').write_text(json.dumps(report,indent=2));return report
