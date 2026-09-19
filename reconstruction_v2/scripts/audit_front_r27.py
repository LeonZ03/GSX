"""Targeted r26/r27 geometry diagnostics; private numerical output only."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from audit_stage_bc import signature
NAMES=['Body_SideFairing','Body_UpperCowling','Body_CowlingSide','Cockpit_InnerPanel']

def sample(scene):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();quality={};trees={}
    for n in NAMES+['Body_NoseSideReturn','Body_NoseAssembly','Radiator']:
        o=scene.objects[n];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
        bm=bmesh.new();bm.from_mesh(me)
        quality[n]={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.area<1e-13 for f in me.polygons),'evaluated_vertices':len(me.vertices),'construction_only':bool(o.get('construction_control_only'))}
        if n!='Body_NoseAssembly':quality[n]['nonadjacent_bvh_candidates']=sum(i<j and not set(fs[i]).intersection(fs[j]) for i,j in tree.overlap(tree))
        bm.free();ev.to_mesh_clear();trees[n]=tree
    pairs={a+' / '+b:len(trees[a].overlap(trees[b])) for a,b in [('Body_SideFairing','Radiator'),('Body_SideFairing','Body_CowlingSide'),('Body_UpperCowling','Body_CowlingSide'),('Body_NoseAssembly','Body_UpperCowling')]}
    o=scene.objects['Body_SideFairing'];a=o.data.attributes.new('QA_ColumnParameter','FLOAT','POINT')
    for i,q in enumerate(a.data):q.value=float(i%7)
    flags={m:m.show_viewport for m in o.modifiers if m.type=='SOLIDIFY'}
    for m in flags:m.show_viewport=False
    bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();attr=me.attributes.get('QA_ColumnParameter');edge=[]
    if attr:
        edge=[list(ev.matrix_world@v.co) for v,q in zip(me.vertices,attr.data) if abs(q.value)<1e-5 and v.co.x>0]
    ev.to_mesh_clear();o.data.attributes.remove(a)
    for m,f in flags.items():m.show_viewport=f
    return {'quality':quality,'overlap_candidates':pairs,'evaluated_upper_rail_m':edge,'signatures':{o.name:signature(o) for o in scene.objects}}

def run(candidate):
    current=sample(bpy.context.scene)
    bpy.ops.wm.open_mainfile(filepath=str(V/'blends/26_gray_review.blend'));base=sample(bpy.context.scene)
    changes=[n for n,h in current['signatures'].items() if base['signatures'].get(n)!=h]
    report={'candidate':str(candidate),'baseline':'26_gray_review.blend','changed_geometry_or_transforms':changes,'expected_changes':NAMES,'unexpected_changes':[n for n in changes if n not in NAMES], 'removed_objects':sorted(set(base['signatures'])-set(current['signatures'])),'baseline_diagnostics':base,'candidate_diagnostics':current,'stage_B':'NOT_PASSED','stage_C':'NOT_PASSED','note':'BVH overlaps are candidate triangle contacts, not clearance or visual acceptance. Hidden construction sheets may overlap intentionally in the union host.'}
    out=V/'qa/front_r27/geometry.json';out.write_text(json.dumps(report,indent=2))
    return {'unexpected':report['unexpected_changes'],'removed':report['removed_objects'],'quality':current['quality'],'overlaps_before':base['overlap_candidates'],'overlaps_after':current['overlap_candidates'],'upper_rail_samples':len(current['evaluated_upper_rail_m'])}
