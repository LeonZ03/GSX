"""Evaluated cap/tank topology and interference diagnostic."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from audit_stage_bc import cap_wall_vertex_contact

def one_sided_boundary_contact(i,j,vs,fs,tol=1e-7):
    # Noncoplanar faces whose vertices remain on one side of each other's
    # planes meet only at their boundaries. 0.1 um covers float tessellation
    # roundoff; coplanar faces are deliberately not exempted here.
    A=[vs[k] for k in fs[i]];B=[vs[k] for k in fs[j]]
    na=(A[1]-A[0]).cross(A[2]-A[0]).normalized();nb=(B[1]-B[0]).cross(B[2]-B[0]).normalized()
    if abs(na.dot(nb))>.9999:return False
    aa=[(p-B[0]).dot(nb) for p in A];bb=[(p-A[0]).dot(na) for p in B]
    def boundary(ds):return min(abs(x) for x in ds)<=tol and (min(ds)>=-tol or max(ds)<=tol)
    return boundary(aa) and boundary(bb)

def run(scene,tag):
    dg=bpy.context.evaluated_depsgraph_get();trees={};q={}
    for o in scene.objects:
        if not ((o.get('stage_c_owner')=='fuel_cap_r38' and not o.hide_render) or o.name=='Body_Tank'):continue
        ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles]
        tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);trees[o.name]=tree;bm=bmesh.new();bm.from_mesh(me)
        pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(fs[i]).intersection(fs[j])]
        verified=sum((cap_wall_vertex_contact(i,j,vs,fs) or one_sided_boundary_contact(i,j,vs,fs)) for i,j in pairs)
        q[o.name]={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate':sum(p.area<1e-13 for p in me.polygons),'raw_self_candidates':len(pairs),'verified_boundary_contacts':verified,'self_candidates':len(pairs)-verified}
        if pairs:q[o.name]['contact_bounds_mm']=[[min(vs[k][axis] for i,j in pairs for f in [fs[i],fs[j]] for k in f)*1000,max(vs[k][axis] for i,j in pairs for f in [fs[i],fs[j]] for k in f)*1000] for axis in range(3)]
        bm.free();ev.to_mesh_clear()
    overlaps={n+'/Body_Tank':len(t.overlap(trees['Body_Tank'])) for n,t in trees.items() if n!='Body_Tank'}
    report={'quality':q,'overlaps':overlaps,'acceptance':'B/C NOT_PASSED; local construction checks only'}
    (V/'qa'/f'fuel_cap_geometry_{tag}.json').write_text(json.dumps(report,indent=2));return report
