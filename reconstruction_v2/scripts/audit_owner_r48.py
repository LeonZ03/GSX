"""r48 scoped mesh quality, clearances and supported attachment checks."""
import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]
def run(tag='r48'):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cache={};quality={}
 names=['Body_NoseAssembly','Body_MidSideCover','Body_BellyPan','Cockpit_InnerPanel','Seat_Rider','Body_Tank','Headlight_Reflector','Headlight_InnerMask','LicensePlate_Carrier','LicensePlate_LampBridge','LicensePlate_ReflectorBridge']
 names += [o.name for o in s.objects if not o.hide_render and o.name.startswith(('PassengerPegHanger','PassengerPegFrameTab','SteeringDamper_Fixed','SteeringDamper_Moving','SteeringDamper_BodyPivot','SteeringDamper_EndPivot'))]
 def ev(n):
  if n in cache:return cache[n]
  o=s.objects[n];e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();vs=[e.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
  bm=bmesh.new();bm.from_mesh(me);quality[n]={'vertices':len(vs),'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_area':sum(p.area<1e-13 for p in me.polygons)};bm.free();e.to_mesh_clear();cache[n]=(vs,fs,BVHTree.FromPolygons(vs,fs,all_triangles=True));return cache[n]
 def pair(a,b):
  vs,fs,t=ev(a);ws,gs,u=ev(b);return {'surface_crossings':len(t.overlap(u)),'min_sampled_gap_mm':round(min(min(u.find_nearest(p)[3] for p in vs),min(t.find_nearest(p)[3] for p in ws))*1000,4)}
 for n in names:ev(n)
 connections={}
 for lab in ['L','R']:
  for j in [0,1]:
   n=f'PassengerPegFrameTab_{lab}_{j}'
   for other in ['Frame_Subframe_'+lab,'PassengerPegHanger_'+lab]:connections[n+'/'+other]=pair(n,other)
  connections['PegPivot_'+lab]=pair('PassengerPegHanger_'+lab,'PassengerPegPivot_'+lab)
 for a,b in [('SteeringDamper_FixedBracket','Frame_SteeringHead'),('SteeringDamper_FixedBracket','SteeringDamper_Clamp'),('SteeringDamper_MovingBracket','TripleClamp_Upper'),('SteeringDamper_EndPivot','SteeringDamper_Eye_End'),('SteeringDamper_BodyPivot','SteeringDamper_Clamp'),('LicensePlate_Carrier','Body_Tail'),('LicensePlate_Carrier','LicensePlate_Crossmember'),('LicensePlate_LampBridge','LicensePlate_Carrier'),('LicensePlate_LampBridge','LicensePlate_LampHousing'),('LicensePlate_ReflectorBridge','LicensePlate_Carrier'),('LicensePlate_ReflectorBridge','Reflector_Rear_Housing')]:connections[a+'/'+b]=pair(a,b)
 clear={}
 for a,b in [('Body_MidSideCover','Engine_Crankcase'),('Body_MidSideCover','Engine_ClutchCover'),('Body_MidSideCover','Body_SeatSide'),('Body_BellyPan','Exhaust_Header_L'),('Body_BellyPan','Exhaust_Header_R'),('Body_BellyPan','Frame_Cradle_R'),('Seat_Rider','Body_Tank'),('Seat_Rider','Body_Tail'),('Seat_Rider','Body_SeatSide'),('Headlight_Reflector','Headlight_Lens'),('Headlight_InnerMask','Headlight_Lens'),('Headlight_InnerMask','Headlight_PositionLens')]:clear[a+'/'+b]=pair(a,b)
 selfs={}
 from audit_fuel_cap_r38 import one_sided_boundary_contact
 for n in names:
  vs,fs,t=ev(n);raw=[(i,j) for i,j in t.overlap(t) if i<j and not set(fs[i]).intersection(fs[j])];contact=sum(one_sided_boundary_contact(i,j,vs,fs) for i,j in raw);selfs[n]={'raw':len(raw),'boundary_contacts':contact,'unresolved':len(raw)-contact}
 report={'revision':s.get('revision'),'quality':quality,'connections':connections,'clearance':clear,'self_intersections':selfs,'acceptance':'NOT_PASSED: scope-only mesh diagnostics, hidden dimensions and photo accuracy unverified'}
 (V/'qa'/('owner_'+tag+'.json')).write_text(json.dumps(report,indent=2));return report
