"""Limited evaluated geometry and interface report. Not photographic acceptance."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]
def run(tag='r47'):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};quality={}
 names=['Body_Tank','Body_Tail','Body_SeatSide','Body_NoseAssembly','Windscreen','Headlight_Lens','Headlight_PositionLens','Headlight_PositionSurround_L','Headlight_PositionSurround_R','Headlight_Surround','Headlight_Housing','Headlight_Reflector','LicensePlate','LicensePlate_Carrier']
 names += [o.name for o in s.objects if o.name.startswith(('LicensePlate_EdgeFlange','Frame_Main_','Frame_Subframe_','Frame_Cradle_'))]
 def mesh(n):
  if n in cache:return cache[n]
  o=s.objects[n];e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();vs=[e.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
  bm=bmesh.new();bm.from_mesh(me);todo=set(bm.verts);sizes=[]
  while todo:
   stack=[todo.pop()];size=0
   while stack:
    v=stack.pop();size+=1
    for ed in v.link_edges:
     w=ed.other_vert(v)
     if w in todo:todo.remove(w);stack.append(w)
   sizes.append(size)
  quality[n]={'vertices':len(vs),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_area':sum(f.area<1e-13 for f in me.polygons),'component_sizes':sorted(sizes,reverse=True)}
  bm.free();e.to_mesh_clear();tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);cache[n]=(vs,fs,tree);return cache[n]
 for n in names:mesh(n)
 pairs={}
 for a,c in [('Body_Tank','Seat_Rider'),('Body_Tank','Body_TankSideTrim'),('Body_Tail','Body_SeatSide'),('Body_SeatSide','Seat_Rider'),('Headlight_Lens','Body_NoseAssembly'),('Headlight_PositionLens','Body_NoseAssembly'),('Headlight_Lens','Headlight_Reflector'),('Windscreen','Body_NoseAssembly'),('LicensePlate_Carrier','Body_Tail'),('LicensePlate_Carrier','LicensePlate_Crossmember')]:
  vs,fs,t=mesh(a);ws,gs,u=mesh(c);pairs[a+'/'+c]={'raw_surface_intersections':len(t.overlap(u)),'sampled_min_distance_mm':min(min(u.find_nearest(v)[3] for v in vs),min(t.find_nearest(w)[3] for w in ws))*1000}
 selfs={}
 from audit_fuel_cap_r38 import one_sided_boundary_contact
 for n in ['Body_SeatSide','Body_NoseAssembly','Windscreen','Headlight_Lens','Headlight_PositionLens','LicensePlate_Carrier']:
  vs,fs,t=mesh(n);raw=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])];contacts=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw)
  selfs[n]={'raw':len(raw),'boundary_contacts':contacts,'unresolved':len(raw)-contacts}
 plate=s.objects['LicensePlate'];normal=plate.matrix_world.to_3x3()@Vector((0,-1,0));up=plate.matrix_world.to_3x3()@Vector((0,0,1))
 o=s.objects['Windscreen'];e=o.evaluated_get(dg);me=e.to_mesh();coords=[v.co for v in me.vertices];center=max((v.z for v in coords if abs(v.x)<.004));edges=max(v.z for v in coords if abs(v.x)>.145);e.to_mesh_clear()
 report={'revision':s.get('revision'),'quality':quality,'interfaces':pairs,'self_intersections':selfs,'plate_normal':list(normal),'plate_up':list(up),'windscreen_center_to_side_upper_height_mm':(center-edges)*1000,'acceptance':'NOT_PASSED: scoped mesh checks only, no complete calibrated photo comparison'}
 (V/'qa'/('shell_front_'+tag+'.json')).write_text(json.dumps(report,indent=2));return report
