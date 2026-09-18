"""Local tank interface checks on evaluated triangles; not whole-model acceptance."""
from pathlib import Path
import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();data={};trees={};quality={}
for name in ['Body_Tank','Seat_Rider']:
 o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/'+name+'.json'));e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];f=[list(p.vertices) for p in m.loop_triangles];tree=BVHTree.FromPolygons(v,f,all_triangles=True)
 pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])]
 bm=bmesh.new();bm.from_mesh(m);quality[name]={'nonmanifold_edges':sum(not ed.is_manifold for ed in bm.edges),'possible_nonadjacent_self_intersections':len(pairs)};bm.free()
 data[name]={'vertices':[list(p) for p in v],'triangles':f};trees[name]=tree;e.to_mesh_clear()
pairs=trees['Seat_Rider'].overlap(trees['Body_Tank']);pts=[data['Seat_Rider']['vertices'][v] for i,j in pairs for v in data['Seat_Rider']['triangles'][i]]
report={'status':'NOT_PASSED','revision':s.get('revision'),'source':Path(bpy.data.filepath).name,'intersection_triangle_pairs':len(pairs),'affected_rider_bbox_mm':[[min(p[k] for p in pts)*1000 for k in range(3)],[max(p[k] for p in pts)*1000 for k in range(3)]] if pts else None,'quality':quality,'note':'Triangle-pair diagnostics have a different count from quad BVH audits; do not compare unlike counts as a quality score.'}
(V2/f"qa/tank_interface_{Path(bpy.data.filepath).stem}.json").write_text(json.dumps(report,indent=2),encoding='utf8');(V2/f"qa/tank_seat_mesh_{s.get('revision')}.json").write_text(json.dumps(data),encoding='utf8');result=report;print(json.dumps(report,indent=2))