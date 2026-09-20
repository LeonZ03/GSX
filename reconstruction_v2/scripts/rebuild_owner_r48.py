"""r48 owner corrections: short tail carrier, actual attachments and body silhouettes.
Photo-led estimates; run through Blender MCP only. No camera changes.
"""
import bpy,json,copy,math,sys,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_structure import init,purge,solid_tube,box_basis
from rebuild_owner_shapes import put,remove
from rebuild_clutch_r30 import loft
BASE=json.loads((V/'data/revisions/r47_owner_baseline/controls.json').read_text())

def control(s,n,g,**kw):
 d=copy.deepcopy(BASE[n]);d.update(grid=g,**kw);o=put(s,d);d['revision']='r48'
 for m in o.modifiers:
  if m.type=='SOLIDIFY':m.thickness=d.get('thickness_mm',2.5)*.001
 (V/'data/current_controls'/(n+'.json')).write_text(json.dumps(d,indent=2));return o

def tail(s,b):
 from rebuild_shell_front_r47 import plate
 plate(s,b)
 # Short broad moulded carrier: root beneath lamp, not from top of tail tip.
 purge(s,('LicensePlate_Carrier','LicensePlate_EdgeFlange','LicensePlate_LampBridge'))
 shift=Vector((0,38,91))*.001
 for o in s.objects:
  if o.name=='LicensePlate' or o.name.startswith(('LicensePlate_Crossmember','LicensePlate_Bolt','LicensePlate_Lamp')):o.location+=shift
 rows=[(-879,947,40),(-913,919,48),(-956,869,57),(-1009,802,74)]
 # Root meets rear undertray with two short integral fastener ears.
 b.COL=b.C['Details'];b.patch('LicensePlate_Carrier',[[[-w,y,z],[0,y-3,z+2],[w,y,z]] for y,z,w in rows],'black',4,2)
 for side,lab in [(-1,'L'),(1,'R')]:
  edge=[(side*w,y,z) for y,z,w in rows]
  b.panel('LicensePlate_EdgeFlange_'+lab,edge+[(x,y+13,z-2) for x,y,z in reversed(edge)],'black',3,.6)
  b.panel('LicensePlate_RootEar_'+lab,[(side*25,-865,948),(side*51,-865,948),(side*47,-892,934),(side*24,-892,934)],'black',5,.8)
  b.cyl('LicensePlate_RootBolt_'+lab,(side*37,-877,950),4,12,'steel',(0,0,1),24,.3)
 b.panel('LicensePlate_LampBridge',[(-38,-989,860),(38,-989,860),(39,-967,854),(-39,-967,854)],'black',4,.6)
 b.panel('LicensePlate_ReflectorBridge',[(-33,-1005,805),(33,-1005,805),(33,-1006,842),(-33,-1006,842)],'black',4,.6)
 # Rear indicator/reflector bar must follow the same supported carrier.
 for n in ['Reflector_Rear','Reflector_Rear_Housing']:
  o=s.objects.get(n)
  if o:o.location+=Vector((0,.024,.036))
 return {'plate_translation_mm':[0,38,91],'carrier_stations_mm':rows,'evidence':'owner69 and70 side/rear carrier, dimensions unmeasured'}

def mounts(s,b):
 from rebuild_rear_hardware_r36 import hull,boolean,cylinder
 b.COL=b.C['Details'];report={}
 # Retain folded pegs and exhaust connection; rebuild only mounting triangle.
 data=json.loads((V/'data/revisions/r36_rear_hardware/control.json').read_text())
 for side,lab in [(-1,'L'),(1,'R')]:
  src=data['hanger_points'] if side<0 else data['hanger_points_R']
  A,B,C=[Vector(src[n]) for n in ['hanger_mount_front','hanger_mount_rear','hanger_pivot']]
  for q in [A,B,C]:q.x=side*abs(q.x)
  A.z+=41;B.z+=37
  remove(s,'Frame_Subframe_'+lab)
  path=[(side*105,-226,570),(side*118,-445,683),(side*95,-650,829),(side*35,-900,983)]
  frame=solid_tube(b,'Frame_Subframe_'+lab,path,14,'black',False)
  purge(s,('PassengerPegHanger_'+lab,'PassengerPegFrameTab_'+lab,'PassengerPegMountBolt_'+lab,'Tool_PillionWindow_'+lab,'Tool_PillionBoltHole_'+lab))
  normal=(B-A).cross(C-A)
  def x_at(y,z):return A.x-(normal.y*(y-A.y)+normal.z*(z-A.z))/normal.x
  poly=hull([(p.y+10*math.cos(j*math.tau/16),p.z+10*math.sin(j*math.tau/16)) for p in [A,B,C] for j in range(16)])
  o=loft(s,'PassengerPegHanger_'+lab,[[[x_at(y,z)+dx,y,z] for y,z in poly] for dx in [-4,4]],b.M['gun'],.8)
  center=(A+B+C)/3;inner=[center+(p-center)*.62 for p in [A,B,C]]
  boolean(o,loft(s,'Tool_PillionWindow_'+lab,[[[x,p.y,p.z] for p in inner] for x in [-300,300]],b.M['gun']))
  bpy.context.view_layer.update();ev=frame.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co*1000 for v in me.vertices];ev.to_mesh_clear()
  endpoints=[]
  for j,p in enumerate([A,B]):
   boolean(o,cylinder(s,f'Tool_PillionBoltHole_{lab}_{j}',p,4.3,50,b.M['gun'],32))
   cylinder(s,f'PassengerPegMountBolt_{lab}_{j}',p+Vector((side*6,0,0)),6.5,14,b.M['steel'],6)
   target=min(vs,key=lambda v:(v-p).length);target.x-=side*4
   axis=target-p;perp=Vector((0,-axis.z,axis.y)).normalized()*10
   poly=[p+perp,p-perp,target-perp,target+perp]
   loft(s,f'PassengerPegFrameTab_{lab}_{j}',[[list(q+Vector((dx,0,0))) for q in poly] for dx in [-5,5]],b.M['gun'],.7);endpoints.append([list(p),list(target)])
  report[lab]={'frame':path,'bolts':[list(A),list(B)],'tab_endpoints':endpoints}
 # Damper: fixed body clevis to steering head, moving eye to upper fork clamp.
 for o in s.objects:
  if o.name.startswith('SteeringDamper'):o.location+=Vector((0,.040,-.012))
 fixed=[(-20,461,837),(12,461,837),(12,410,897),(-20,410,897)]
 b.panel('SteeringDamper_FixedBracket',fixed,'black',6,1)
 for side in [-1,1]:b.cyl('SteeringDamper_HeadBolt_'+str(side),(side*19,446,855),4.5,15,'steel',(1,0,0),24,.4)
 b.rod('SteeringDamper_BodyPivot',(-5,410,888),(-5,410,916),6,'steel')
 p=[(91,433,900),(108,441,897),(149,415,902),(151,399,902),(134,397,902)]
 o=b.panel('SteeringDamper_MovingBracket',p,'black',7,1);o['steer_with_front']=True
 b.rod('SteeringDamper_EndPivot',(142,406,898),(142,406,920),6,'steel')
 b.rod('SteeringDamper_ClampBolt',(98,436,890),(98,436,909),5,'steel')
 report['damper']={'translation_mm':[0,40,-12],'fixed_to':'Frame_SteeringHead','moving_to':'TripleClamp_Upper','hidden_fastener_depth':'unmeasured'}
 return report

def body(s,b):
 # Broad folded black triangular cover follows the under-seat edge down to
 # the rider rearset; old narrow floating rectangle was behind an exposed rail.
 g=[]
 for a,c in [((168,-9,698),(155,-239,645)),((167,-10,694),(153,-240,640)),((159,-31,646),(148,-227,611)),((153,-58,570),(139,-198,550)),((145,-83,495),(129,-166,480)),((137,-108,427),(121,-137,419)),((135,-111,419),(121,-133,414)),((134,-112,416),(122,-131,413))]:
  g.append([list(Vector(a).lerp(Vector(c),t)+Vector((6*math.sin(math.pi*t),0,0))) for t in [0,.05,.25,.5,.75,.95,1]])
 for row in g:
  for q in row:q[2]-=3
 control(s,'Body_MidSideCover',g,crease_columns={'3':.55},crease_boundary=.8)
 g=copy.deepcopy(BASE['Body_BellyPan']['grid'])
 for i,r in enumerate(g):
  dz=[12,40,75,65,18][i]
  for j,p in enumerate(r):p[2]+=dz*(1-j/(len(r)-1))**1.1
 control(s,'Body_BellyPan',g,crease_boundary=.75)
 g=copy.deepcopy(BASE['Cockpit_InnerPanel']['grid'])
 for i,r in enumerate(g):
  for j,p in enumerate(r):p[2]-=[10,14,21,29,25,20][i]*(1-j/(len(r)-1))
 ob=control(s,'Cockpit_InnerPanel',g,crease_columns={'3':.3},crease_boundary=.75)
 m=ob.modifiers.new('R48_ShellVolume','REMESH');m.mode='VOXEL';m.voxel_size=.0007;m.use_smooth_shade=True
 m=ob.modifiers.new('R48_ShellSmooth','SMOOTH');m.factor=.15;m.iterations=1
 return {'covers':['Body_MidSideCover','Body_BellyPan','Cockpit_InnerPanel']}

def front(s,b):
 # Lower cheek tapers to an outward blade, not a flat full-width jaw.
 cg=copy.deepcopy(BASE['Body_NoseCheek']['grid']);rg=copy.deepcopy(BASE['Body_NoseSideReturn']['grid'])
 for i,a,c in [(5,(151,798,834),(195,798,843)),(6,(134,833,788),(190,805,794)),(7,(155,821,740),(193,790,737)),(8,(185,798,709),(194,790,706))]:
  cg[i]=[list(Vector(a).lerp(Vector(c),t)) for t in [0,.04,.2,.5,.8,.96,1]]
  old=rg[i][0];delta=Vector(c)-Vector(old)
  for j,p in enumerate(rg[i]):rg[i][j]=list(Vector(p)+delta*(1-j/(len(rg[i])-1)))
 control(s,'Body_NoseCheek',cg,crease_columns={},crease_boundary=.72)
 control(s,'Body_NoseSideReturn',rg,crease_columns={'3':.2},crease_boundary=.72)
 # Remove the spiderweb-shaped reflector and replace its annular bowl with
 # an elliptic parabolic center and a shield-shaped outer transition.
 o=s.objects['Headlight_Reflector'];N=96
 lens=s.objects['Headlight_Lens'].evaluated_get(bpy.context.evaluated_depsgraph_get());lm=lens.to_mesh()
 from rebuild_rear_hardware_r36 import hull
 contour=hull([(v.co.x*1000,v.co.z*1000) for v in lm.vertices]);lens.to_mesh_clear();center=Vector((0,817));radii=[]
 # Uniform angular sampling avoids clustered corners and the false circular rim.
 for j in range(N):
  direction=Vector((math.cos(j*math.tau/N),math.sin(j*math.tau/N)));candidates=[]
  for k,p in enumerate(contour):
   a=Vector(p);edge=Vector(contour[(k+1)%len(contour)])-a
   mat=Matrix(((direction.x,-edge.x),(direction.y,-edge.y)))
   if abs(mat.determinant())<1e-8:continue
   distance,u=mat.inverted()@(a-center)
   if distance>0 and -.00001<=u<=1.00001:candidates.append(distance)
  radii.append(min(candidates)*.945)
 vs=[]
 for r in [1,.93,.8,.65,.50,.36,.22]:
  for j in range(N):
   a=j*math.tau/N;rad=radii[j]*r;q=Vector((rad*math.cos(a),0,817+rad*math.sin(a)))
   hit,loc,n,idx=lens.ray_cast(Vector((q.x*.001,2,q.z*.001)),Vector((0,-1,0)))
   if not hit:raise RuntimeError('Reflector outside lens')
   q.y=loc.y*1000-4-38*(1-r*r);vs.append(q)
 fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(6) for i in range(N)]
 K=len(vs);vs += [p-Vector((0,1,0)) for p in vs];fs += [tuple(i+K for i in reversed(f)) for f in fs]
 for start in [0,6*N]:
  for i in range(N):a=start+i;c=start+(i+1)%N;fs.append((a,c,c+K,a+K))
 mat=o.data.materials[0].copy();mat.name='MAT_Gray_Reflector_R48';mat.diffuse_color=(.62,.62,.62,1)
 me=bpy.data.meshes.new('Headlight_Reflector_R48');me.from_pydata([p*.001 for p in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat)
 for f in me.polygons:f.use_smooth=True
 o.data=me;o.modifiers.clear()
 mask_front(s,b,lens,radii)
 return {'lower_cheek':'outward taper','reflector':'uniform angular sampling of shield perimeter, parabolic bowl and bulb socket'}

def mask_front(s,b,lens,radii):
 # A closed four-row annulus follows the actual shield lens. No planar
 # polygon spanning the lamp openings and no disconnected remesh fragments.
 b.COL=b.C['FrontEnd'];purge(s,('Headlight_InnerMask','Tool_R48WingOpening'))
 N=len(radii);vs=[]
 for ring in range(4):
  for j,rr in enumerate(radii):
   a=j*math.tau/N;radius=rr/.945
   hit,loc,normal,index=lens.ray_cast(Vector((radius*.945*math.cos(a)*.001,2,(817+radius*.945*math.sin(a))*.001)),Vector((0,-1,0)))
   if not hit:raise RuntimeError('Mask edge ray missed lens')
   r=radius+(1.5 if ring in (0,3) else 14)
   vs.append((r*math.cos(a),loc.y*1000-17-(4 if ring in (2,3) else 0),817+r*math.sin(a)))
 fs=[(k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j) for k in range(4) for j in range(N)]
 o=b.mesh('Headlight_InnerMask',vs,fs,'black',smo=True)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 mat=o.data.materials[0].copy();mat.name='MAT_Gray_HeadlightInner';mat.diffuse_color=(.06,.065,.07,1);o.data.materials.clear();o.data.materials.append(mat)


def apply(s):
 if s.get('revision')!='r47':raise ValueError('Requires checkpointed r47')
 b=init(s);report={'tail':tail(s,b),'mounts':mounts(s,b),'body':body(s,b),'front':front(s,b)}
 s['revision']='r48';s.name='GSX250R_Reconstruction_V2_Gray_r48'
 bpy.context.view_layer.update();(V/'data/current_controls/owner_r48_layout.json').write_text(json.dumps(report,indent=2))
 return report
