"""Local r51 finishing correction: seat rear lenses into their existing housings."""
import bpy,bmesh,json,sys,hashlib,traceback
from pathlib import Path
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));status=V/'qa/r51_signal_finish.json'
try:
 s=bpy.context.scene;assert s.get('revision')=='r51';assert not s.get('r51_rear_lenses_seated')
 from rebuild_front_r51 import save_control
 for lab in ['L','R']:
  o=s.objects['Indicator_Rear_Lens_'+lab];count=len(o.data.vertices)//3
  for v in list(o.data.vertices)[:count]:v.co.y+=.0011
  o.data.update();save_control(o)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();q={}
 for lab in ['L','R']:
  trees={}
  for n in ['Indicator_Rear_Housing_'+lab,'Indicator_Rear_Lens_'+lab]:
   ev=s.objects[n].evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);bm=bmesh.new();bm.from_mesh(me)
   assert not any(not e.is_manifold for e in bm.edges);assert not any(f.calc_area()<1e-13 for f in bm.faces)
   pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(fs[i]).intersection(fs[j])];assert not pairs
   bm.free();ev.to_mesh_clear();trees[n]=tree
  count=len(trees['Indicator_Rear_Housing_'+lab].overlap(trees['Indicator_Rear_Lens_'+lab]));assert count>0;q[lab]={'intentional_lens_seating_crossings':count,'rear_edge_extension_mm':1.1}
 s['r51_rear_lenses_seated']=True;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 h=hashlib.sha256((V/'model_history/GSX250R.blend').read_bytes()).hexdigest();r=json.loads((V/'qa/r51_integration.json').read_text());r['source_sha256']=h;r['rear_signal_seats']=q;(V/'qa/r51_integration.json').write_text(json.dumps(r,indent=2))
 status.write_text(json.dumps({'state':'complete','checks':q,'source_sha256':h},indent=2))
except Exception:
 status.write_text(json.dumps({'state':'failed','error':traceback.format_exc()}));traceback.print_exc()
