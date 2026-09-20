"""Apply reviewed front junction migration to the single local working blend."""
import bpy,json,sys
from pathlib import Path
from integrate_r47 import signature
V=Path(__file__).resolve().parents[1]

def run(additional_only=False):
 print('R50 integration started',additional_only,flush=True)
 s=bpy.context.scene
 if s.get('revision')!=('r50' if additional_only else 'r49'):raise RuntimeError('Incorrect parent revision')
 prefixes=('Wheel_','Tire_','Spoke_','BrakeDisc','Guard','Chain','Sprocket','Seat_','Body_Tank','Body_Tail','LicensePlate','Passenger','SteeringDamper')
 before={o.name:signature(o) for o in s.objects if o.type=='CAMERA' or o.name.startswith(prefixes)}
 if not additional_only:
  from rebuild_front_junction_r50 import apply
  apply(s)
 if additional_only:
  from finish_panel_junctions_r50 import apply as finish_panels
  finish_panels(s)
  print('R50 panel construction finished',flush=True)
 for n,d in before.items():
  if n not in s.objects or signature(s.objects[n])!=d:raise RuntimeError('Unexpected protected change '+n)
 if additional_only:
  from audit_panel_junctions_r50 import run as audit
  print('R50 panel audit started',flush=True)
  r=audit('r50')
  print('R50 panel audit finished',flush=True)
 else:
  from audit_front_junction_r50 import run as audit
  r=audit('r50',front_only=True)
 bad={n:d for n,d in r['quality'].items() if not d['vertices'] or d['boundary'] or d['nonmanifold'] or d['zero_area']}
 if bad:raise RuntimeError('Mesh check failed '+str(bad))
 for n,count in [('Body_SeatSide',2),('Body_NoseAssembly',1),('Cockpit_InnerPanel',2),('Body_SideFairing',2),('Headlight_InnerMask',1),('Headlight_PositionLens',2),('Body_BellyPan',2),('Body_PillionSidePanel',2),('Body_PillionBase',1)]:
  if n in r['quality'] and len(r['quality'][n]['components'])!=count:raise RuntimeError('Detached pieces '+n)
 if any(d['unresolved'] for d in r['self_intersections'].values()):raise RuntimeError('Unresolved self intersection')
 if any(d['crossings'] for d in r['pairs'].values()):raise RuntimeError('Adjacent shells intersect')
 if any(not d['first_hit'] or d['first_hit'][0]!='Headlight_InnerMask' for d in r.get('local_open_slot_rays',[])):raise RuntimeError('Open local lamp recess')
 for o in s.objects:
  if o.get('export_exclude') and o.name.startswith('Tool_'):o.hide_render=True;o.hide_set(True)
 s['revision']='r50';s['acceptance']='B_C_NOT_PASSED';s['stage_B']=s['stage_C']='NOT_PASSED'
 report={'revision':'r50','protected_source_signatures':before,'checked_objects':len(r['quality']),'checked_surface_pairs':len(r['pairs']),'acceptance':'NOT_PASSED: scoped geometry checked; photos and hidden dimensions unverified','mount_overlap':'Mask contacts with rear housing and wing seats intentionally retained; not full fit certification'}
 (V/'qa'/('r50_panel_integration.json' if additional_only else 'r50_integration.json')).write_text(json.dumps(report,indent=2))
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'saved':str(V/'model_history/GSX250R.blend'),'revision':'r50','protected_unchanged':len(before),'checked_objects':len(r['quality']),'checked_pairs':len(r['pairs']),'acceptance':'NOT_PASSED'}
