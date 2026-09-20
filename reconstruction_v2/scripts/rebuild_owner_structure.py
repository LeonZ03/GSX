"""r42 -> r43 owner structural corrections. Run through Blender MCP.
Photo72/65 supply appearance; hidden measurements remain provisional.
One work file, checkpoint before execution. No camera calibration changes.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,copy
from mathutils import Vector,Matrix
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_shapes import get,put,remove,setup_helpers
from rebuild_clutch_r30 import loft
import build_gray as bg
CHANGES=[]

def init(s):
 b=setup_helpers(s)
 for key,n in {'black':'Body_TankSideTrim','gun':'Engine_ClutchCover','rubber':'Seat_Rider','silver':'FuelCap','steel':'BrakeDisc_Front','glass':'Headlight_Lens','trim':'Body_TankSideTrim'}.items():b.M[key]=s.objects[n].data.materials[0]
 b.COL=b.C['FrontEnd'];return b

def purge(s,prefix):
 for o in list(s.objects):
  if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)

def solid_tube(b,n,pts,r,mat='black',curved=True):
 o=b.tube(n,pts,r,mat,False,curved);o.data.use_fill_caps=True
 m=o.modifiers.new('Cap_weld','WELD');m.merge_threshold=.000001
 return o

def box_basis(s,b,n,center,u,v,normal,w,h,th,mat='black',bev=1):
 c=Vector(center);u=Vector(u);v=Vector(v);normal=Vector(normal)
 return loft(s,n,[[list(c+u*x+v*y+normal*z) for x,y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]] for z in [-th/2,th/2]],b.M[mat],bev)

def ring(s,b,n,outer,inner,depth,mat='black'):
 # Corresponding contours, both in front-to-back view. Closed annular solid.
 k=len(outer);pts=[Vector(p) for p in outer+inner];dv=Vector(depth)
 vs=pts+[p+dv for p in pts];fs=[]
 for i in range(k):
  j=(i+1)%k
  fs.extend([(i,j,k+j,k+i),(i+2*k,k+i+2*k,k+j+2*k,j+2*k),(i,i+2*k,j+2*k,j),(k+i,k+j,3*k+j,3*k+i)])
 return b.mesh(n,vs,fs,mat,bev=.6,smo=True)

def phone_controls(s,b):
 purge(s,('PhoneMount',))
 c=Vector((-185,408,1001));u=Vector((1,0,0));v=Vector((0,.30,.953939));n=u.cross(v)
 q=lambda x,z,d=0:c+u*x+v*z+n*d
 # All members share the same world basis, unlike r41 mixed transform scaling.
 pad=box_basis(s,b,'PhoneMount',c,u,v,n,62,82,12,'black',5)
 box_basis(s,b,'PhoneMount_RubberPad',q(0,0,7),u,v,n,51,67,3,'rubber',5)
 for sx in [-1,1]:
  for sz in [-1,1]:
   lab=('L' if sx<0 else 'R')+('Lower' if sz<0 else 'Upper')
   # Broad sliding arm intersects the backplate over 14mm, not a free hook.
   A=q(sx*17,sz*20,-3);B=q(sx*36,sz*44,-3);ax=(B-A).normalized();cross=n.cross(ax)
   box_basis(s,b,'PhoneMount_Arm_'+lab,(A+B)/2,ax,cross,n,(B-A).length+9,12,8,'black',2)
   box_basis(s,b,'PhoneMount_Jaw_'+lab,q(sx*36,sz*45,3),u,v,n,12,23,17,'black',2)
   box_basis(s,b,'PhoneMount_Contact_'+lab,q(sx*32,sz*46,12),u,v,n,7,17,5,'rubber',1.5)
 ball=q(0,-20,-23);base=Vector((-160,407,931))
 box_basis(s,b,'PhoneMount_HandleClamp',base,(1,0,0),(0,0,1),(0,1,0),31,29,30,'black',3)
 b.rod('PhoneMount_Stem',base,ball,8,'black');b.sphere('PhoneMount_BallJoint',ball,(12,12,12),'black')
 b.rod('PhoneMount_Socket',ball,q(0,-15,-6),11,'black')
 b.cyl('PhoneMount_LockWheel',ball+Vector((-13,0,0)),14,9,'black',(1,0,0),32,1)
 b.rod('PhoneMount_ClampBridge',base,(-161,411,923),9,'black')
 # Correct the too-close lever blades while retaining the accepted hinge positions.
 for side,lab in [(-1,'L'),(1,'R')]:
  remove(s,'Lever_'+lab);remove(s,'Lever_End_'+lab)
  pts=[(side*186,427,935),(side*214,457,935),(side*254,456,932),(side*302,429,925),(side*337,413,922)]
  loft(s,'Lever_'+lab,[[[x,y+dy,z+dz] for dy,dz in [(-w,-2.8),(w,-2.8),(w,2.8),(-w,2.8)]] for (x,y,z),w in zip(pts,[8,8,6,5,4])],b.M['silver'],1.5)
  b.sphere('Lever_End_'+lab,pts[-1],(6,6,5),'silver')
  # Cables leave supported perches and terminate on lower controls, no cut ends.
  if side<0:solid_tube(b,'ClutchCable_Upper',[(-184,427,924),(-157,460,914),(-94,451,823),(-91,260,672),(-120,50,564)],3,'rubber')
 CHANGES.extend(['connected_phone_holder','lever_clearance'])

def windscreen(s,b):
 d=get(s,'Windscreen');g=[]
 # Smooth monotonic bow; preserve base anchoring but remove transverse wave.
 sections=[(761.329,886.534,72),(736,903,98),(701,930,111),(657,965,124),(610,1004,136),(563,1043,147),(524,1076,153),(510,1096,151)]
 for i,(y,z,w) in enumerate(sections):
  row=[]
  for t in [0,.2,.4,.6,.8,.96,1]:
   row.append([w*t,y-25*t*t,z-3*t*t])
  g.append(row)
 d.update(grid=g,crease_boundary=.62,crease_columns={},thickness_mm=3);o=put(s,d)
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=3;m.render_levels=3
 CHANGES.append('smooth_windscreen')

def cockpit(s,b):
 # Surround and backbox are attached to the existing instrument, with a hood.
 c=Vector((0,526,971));up=Vector((0,.4,.916515));normal=Vector((0,-.916515,.4))
 outline=[(-98,-35),(-98,36),(-83,53),(-67,59),(-56,49),(56,49),(67,59),(83,53),(98,36),(98,-35),(76,-47),(0,-51),(-76,-47)]
 def q(p,scale,dep):return list(c+Vector((p[0]*scale,0,0))+up*(p[1]*scale)+normal*dep)
 ring(s,b,'Dashboard_CowlRim',[q(p,1.18,5) for p in outline],[q(p,1.01,7) for p in outline],normal*-13,'black')
 # Gauge support connects housing rear to the fixed steering-head structure.
 for side,lab in [(-1,'L'),(1,'R')]:
  a=(side*66,555,948);z=(side*48,494,830)
  solid_tube(b,'Dashboard_Support_'+lab,[z,(side*66,530,877),a],7,'black')
  b.cube('Dashboard_Isolator_'+lab,a,(22,18,16),'rubber',3)
  b.panel('Cockpit_GaugeCheek_'+lab,[(side*112,553,980),(side*152,544,925),(side*163,497,899),(side*121,498,916)],'black',3,2)
 # Moulded under-instrument pan around steering stem, not a flat lid across it.
 rows=[]
 for y,z,w,inner in [(468,871,143,50),(497,897,162,52),(529,922,158,46),(552,931,120,34)]:
  rows.append([[inner+(w-inner)*t,y,z-8*math.sin(math.pi*t)] for t in [0,.1,.3,.7,.9,1]])
 for side,lab in [(-1,'L'),(1,'R')]:
  grid=[[[side*x,y,z] for x,y,z in r] for r in rows];b.patch('Cockpit_InnerDeck_'+lab,grid,'black',3,2)
 # Neck dust boot and actual loom occupy the lower gap; leave fork movement free.
 b.cyl('SteeringStem_DustCover',(0,465,857),39,32,'rubber',(0,-.42,.9075),48,2)
 solid_tube(b,'Cockpit_MainHarness',[(0,551,947),(-44,551,910),(-62,470,858),(-63,363,814),(-70,230,749)],10,'rubber')
 b.cube('Cockpit_HarnessConnector',(-46,524,894),(24,29,35),'black',3)
 for y,z in [(494,876),(414,838)]:b.cube('Cockpit_HarnessClip',(-60,y,z),(25,7,23),'black',2)
 CHANGES.append('cockpit_shroud_and_mounts')

def seats_tank(s,b):
 basis=json.loads((V/'data/current_controls/r39_shape_basis.json').read_text())
 d=copy.deepcopy(basis['Body_Tank']);d['name']='Body_Tank'
 # Subtractive control sculpting of the r39 shoulders/knee hollows only.
 for i,row in enumerate(d['grid']):
  w=[0,0,.35,.8,1,.8,.3,0,0,0][i]
  row[4][0]-=10*w;row[5][0]-=22*w
  row[3][2]-=3*w;row[2][2]-=5*w
 d['crease_columns']={'2':.20,'3':.35,'4':.30};d['crease_boundary']=.35
 tank=put(s,d);tank['sculpt_baseline']='local r39 987998d5; subtractive shoulder/knee control cuts'
 for n,mat in basis['fuelcap_transforms'].items():
  if n in s.objects:s.objects[n].matrix_world=Matrix(mat)
 # R39 rider pocket plus upholstered upper rear/front rise, not uniform crown.
 d=copy.deepcopy(basis['Seat_Rider']);d['name']='Seat_Rider'
 for i,row in enumerate(d['grid']):
  rise=[10,12,5,1,1,7,7,5][i]
  for j,w in enumerate([1,.85,.35,0,0,0]):row[j][2]+=rise*w
 d['crease_boundary']=.35;seat=put(s,d)
 # Synchronize all operative Boolean dependants after replacing source mesh.
 for n in ['Tool_SeatClearance','Tool_RiderTankClearance']:
  if n in s.objects:s.objects[n].data=seat.data
 # Existing pillion crown is retained; its tilt/undertray is separately inspectable.
 CHANGES.extend(['r39_tank_subtractive_sculpt','longitudinal_saddle'])

def right_peg(s,b):
 # Match the user-approved LEFT folded assembly exactly about vehicle centreline.
 purge(s,('PassengerPeg_R','PassengerPegPivot_R'))
 reflect=Matrix.Diagonal((-1,1,1,1))
 for src in list(s.objects):
  if src.name=='PassengerPeg_L' or src.name.startswith('PassengerPeg_L_Grip_') or src.name=='PassengerPegPivot_L':
   o=src.copy();o.data=src.data.copy();o.name=src.name.replace('Peg_L','Peg_R').replace('Pivot_L','Pivot_R');src.users_collection[0].objects.link(o)
   if o.type=='MESH':
    mw=reflect@src.matrix_world
    for v in o.data.vertices:v.co=mw@v.co
    o.matrix_world=Matrix.Identity(4);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   else:o.matrix_world=reflect@src.matrix_world
 CHANGES.append('right_pillion_peg_folded')

def stand(s,b):
 # User accepted the pivot/foot location. Rebuild tapered forged leg, bent ankle.
 purge(s,('SideStand',));a=Vector((-145,-5.86,253.74));foot=Vector((-227.4,17.28,14))
 pts=[a,a.lerp(foot,.10),a.lerp(foot,.70)+Vector((4,-7,0)),a.lerp(foot,.90)+Vector((2,-2,0)),foot]
 axis=(foot-a).normalized();u=Vector((0,1,0));v=axis.cross(u).normalized()
 rings=[]
 for p,r in zip(pts,[11,10.5,8.5,8,10]):rings.append([list(p+u*(r*math.cos(j*math.tau/10))+v*(r*.86*math.sin(j*math.tau/10))) for j in range(10)])
 loft(s,'SideStand',rings,b.M['gun'],1)
 b.panel('SideStand_Foot',[(-248,-4,9),(-236,44,9),(-211,48,9),(-206,1,9)],'gun',7,3)
 # Forked hinge rather than a single arbitrary connecting tube.
 for x in [-160,-133]:b.panel('SideStand_Hinge_'+str(x),[(x,-23,239),(x,13,239),(x,15,272),(x,-10,282)],'gun',6,2)
 b.cyl('SideStand_Pivot',a,11,38,'steel',(1,0,0),32,1)
 b.panel('SideStand_FrameBracket',[(-143,-23,270),(-112,-23,284),(-110,20,281),(-144,20,270)],'gun',7,2)
 solid_tube(b,'SideStand_DeployTab',[pts[2],(-249,30,69),(-253,47,68)],4,'gun',False)
 start=a+Vector((-17,-7,1));end=pts[2]+Vector((-16,-7,5));ax=(end-start).normalized();uu=ax.cross(Vector((1,0,0))).normalized();vv=ax.cross(uu)
 coil=[start.lerp(end,i/150)+4*(uu*math.cos(i/150*math.tau*16)+vv*math.sin(i/150*math.tau*16)) for i in range(151)]
 solid_tube(b,'SideStand_Spring',coil,1.1,'steel',False)
 for n,p,q in [('Upper',start,a),('Lower',end,pts[2])]:b.rod('SideStand_SpringHook_'+n,p,q,1.7,'steel')
 CHANGES.append('forged_side_stand_same_endpoints')

def seal_visible(s):
 fixed=[]
 for o in s.objects:
  if o.hide_render or o.get('export_exclude'):continue
  if o.type=='CURVE' and o.data.bevel_depth>0:
   o.data.use_fill_caps=True
   if not any(m.type=='WELD' for m in o.modifiers):m=o.modifiers.new('Closed_end_seam','WELD');m.merge_threshold=.000001
   fixed.append(o.name)
  if o.name=='Headlight_Reflector' and not any(m.type=='SOLIDIFY' for m in o.modifiers):m=o.modifiers.new('Reflector_wall','SOLIDIFY');m.thickness=.0015
 return fixed

def run():
 s=bpy.context.scene
 if s.get('revision')!='r42':raise ValueError('Requires committed r42')
 b=init(s);phone_controls(s,b);windscreen(s,b);cockpit(s,b);seats_tank(s,b);right_peg(s,b);stand(s,b);sealed=seal_visible(s)
 from attach_steering_controls import apply
 apply(s)
 s['revision']='r43';s.name='GSX250R_Reconstruction_V2_Gray_r43';s['stage_B']=s['stage_C']='NOT_PASSED'
 bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 report={'changes':CHANGES,'sealed_curve_ends':sealed,'remaining':'front/indicators/guard/plate/frame/underbody and integrated QA next','status':'NOT_PASSED'}
 (V/'qa/structural_r43.json').write_text(json.dumps(report,indent=2));return report
