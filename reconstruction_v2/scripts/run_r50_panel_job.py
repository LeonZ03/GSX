"""Background job entry, launched by Blender MCP; status/logs remain local."""
import bpy,sys,json,traceback
from pathlib import Path
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));status=V/'qa/r50_panel_job_status.json'
try:
 status.write_text(json.dumps({'state':'running'}))
 from integrate_r50 import run
 result=run(additional_only=True)
 status.write_text(json.dumps({'state':'rendering','result':result},indent=2))
 from render_front_junction_r50 import run as render
 images=render('r50',['Nose','FrontSymmetry','NoseSide','RightSide','SeatProfile'])
 status.write_text(json.dumps({'state':'complete','result':result,'renders':images},indent=2))
 print('R50_JOB_COMPLETE',flush=True)
except Exception:
 status.write_text(json.dumps({'state':'failed','error':traceback.format_exc()},indent=2));traceback.print_exc()
