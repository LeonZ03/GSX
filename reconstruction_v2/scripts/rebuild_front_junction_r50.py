"""r49 -> r50: fitted front-lamp recess and actual rolled fairing aperture.
Photo-led construction, not measured dimensions. Run only via Blender MCP.
"""
import bpy,bmesh,json,math,sys,heapq
from pathlib import Path
from mathutils import Vector,Matrix
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_structure import init,purge
from rebuild_owner_shapes import remove
from rebuild_rear_hardware_r36 import hull


def mesh(s,name,vs,fs,mat):
 old=s.objects.get(name)
 if old: remove(s,name)
 me=bpy.data.meshes.new(name+'_R50');me.from_pydata([Vector(p)*.001 for p in vs],[],fs);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for f in me.polygons:f.use_smooth=True
 me.materials.append(mat);o=bpy.data.objects.new(name,me)
 next(c for c in s.collection.children if c.name=='Collection_FrontEnd').objects.link(o)
 return o


def closed_surface(s,name,front,faces,boundary,depth,mat):
 K=len(front);vs=list(front)+[Vector(p)-Vector((0,depth,0)) for p in front]
 fs=list(faces)+[tuple(i+K for i in reversed(f)) for f in faces]
 fs += [(a,a+K,c+K,c) for a,c in boundary]
 return mesh(s,name,vs,fs,mat)


def aperture_edge(s):
 # Extract the actual subdivided inner edge, not the coarse control polygon.
 src=s.objects['Body_NoseCheek'];o=src.copy();o.data=src.data.copy();s.collection.objects.link(o)
 for m in list(o.modifiers):
  if m.type not in ('MIRROR','SUBSURF'):o.modifiers.remove(m)
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh()
 bm=bmesh.new();bm.from_mesh(me);pts=[v.co.copy()*1000 for v in bm.verts];adj={}
 for edge in bm.edges:
  if edge.is_boundary:
   a,c=[v.index for v in edge.verts];adj.setdefault(a,[]).append(c);adj.setdefault(c,[]).append(a)
 baseline=json.loads((V/'data/revisions/r49_front_baseline/controls.json').read_text())['Body_NoseCheek']['grid']
 a=Vector(baseline[0][0]);c=Vector(baseline[-1][0]);start=min(adj,key=lambda i:(pts[i]-a).length);end=min(adj,key=lambda i:(pts[i]-c).length)
 # Shortest boundary path stays on the positive-X inner contour.
 dist={start:0};prev={};q=[(0,start)]
 while q:
  d,i=heapq.heappop(q)
  if i==end:break
  if d!=dist[i]:continue
  for j in adj[i]:
   nd=d+(pts[i]-pts[j]).length*(100 if pts[j].x<-.1 else 1)
   if nd<dist.get(j,1e30):dist[j]=nd;prev[j]=i;heapq.heappush(q,(nd,j))
 path=[end]
 while path[-1]!=start:path.append(prev[path[-1]])
 path.reverse();right=[pts[i] for i in path]
 bm.free();e.to_mesh_clear();bpy.data.objects.remove(o,do_unlink=True)
 if len(right)<12 or max(p.x for p in right)>200:raise RuntimeError('Unexpected fairing inner edge')
 # Lower return follows the real V below the lamp, rather than an open strap.
 bottom=[Vector((105,864,712)),Vector((64,869,706)),Vector((0,871,701))]
 contour=right+bottom+[Vector((-p.x,p.y,p.z)) for p in reversed(bottom[:-1]+[])]
 # Mirror the right path, excluding the center vertex duplicated at closure.
 contour=right+bottom+[Vector((-p.x,p.y,p.z)) for p in reversed(bottom[:-1])]+[Vector((-p.x,p.y,p.z)) for p in reversed(right[1:])]
 return contour,right


def radial(contour,theta,center_z=800):
 d=Vector((math.cos(theta),math.sin(theta)));center=Vector((0,center_z));hits=[]
 for j,p in enumerate(contour):
  c=contour[(j+1)%len(contour)];a=Vector((p.x,p.z));edge=Vector((c.x-p.x,c.z-p.z))
  mat=Matrix(((d.x,-edge.x),(d.y,-edge.y)))
  if abs(mat.determinant())<1e-10:continue
  r,t=mat.inverted()@(a-center)
  if r>0 and -.00001<=t<=1.00001:hits.append((r,p.y+(c.y-p.y)*t))
 if not hits:raise RuntimeError('Aperture ray miss')
 return min(hits)


def largest_component(o):
 ng=bpy.data.node_groups.new('R50_MainRecessOnly','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 inp=ng.nodes.new('NodeGroupInput');out=ng.nodes.new('NodeGroupOutput');island=ng.nodes.new('GeometryNodeInputMeshIsland');acc=ng.nodes.new('GeometryNodeAccumulateField');acc.data_type='INT';acc.domain='POINT';acc.inputs['Value'].default_value=1
 stat=ng.nodes.new('GeometryNodeAttributeStatistic');stat.data_type='FLOAT';stat.domain='POINT'
 less=ng.nodes.new('FunctionNodeCompare');less.data_type='FLOAT';less.operation='LESS_THAN';delete=ng.nodes.new('GeometryNodeDeleteGeometry');delete.domain='POINT';delete.mode='ALL'
 ng.links.new(island.outputs['Island Index'],acc.inputs['Group ID']);ng.links.new(acc.outputs['Total'],less.inputs['A']);ng.links.new(acc.outputs['Total'],stat.inputs['Attribute']);ng.links.new(inp.outputs['Geometry'],stat.inputs['Geometry']);ng.links.new(stat.outputs['Max'],less.inputs['B']);ng.links.new(less.outputs['Result'],delete.inputs['Selection']);ng.links.new(inp.outputs['Geometry'],delete.inputs['Geometry']);ng.links.new(delete.outputs['Geometry'],out.inputs['Geometry'])
 m=o.modifiers.new('R50_RemoveBuriedCutRemnants','NODES');m.node_group=ng


def apply(s):
 if s.get('revision')!='r49':raise RuntimeError('Requires checkpointed r49')
 b=init(s);black=s.objects['Headlight_InnerMask'].data.materials[0];glass=s.objects['Headlight_PositionLens'].data.materials[0]
 outline,right=aperture_edge(s)
 lens=s.objects['Headlight_Lens'].evaluated_get(bpy.context.evaluated_depsgraph_get());lm=lens.to_mesh();ch=hull([(v.co.x*1000,v.co.z*1000) for v in lm.vertices]);lens.to_mesh_clear()
 main=[Vector((x,0,z)) for x,z in ch];N=384;outer=[];inner=[]
 for j in range(N):
  a=j*math.tau/N;rr,y=radial(outline,a);ri,_=radial(main,a)
  # Actual optical-surface depth just inside its silhouette.
  for f in [.98,.96,.94,.90,.85]:
   hit,p,n,idx=lens.ray_cast(Vector((ri*f*math.cos(a)*.001,2,(800+ri*f*math.sin(a))*.001)),Vector((0,-1,0)))
   if hit:break
  if not hit:raise RuntimeError('Main glass edge missing')
  inner.append(Vector(((ri+1.0)*math.cos(a),p.y*1000-3.8,800+(ri+1.0)*math.sin(a))))
  ro=max(rr+3.0,ri+5.0)
  outer.append(Vector((ro*math.cos(a),min(y-7.5,p.y*1000-6.8),800+ro*math.sin(a))))
 ts=[0,.07,.25,.50,.75,.94,1];vs=[]
 for t in ts:
  for a,c in zip(inner,outer):
   p=a.lerp(c,t);p.y-=2.0*math.sin(math.pi*t);vs.append(p)
 fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(len(ts)-1) for i in range(N)]
 boundary=[(i,(i+1)%N) for i in range(N)]+[((len(ts)-1)*N+(i+1)%N,(len(ts)-1)*N+i) for i in range(N)]
 purge(s,('Headlight_InnerMask','Headlight_PositionSurround','Headlight_Surround'))
 mask=closed_surface(s,'Headlight_InnerMask',vs,fs,boundary,2.5,black)
 mask['evidence']='Owner front photo72: continuous recessed black lamp surround; no open slot through to fork'
 # Position glazing conforms to the surrounding three-dimensional lamp recess.
 bpy.context.view_layer.update();ev=mask.evaluated_get(bpy.context.evaluated_depsgraph_get())
 from rebuild_owner_shapes import rounded_path
 poly=rounded_path([(169,0,889),(117,0,851),(119,0,812)],r=4)
 cen=sum(poly,Vector())/len(poly);pv=[];K=len(poly)
 for t in [1,.80,.45]:
  for p in poly:
   q=cen.lerp(p,t);hit,loc,n,idx=ev.ray_cast(Vector((q.x*.001,2,q.z*.001)),Vector((0,-1,0)))
   if not hit:raise RuntimeError('Wing not seated on lamp recess '+str(list(q)))
   q.y=loc.y*1000+2.0;pv.append(q)
 q=cen.copy();hit,p,n,idx=ev.ray_cast(Vector((q.x*.001,2,q.z*.001)),Vector((0,-1,0)));q.y=p.y*1000+2;pv.append(q)
 pf=[(k*K+i,k*K+(i+1)%K,(k+1)*K+(i+1)%K,(k+1)*K+i) for k in range(2) for i in range(K)]+[(2*K+i,2*K+(i+1)%K,3*K) for i in range(K)]
 o=closed_surface(s,'Headlight_PositionLens',pv,pf,[(i,(i+1)%K) for i in range(K)],1.0,glass);m=o.modifiers.new('Symmetry_X','MIRROR')
 # Recess lip: narrow integral housing frame, following the same surface.
 # Contact is the intended mounting interface, not a floating rim.
 for side,lab in [(-1,'L'),(1,'R')]:
  pr=[]
  for t in [1,1.045]:
   for p in pv[:K]:
    q=cen.lerp(Vector((p.x,0,p.z)),t);q.x*=side
    hit,loc,n,idx=ev.ray_cast(Vector((q.x*.001,2,q.z*.001)),Vector((0,-1,0)))
    if not hit:raise RuntimeError('Wing bezel leaves housing')
    q.y=loc.y*1000+1.7;pr.append(q)
  ff=[(i,(i+1)%K,K+(i+1)%K,K+i) for i in range(K)]
  bd=[(i,(i+1)%K) for i in range(K)]+[(K+(i+1)%K,K+i) for i in range(K)]
  closed_surface(s,'Headlight_PositionSeat_'+lab,pr,ff,bd,2.2,black)
 # Editable, physically thick inward return along both painted aperture edges.
 # Welded into the existing live nose assembly; no external structural tube.
 remove(s,'Body_NoseApertureReturn');b.COL=b.C['Body']
 rows=[[list(p+Vector((0,-d,0))) for d in [-.5,.2,2.0,6.0,8.5]] for p in right]
 ret=b.patch('Body_NoseApertureReturn',rows,'black',2.5,1);ret.data.materials.clear();ret.data.materials.append(s.objects['Body_NoseCheek'].data.materials[0]);m=ret.modifiers.new('Symmetry_X','MIRROR');m.use_clip=True
 ret.hide_render=True;ret.hide_set(True);ret['export_exclude']=True
 ng=next(m.node_group for m in s.objects['Body_NoseAssembly'].modifiers if m.type=='NODES');join=next(n for n in ng.nodes if n.bl_idname=='GeometryNodeJoinGeometry')
 info=ng.nodes.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=ret;info.transform_space='ORIGINAL';ng.links.new(info.outputs['Geometry'],join.inputs['Geometry'])
 for mod in s.objects['Body_NoseAssembly'].modifiers:
  if mod.type=='BOOLEAN':mod.solver='MANIFOLD'
 # Finish the lamp-to-paint joint against the live evaluated shell.
 # This cuts only the recessed overlap; it is not a flat filler on top.
 m=mask.modifiers.new('R50_PaintInterface','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=s.objects['Tool_R49NoseJoint']
 m=mask.modifiers.new('R50_ClosedRecessVolume','REMESH');m.mode='VOXEL';m.voxel_size=.0006;m.use_smooth_shade=True
 m=mask.modifiers.new('R50_RecessRelax','SMOOTH');m.factor=.15;m.iterations=2
 largest_component(mask)
 # The changed neighbor produces microscopic slivers in the existing fairing
 # cut. A finite-volume finish retains its editable parent and two sides.
 side=s.objects['Body_SideFairing'];m=side.modifiers.new('R50_JointVolumeFinish','REMESH');m.mode='VOXEL';m.voxel_size=.0007;m.use_smooth_shade=True
 m=side.modifiers.new('R50_JointRelax','SMOOTH');m.factor=.12;m.iterations=2
 m=side.modifiers.new('R50_CurvatureReduction','DECIMATE');m.ratio=.15
 # Every visible part retains its finite wall. The supporting mask mounts
 # against the pre-existing rear headlight housing.
 s['revision']='r50';s.name='GSX250R_Reconstruction_V2_Gray_r50'
 report={'revision':'r50','main_aperture_nominal_gap_mm':1.0,'recess_wall_mm':2.5,'paint_return_depth_mm':8.5,'position_lens_wall_mm':1.0,'fit_basis':'evaluated subdivided painted edge and actual lens silhouette','references':['owner photo72 front','owner photo63 oblique','owner photo69 side'],'unverified':'clearance, hidden mount depths and photo similarity not measured','editable_return_grid_mm':rows}
 (V/'data/current_controls/front_junction_r50.json').write_text(json.dumps(report,indent=2))
 for name in ['Headlight_InnerMask','Headlight_PositionLens','Headlight_PositionSeat_L','Headlight_PositionSeat_R']:
  o=s.objects[name];d={'name':name,'revision':'r50','vertices_mm':[[float(c*1000) for c in v.co] for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'mirror_x':name=='Headlight_PositionLens'}
  path=V/'data/current_controls'/(name+'_r50.json');path.write_text(json.dumps(d,indent=2));o['control_cage_source']='reconstruction_v2/data/current_controls/'+path.name
 bpy.context.view_layer.update();return report
