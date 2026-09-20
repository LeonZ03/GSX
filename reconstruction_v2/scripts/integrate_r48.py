"""Integrate the reviewed r48 corrections into the unique local working source.
Requires checkpointed r47. Inspection rendering must run in a separate process.
"""
import bpy,json,sys
from pathlib import Path
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from integrate_r47 import signature

def bounds(name):
 o=bpy.context.scene.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.to_mesh();v=[o.matrix_world@p.co for p in m.vertices];o.to_mesh_clear()
 return [[min(p[k] for p in v)*1000,max(p[k] for p in v)*1000] for k in range(3)]

def run():
 s=bpy.context.scene
 if s.get('revision')!='r47':raise RuntimeError('Only checkpointed r47 is accepted')
 protected={o.name:signature(o) for o in s.objects if o.type=='CAMERA' or o.name.startswith(('GuardBar','GuardMount','Wheel_','Tire_','BrakeDisc','Chain','Sprocket','Seat_Pillion')) or o.name=='Body_Tank'}
 before=bounds('LicensePlate_Carrier')
 from rebuild_owner_r48 import apply
 from rebuild_saddle_r48 import apply as saddle
 apply(s);seat=saddle(s)
 for n,d in protected.items():
  if n not in s.objects or signature(s.objects[n])!=d:raise RuntimeError('Unexpected protected change '+n)
 from audit_owner_r48 import run as audit
 r=audit('r48')
 bad={n:d for n,d in r['quality'].items() if d['boundary'] or d['nonmanifold'] or d['zero_area']}
 if bad:raise RuntimeError('Geometry failed '+str(bad))
 if any(d['unresolved'] for d in r['self_intersections'].values()):raise RuntimeError('Unresolved self contact')
 if any(d['surface_crossings'] for d in r['clearance'].values()):raise RuntimeError('Non-fitting surfaces cross')
 if any(not d['surface_crossings'] for d in r['connections'].values()):raise RuntimeError('An attachment path is disconnected')
 for o in s.objects:
  if o.get('export_exclude') and o.name.startswith('Tool_'):o.hide_render=True;o.hide_set(True)
 s['acceptance']='B_C_NOT_PASSED';s['stage_B']=s['stage_C']='NOT_PASSED'
 after=bounds('LicensePlate_Carrier')
 report={'revision':'r48','protected_source_signatures':protected,'plate_carrier_bounds_before_mm':before,'plate_carrier_bounds_after_mm':after,'seat':seat,'quality_objects':len(r['quality']),'attachment_pairs':len(r['connections']),'clearance_pairs':len(r['clearance']),'acceptance':'NOT_PASSED: scoped geometry only; photo likeness and hidden dimensions unverified'}
 (V/'qa/r48_integration.json').write_text(json.dumps(report,indent=2))
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'saved':str(V/'model_history/GSX250R.blend'),'revision':'r48','protected_unchanged':len(protected),'quality_objects':len(r['quality']),'attachment_pairs':len(r['connections']),'plate_before_mm':before,'plate_after_mm':after,'acceptance':'NOT_PASSED'}
