"""Scoped evaluated geometry audit; never a claim of photo or full-bike acceptance."""
import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from audit_fuel_cap_r38 import one_sided_boundary_contact
V=Path(__file__).resolve().parents[1]
def run(s):
 dg=bpy.context.evaluated_depsgraph_get();data={};q={}
 names=['Body_NoseAssembly','Headlight_Lens','Headlight_InnerMask','Headlight_Reflector','Headlight_Housing','Headlight_PositionLens_L','Headlight_PositionLens_R','Mirror_L','Mirror_R','Mirror_Glass_L','Mirror_Glass_R','Indicator_Rear_Housing_L','Indicator_Rear_Housing_R','Indicator_Rear_Lens_L','Indicator_Rear_Lens_R','Body_SideFairing','Cockpit_InnerPanel','Fender_Front']
 for n in names:
  ev=s.objects[n].evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
  tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);bm=bmesh.new();bm.from_mesh(me)
  parent=list(range(len(vs)))
  def root(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  for e in me.edges:a,c=map(root,e.vertices);parent[a]=c
  counts={}
  for i in range(len(vs)):r=root(i);counts[r]=counts.get(r,0)+1
  raw=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(fs[i]).intersection(fs[j])]
  contact=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw)
  q[n]={'vertices':len(vs),'faces':len(me.polygons),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_area':sum(f.calc_area()<1e-13 for f in bm.faces),'components':sorted(counts.values(),reverse=True),'self_raw':len(raw),'boundary_contacts':contact,'self_unresolved':len(raw)-contact}
  bm.free();ev.to_mesh_clear();data[n]=(vs,fs,tree)
  print('AUDIT',n,q[n],flush=True)
 pairs={}
 for a,b in [('Body_NoseAssembly','Headlight_Lens'),('Body_NoseAssembly','Headlight_InnerMask'),('Body_NoseAssembly','Headlight_PositionLens_L'),('Body_NoseAssembly','Headlight_PositionLens_R'),('Body_NoseAssembly','Body_SideFairing'),('Body_NoseAssembly','Cockpit_InnerPanel'),('Headlight_Lens','Headlight_Reflector'),('Headlight_Lens','Headlight_Housing')]:
  pairs[a+'/'+b]=len(data[a][2].overlap(data[b][2]))
 report={'revision':'r51','quality':q,'surface_crossing_candidates':pairs,'acceptance':'NOT_PASSED; no photo IoU/keypoint certification; mounting and other pairs outside scope'}
 (V/'qa/r51_geometry.json').write_text(json.dumps(report,indent=2));return report
