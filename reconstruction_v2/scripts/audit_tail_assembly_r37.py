"""Evaluated candidate diagnostics, not a certificate of photo fidelity."""
from pathlib import Path
import bpy,bmesh,json
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]

def run(scene,tag):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    names=[o.name for o in scene.objects if o.get('stage_c_owner')=='tail_assembly_r37' and not o.hide_render]
    extra=['Tire_Rear','Body_Tail','Seat_Pillion','Body_PillionBase','LicensePlate','Frame_SeatRail_L','Frame_SeatRail_R','Frame_Subframe_L','Frame_Subframe_R']
    quality={};trees={}
    for n in names+extra:
        o=scene.objects[n];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        vs=[ev.matrix_world@p.co for p in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
        tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);trees[n]=tree
        if n in names or n in ['Body_Tail','Frame_SeatRail_L','Frame_SeatRail_R','Frame_Subframe_L','Frame_Subframe_R']:
            bm=bmesh.new();bm.from_mesh(me)
            quality[n]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(p.area<1e-13 for p in me.polygons),'self_candidates':sum(i<j and not set(fs[i]).intersection(fs[j]) for i,j in tree.overlap(tree))};bm.free()
        ev.to_mesh_clear()
    overlaps={n+'/Tire_Rear':len(trees[n].overlap(trees['Tire_Rear'])) for n in names+['LicensePlate']}
    for n in [x for x in ['Taillight_Lens','Taillight_Housing'] if x in trees]:
        for b in ['Body_Tail','Seat_Pillion','Body_PillionBase']:overlaps[n+'/'+b]=len(trees[n].overlap(trees[b]))
    for n in ['Frame_SeatRail_L','Frame_SeatRail_R','Frame_Subframe_L','Frame_Subframe_R']:
        overlaps[n+'/Body_Tail']=len(trees[n].overlap(trees['Body_Tail']))
    r={'revision':scene.get('revision'),'quality':quality,'overlaps':overlaps,'note':'Raw BVH surface intersections are diagnostics; intended contact and hidden fit need separate review. B/C not passed.'}
    (V/'qa'/f'tail_assembly_{tag}.json').write_text(json.dumps(r,indent=2));return r
