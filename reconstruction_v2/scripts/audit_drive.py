"""Read-only checks of actual pin locations, gear meshes and attachment counts."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
from audit_stage_bc import cap_wall_vertex_contact

def audit(scene):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    pins=sorted((o for o in scene.objects if o.name.startswith('Chain_Pin_')),key=lambda o:o['pin_index'])
    points=[o.matrix_world.translation.copy() for o in pins]
    if not points:raise ValueError('No rebuilt chain pins in this source')
    pitches=[(points[(i+1)%len(points)]-p).length*1000 for i,p in enumerate(points)]
    q={'source':bpy.data.filepath,'revision':scene.get('revision'),'status':'CONSTRUCTION_CHECK_ONLY_NOT_REAL_BIKE_ACCEPTANCE',
       'pin_count':len(pins),'pitch_min_mm':min(pitches),'pitch_max_mm':max(pitches),
       'pitch_max_error_mm':max(abs(v-15.875) for v in pitches),'chain_plane_spread_mm':(max(p.x for p in points)-min(p.x for p in points))*1000,
       'local_geometry':{},'counts':{},'uncertainty':'Ideal taut chain. Output height/plane, owner modifications, sag, installation and tooth flank shapes not accepted.'}
    trees={}
    for name in ['Sprocket_Front','Sprocket_Rear','ABS_Ring_Front','ABS_Ring_Rear','Engine_Crankcase','Body_SideFairing']:
        o=scene.objects[name];ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(p.vertices) for p in me.loop_triangles]
        tree=BVHTree.FromPolygons(v,f,all_triangles=True);pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])]
        contacts=sum(cap_wall_vertex_contact(i,j,v,f) for i,j in pairs)
        bm=bmesh.new();bm.from_mesh(me)
        entry={'vertices':len(v),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
               'zero_area_faces':sum(p.area<1e-13 for p in me.polygons),'euler':len(me.vertices)-len(me.edges)+len(me.polygons),
               'raw_bvh_pairs':len(pairs),'verified_vertex_on_edge_contacts':contacts,'remaining_self_candidates':len(pairs)-contacts}
        if name.startswith('Sprocket_'):
            cy=(max(p.y for p in v)+min(p.y for p in v))/2;cz=(max(p.z for p in v)+min(p.z for p in v))/2
            r=[math.hypot(p.y-cy,p.z-cz) for p in v];mx=max(r)
            peak_angles={round(math.atan2(p.y-cy,p.z-cz),5) for p,rr in zip(v,r) if mx-rr<1e-6}
            entry['actual_outer_peak_count']=len(peak_angles);entry['center_yz_mm']=[cy*1000,cz*1000]
        q['local_geometry'][name]=entry;trees[name]=tree;bm.free();ev.to_mesh_clear()
    q['counts']={'rotor_bolts':{k:sum(o.name.startswith('RotorCarrier_'+k+'_Bolt_') for o in scene.objects) for k in ['Front','Rear']},
      'abs_bolts':{k:sum(o.name.startswith('ABS_Bolt_'+k+'_') for o in scene.objects) for k in ['Front','Rear']},
      'rear_sprocket_bolts':sum(o.name.startswith('Sprocket_Bolt') for o in scene.objects),
      'side_plates':sum(o.name.startswith('Chain_Link_') for o in scene.objects),'rollers':sum(o.name.startswith('Chain_Roller_') for o in scene.objects)}
    # Local chain-to-case clearance, excluding intentional shaft/gear mating.
    overlaps=[]
    for o in scene.objects:
        if not o.name.startswith(('Chain_Link_','Chain_Roller_')):continue
        ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        tree=BVHTree.FromPolygons([ev.matrix_world@p.co for p in me.vertices],[tuple(p.vertices) for p in me.loop_triangles],all_triangles=True)
        n=len(tree.overlap(trees['Engine_Crankcase']))
        if n:overlaps.append({'object':o.name,'triangle_pairs':n})
        ev.to_mesh_clear()
    q['chain_to_case_surface_intersections']=overlaps
    (V/f"qa/drive_{scene.get('revision','working')}.json").write_text(json.dumps(q,indent=2),encoding='utf8')
    return q
if __name__=='__main__':result=audit(bpy.context.scene)
