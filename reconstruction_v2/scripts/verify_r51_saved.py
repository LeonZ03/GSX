"""Read the saved source, inspect new mounts and verify it remains unchanged."""
import bpy,sys,json,hashlib,traceback
from pathlib import Path
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));status=V/'qa/r51_saved_readback.json'
try:
 s=bpy.context.scene;assert s.get('revision')=='r51';source=V/'model_history/GSX250R.blend';h=hashlib.sha256(source.read_bytes()).hexdigest();dg=bpy.context.evaluated_depsgraph_get();cache={}
 def get(n):
  if n in cache:return cache[n]
  ev=s.objects[n].evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();cache[n]=(vs,BVHTree.FromPolygons(vs,fs,all_triangles=True));return cache[n]
 contacts={}
 for lab in ['L','R']:
  pairs=[('Indicator_Rear_Bridge_'+lab,'LicensePlate_Carrier'),('Indicator_Rear_Stem_'+lab,'Indicator_Rear_Bridge_'+lab),('Indicator_Rear_Stem_'+lab,'Indicator_Rear_Housing_'+lab),('Indicator_Rear_Housing_'+lab,'Indicator_Rear_Lens_'+lab),('Mirror_InternalBallSeat_'+lab,'Mirror_'+lab),('Mirror_InternalBallSeat_'+lab,'Mirror_Stem_'+lab),('Mirror_Glass_'+lab,'Mirror_'+lab)]
  for a,b in pairs:
   vs,ta=get(a);ws,tb=get(b);crossings=len(ta.overlap(tb));near=min(tb.find_nearest(v)[3] for v in vs)*1000
   contacts[a+'/'+b]={'surface_crossings':crossings,'sample_nearest_mm':near,'explanation':'intentional assembly contacts; closest vertex sample is not exact clearance'}
 assert hashlib.sha256(source.read_bytes()).hexdigest()==h
 status.write_text(json.dumps({'state':'complete','revision':s.get('revision'),'source_sha256':h,'objects':len(s.objects),'new_mount_diagnostics':contacts,'source_unchanged':True,'acceptance':'NOT_PASSED; static assembly diagnostic, no full movement or photo precision proof'},indent=2))
except Exception:
 status.write_text(json.dumps({'state':'failed','error':traceback.format_exc()}));traceback.print_exc()
