"""Photo-supported guard topology, r46. All dimensions remain inferred.

The owner's three product photographs supersede the r45 open return and the
AI-generated sketch. Editable path controls feed a live welded mesh assembly.
No calibrated camera, non-guard geometry, or owner photograph is modified.
"""
from pathlib import Path
import bpy, bmesh, json, math, sys
from mathutils import Vector
V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V / 'scripts'))
from rebuild_owner_structure import init, purge
from rebuild_clutch_r30 import loft


def fillet(points, cut=18):
    points = [Vector(p) for p in points]
    out = [points[0]]
    for i, p in enumerate(points[1:-1], 1):
        d = min(cut, (points[i-1]-p).length*.3, (points[i+1]-p).length*.3)
        a = p + (points[i-1]-p).normalized()*d
        c = p + (points[i+1]-p).normalized()*d
        out.extend(a*(1-t)**2 + p*2*t*(1-t) + c*t*t for t in [k/8 for k in range(9)])
    return out + [points[-1]]


def annulus(b, name, a, c, outer, inner):
    a,c=Vector(a),Vector(c);ax=(c-a).normalized()
    u=ax.cross(Vector((0,0,1))).normalized();v=ax.cross(u);n=48
    pts=[]
    for p,r in [(a,outer),(c,outer),(a,inner),(c,inner)]:
        pts.extend(p+r*(u*math.cos(k*math.tau/n)+v*math.sin(k*math.tau/n)) for k in range(n))
    faces=[]
    for k in range(n):
        j=(k+1)%n
        faces.extend([(k,j,n+j,n+k),(2*n+k,3*n+k,3*n+j,2*n+j),
                      (k,2*n+k,2*n+j,j),(n+k,n+j,3*n+j,3*n+k)])
    o=b.mesh(name,pts,faces,'black',smo=True)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    return o


def apply(scene=None):
    s=scene or bpy.context.scene;b=init(s);b.COL=b.C['Details']
    purge(s,('GuardBar','GuardMount','Tool_Guard'))
    # These outer nodes retain the owner-photo layout. New topology comes from
    # product right/left and detached views; no product pixel is treated as mm.
    R=Vector((177,-34.68,484.86));U=Vector((282.63,275.66,544.3))
    M=Vector((260,225.15,437.79));B=Vector((239,170,327))
    T=R.lerp(U,.47);K=R.lerp(B,.48)
    paths={
      'UpperRail':[R, R.lerp(U,.13)+Vector((-5,-2,0)), U],
      'LowerRail':[R, R.lerp(B,.13), B],
      'FrontUpright':[U,M,B],
      'InnerDiagonal':[T,M],
      'InnerVertical':[T,K],
      'InnerCrossbar':[K,M],
    }
    controls={k:[list(p) for p in ps] for k,ps in paths.items()}
    for sign,lab in [(-1,'L'),(1,'R')]:
        q=lambda p:Vector((sign*p[0],p[1],p[2]))
        sources=[]
        for key,path in paths.items():
            r=11.5 if key in ('UpperRail','LowerRail','FrontUpright') else 9.5
            pts=fillet(path,16) if key in ('UpperRail','LowerRail') else [Vector(p) for p in path]
            o=b.tube('Tool_Guard_'+key+'_'+lab,[q(p) for p in pts],r,'black',False,False)
            o.data.use_fill_caps=True;o.hide_render=True;o.hide_set(True);o['export_exclude']=True
            o['guard_control']=True;o['evidence']='Owner supplied guard product photographs, 2026-09-20'
            sources.append(o)
        # Live Geometry Nodes uses the editable separate tubular paths. Remesh
        # welds intersections; sampling is a construction choice, NOT accuracy.
        me=bpy.data.meshes.new('GuardBar_'+lab+'_assembly')
        ob=bpy.data.objects.new('GuardBar_'+lab,me);b.COL.objects.link(ob)
        ng=bpy.data.node_groups.new('GuardProductAssembly_'+lab,'GeometryNodeTree')
        ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
        ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        join=ng.nodes.new('GeometryNodeJoinGeometry');output=ng.nodes.new('NodeGroupOutput')
        for source in sources:
            info=ng.nodes.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=source;info.transform_space='RELATIVE'
            # Object Info on bevelled curve produces mesh geometry already.
            ng.links.new(info.outputs['Geometry'],join.inputs['Geometry'])
        ng.links.new(join.outputs['Geometry'],output.inputs['Geometry'])
        mod=ob.modifiers.new('Editable_guard_paths','NODES');mod.node_group=ng
        mod=ob.modifiers.new('Tube_junction_weld','REMESH');mod.mode='VOXEL';mod.voxel_size=.001;mod.use_smooth_shade=True
        mod=ob.modifiers.new('Weld_surface_finish','SMOOTH');mod.factor=.24;mod.iterations=2
        ob.data.materials.append(b.M['black'])
        ob['control_cage_source']='reconstruction_v2/data/current_controls/guard_product_r46.json'
        ob['acceptance']='NOT_PASSED; topology photo-supported, dimensions inferred'
        # Two replaceable rubber heads; third bottom location is a mounting
        # sleeve/cap, distinctly smaller. No invented third large crash puck.
        for label,p,length in [('Upper',U,53),('Middle',M,36)]:
            a=q(p);out=Vector((sign,0,0))
            annulus(b,'GuardMount_Sleeve_'+label+'_'+lab,a-out*17,a+out*(length-13),16.5,10.5)
            b.rod('GuardBar_Slider_'+label+'_'+lab,a+out*(length-21),a+out*(length-4),12,'rubber',40)
            cap=b.cyl('GuardBar_SliderCap_'+label+'_'+lab,a+out*(length-1),18,16,'rubber',out,48,5)
            for suffix,z in [('Top',18),('Bottom',-18)]:
                b.cyl('GuardMount_LockBolt_'+label+'_'+suffix+'_'+lab,a+out*(length-27)+Vector((0,0,z)),3.4,6,'steel',(0,0,1),6,.3)
        a=q(B);out=Vector((sign,0,0))
        annulus(b,'GuardMount_Sleeve_Bottom_'+lab,a-out*13,a+out*20,13,7)
        b.cyl('GuardMount_BottomCap_'+lab,a+out*21,12.8,8,'black',out,40,3)
        # Rear flat strap reaches the retained rider rearset attachment.
        start=q((172.47,-201.34,441.41));end=q(R);axis=(end-start).normalized()
        u=Vector((0,-axis.z,axis.y)).normalized();v=axis.cross(u).normalized()
        strap=loft(s,'GuardMount_Rear_'+lab,[[list(c+u*x+v*y) for x,y in [(-13,-3),(13,-3),(13,3),(-13,3)]] for c in [start-axis*10,end+axis*5]],b.M['black'],2)
        b.rod('GuardMount_RearBolt_'+lab,start-Vector((sign*9,0,0)),start+Vector((sign*11,0,0)),6,'steel',24)
        for label,p,root in [('Upper',U,(143,276,544)),('Lower',B,(153,170,327))]:
            b.rod('GuardMount_'+label+'_'+lab,q(root),q(p),9,'black',32)
        b.rod('GuardMount_UpperFoot_'+lab,q((134,272,542)),q((153,279,546)),11,'black',32)
        b.rod('GuardMount_LowerFoot_'+lab,q((135,170,327)),q((163,170,327)),11,'black',32)
        for n in s.objects:
            if n.name.startswith(('GuardBar','GuardMount')) and n.name.endswith('_'+lab):
                n['evidence']='Owner product guard images; photo layout retained, hidden mounting depth provisional'
    from prune_geometry_islands import apply as keep_main
    keep_main(s.objects['GuardBar_R'],'Guard_MainWeldOnly')
    # Mirror evaluated right assembly, avoiding independent voxel-grid drift.
    left=s.objects['GuardBar_L'];left.modifiers.clear()
    ng=bpy.data.node_groups.new('GuardProductExactMirror','GeometryNodeTree')
    ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    info=ng.nodes.new('GeometryNodeObjectInfo');info.inputs['Object'].default_value=s.objects['GuardBar_R'];info.transform_space='RELATIVE'
    tf=ng.nodes.new('GeometryNodeTransform');tf.inputs['Scale'].default_value=(-1,1,1)
    out=ng.nodes.new('NodeGroupOutput');ng.links.new(info.outputs['Geometry'],tf.inputs['Geometry']);ng.links.new(tf.outputs['Geometry'],out.inputs['Geometry'])
    mod=left.modifiers.new('Exact_right_assembly_mirror','NODES');mod.node_group=ng
    (V/'data/current_controls/guard_product_r46.json').write_text(json.dumps({'revision':'r46','paths_mm':controls,'outer_radius_mm':11.5,'brace_radius_mm':9.5,'rubber_sliders_per_side':2,'lower_end':'smaller mounting sleeve and cap','evidence':'Owner-provided installed L/R and detached product views','unverified':['tube diameters','lateral offset','hidden mount depth','exact radii']},indent=2))
    bpy.context.view_layer.update()
    return {'replaced':'all guard objects','outer_paths':3,'inner_braces':3,'sliders_per_side':2,'lower_rail_restored':True,'left_mirrored':True}
