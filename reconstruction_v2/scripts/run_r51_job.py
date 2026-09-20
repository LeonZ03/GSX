import bpy,sys,json,traceback
from pathlib import Path
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));status=V/'qa/r51_job_status.json'
try:
 status.write_text(json.dumps({'state':'building'}))
 from rebuild_front_r51 import apply
 changed=apply(bpy.context.scene)
 from refine_assembly_r51 import apply as secondary
 changed+=secondary(bpy.context.scene)
 status.write_text(json.dumps({'state':'auditing','changed':changed}))
 from finish_front_r51 import apply as finish
 finish(bpy.context.scene)
 from audit_r51 import run as audit
 report=audit(bpy.context.scene)
 status.write_text(json.dumps({'state':'rendering_candidate','changed':changed,'quality_report':'r51_geometry.json'}))
 from render_front_junction_r50 import run
 # New explicit lamp geometry has no expensive dependency to freeze.
 run('r51_candidate',['Nose','FrontSymmetry','NoseSide','RightSide','Rear','CockpitTop'])
 status.write_text(json.dumps({'state':'candidate_complete','changed':changed}))
except Exception:
 status.write_text(json.dumps({'state':'failed','error':traceback.format_exc()}));traceback.print_exc()
