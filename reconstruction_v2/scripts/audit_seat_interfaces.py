"""Evaluated local seat interface diagnostics, not complete assembly approval."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();trees={};manifold={}
for o in s.objects:
 name=Path(o.get('control_cage_source','')).stem
 if name not in ['Seat_Rider','Body_SeatSide','Body_Tail','Body_PillionBase','Body_Tank']:continue
 e=o.evaluated_get(dg);m=e.to_mesh();trees[name]=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(f.vertices) for f in m.polygons]);bm=bmesh.new();bm.from_mesh(m);manifold[name]=sum(not e.is_manifold for e in bm.edges);bm.free();e.to_mesh_clear()
report={'status':'NOT_PASSED','revision':s.get('revision'),'possible_surface_overlap_pairs':{name:len(trees['Seat_Rider'].overlap(t)) for name,t in trees.items() if name!='Seat_Rider'},'nonmanifold_evaluated_edges':manifold,'note':'Counts flag local surface intersections. Hidden mounts and full assembly still require review; 3mm clearance is modeled, not measured.'}
report['camera_signature']={str(o.get('image_id')):[*[v for row in o.matrix_world for v in row],o.data.lens,o.data.shift_x,o.data.shift_y,o.data.sensor_width] for o in s.objects if o.type=='CAMERA' and o.get('image_id')}
helper=next((o for o in s.objects if o.get('construction_role')=='rider_clearance_operand'),None)
seat=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'))
report['clearance_operand']={'exists':helper is not None,'shares_current_rider_mesh':helper.data==seat.data if helper else None,'render_hidden':helper.hide_render if helper else None,'export_excluded':bool(helper.get('export_exclude')) if helper else None}
(V2/f"qa/seat_interfaces_{s.get('revision')}.json").write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='camera_signature'},indent=2))