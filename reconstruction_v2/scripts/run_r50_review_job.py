"""Read-only final review job, launched through Blender MCP."""
import bpy,sys,json,hashlib,traceback
from pathlib import Path
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));status=V/'qa/r50_review_job_status.json'
try:
 assert bpy.context.scene.get('revision')=='r50' and bpy.context.scene.get('r50_remaining_panel_joints')
 original=hashlib.sha256((V/'model_history/GSX250R.blend').read_bytes()).hexdigest()
 status.write_text(json.dumps({'state':'rendering'}))
 from render_front_junction_r50 import run
 images=run('r50',['Nose','FrontSymmetry','NoseSide','RightSide','SeatProfile'])
 assert hashlib.sha256((V/'model_history/GSX250R.blend').read_bytes()).hexdigest()==original
 status.write_text(json.dumps({'state':'complete','renders':images,'source_unchanged':True},indent=2))
 print('R50_REVIEW_COMPLETE',flush=True)
except Exception:
 status.write_text(json.dumps({'state':'failed','error':traceback.format_exc()},indent=2));traceback.print_exc()
