"""Apply the reviewed r47 candidates to the checkpointed r46 working source."""
from pathlib import Path
import bpy,json,hashlib,sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
def signature(o):
 d={'matrix':[list(r) for r in o.matrix_world],'type':o.type}
 if o.type=='CAMERA':d.update(lens=o.data.lens,sensor_width=o.data.sensor_width,shift_x=o.data.shift_x,shift_y=o.data.shift_y,ortho_scale=o.data.ortho_scale)
 if o.type=='MESH':d.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(f.vertices) for f in o.data.polygons])
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def run():
 s=bpy.context.scene
 if s.get('revision')!='r46':raise RuntimeError('Only the checkpointed r46 source is accepted')
 protected={o.name:signature(o) for o in s.objects if o.type=='CAMERA' or o.name.startswith(('GuardBar','GuardMount','Wheel_','Tire_','BrakeDisc','Chain','Sprocket','Seat_Rider','Seat_Pillion'))}
 from rebuild_shell_front_r47 import apply,tank_interface
 from rebuild_tank_orientation_r47 import apply as tank
 apply(s);pose=tank(s);tank_interface(s)
 for name,digest in protected.items():
  if name not in s.objects or signature(s.objects[name])!=digest:raise RuntimeError('Unexpected protected change '+name)
 from audit_shell_front_r47 import run as audit
 report=audit('r47')
 bad={n:d for n,d in report['quality'].items() if d['boundary'] or d['nonmanifold'] or d['zero_area']}
 if bad:raise RuntimeError('Geometry failed '+str(bad))
 if any(d['unresolved'] for d in report['self_intersections'].values()):raise RuntimeError('Unresolved self-intersections')
 for names,d in report['interfaces'].items():
  if names.startswith('LicensePlate_Carrier/'):continue # intended connected mount footprints, not clearance pairs
  if d['raw_surface_intersections']:raise RuntimeError('Clearance failed '+names)
 if len(report['quality']['Body_NoseAssembly']['component_sizes'])!=1:raise RuntimeError('Front shell disconnected')
 (V/'qa/r47_integration.json').write_text(json.dumps({'revision':'r47','protected_signatures_unchanged':protected,'tank':pose,'source':'single working file','acceptance':'NOT_PASSED: photo likeness and unmeasured dimensions remain open'},indent=2))
 # Export helpers are hidden in every view; preserve construction dependencies.
 for o in s.objects:
  if o.get('export_exclude') and o.name.startswith('Tool_'):o.hide_render=True;o.hide_set(True)
 s['acceptance']='B_C_NOT_PASSED';s['revision']='r47'
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'saved':str(V/'model_history/GSX250R.blend'),'revision':'r47','checked_objects':len(report['quality']),'protected_unchanged':len(protected),'shape_acceptance':'NOT_PASSED'}
