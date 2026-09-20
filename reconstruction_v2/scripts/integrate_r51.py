"""Integrate reviewed r51 into the one private working file; fail closed on geometry."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from integrate_r47 import signature
V=Path(__file__).resolve().parents[1]
def run():
 s=bpy.context.scene
 assert s.get('revision')=='r50'
 protected={o.name:signature(o) for o in s.objects if o.type=='CAMERA' or o.name.startswith(('Wheel_','Tire_','Spoke_','BrakeDisc','Guard','Engine_','Chain','Sprocket','Body_Tank','Seat_','Body_Tail','LicensePlate','PhoneMount','SteeringDamper'))}
 from rebuild_front_r51 import apply
 from refine_assembly_r51 import apply as secondary
 from finish_front_r51 import apply as finish
 changed=list(apply(s));changed+=secondary(s);finish(s)
 for n,d in protected.items():
  if n not in s.objects or signature(s.objects[n])!=d:raise RuntimeError('Protected source changed '+n)
 from audit_r51 import run as audit
 r=audit(s)
 bad={n:d for n,d in r['quality'].items() if d['boundary'] or d['nonmanifold'] or d['zero_area'] or d['self_unresolved'] or not d['vertices']}
 if bad:raise RuntimeError('Invalid geometry '+str(bad))
 if any(r['surface_crossing_candidates'].values()):raise RuntimeError('Unresolved neighbor crossings')
 for n,d in r['quality'].items():
  expected=2 if n in ['Body_SideFairing','Cockpit_InnerPanel'] else 1
  if len(d['components'])!=expected:raise RuntimeError('Detached component '+n)
 # Measure evaluated tyre geometry, not a constant copied from the input.
 centers={}
 dg=bpy.context.evaluated_depsgraph_get()
 for n in ['Tire_Front','Tire_Rear']:
  ev=s.objects[n].evaluated_get(dg);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices]
  centers[n]=[(min(p[k] for p in vs)+max(p[k] for p in vs))*500 for k in range(3)];ev.to_mesh_clear()
 measurement={'tyre_bbox_centers_mm':centers,'wheelbase_horizontal_mm':abs(centers['Tire_Front'][1]-centers['Tire_Rear'][1])}
 if abs(measurement['wheelbase_horizontal_mm']-1430)>1:raise RuntimeError('Wheelbase changed')
 for o in s.objects:
  if o.name.startswith('Tool_') and o.get('export_exclude'):o.hide_render=True;o.hide_set(True)
 s['r51_rear_lenses_seated']=True;s['stage_B']=s['stage_C']='NOT_PASSED';s['revision']='r51';s['acceptance']='B_C_NOT_PASSED'
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 result={'revision':'r51','changed':sorted(set(changed)),'protected_source_signatures_unchanged':len(protected),'protected_signatures':protected,'measurement':measurement,'checked_objects':len(r['quality']),'checked_neighbor_pairs':len(r['surface_crossing_candidates']),'source_sha256':hashlib.sha256((V/'model_history/GSX250R.blend').read_bytes()).hexdigest(),'acceptance':'NOT_PASSED: photo accuracy and remaining components not certified'}
 (V/'qa/r51_integration.json').write_text(json.dumps(result,indent=2));return result
