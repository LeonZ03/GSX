"""Scoped front recess, shell junction and thickness checks. Never 1:1 certification."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from audit_fuel_cap_r38 import one_sided_boundary_contact
V=Path(__file__).resolve().parents[1]

def run(tag='r50',front_only=False):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};quality={}
 targets=['Body_NoseAssembly','Cockpit_InnerPanel','Body_SideFairing','Headlight_InnerMask','Headlight_PositionLens','Headlight_PositionSeat_L','Headlight_PositionSeat_R','Body_BellyPan','Body_PillionSidePanel','Body_PillionBase']
 if front_only:targets=targets[:7]
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
  vs,fs,t=ev(a);ws,gs,u=ev(b);return {'crossings':len(t.overlap(u))}
 selfq={}
 for n in targets:
  vs,fs,t=ev(n);raw=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])];contact=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw)
  selfq[n]={'raw':len(raw),'boundary_contact':contact,'unresolved':len(raw)-contact}
 pairs={}
 for a,b in [('Body_SeatSide','Seat_Rider'),('Body_SeatSide','Body_Tank'),('Body_SeatSide','Body_TankSideTrim'),('Body_SeatSide','Body_Tail'),('Body_SeatSide','Body_MidSideCover'),('Body_NoseAssembly','Headlight_Lens'),('Body_NoseAssembly','Headlight_PositionLens'),('Body_NoseAssembly','Windscreen'),('Body_NoseAssembly','Cockpit_InnerPanel'),('Body_NoseAssembly','Body_SideFairing')]:pairs[a+'/'+b]=pair(a,b)
 # Additional recess / lens surfaces; intentional bezel seating overlap is
 # reported separately and is never presented as a zero-intersection pair.
 for a,b in [('Body_NoseAssembly','Headlight_InnerMask'),('Headlight_InnerMask','Headlight_Lens'),('Headlight_InnerMask','Headlight_PositionLens')]:pairs[a+'/'+b]=pair(a,b)
 if not front_only:
  for a,b in [('Body_SideFairing','Body_BellyPan'),('Body_SideFairing','Body_TankSideTrim'),('Body_SideFairing','Body_SeatSide'),('Body_Tail','Body_PillionSidePanel'),('Body_Tail','Body_PillionBase'),('Body_MidSideCover','Body_BellyPan')]:pairs[a+'/'+b]=pair(a,b)
 contacts={a+'/'+b:pair(a,b) for a,b in [('Headlight_InnerMask','Headlight_Housing'),('Headlight_InnerMask','Headlight_PositionSeat_L'),('Headlight_InnerMask','Headlight_PositionSeat_R')]}
 rays=[]
 for x,z in [(130,820),(133,800),(122,785),(105,760),(82,745),(145,845)]:
  for side in [-1,1]:
   p=Vector((x*side*.001,2,z*.001));direction=Vector((0,-1,0));hits=[]
   for name in ['Body_NoseAssembly','Headlight_InnerMask','Headlight_PositionLens','Headlight_Lens','Headlight_Housing']:
    loc,normal,index,distance=ev(name)[2].ray_cast(p,direction)
    if loc is not None:hits.append((distance,name,loc.y*1000))
   rays.append({'xz_mm':[x*side,z],'first_hit':min(hits)[1:] if hits else None})
 result={'revision':s.get('revision'),'quality':quality,'self_intersections':selfq,'pairs':pairs,'mount_contacts':contacts,'local_open_slot_rays':rays,'acceptance':'NOT_PASSED: scoped geometry and coverage, not photo similarity certification'}
 (V/'qa'/('front_junction_'+tag+'.json')).write_text(json.dumps(result,indent=2));return result
