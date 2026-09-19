"""Evaluated rear-hardware candidate checks; no photo accuracy certification."""
from pathlib import Path
import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]
def run(scene,tag):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();quality={};trees={}
 names=[o.name for o in scene.objects if o.name.startswith(('PassengerPeg','ChainGuard','Exhaust_HangerBolt','Exhaust_MufflerHangerTab')) and not o.hide_render]
 for n in names+['Tire_Rear','Swingarm_L','Swingarm_R','Exhaust_Muffler','Body_SeatSide','Body_MidSideCover']:
  o=scene.objects[n];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);trees[n]=tree
  if n in names:
   bm=bmesh.new();bm.from_mesh(me);comp=[];todo=set(bm.verts)
   while todo:
    stack=[todo.pop()];count=0
    while stack:
     v=stack.pop();count+=1
     for e in v.link_edges:
      w=e.other_vert(v)
      if w in todo:todo.remove(w);stack.append(w)
    comp.append(count)
   quality[n]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.area<1e-13 for f in me.polygons),'self_candidates':sum(i<j and not set(fs[i]).intersection(fs[j]) for i,j in tree.overlap(tree)),'components':len(comp),'component_vertices':sorted(comp,reverse=True)};bm.free()
  ev.to_mesh_clear()
 pairs=[('ChainGuard',n) for n in ['Tire_Rear','Swingarm_L','Swingarm_R']]+[(f'PassengerPegHanger_{lab}',n) for lab in ['L','R'] for n in ['Tire_Rear','Body_SeatSide','Body_MidSideCover','Exhaust_Muffler']]
 overlaps={a+'/'+b:len(trees[a].overlap(trees[b])) for a,b in pairs}
 vertices=[];faces=[]
 for o in scene.objects:
  if o.name.startswith(('Chain_Link_','Chain_Pin_','Chain_Roller_')):
   ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();offset=len(vertices);vertices.extend(ev.matrix_world@v.co for v in me.vertices);faces.extend(tuple(i+offset for i in t.vertices) for t in me.loop_triangles);ev.to_mesh_clear()
 chain=BVHTree.FromPolygons(vertices,faces,all_triangles=True);overlaps['ChainGuard/Chain']=len(trees['ChainGuard'].overlap(chain))
 mount_pairs=[('PassengerPegExhaustEar_R','Exhaust_MufflerHangerTab'),('Exhaust_HangerBolt','Exhaust_MufflerHangerTab'),('Exhaust_MufflerHangerTab','Exhaust_Muffler')]
 contacts={a+'/'+b:len(trees[a].overlap(trees[b])) for a,b in mount_pairs}
 report={'intended_mount_surface_contacts':contacts,'revision':scene.get('revision'),'quality':quality,'overlaps':overlaps,'stage_C':'NOT_PASSED','note':'BVH contacts are diagnostics, not volumetric or movement clearance proof.'};(V/'qa'/f'rear_hardware_{tag}.json').write_text(json.dumps(report,indent=2));return report
