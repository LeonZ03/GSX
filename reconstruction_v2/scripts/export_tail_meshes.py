"""Export evaluated seat/tail meshes locally for fixed-camera diagnostics.
Run in isolated background Blender for each saved revision; no scene is saved.
"""
from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
s=bpy.context.scene;revision=s.get('revision')
if not revision:raise RuntimeError('Expected a revision-tagged reconstruction scene')
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();data={}
for o in s.objects:
 key=Path(o.get('control_cage_source','')).stem
 if key not in ['Seat_Pillion','Seat_Rider','Body_Tail','Body_SeatSide','Body_PillionBase']:continue
 e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles()
 data[key]={'vertices':[list(e.matrix_world@v.co) for v in m.vertices],'triangles':[list(f.vertices) for f in m.loop_triangles]}
 e.to_mesh_clear()
(V2/f'qa/tail_mesh_{revision}.json').write_text(json.dumps(data),encoding='utf8')
print('LOCAL_EVALUATED_TAIL_MESHES',revision,len(data))