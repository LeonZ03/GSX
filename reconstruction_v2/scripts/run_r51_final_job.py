import bpy,sys,json,traceback,hashlib
from pathlib import Path
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));status=V/'qa/r51_final_job_status.json'
try:
 status.write_text(json.dumps({'state':'integrating'}))
 from integrate_r51 import run
 r=run();status.write_text(json.dumps({'state':'saved_rendering','result':r}))
 from render_front_junction_r50 import run as render
 images=render('r51',['Nose','FrontSymmetry','NoseSide','RightSide','Rear','CockpitTop'])
 assert hashlib.sha256((V/'model_history/GSX250R.blend').read_bytes()).hexdigest()==r['source_sha256']
 status.write_text(json.dumps({'state':'complete','result':r,'renders':images,'render_did_not_change_saved_source':True},indent=2))
except Exception:
 status.write_text(json.dumps({'state':'failed','error':traceback.format_exc()}));traceback.print_exc()
