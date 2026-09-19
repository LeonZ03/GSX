"""Scope-limited checks for the user's nine reported geometry issues."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]
def run():
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();q={};trees={}
 names=['Body_PillionSidePanel','Seat_Pillion_Pan','GuardBar_L','GuardBar_R','SideStand','Seat_Rider','Seat_Pillion','Body_Tank','Fender_Front','TripleClamp_Upper','Headlight_Lens','Headlight_PositionLens','Headlight_PositionSurround','Tire_Front','Body_SeatSide','Body_PillionBase','Body_Tail']
 for name in names:
  o=s.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];bm=bmesh.new();bm.from_mesh(me)
  tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);trees[name]=tree
  selfpairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(fs[i]).intersection(fs[j])]
  sys.path.insert(0,str(V/'scripts'))
  from audit_fuel_cap_r38 import one_sided_boundary_contact
  contacts=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in selfpairs)
  q[name]={'verified_boundary_contacts':contacts,'unresolved_self_candidates':len(selfpairs)-contacts,'vertices':len(vs),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(p.area<1e-13 for p in me.polygons),'raw_nonadjacent_self_candidates':len(selfpairs)}
  bm.free();ev.to_mesh_clear()
 pairs=[('Body_PillionSidePanel','Seat_Rider'),('Body_PillionSidePanel','Seat_Pillion'),('Fender_Front','Tire_Front'),('Seat_Rider','Body_Tank'),('Seat_Rider','Body_SeatSide'),('Seat_Rider','Body_PillionBase'),('Seat_Pillion','Body_Tail'),('Seat_Pillion','Body_PillionBase')]
 overlap={a+'/'+b:len(trees[a].overlap(trees[b])) for a,b in pairs}
 def pts(n):
  o=s.objects[n];return [o.matrix_world@p.co.to_3d() for sp in o.data.splines for p in (sp.bezier_points if sp.type=='BEZIER' else sp.points)]
 a,b=pts('GuardBar_L'),pts('GuardBar_R');mirror=max((Vector((-p.x,p.y,p.z))-r).length for p,r in zip(a,b))*1000
 report={'revision':s.get('revision'),'geometry':q,'surface_intersections':overlap,'guard_mirror_max_mm':mirror,'guard_both_visible':all(not s.objects[n].hide_render for n in ['GuardBar_L','GuardBar_R']),'rear_wheel_hugger_absent':not bool(s.objects.get('Tool_ChainGuardHugger')),'notes':'Raw BVH candidates include contacts; scoped diagnostics, not whole-bike visual acceptance'}
 (V/'qa/owner_geometry_review.json').write_text(json.dumps(report,indent=2));return report
