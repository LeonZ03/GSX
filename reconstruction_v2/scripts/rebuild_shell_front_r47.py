"""Owner r47: shell seams, internal frame, compound windscreen, lamps and tail carrier.
Run apply(scene) via Blender MCP. Geometry in mm. Estimated hidden dimensions.
The immutable r46 control snapshot prevents accumulating candidate deformations.
"""
import bpy, math, json, sys, copy
from pathlib import Path
from mathutils import Vector, Matrix
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_shapes import put,remove
from rebuild_owner_structure import init,purge,solid_tube,ring,box_basis
BASE=json.loads((V/'data/revisions/r46_shell_baseline/controls.json').read_text())

def control(s,name,grid,**kwargs):
 d=copy.deepcopy(BASE[name]);d.update(grid=grid,**kwargs);o=put(s,d)
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=m.render_levels=d.get('subdivision',2)
  if m.type=='SOLIDIFY':m.thickness=d.get('thickness_mm',2.5)*.001
 d['revision']='r47';(V/'data/current_controls'/(name+'.json')).write_text(json.dumps(d,indent=2))
 return o

def strip(a,c,ts=(0,.04,.2,.5,.8,.96,1),bulge=0):
 a=Vector(a);c=Vector(c)
 return [list(a.lerp(c,t)+Vector((bulge*math.sin(math.pi*t),0,0))) for t in ts]

def shell(s,b):
 b.COL=b.C['Engine']
 # Tail/seat side share the same exterior edge, rather than an exposed rail.
 # Last tail station, on either side, is a folded continuous moulded side wall.
 tail=copy.deepcopy(BASE['Body_Tail']['grid'])
 tail[-1][2]=[144,-492.19,793];tail[-1][3]=[139,-492.74,731];tail[-1][4]=[110,-493.16,718]
 control(s,'Body_Tail',tail)
 pairs=[([144,-492.2,793],[139,-492.7,731]),([142,-465,787],[144,-454,721]),
 ([137,-393,777],[154,-366,682]),([134,-267,759],[158,-238,648]),
 ([142,-145,779],[166,-115,670]),([158,-38,788],[177,-4,704]),
 ([181,68,779],[196,104,725]),([185,121,750],[196,167,701])]
 pairs[0]=([144,-489.7,793],[139,-490.2,731])
 control(s,'Body_SeatSide',[strip(a,c,bulge=2) for a,c in pairs],crease_boundary=.85,crease_columns={'2':.15,'4':.2})
 # Frame members are internal chassis members, not panel-joining edge trim.
 # Preserve genuine steering and lower mounting points; revise invented bows.
 paths={'Frame_Main':[(61.5,452,791),(86,258,716),(104,-145,586),(115,-265,390)],
 'Frame_Subframe':[(105,-226,620),(93,-440,759),(62,-690,871),(35,-900,983)],
 'Frame_Cradle':[(117,268,629),(124,278,549),(105,244,341),(92,50,269),(96,-233,358)]}
 for side,lab in [(-1,'L'),(1,'R')]:
  for prefix,points in paths.items():
   old=s.objects[prefix+'_'+lab];radius=old.data.bevel_depth*1000;remove(s,old.name)
   ob=solid_tube(b,prefix+'_'+lab,[(side*x,y,z) for x,y,z in points],radius,'black',False)
   ob['unverified']='Internal frame route inferred; no dimensioned factory frame drawing'
 # Inner mounts are rebuilt at shell points, not left at former outer rails.
 purge(s,('Fairing_MountTab_',))
 for side,lab in [(-1,'L'),(1,'R')]:
  for k,(a,c) in enumerate([((104,-145,586),(151,-151,661)),((94,156,684),(179,158,699))]):
   a=Vector((side*a[0],a[1],a[2]));c=Vector((side*c[0],c[1],c[2]));u=Vector((0,0,7))
   b.panel('Fairing_MountTab_'+lab+str(k),[a-u,c-u,c+u,a+u],'black',3,.6)
 return paths

def windscreen(s,b):
 # Double curvature: center spine and transverse bow; upper lip arches in
 # the rider view. Bottom two attachment rows retain the fairing fit.
 g=[]
 rows=[(761.329,886.534,72,25,3),(736,903,98,28,4),(714,934,112,35,6),
 (692,972,125,43,9),(668,1015,137,48,16),(644,1055,147,50,23),
 (627,1085,153,48,32),(617,1105,151,44,38)]
 for y,z,w,bow,drop in rows:
  g.append([[w*t,y-bow*t*t,z-drop*t*t] for t in [0,.2,.4,.6,.8,.96,1]])
 control(s,'Windscreen',g,crease_boundary=.55,crease_columns={},subdivision=3,thickness_mm=3)
 return rows

def front(s,b):
 b.COL=b.C['FrontEnd']
 # Paint follows a compound boundary around the central shield and side wings.
 inner=[(0,754,892),(74,755,890),(105,779,865),(184,750,911),(178,771,870),
 (151,798,834),(117,825,795),(75,851,749),(30,859,714)]
 outer=[(0,712,939),(113,708,940),(145,711,935),(199,728,932),(208,754,885),
 (204,780,843),(188,806,794),(159,829,745),(114,845,710)]
 control(s,'Body_NoseCheek',[strip(a,c,bulge=1) for a,c in zip(inner,outer)],crease_boundary=.68,crease_columns={},subdivision=2)
 # The joined return uses exactly the same outer boundary, with a narrow
 # true wall thickness. It is not an extra structural rod.
 returns=[]
 for i,(a,c) in enumerate(zip(outer,[(0,694,919),(134,651,875),(167,680,822),(190,704,780),(200,729,751),(202,746,732),(199,752,717),(191,748,706),(190,746,699)])):
  returns.append(strip(a,c,bulge=1))
 control(s,'Body_NoseSideReturn',returns,crease_boundary=.68,crease_columns={'3':.2},subdivision=2)
 # Wings are inserted into the opening between paint and main shield; they
 # no longer sit behind the blue cowling. The black rim is a real enclosure.
 pairs=[((180,756,901),(177,759,898)),((164,775,878),(108,791,850)),
 ((144,801,839),(103,825,805)),((115,828,796),(104,834,787))]
 g=[strip(a,c) for a,c in pairs]
 control(s,'Headlight_PositionLens',g,crease_boundary=.8,crease_columns={},subdivision=2,thickness_mm=1)
 purge(s,('Headlight_PositionSurround',))
 for side,lab in [(-1,'L'),(1,'R')]:
  cont=[Vector((side*p[0],p[1]-1.5,p[2])) for p in [g[0][0],g[0][-1],g[1][-1],g[2][-1],g[3][-1],g[3][0],g[2][0],g[1][0]]]
  center=sum(cont,Vector())/len(cont)
  out=[p+Vector((p.x-center.x,0,p.z-center.z)).normalized()*3 for p in cont]
  ring(s,b,'Headlight_PositionSurround_'+lab,out,cont,(0,-5,0),'black')
 # Main shield: broad upper shoulder, rounded lower point, curved lens.
 g=[]
 for z,y,w in [(886,762,69),(876,778,96),(850,807,113),(813,833,111),(773,853,83),(738,865,44),(724,864,10),(723,864,2)]:
  g.append([[w*t,y-13*(w/113)**2*t*t,z+5*(w/113)*t*t] for t in [0,.2,.45,.7,.88,.97,1]])
 control(s,'Headlight_Lens',g,crease_boundary=.7,crease_columns={},subdivision=2,thickness_mm=1.8)
 contour=[Vector(p) for p in reversed(g[0])]+[Vector((-p[0],p[1],p[2])) for p in g[0][1:]]
 contour += [Vector((-r[-1][0],r[-1][1],r[-1][2])) for r in g[1:]]
 contour += [Vector((-p[0],p[1],p[2])) for p in reversed(g[-1][:-1])]+[Vector(p) for p in g[-1][1:]]+[Vector(r[-1]) for r in reversed(g[1:-1])]
 out=[p+Vector((p.x,0,p.z-812)).normalized()*5+Vector((0,-1,0)) for p in contour]
 purge(s,('Headlight_Housing','Headlight_Surround','Headlight_Reflector','Headlight_BrowSeal'))
 ring(s,b,'Headlight_Surround',out,contour,(0,-9,0),'black')
 N=len(out);back=[Vector((p.x*.65,716,814+(p.z-814)*.65)) for p in out]
 verts=[p+Vector((0,-10,0)) for p in out]+back+[Vector((0,716,814))]
 fs=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[(2*N,N+(i+1)%N,N+i) for i in range(N)]
 ob=b.mesh('Headlight_Housing',verts,fs,'black',smo=True);m=ob.modifiers.new('Housing_wall','SOLIDIFY');m.thickness=.002;m.offset=-1
 # Reflector has a recessed central socket and curved longitudinal bowl.
 vs=[];center=Vector((0,779,824))
 for t in [0,.08,.25,.43,.6,.76,.86]:
  for p in contour:
   q=p.lerp(center,t);q.y-=3+26*math.sin(math.pi*t);vs.append(q)
 fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(6) for j in range(N)]
 ob=b.mesh('Headlight_Reflector',vs,fs,'silver');m=ob.modifiers.new('Reflector_wall','SOLIDIFY');m.thickness=.001;m.offset=-1
 # Move lamp body/socket as a unit; no floating bulb.
 for name in ['Headlight_Bulb','Headlight_BulbSocket']:
  s.objects[name].location.z+=.008
 return {'paint_boundary_mm':inner,'wing_points_mm':pairs}

def plate(s,b):
 b.COL=b.C['Details']
 # Photo59/70: lower plate edge retreats toward the rear in side/rear views.
 # Camera roll and bike lean prevent a calibrated angle; rake is provisional.
 purge(s,('LicensePlate_Carrier','LicensePlate_EdgeFlange','LicensePlate_Crossmember','LicensePlate_Bolt','LicensePlate_LampBridge','Fender_Rear_Side','Fender_Rear_Crown'))
 theta=math.radians(25);normal=Vector((0,-math.cos(theta),math.sin(theta)));up=Vector((0,math.sin(theta),math.cos(theta)))
 c=Vector((0,-1074,667));o=s.objects['LicensePlate'];o.rotation_mode='XYZ';o.rotation_euler=Matrix((Vector((1,0,0)),normal,up)).transposed().to_euler();o.location=c*.001
 # Plate local Y is thickness, local Z height; handed frame needs +Y into bike.
 o.rotation_euler=Matrix((Vector((1,0,0)),-normal,up)).transposed().to_euler()
 top=c+up*48-normal*6
 bpy.context.view_layer.update()
 tail=s.objects['Body_Tail'].evaluated_get(bpy.context.evaluated_depsgraph_get())
 hit,p,n,i=tail.ray_cast(Vector((0,-.911,.80)),Vector((0,0,1)))
 if not hit:raise RuntimeError('Tail underside mount not found')
 rows=[(-911,p.z*1000+2,29),(-944,903,43),(-975,851,48),(-1004,795,40),(top.y,top.z,43)]
 b.patch('LicensePlate_Carrier',[[[-w,y,z],[0,y+5,z+1],[w,y,z]] for y,z,w in rows],'black',4,2)
 for side,lab in [(-1,'L'),(1,'R')]:
  edge=[(side*w,y,z) for y,z,w in rows]
  b.panel('LicensePlate_EdgeFlange_'+lab,edge+[(x,y+14,z) for x,y,z in reversed(edge)],'black',3,.5)
 box_basis(s,b,'LicensePlate_Crossmember',top,(1,0,0),up,normal,180,23,8,'black',1)
 for side in [-1,1]:
  p=c+Vector((side*78,0,0))+up*48
  b.rod('LicensePlate_Bolt_'+str(side),p-normal*11,p+normal*5,4,'steel')
 # Plate light follows the carrier below the signal bar; short integral bridge.
 target=Vector((0,-1027,769));old=s.objects['LicensePlate_LampHousing'];me=old.data
 center=sum((old.matrix_world@v.co for v in me.vertices),Vector())/len(me.vertices)
 delta=target*.001-center
 for name in ['LicensePlate_LampHousing','LicensePlate_LampLens']:s.objects[name].location+=delta
 b.panel('LicensePlate_LampBridge',[(-37,-1025,769),(37,-1025,769),(39,-1009,792),(-39,-1009,792)],'black',4,.8)
 return {'plate_center_mm':list(c),'normal':list(normal),'rake_deg':25,'direction':'bottom rearward; front face tilted upward','evidence':'owner59/70; photo perspective, not calibrated plate measurement'}

def finish_lamps_and_openings(s,b):
 import bmesh
 # Constant fore-aft lens thickness avoids Solidify folding at pointed tips.
 # Hidden editable cages remain available; visible glass is the closed result.
 for name,depth in [('Headlight_Lens',1.8)]:
  o=s.objects[name];toolname='Tool_R47Cage_'+name;remove(s,toolname)
  tool=o.copy();tool.data=o.data.copy();tool.name=toolname;s.collection.objects.link(tool)
  tool.hide_render=True;tool.hide_set(True);tool['export_exclude']=True
  for m in list(o.modifiers):
   if m.type=='SOLIDIFY':o.modifiers.remove(m)
  bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh()
  verts=[v.co.copy() for v in me.vertices];faces=[tuple(f.vertices) for f in me.polygons]
  bm=bmesh.new();bm.from_mesh(me);boundary=[tuple(v.index for v in ed.verts) for ed in bm.edges if ed.is_boundary];bm.free();e.to_mesh_clear()
  N=len(verts);verts += [p+Vector((0,-depth*.001,0)) for p in verts]
  fs=faces+[tuple(v+N for v in reversed(f)) for f in faces]+[(a,b,b+N,a+N) for a,b in boundary]
  data=bpy.data.meshes.new(name+'_ClosedOpticalShell');data.from_pydata(verts,[],fs);data.update()
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  for mat in o.data.materials:data.materials.append(mat)
  for f in data.polygons:f.use_smooth=True
  o.data=data;o.modifiers.clear();o['editable_cage']=toolname
 # Triangular position lamps need a fan, not a folded rectangular grid.
 from rebuild_owner_shapes import rounded_path
 o=s.objects['Headlight_PositionLens'];mat=o.data.materials[0]
 outline=rounded_path([(180,0,901),(106,0,850),(105,0,799)],r=4)
 center=sum(outline,Vector())/len(outline)
 a=Matrix([[180,901,1],[106,850,1],[105,799,1]]).inverted()@Vector((756,798,836))
 def depth(p):return a.x*p.x+a.y*p.z+a.z
 N=len(outline);vs=[]
 for t in [1,.55]:
  for p in outline:
   q=center.lerp(p,t);q.y=depth(q)+2*(1-t*t);vs.append(q)
 q=center.copy();q.y=depth(q)+2;vs.append(q)
 fs=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[(N+i,N+(i+1)%N,2*N) for i in range(N)]
 K=len(vs);vs += [p-Vector((0,1,0)) for p in vs]
 fs+= [tuple(i+K for i in reversed(f)) for f in fs]+[(i,i+K,(i+1)%N+K,(i+1)%N) for i in range(N)]
 data=bpy.data.meshes.new('PositionLamp_ClosedTriangle');data.from_pydata([p*.001 for p in vs],[],fs);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(mat)
 for f in data.polygons:f.use_smooth=True
 o.data=data;o.modifiers.clear();m=o.modifiers.new('Symmetry_X','MIRROR');m.use_clip=True
 o['control_cage_source']='reconstruction_v2/data/current_controls/position_lens_r47.json'
 (V/'data/current_controls/position_lens_r47.json').write_text(json.dumps({'vertices_mm':[list(p) for p in vs],'faces':fs,'mirror_x':True,'revision':'r47'},indent=2))
 purge(s,('Headlight_PositionSurround',))
 for side,lab in [(-1,'L'),(1,'R')]:
  cont=[Vector((side*p.x,depth(p)-1.5,p.z)) for p in outline]
  cen=sum(cont,Vector())/len(cont);outer=[p+Vector((p.x-cen.x,0,p.z-cen.z)).normalized()*3 for p in cont]
  ring(s,b,'Headlight_PositionSurround_'+lab,outer,cont,(0,-4,0),'black')
 # Continuous lower nose return connects the two side cowls below the lamp.
 remove(s,'Body_NoseLowerValance')
 rows=[]
 for offset in [0,9,19]:
  rows.append([[170*t,858-30*abs(t)-offset,716+42*t*t-offset*.7] for t in [-1,-.85,-.65,-.35,0,.35,.65,.85,1]])
 b.COL=b.C['Body']
 (V/'data/current_controls/nose_valance_r47.json').write_text(json.dumps({'name':'Body_NoseLowerValance','grid_mm':rows,'thickness_mm':3,'subdivision':2},indent=2))
 ob=b.patch('Body_NoseLowerValance',rows,'black',3,2);ob.hide_render=True;ob.hide_set(True);ob['export_exclude']=True
 ng=next(m.node_group for m in s.objects['Body_NoseAssembly'].modifiers if m.type=='NODES')
 join=next(n for n in ng.nodes if n.bl_idname=='GeometryNodeJoinGeometry')
 node=ng.nodes.new('GeometryNodeObjectInfo');node.inputs['Object'].default_value=ob;node.transform_space='ORIGINAL';ng.links.new(node.outputs['Geometry'],join.inputs['Geometry'])
 # Cast opening volumes from actual evaluated silhouettes. These are retained
 # dependencies, so the main fairing is a continuous shell around the glazing.
 assembly=s.objects['Body_NoseAssembly']
 for m in list(assembly.modifiers):
  if m.name.startswith('R47_'):assembly.modifiers.remove(m)
 for name in ['Headlight_Lens','Windscreen']:
  o=s.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh()
  # Front projection convex hull for a central shield or windshield aperture.
  pts=sorted(set((round(v.co.x*1000,4),round(v.co.z*1000,4)) for v in me.vertices));e.to_mesh_clear()
  def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  halves=[]
  for seq in [pts,list(reversed(pts))]:
   h=[]
   for p in seq:
    while len(h)>=2 and cross(h[-2],h[-1],p)<=0:h.pop()
    h.append(p)
   halves+=h[:-1]
  cen=Vector((sum(p[0] for p in halves)/len(halves),sum(p[1] for p in halves)/len(halves)))
  boundary=[Vector(p)+(Vector(p)-cen).normalized()*1.8 for p in halves]
  N=len(boundary);vs=[(p.x,y,p.y) for y in [450,970] for p in boundary]
  fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
  toolname='Tool_R47Aperture_'+name;remove(s,toolname);tool=b.mesh(toolname,vs,fs)
  tool.hide_render=True;tool.hide_set(True);tool['export_exclude']=True
  mod=assembly.modifiers.new('R47_'+name+'_opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
 m=assembly.modifiers.new('R47_OpeningVolumeFinish','REMESH');m.mode='VOXEL';m.voxel_size=.0008;m.use_smooth_shade=True
 m=assembly.modifiers.new('R47_OpeningSmooth','SMOOTH');m.factor=.15;m.iterations=1

def apply(s):
 if s.get('revision') != 'r46':raise ValueError('Expected r46 base')
 b=init(s);report={'frame':shell(s,b),'windscreen_stations':windscreen(s,b),'front':front(s,b),'plate':plate(s,b)}
 s['revision']='r47';s.name='GSX250R_Reconstruction_V2_Gray_r47'
 finish_lamps_and_openings(s,b)
 bpy.context.view_layer.update()
 (V/'data/current_controls/shell_front_r47_layout.json').write_text(json.dumps(report,indent=2))
 return report


def tank_interface(s):
 # Extend the upper edge of the same thick side panel to the tank flank.
 # Ray positions are queried from the evaluated tank, not input constants.
 bpy.context.view_layer.update();tank=s.objects['Body_Tank'].evaluated_get(bpy.context.evaluated_depsgraph_get())
 d=copy.deepcopy(BASE['Body_TankSideTrim']);g=d['grid'];hits=[]
 for i,z in enumerate([824,830,832,831,832,835]):
  y=g[i][0][1];hit,p,n,idx=tank.ray_cast(Vector((.5,y*.001,z*.001)),Vector((-1,0,0)))
  if not hit:raise RuntimeError('Missing tank side interface '+str(i))
  p*=1000;p.x+=3.5;end=g[i][-1];g[i]=strip(p,end,bulge=1.0);hits.append(list(p))
 ob=control(s,'Body_TankSideTrim',g,crease_boundary=.7,crease_columns={'2':.25,'4':.35})
 name='Tool_R47TankTrimClearance';remove(s,name)
 me=bpy.data.meshes.new_from_object(tank,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
 for v in me.vertices:v.co+=v.normal*.0015
 tool=bpy.data.objects.new(name,me);s.collection.objects.link(tool);tool.hide_render=True;tool.hide_set(True);tool['export_exclude']=True
 mod=ob.modifiers.new('R47_TankClearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
 (V/'data/current_controls/tank_trim_r47_interface.json').write_text(json.dumps({'points_mm':hits,'clearance_setting_mm':3.5,'not_a_measured_clearance':True},indent=2))
 return hits
