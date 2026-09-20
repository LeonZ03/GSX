"""Save the reviewed r49 shell migration only after scoped acceptance checks.
Source is the unique checkpointed r48 blend. Never run after preview caching.
"""
import bpy,json,sys
from pathlib import Path
from integrate_r47 import signature
V=Path(__file__).resolve().parents[1]

def run():
 s=bpy.context.scene
 if s.get('revision')!='r48':raise RuntimeError('Requires checkpointed r48')
 prefixes=('Wheel_','Tire_','Spoke_','BrakeDisc','Guard','Chain','Sprocket','Seat_','Body_Tank','LicensePlate','Passenger','SteeringDamper')
 before={o.name:signature(o) for o in s.objects if o.type=='CAMERA' or o.name.startswith(prefixes)}
 from rebuild_shell_r49 import apply
 layout=apply(s)
 for n,d in before.items():
  if n not in s.objects or signature(s.objects[n])!=d:raise RuntimeError('Unexpected protected change '+n)
 from audit_shell_r49 import run as audit
 r=audit('r49')
 bad={n:d for n,d in r['quality'].items() if not d['vertices'] or d['boundary'] or d['nonmanifold'] or d['zero_area']}
 if bad:raise RuntimeError('Mesh check failed '+str(bad))
 for n,count in [('Body_SeatSide',2),('Body_NoseAssembly',1),('Cockpit_InnerPanel',2),('Body_SideFairing',2)]:
  if len(r['quality'][n]['components'])!=count:raise RuntimeError('Unexpected detached pieces '+n)
 if any(d['unresolved'] for d in r['self_intersections'].values()):raise RuntimeError('Unresolved self intersection')
 if any(d['crossings'] for d in r['pairs'].values()):raise RuntimeError('Adjacent shells intersect')
 for o in s.objects:
  if o.get('export_exclude') and o.name.startswith('Tool_'):o.hide_render=True;o.hide_set(True)
 s['revision']='r49';s['acceptance']='B_C_NOT_PASSED';s['stage_B']=s['stage_C']='NOT_PASSED'
 report={'revision':'r49','protected_source_signatures':before,'checked_objects':len(r['quality']),'checked_surface_pairs':len(r['pairs']),'source':'single local working blend','acceptance':'NOT_PASSED: scoped geometry checked, photo accuracy and hidden dimensions unverified'}
 (V/'qa/r49_integration.json').write_text(json.dumps(report,indent=2))
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'saved':str(V/'model_history/GSX250R.blend'),'revision':'r49','protected_unchanged':len(before),'checked_objects':len(r['quality']),'checked_surface_pairs':len(r['pairs']),'acceptance':'NOT_PASSED'}
