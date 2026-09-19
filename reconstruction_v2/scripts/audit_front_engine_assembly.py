"""Evaluated assembly diagnostics; contacts are not visual acceptance scores."""
from pathlib import Path
import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]
NAMES=['Body_NoseAssembly','Body_SideFairing','Radiator','Cockpit_InnerPanel','Headlight_Lens','Headlight_Surround','Headlight_PositionLens','Headlight_PositionSurround','Exhaust_Muffler','Exhaust_HeatShield','Exhaust_EndCap','Exhaust_Outlet','Exhaust_Outlet_Lip','Engine_ClutchCover','Engine_Crankcase','Engine_CoverInset_R','Engine_AlternatorCover','Engine_CoverInset_L','Engine_SprocketCover']
PAIRS=[('Body_SideFairing','Radiator'),('Body_NoseAssembly','Body_SideFairing'),('Body_NoseAssembly','Cockpit_InnerPanel'),('Headlight_Lens','Headlight_Surround'),('Headlight_Lens','Body_NoseAssembly'),('Headlight_PositionLens','Headlight_PositionSurround'),('Exhaust_Muffler','Exhaust_HeatShield'),('Engine_ClutchCover','Engine_Crankcase'),('Engine_AlternatorCover','Engine_SprocketCover')]
def run(scene,tag):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();trees={};quality={}
 for n in NAMES:
  o=scene.objects[n];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);bm=bmesh.new();bm.from_mesh(me)
  quality[n]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(f.area<1e-13 for f in me.polygons),'self_candidates':sum(i<j and not set(fs[i]).intersection(fs[j]) for i,j in tree.overlap(tree)),'vertices':len(me.vertices)}
  bm.free();ev.to_mesh_clear();trees[n]=tree
 report={'revision':scene.get('revision'),'quality':quality,'overlap_candidates':{a+'/'+b:len(trees[a].overlap(trees[b])) for a,b in PAIRS},'stage_B':'NOT_PASSED','stage_C':'NOT_PASSED','note':'Assembly diagnostics only; intentional mounting contacts require individual inspection.'}
 (V/'qa'/f'assembly_{tag}.json').write_text(json.dumps(report,indent=2));return report
