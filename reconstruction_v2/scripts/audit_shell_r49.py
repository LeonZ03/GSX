"""Scoped r49 evaluated geometry and visible seam diagnostics, never 1:1 certification."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from audit_fuel_cap_r38 import one_sided_boundary_contact
V=Path(__file__).resolve().parents[1]

def run(tag='r49'):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};quality={}
 targets=['Body_SeatSide','Body_NoseAssembly','Cockpit_InnerPanel','Body_SideFairing']
 def ev(n):
  if n in cache:return cache[n]
  o=s.objects[n].evaluated_get(dg);m=o.to_mesh();m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];fs=[tuple(t.vertices) for t in m.loop_triangles]
  bm=bmesh.new();bm.from_mesh(m);parent=list(range(len(m.vertices)))
  def root(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for e in m.edges:a,b=map(root,e.vertices);parent[a]=b
  counts={}
  for i in range(len(parent)):r=root(i);counts[r]=counts.get(r,0)+1
  quality[n]={'vertices':len(vs),'faces':len(m.polygons),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_area':sum(f.calc_area()<1e-13 for f in bm.faces),'components':sorted(counts.values(),reverse=True)}
  bm.free();o.to_mesh_clear();cache[n]=(vs,fs,BVHTree.FromPolygons(vs,fs,all_triangles=True));return cache[n]
 def pair(a,b):
  vs,fs,t=ev(a);ws,gs,u=ev(b);return {'crossings':len(t.overlap(u)),'min_vertex_surface_mm':round(min(min(u.find_nearest(p)[3] for p in vs),min(t.find_nearest(p)[3] for p in ws))*1000,4)}
 selfq={}
 for n in targets:
  vs,fs,t=ev(n);raw=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])];contact=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw)
  selfq[n]={'raw':len(raw),'boundary_contact':contact,'unresolved':len(raw)-contact}
 pairs={}
 for a,b in [('Body_SeatSide','Seat_Rider'),('Body_SeatSide','Body_Tank'),('Body_SeatSide','Body_TankSideTrim'),('Body_SeatSide','Body_Tail'),('Body_SeatSide','Body_MidSideCover'),('Body_NoseAssembly','Headlight_Lens'),('Body_NoseAssembly','Headlight_PositionLens'),('Body_NoseAssembly','Windscreen'),('Body_NoseAssembly','Cockpit_InnerPanel'),('Body_NoseAssembly','Body_SideFairing')]:pairs[a+'/'+b]=pair(a,b)
 pts=json.loads((V/'data/current_controls/shell_r49_layout.json').read_text())['side_shell']['upper_lip_targets_mm'];tree=ev('Body_SeatSide')[2]
 seam=[round(tree.find_nearest(Vector(p)*.001)[3]*1000,3) for p in pts]
 result={'revision':s.get('revision'),'quality':quality,'self_intersections':selfq,'pairs':pairs,'upper_lip_target_to_actual_shell_mm':seam,'acceptance':'NOT_PASSED: local geometry diagnostics and construction seam estimates only'}
 (V/'qa'/('shell_'+tag+'.json')).write_text(json.dumps(result,indent=2));return result
