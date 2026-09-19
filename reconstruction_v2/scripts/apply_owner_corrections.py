"""Apply explicit owner corrections to the single local working source."""
from pathlib import Path
import bpy,json
V=Path(__file__).resolve().parents[1]
def apply():
 s=bpy.context.scene
 if s.get('revision')!='r38':raise ValueError('Expected accepted r38 parent')
 case=s.objects['ChainGuard']
 for m in list(case.modifiers):
  if m.type=='BOOLEAN' and m.object and m.object.name=='Tool_ChainGuardHugger':case.modifiers.remove(m)
 tool=s.objects.get('Tool_ChainGuardHugger')
 if tool:bpy.data.objects.remove(tool,do_unlink=True)
 case['evidence']='Owner correction: no rear wheel hugger; chain guard retained'
 for o in s.objects:
  if o.name.startswith(('GuardBar','GuardMount')):o.hide_render=False;o.hide_set(False)
 # Verify centreline mirror symmetry from actual world coordinates.
 curves=[]
 for name in ['GuardBar_L','GuardBar_R']:
  o=s.objects[name];pts=[]
  for sp in o.data.splines:
   for p in (sp.bezier_points if sp.type=='BEZIER' else sp.points):pts.append(o.matrix_world@p.co.to_3d())
  curves.append(pts)
 if len(curves[0])!=len(curves[1]):raise ValueError('Guard topology mismatch')
 error=max(((a.x+b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2)**.5 for a,b in zip(*curves))*1000
 if error>.001:raise ValueError('Guard asymmetry '+str(error))
 s['revision']='r39';s['visual_acceptance']='NOT_PASSED'
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 report={'revision':'r39','guard_centerline_mirror_max_mm':error,'guard_shapes_accepted':False,'wheel_hugger_removed':True,'remaining_owner_items':['guard_shape','side_stand','front_fender','front_face','both_seats','handlebars_from_photo65','tank_shape'],'BC':'NOT_PASSED'}
 (V/'qa/owner_corrections_r39.json').write_text(json.dumps(report,indent=2))
 return report
