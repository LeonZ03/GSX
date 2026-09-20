"""Whole-scene closure and explicit mounting diagnostics; not likeness acceptance."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]

def run():
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};open_mesh=[];deg=[];count=0
 def ev(n):
  if n in cache:return cache[n]
  o=s.objects[n];e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();vs=[e.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);e.to_mesh_clear();cache[n]=(vs,fs,tree);return cache[n]
 for o in s.objects:
  if o.type not in ('MESH','CURVE') or o.hide_render or o.get('export_exclude'):continue
  e=o.evaluated_get(dg);me=e.to_mesh();bm=bmesh.new();bm.from_mesh(me);bd=sum(ed.is_boundary for ed in bm.edges);bad=sum(not ed.is_manifold for ed in bm.edges);z=sum(f.area<1e-13 for f in me.polygons)
  if bd or bad:open_mesh.append({'name':o.name,'boundary':bd,'nonmanifold':bad})
  if z:deg.append({'name':o.name,'zero_area':z})
  count+=1;bm.free();e.to_mesh_clear()
 def distance(a,b):
  vs,fs,t=ev(a);ws,gs,u=ev(b);over=len(t.overlap(u))
  dist=min((u.find_nearest(v)[3] for v in vs),default=999)*1000
  dist=min(dist,min((t.find_nearest(v)[3] for v in ws),default=999)*1000)
  return {'surface_intersection_pairs':over,'sampled_surface_gap_mm':round(dist,4),'note':'intersection may be intended mounting fit; zero gap is not mechanical validation'}
 links={}
 pairs=[('PhoneMount','PhoneMount_RubberPad'),('PhoneMount_Stem','PhoneMount_BallJoint'),('PhoneMount_BallJoint','PhoneMount_Socket'),('PhoneMount_Socket','PhoneMount'),('PhoneMount_HandleClamp','PhoneMount_Stem'),('PhoneMount_HandleClamp','Handlebar_Riser_L'),('LicensePlate_Carrier','LicensePlate_Crossmember'),('LicensePlate_Crossmember','LicensePlate'),('Exhaust_Header_L','Exhaust_Collector'),('Exhaust_Header_R','Exhaust_Collector'),('Exhaust_Collector','Exhaust_LinkPipe'),('Exhaust_LinkPipe','Exhaust_Muffler')]
 for lab in ['LLower','LUpper','RLower','RUpper']:
  pairs += [('PhoneMount','PhoneMount_Arm_'+lab),('PhoneMount_Arm_'+lab,'PhoneMount_Jaw_'+lab),('PhoneMount_Jaw_'+lab,'PhoneMount_Contact_'+lab)]
 for lab in ['L','R']:
  pairs += [('GuardMount_RearBolt_'+lab,'Rearset_'+lab),('GuardMount_RearBolt_'+lab,'GuardMount_Rear_'+lab),('GuardMount_UpperFoot_'+lab,'Frame_Cradle_'+lab),('GuardMount_UpperFoot_'+lab,'GuardMount_Upper_'+lab),('GuardMount_LowerFoot_'+lab,'Engine_Crankcase'),('GuardMount_LowerFoot_'+lab,'GuardMount_Lower_'+lab),('GuardMount_Rear_'+lab,'Rearset_'+lab),('Frame_HeadGusset_'+lab,'Frame_Main_'+lab),('Frame_HeadGusset_'+lab,'Frame_SteeringHead'),('Dashboard_StayRoot_'+lab,'Frame_SteeringHead'),('Dashboard_StayRoot_'+lab,'Dashboard_Support_'+lab)]
 for a,b in pairs:
  if a in s.objects and b in s.objects:links[a+'/'+b]=distance(a,b)
 # Critical non-mating surfaces: raw counts are preserved, not promoted to a pass.
 clearance={}
 for a,b in [('Seat_Rider','Body_Tank'),('Seat_Rider','Body_SeatSide'),('Seat_Rider','Body_PillionBase'),('Exhaust_Collector','Engine_Crankcase'),('Exhaust_Header_L','Engine_Crankcase'),('Exhaust_Header_R','Engine_Crankcase'),('PhoneMount','Grip_L'),('Windscreen','Dashboard')]:
  if a in s.objects and b in s.objects:clearance[a+'/'+b]=distance(a,b)
 def cp(n):
  o=s.objects[n];return [o.matrix_world@p.co.to_3d() for sp in o.data.splines for p in (sp.bezier_points if sp.type=='BEZIER' else sp.points)]
 a,b=cp('GuardBar_L'),cp('GuardBar_R');sym=max((Vector((-p.x,p.y,p.z))-q).length for p,q in zip(a,b))*1000
 selfcheck={}
 for n in ['Windscreen','Body_Tank','Seat_Rider','SideStand','Headlight_Lens','Headlight_Housing','Headlight_Surround','Exhaust_Collector','GuardBar_L','GuardBar_R','LicensePlate_Carrier']:
  vs,fs,t=ev(n);cand=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])]
  from audit_fuel_cap_r38 import one_sided_boundary_contact
  boundary=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in cand)
  selfcheck[n]={'raw':len(cand),'boundary_contacts':boundary,'unresolved':len(cand)-boundary}
 report={'revision':s.get('revision'),'visible_mesh_objects_checked':count,'open_or_nonmanifold':open_mesh,'degenerate':deg,'connection_diagnostics':links,'clearance_diagnostics':clearance,'scoped_self_intersections':selfcheck,'guard_mirror_mm':sym,'acceptance':'NOT_PASSED; these tests do not certify all mounts or photo likeness'}
 (V/'qa/owner_fifteen_assembly.json').write_text(json.dumps(report,indent=2));return report
