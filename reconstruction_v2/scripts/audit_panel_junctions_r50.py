"""Check only the additional body junctions changed after the r50 front pass."""
import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from audit_fuel_cap_r38 import one_sided_boundary_contact
V=Path(__file__).resolve().parents[1]

def run(tag='r50'):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};quality={}
 def ev(n):
  if n in cache:return cache[n]
  o=s.objects[n].evaluated_get(dg);me=o.to_mesh();me.calc_loop_triangles();vs=[o.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
  bm=bmesh.new();bm.from_mesh(me);p=list(range(len(vs)))
  def root(i):
   while p[i]!=i:p[i]=p[p[i]];i=p[i]
   return i
  for e in me.edges:a,b=map(root,e.vertices);p[a]=b
  groups={}
  for i in range(len(p)):a=root(i);groups[a]=groups.get(a,0)+1
  quality[n]={'vertices':len(vs),'faces':len(me.polygons),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_area':sum(f.calc_area()<1e-13 for f in bm.faces),'components':sorted(groups.values(),reverse=True)}
  bm.free();o.to_mesh_clear();cache[n]=(vs,fs,BVHTree.FromPolygons(vs,fs,all_triangles=True));return cache[n]
 selfq={}
 for n in ['Body_SideFairing','Body_BellyPan','Body_PillionSidePanel','Body_PillionBase']:
  vs,fs,t=ev(n);raw=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])];c=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw);selfq[n]={'raw':len(raw),'boundary_contact':c,'unresolved':len(raw)-c}
 pairs={}
 for a,b in [('Body_SideFairing','Body_BellyPan'),('Body_SideFairing','Body_TankSideTrim'),('Body_SideFairing','Body_SeatSide'),('Body_Tail','Body_PillionSidePanel'),('Body_Tail','Body_PillionBase'),('Body_MidSideCover','Body_BellyPan'),('Body_NoseAssembly','Body_SideFairing')]:pairs[a+'/'+b]={'crossings':len(ev(a)[2].overlap(ev(b)[2]))}
 result={'revision':'r50','scope':'additional panel finish; unchanged front checks remain in front_junction_r50.json','quality':quality,'self_intersections':selfq,'pairs':pairs,'acceptance':'NOT_PASSED: local assembly diagnostics only'}
 (V/'qa'/('panel_junctions_'+tag+'.json')).write_text(json.dumps(result,indent=2));return result
