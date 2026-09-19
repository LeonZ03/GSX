"""Audit stage B/C evaluated geometry and unchanged baseline assemblies."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]

def signature(o):
 d={'type':o.type,'matrix':[round(x,8) for r in o.matrix_world for x in r]}
 if o.type=='MESH':d['v']=[[round(x,8) for x in v.co] for v in o.data.vertices];d['f']=[list(p.vertices) for p in o.data.polygons]
 elif o.type=='CURVE':d['p']=[[[round(x,8) for x in p.co] for p in (s.bezier_points if s.type=='BEZIER' else s.points)] for s in o.data.splines]
 elif o.type=='CAMERA':d['intrinsics']=[o.data.type,o.data.lens,o.data.sensor_width,o.data.shift_x,o.data.shift_y,o.data.sensor_fit]
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()

def cap_wall_vertex_contact(a,b,verts,faces,tol=1e-7):
 """Separate point-on-edge contacts from crossings at Boolean disc cap walls.
 Requires a triangle supported entirely to one side of the wall's plane edge;
 it therefore cannot dismiss an edge crossing the triangle's interior.
 """
 for ia,ib in [(a,b),(b,a)]:
  aa=[verts[i] for i in faces[ia]];bb=[verts[i] for i in faces[ib]]
  for axis in range(3):
   if max(p[axis] for p in aa)-min(p[axis] for p in aa)>1e-9:continue
   plane=aa[0][axis];edge=[p for p in bb if abs(p[axis]-plane)<1e-9]
   if len(edge)!=2:continue
   dims=[i for i in range(3) if i!=axis];u,v=edge;dx=v[dims[0]]-u[dims[0]];dy=v[dims[1]]-u[dims[1]];ll=(dx*dx+dy*dy)**.5
   if ll<1e-10:continue
   dist=[(dx*(p[dims[1]]-u[dims[1]])-dy*(p[dims[0]]-u[dims[0]]))/ll for p in aa]
   near=[i for i,d in enumerate(dist) if abs(d)<tol]
   if len(near)!=1:continue
   other=[d for i,d in enumerate(dist) if i!=near[0]]
   pp=aa[near[0]];q=((pp[dims[0]]-u[dims[0]])*dx+(pp[dims[1]]-u[dims[1]])*dy)/(ll*ll)
   if other[0]*other[1]>0 and -1e-6<=q<=1+1e-6:return True
 return False

def audit(scene):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();q={};trees={};normals={}
 targets=[o for o in scene.objects if not o.get('construction_control_only') and o.name.startswith(('Body_Nose','Body_SideFairing','Body_WindscreenSeat','Cockpit_InnerPanel','BrakeDisc_','ABS_Ring_','Sprocket_Front','Sprocket_Rear','Engine_Crankcase','Spoke_','Engine_ClutchCover','Engine_AlternatorCover','Exhaust_HeatShield'))]
 for o in targets:
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.loop_triangles]
  tree=BVHTree.FromPolygons(v,f,all_triangles=True);pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])]
  boundary=sum(cap_wall_vertex_contact(i,j,v,f) for i,j in pairs)
  bm=bmesh.new();bm.from_mesh(me)
  q[o.name]={'evaluated_vertices':len(me.vertices),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_edges for v in bm.verts),'zero_area_faces':sum(p.area<1e-13 for p in me.polygons),'raw_nonadjacent_bvh_pairs':len(pairs),'verified_vertex_on_edge_contacts':boundary,'nonadjacent_self_intersection_candidates':len(pairs)-boundary}
  bm.free();trees[o.name]=tree;ev.to_mesh_clear()
 check=[('Body_NoseCheek','Body_NoseSideReturn'),('Body_NoseCheek','Body_NoseCrown'),('Body_NoseCrown','Body_WindscreenSeat'),('Body_NoseSideReturn','Body_WindscreenSeat')]
 overlap={a+' / '+b:len(trees[a].overlap(trees[b])) for a,b in check if a in trees and b in trees}
 # Capture immutable hashes before opening the baseline in this isolated audit
 # process. This avoids Blender suffix renaming corrupting duplicate-object checks.
 revision=scene.get('revision');source=bpy.data.filepath;drive_changed=bool(scene.get('stage_c_drive_rebuilt'))
 now={o.name:signature(o) for o in scene.objects}
 bpy.ops.wm.open_mainfile(filepath=str(V/'blends/15_gray_review.blend'))
 old={o.name:o for o in bpy.context.scene.objects}
 retain=('Tire_','Wheel_','Hub_','Axle_','Frame_','Swingarm','Rearset_','Footpeg_','PassengerPeg','SideStand','RearShock_','Shock_','Chain','Sprocket_','GuardBar','GuardMount')
 preserved={n:(n in now and signature(o)==now[n]) for n,o in old.items() if n.startswith(retain)}
 intentional={n:p for n,p in preserved.items() if drive_changed and (n=='Chain' or n.startswith(('Chain_Link','Chain_Roller','Sprocket_')))}
 preserved={n:p for n,p in preserved.items() if n not in intentional}
 cameras={n:(n in now and signature(o)==now[n]) for n,o in old.items() if o.type=='CAMERA' and o.get('image_id')}
 report={'revision':revision,'source':source,'stage_B':'NOT_PASSED','stage_C':'NOT_PASSED','quality':q,'construction_source_note':'Hidden live control sheets may overlap; final voxel-unioned assembly is audited instead. Original quad cages are preserved for editing, not export.','front_surface_overlap_triangle_pairs':overlap,'preserved_assembly_objects':preserved,'intentional_drive_rebuild_against_r15':intentional,'photo_cameras_unchanged':cameras,'note':'Triangle counts are topology diagnostics, not visual accuracy scores. Shared seams may yield candidate contacts; inspect affected regions.'}
 (V/f"qa/stage_bc_{revision}.json").write_text(json.dumps(report,indent=2),encoding='utf8')
 result={'quality':q,'front_overlaps':overlap,'intentional_drive_objects':len(intentional),'preserved_count':len(preserved),'preservation_failures':[n for n,p in preserved.items() if not p],'photo_camera_failures':[n for n,p in cameras.items() if not p]}
 return result
if __name__=='__main__':result=audit(bpy.context.scene)
