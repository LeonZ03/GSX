"""Reference-led r50->r51 front reconstruction; commercial previews stay local.
The dimensions below are visual estimates, not factory measurements.
"""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
V=Path(__file__).resolve().parents[1]
from rebuild_owner_structure import init,purge,ring
from rebuild_owner_shapes import rounded_path,remove
from rebuild_front_junction_r50 import closed_surface as raw_closed_surface,radial,mesh

def closed_surface(s,n,vs,fs,bd,depth,mat):
 triangles=[]
 for f in fs:
  for j in range(1,len(f)-1):triangles.append((f[0],f[j],f[j+1]))
 return raw_closed_surface(s,n,vs,triangles,bd,depth,mat)

CHANGED=[]
def save_control(o):
 d={'name':o.name,'revision':'r51','units':'mm','vertices_mm':[[round(c*1000,5) for c in v.co] for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'materials':[m.name for m in o.data.materials],'material_indices':[f.material_index for f in o.data.polygons],'status':'VISUAL_ESTIMATE_NOT_PASSED'}
 p=V/'data/current_controls'/(o.name+'_r51.json');p.write_text(json.dumps(d,indent=2));o['control_cage_source']='reconstruction_v2/data/current_controls/'+p.name;CHANGED.append(o.name)

def symmetric(points):return [Vector(p) for p in points]+[Vector((-p[0],p[1],p[2])) for p in reversed(points[1:-1])]
def surf(s,n,vs,fs,mat,th=2):
 o=mesh(s,n,vs,fs,mat);m=o.modifiers.new('Editable_quad_subdivision','SUBSURF');m.levels=m.render_levels=2
 m=o.modifiers.new('Physical_wall','SOLIDIFY');m.thickness=th*.001;m.offset=-1
 save_control(o);return o

def apply(s):
 assert s.get('revision')=='r50','Migration requires unchanged r50 parent'
 b=init(s);paint=s.objects['Body_NoseCheek'].data.materials[0];black=s.objects['Headlight_InnerMask'].data.materials[0];glass=s.objects['Headlight_Lens'].data.materials[0];silver=s.objects['Headlight_Reflector'].data.materials[0]
 # Three homologous boundaries: lamp aperture, painted crease, rear attachment.
 # Upper shoulders now rise alongside the windscreen. The chin is swept forward.
 inner=[(0,763,898),(72,764,897),(100,784,873),(180,755,915),(175,780,879),(155,807,843),(133,838,798),(108,859,753),(111,875,718),(0,884,711)]
 ridge=[(0,755,910),(116,710,959),(145,687,984),(203,714,950),(216,750,898),(214,780,854),(198,814,806),(148,850,753),(129,875,712),(0,894,695)]
 back=[(0,734,910),(130,610,930),(162,557,916),(187,575,878),(203,611,829),(212,637,782),(213,642,749),(193,683,721),(166,727,705),(0,826,681)]
 # The old hidden components are retained for history but removed from live output.
 A=symmetric(inner);B=symmetric(ridge);C=symmetric(back);N=len(A)
 rings=[]
 for t in [0,.025,.14,.38,.70,.96,1]:rings.append([a.lerp(c,t) for a,c in zip(A,B)])
 for t in [.04,.18,.42,.72,.96,1]:rings.append([a.lerp(c,t)+Vector((math.copysign(2*math.sin(math.pi*t),a.x) if abs(a.x)>.01 else 0,0,0)) for a,c in zip(B,C)])
 vs=[p for rr in rings for p in rr];fs=[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(rings)-1) for i in range(N)]
 cage=surf(s,'Tool_R51NoseCage',vs,fs,paint,3);cage.data.materials.append(black)
 for face in cage.data.polygons:
  sector=face.index%N
  if sector in (8,9):face.material_index=1
 save_control(cage)
 cage.hide_render=True;cage.hide_set(True);cage['export_exclude']=True
 # Reuse the existing assembly object: all downstream live seam tools keep their target.
 out=s.objects['Body_NoseAssembly'];out.modifiers.clear()
 ng=bpy.data.node_groups.new('R51_EditableNoseAndSide','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 join=ng.nodes.new('GeometryNodeJoinGeometry');end=ng.nodes.new('NodeGroupOutput');ng.links.new(join.outputs[0],end.inputs[0])
 for o in [cage,s.objects['Body_UpperSideCowl']]:
  no=ng.nodes.new('GeometryNodeObjectInfo');no.inputs['Object'].default_value=o;no.transform_space='ORIGINAL';ng.links.new(no.outputs['Geometry'],join.inputs['Geometry'])
 m=out.modifiers.new('R51_Editable_shell_sources','NODES');m.node_group=ng
 m=out.modifiers.new('R51_Joined_shell','REMESH');m.mode='VOXEL';m.voxel_size=.0009;m.use_smooth_shade=True
 m=out.modifiers.new('R51_Surface_relax','SMOOTH');m.factor=.22;m.iterations=2
 m=out.modifiers.new('R51_Windscreen_clearance','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=s.objects['Tool_R47Aperture_Windscreen']
 CHANGED.append(out.name)
 bpy.context.view_layer.update()
 # Main lamp is a tall, shouldered optical housing, not a featureless shield.
 main=symmetric([(0,772,895),(66,775,892),(87,786,877),(104,808,846),(103,833,806),(77,856,766),(36,872,734),(0,877,722)])
 path=rounded_path(main,r=5);N=len(path);center=Vector((0,821,816))
 # Main glazing: gentle double curvature and finite wall, independent of bowl.
 vs=[]
 for t in [1,.94,.72,.44,.18]:
  for p in path:
   q=center.lerp(p,t);q.y+=16*(1-t*t);vs.append(q)
 vs.append(center+Vector((0,16,0)));fs=[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(4) for i in range(N)]
 fs += [(4*N+i,4*N+(i+1)%N,5*N) for i in range(N)]
 # Retire objects whose geometry is now replaced, including stale rims.
 purge(s,('Headlight_Lens','Headlight_InnerMask','Headlight_PositionLens','Headlight_PositionSeat','Headlight_Housing','Headlight_Reflector','Headlight_Bulb','Headlight_BrowSeal'))
 o=closed_surface(s,'Headlight_Lens',vs,fs,[(i,(i+1)%N) for i in range(N)],1.8,glass);save_control(o)
 # Black annulus shares the actual painted opening, with a shallow assembly reveal.
 M=256;outer=[];inside=[]
 for j in range(M):
  ang=j*math.tau/M;ri,yi=radial(path,ang,800);ro,yo=radial(A,ang,800)
  inside.append(Vector(((ri+.9)*math.cos(ang),yi-3.2,800+(ri+.9)*math.sin(ang))))
  outer.append(Vector(((ro+2)*math.cos(ang),yo-6,800+(ro+2)*math.sin(ang))))
 vs=[a.lerp(c,t)+Vector((0,-3*math.sin(math.pi*t),0)) for t in [0,.1,.4,.75,1] for a,c in zip(inside,outer)]
 fs=[(k*M+i,k*M+(i+1)%M,(k+1)*M+(i+1)%M,(k+1)*M+i) for k in range(4) for i in range(M)]
 o=closed_surface(s,'Headlight_InnerMask',vs,fs,[(i,(i+1)%M) for i in range(M)]+[(4*M+(i+1)%M,4*M+i) for i in range(M)],2.5,black);save_control(o)
 # Optical bowl uses horizontal and longitudinal facets, not a radial fan.
 rows=[(891,775,63),(884,783,77),(869,798,91),(849,812,102),(825,825,103),(802,837,96),(779,850,82),(759,859,65),(741,868,41),(728,874,12)]
 vv=[];cols=17
 for j,(z,y,w) in enumerate(rows):
  for i in range(cols):
   u=-1+2*i/(cols-1);depth=48*(1-u*u)*math.sin(math.pi*(j+.6)/(len(rows)+.2))**.65
   flute=1.5*(i%2)*math.sin(math.pi*j/(len(rows)-1))*(1-u*u)
   vv.append(Vector((w*u,y-8-depth+flute,z)))
 ff=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(len(rows)-1) for i in range(cols-1)]
 bd=[(i,i+1) for i in range(cols-1)]+[((len(rows)-1)*cols+i+1,(len(rows)-1)*cols+i) for i in range(cols-1)]+[(j*cols,(j+1)*cols) for j in range(len(rows)-1)]+[((j+1)*cols+cols-1,j*cols+cols-1) for j in range(len(rows)-1)]
 lens_ev=s.objects['Headlight_Lens'].evaluated_get(bpy.context.evaluated_depsgraph_get())
 for q in vv:
  for retry in range(12):
   hit,loc,normal,idx=lens_ev.ray_cast(Vector((q.x*.001,2,q.z*.001)),Vector((0,-1,0)))
   if hit:break
   q.x*=.97
  if not hit:raise RuntimeError('Reflector is outside glazing')
  q.y=min(q.y,loc.y*1000-7)
 o=closed_surface(s,'Headlight_Reflector',vv,ff,bd,1.2,silver)
 for poly in o.data.polygons:poly.use_smooth=False
 save_control(o)
 N=len(path)
 # Back housing closes behind the bowl and reaches the original supports.
 front=[p-Vector((0,12,0)) for p in path];rear=[Vector((p.x*.63,706,816+(p.z-816)*.66)) for p in path]
 vs=front+rear+[Vector((0,706,816))];fs=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]+[(N+i,N+(i+1)%N,2*N) for i in range(N)]
 o=closed_surface(s,'Headlight_Housing',vs,fs,[(i,(i+1)%N) for i in range(N)],2.2,black);save_control(o)
 b.COL=b.C['FrontEnd'];b.rod('Headlight_BulbSocket',(0,720,816),(0,778,816),12,'black',48);b.sphere('Headlight_Bulb',(0,782,816),(9,15,9),'glass')
 # Curved small metal shield over the filament, mounted back to the socket.
 b.rod('Headlight_FilamentSupport',(0,766,805),(0,806,805),2,'silver')
 b.sphere('Headlight_FilamentShield',(0,805,816),(12,3,14),'silver')
 bpy.context.view_layer.update();mask=s.objects['Headlight_InnerMask'].evaluated_get(bpy.context.evaluated_depsgraph_get())
 for sign,label in [(-1,'L'),(1,'R')]:
  pp=rounded_path([(sign*169,0,899),(sign*119,0,864),(sign*117,0,820)],r=3);cen=sum(pp,Vector())/len(pp);K=len(pp);vv=[]
  for t in [1,.7,.3]:
   for p in pp:
    q=cen.lerp(p,t);hit,loc,normal,idx=mask.ray_cast(Vector((q.x*.001,2,q.z*.001)),Vector((0,-1,0)))
    if not hit:raise RuntimeError('Position lamp outside recess')
    q.y=loc.y*1000+1.8;vv.append(q)
  hit,loc,normal,idx=mask.ray_cast(Vector((cen.x*.001,2,cen.z*.001)),Vector((0,-1,0)));cen.y=loc.y*1000+1.8;vv.append(cen)
  ff=[(k*K+i,k*K+(i+1)%K,(k+1)*K+(i+1)%K,(k+1)*K+i) for k in range(2) for i in range(K)]+[(2*K+i,2*K+(i+1)%K,3*K) for i in range(K)]
  o=closed_surface(s,'Headlight_PositionLens_'+label,vv,ff,[(i,(i+1)%K) for i in range(K)],1,glass);save_control(o)
  # A separate bright bowl behind each small lens keeps the optical silhouette legible.
  o=closed_surface(s,'Headlight_PositionReflector_'+label,[p-Vector((0,1.2,0)) for p in vv],ff,[(i,(i+1)%K) for i in range(K)],.8,silver);save_control(o)
 s['revision']='r51';s['acceptance']='B_C_NOT_PASSED';s.name='GSX250R_Reconstruction_V2_Gray_r51'
 (V/'data/current_controls/front_layout_r51.json').write_text(json.dumps({'revision':'r51','aperture_mm':inner,'ridge_mm':ridge,'rear_boundary_mm':back,'main_lens_contour_mm':[list(p) for p in main],'source':'Owner 72 / 69 / 65 and downloaded previews 0003,0004,0008..0012','unverified':'visual estimates, not measured depth or photo acceptance'},indent=2))
 return CHANGED
