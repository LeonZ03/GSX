"""Scoped geometric tests for the product-photo guard/tank revision."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]


def run(tag='r46'):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};quality={}
 names=[o.name for o in s.objects if o.name.startswith(('GuardBar','GuardMount')) and not o.hide_render]+['Body_Tank']
 def ev(n):
  if n in cache:return cache[n]
  o=s.objects[n];e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();vs=[e.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
  bm=bmesh.new();bm.from_mesh(me);quality[n]={'vertices':len(vs),'boundary':sum(ed.is_boundary for ed in bm.edges),'nonmanifold':sum(not ed.is_manifold for ed in bm.edges),'zero_area':sum(f.area<1e-13 for f in me.polygons)}
  # Connected components on each complete welded guard; other separate mounting
  # pieces are intentionally different objects and checked by pair diagnostics.
  if n in ('GuardBar_L','GuardBar_R','Body_Tank'):
   todo=set(bm.verts);count=0
   while todo:
    stack=[todo.pop()];count+=1
    while stack:
     v=stack.pop()
     for ed in v.link_edges:
      w=ed.other_vert(v)
      if w in todo:todo.remove(w);stack.append(w)
   quality[n]['connected_components']=count
  bm.free();e.to_mesh_clear();tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);cache[n]=(vs,fs,tree);return cache[n]
 for n in names:ev(n)
 def pair(a,b):
  vs,fs,t=ev(a);ws,gs,u=ev(b)
  return {'intersection_pairs':len(t.overlap(u)),'sampled_gap_mm':round(min(min(u.find_nearest(v)[3] for v in vs),min(t.find_nearest(v)[3] for v in ws))*1000,4)}
 clearance={}
 for a,b in [('Body_Tank','Seat_Rider'),('Body_Tank','Body_TankSideTrim')]+[(g,c) for g in ['GuardBar_L','GuardBar_R'] for c in ['Body_SideFairing','Engine_Crankcase','Engine_ClutchCover','Engine_AlternatorCover']]:
  if a in s.objects and b in s.objects:clearance[a+'/'+b]=pair(a,b)
 links={}
 for lab in ['L','R']:
  for label in ['Upper','Middle','Bottom']:
   links['GuardBar_'+lab+'/Sleeve_'+label]=pair('GuardBar_'+lab,'GuardMount_Sleeve_'+label+'_'+lab)
  for a,b in [('GuardMount_RearBolt','Rearset'),('GuardMount_RearBolt','GuardMount_Rear'),('GuardMount_Rear','GuardBar'),('GuardMount_Rear','Rearset'),('GuardMount_Upper','GuardMount_UpperFoot'),('GuardMount_UpperFoot','Frame_Cradle'),('GuardMount_Lower','GuardMount_LowerFoot')]:
   links[a+'_'+lab+'/'+b+'_'+lab]=pair(a+'_'+lab,b+'_'+lab)
 # Evaluated surfaces, not merely identical input constants.
 lv=ev('GuardBar_L')[0];rv=ev('GuardBar_R')[0];kd=KDTree(len(rv))
 for i,p in enumerate(rv):kd.insert(p,i)
 kd.balance();sym=max(kd.find(Vector((-p.x,p.y,p.z)))[2] for p in lv)*1000
 vs,fs,t=ev('Body_Tank');raw=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])]
 from audit_fuel_cap_r38 import one_sided_boundary_contact
 boundary=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw)
 report={'revision':s.get('revision'),'quality':quality,'guard_surface_mirror_max_mm':sym,'clearance':clearance,'mount_connections':links,'tank_self_intersection':{'raw':len(raw),'boundary':boundary,'unresolved':len(raw)-boundary},'acceptance':'NOT_PASSED: geometric scope only; photo likeness and hidden dimensions unverified'}
 (V/'qa'/('product_refinement_'+tag+'.json')).write_text(json.dumps(report,indent=2));return report
