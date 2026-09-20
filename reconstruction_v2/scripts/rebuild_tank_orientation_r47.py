"""Photo-led tank crown and filler orientation correction, r46 -> r47.

Run only through Blender MCP.  Does not save the shared blend or overwrite the
canonical tank control. Dimensions and pose are proportional photo estimates.
"""
from pathlib import Path
import json, math
import bpy, bmesh
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]


def _center(obj):
    return sum((obj.matrix_world @ v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)


def apply(scene=None):
    scene = scene or bpy.context.scene
    tank = scene.objects['Body_Tank']
    if len(tank.data.vertices) != 120 or tank.get('tank_orientation_revision'):
        raise ValueError('Requires unmodified r46 10x12 tank; migration is not repeatable')
    before = [[list(tank.matrix_world @ v.co * 1000) for v in tank.data.vertices[i:i+12]] for i in range(0,120,12)]
    grid = json.loads(json.dumps(before))
    # Rear and front interface rows retain their existing positions. The crown
    # now rises onto a broad plateau rather than peaking behind a forward-facing
    # cap. IMG65 sees almost the full circular cap from the rider side.
    top_delta = [0,0,20,14,-27,-5,31,8,0,0]
    crown_weight = [1,1,.85,.50,.18,0,0,0,0,0,0,0]
    flank_weight = [0,0,.25,.8,1,1,.7,.2,0,0]
    for i,row in enumerate(grid):
        w=flank_weight[i]
        for j,p in enumerate(row):
            p[2] += top_delta[i]*crown_weight[j]
            if j not in (0,11):
                # Resolve the actual broad shoulder and shallow pressed flank:
                # remove r46's excessive concavity without losing the lower lip.
                p[0] += w*[0,2,8,12,10,22,26,19,13,8,4,0][j]
                p[2] += w*[0,0,0,0,3,6,9,5,2,0,0,0][j]
        if 2 <= i <= 7:
            # Flat transverse filler land; remove the inverted centre crown.
            row[1][2]=row[0][2]
            # The pressed low lip is a narrow feature close to the bottom,
            # not the thick continuous ledge of the earlier candidate.
            a,b=Vector(row[7]),Vector(row[10])
            row[8]=list(a.lerp(b,.70))
            row[9]=list(a.lerp(b,.90)+Vector((2*flank_weight[i],0,0)))
    inv=tank.matrix_world.inverted()
    for v,p in zip(tank.data.vertices,[p for row in grid for p in row]):
        v.co=inv@(Vector(p)*.001)
    tank.data.update()
    # Existing creases are retained as topology attributes, reduced at the old
    # bowl transition so a broad pressed panel replaces the pinched channel.
    crease=tank.data.attributes.get('crease_edge')
    if crease:
        for e in tank.data.edges:
            cols=[v%12 for v in e.vertices]
            if cols[0]==cols[1] and cols[0] in (3,4,7,8,9):
                crease.data[e.index].value={3:.50,4:.30,7:.16,8:.25,9:.45}[cols[0]]
    bpy.context.view_layer.update()
    # Inspect the uncut crown, then rigidly move all cap details and every
    # Boolean dependency together; never rotate only the decorative cover.
    recess_mod=next(m for m in tank.modifiers if m.type=='BOOLEAN' and m.object and m.object.name=='Tool_FuelCapRecess')
    visible=recess_mod.show_viewport
    recess_mod.show_viewport=False
    bpy.context.view_layer.update()
    ev=tank.evaluated_get(bpy.context.evaluated_depsgraph_get())
    cap_y=.100
    hits=[]
    for y in [cap_y-.012,cap_y,cap_y+.012]:
        ok,p,n,idx=ev.ray_cast(inv@Vector((0,y,1.5)),Vector((0,0,-1)))
        if not ok:raise RuntimeError('Missing tank crown mounting surface')
        hits.append(tank.matrix_world@p)
    target=hits[1]
    tangent=(hits[2]-hits[0]).normalized()
    normal=Vector((1,0,0)).cross(tangent).normalized()
    # Gasket geometry contains two planar end caps. Read its actual normal,
    # because all original meshes have baked coordinates and identity poses.
    gasket=scene.objects['FuelCap_Gasket']
    poly=max(gasket.data.polygons,key=lambda p:p.area)
    old_normal=(gasket.matrix_world.to_3x3()@poly.normal).normalized()
    if old_normal.z<0:old_normal=-old_normal
    cap=scene.objects['FuelCap']
    old_center=_center(cap)
    new_center=target+normal*.0005
    rot=old_normal.rotation_difference(normal).to_matrix().to_4x4()
    transform=Matrix.Translation(new_center)@rot@Matrix.Translation(-old_center)
    moved=[]
    for obj in scene.objects:
        if obj.name.startswith(('FuelCap','Tool_FuelCap')):
            obj.matrix_world=transform@obj.matrix_world
            moved.append(obj.name)
    recess_mod.show_viewport=visible
    bpy.context.view_layer.update()
    # Transfer smooth crown normals from a live, uncut copy of the same cage.
    # This removes Boolean triangulation shading around the circular recess;
    # it does not change the evaluated surface or hide geometric intersections.
    donor=tank.copy();donor.name='Tool_TankR47SurfaceNormals';donor.data=tank.data
    scene.collection.objects.link(donor)
    for mod in list(donor.modifiers):
        if mod.type=='BOOLEAN' and mod.object and mod.object.name=='Tool_FuelCapRecess':
            donor.modifiers.remove(mod)
    donor.hide_render=True;donor.hide_set(True);donor['export_exclude']=True
    donor['dependency_note']='Live uncut Body_Tank cage for filler recess normals'
    normals=tank.modifiers.new('FillerLand_SurfaceNormals','DATA_TRANSFER')
    normals.object=donor;normals.use_loop_data=True
    normals.data_types_loops={'CUSTOM_NORMAL'};normals.loop_mapping='POLYINTERP_NEAREST'
    tank['tank_orientation_revision']='r47'
    tank['acceptance']='NOT_PASSED'
    tank['control_cage_source']='reconstruction_v2/data/current_controls/tank_r47_control.json'
    control=json.loads((ROOT/'data/current_controls/Body_Tank.json').read_text())
    control.update({'name':'Body_Tank','units':'mm','mirror_x':True,'grid':grid,
             'faces':[list(p.vertices) for p in tank.data.polygons],
             'revision':'r47','status':'PHOTO_LED_UNVERIFIED_DIMENSIONS',
             'crease_columns':{'2':.18,'3':.50,'4':.30,'7':.16,'8':.25,'9':.45},'current_snapshot':'r47'})
    (ROOT/'data/current_controls/tank_r47_control.json').write_text(json.dumps(control,indent=2))
    report={'revision':'r47','old_cap_center_mm':list(old_center*1000),'new_cap_center_mm':list(new_center*1000),
            'old_cap_normal':list(old_normal),'new_cap_normal':list(normal),
            'normal_rotation_deg':math.degrees(old_normal.angle(normal)),
            'moved_cap_objects':sorted(moved),'changed_control_points':sum(Vector(a)!=Vector(b) for r,s in zip(before,grid) for a,b in zip(r,s)),
            'fixed_interface_rows':[0,1,8,9],
            'evidence':'Actually viewed IMG65/62/63/69/77 and rider screenshot; circular cap visible to rider, broad crowned pressed tank flank',
            'uncertainty':'Y=100mm is proportional estimate; no calibrated IMG65 camera, measured cap tilt or hidden tank dimensions',
            'acceptance':'NOT_PASSED'}
    (ROOT/'data/current_controls/tank_r47_pose.json').write_text(json.dumps(report,indent=2))
    return report


def audit(scene=None):
    from mathutils.bvhtree import BVHTree
    scene=scene or bpy.context.scene
    dg=bpy.context.evaluated_depsgraph_get();cache={}
    def ev(name):
        obj=scene.objects[name];e=obj.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles()
        verts=[e.matrix_world@v.co for v in me.vertices];faces=[tuple(t.vertices) for t in me.loop_triangles]
        bm=bmesh.new();bm.from_mesh(me);todo=set(bm.verts);count=0
        while todo:
            stack=[todo.pop()];count+=1
            while stack:
                v=stack.pop()
                for edge in v.link_edges:
                    q=edge.other_vert(v)
                    if q in todo:todo.remove(q);stack.append(q)
        quality={'vertices':len(verts),'open_edges':sum(e.is_boundary for e in bm.edges),
                 'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
                 'zero_area':sum(p.area<1e-13 for p in me.polygons),'components':count}
        bm.free();e.to_mesh_clear();cache[name]=(verts,faces,BVHTree.FromPolygons(verts,faces,all_triangles=True));return quality
    names=['Body_Tank','Seat_Rider','Body_TankSideTrim']+[o.name for o in scene.objects if o.name.startswith('FuelCap')]
    result={'quality':{n:ev(n) for n in names if n in scene.objects},'intersections':{}}
    for n in ['Seat_Rider','Body_TankSideTrim']:
        if n in cache:result['intersections']['Body_Tank/'+n]=len(cache['Body_Tank'][2].overlap(cache[n][2]))
    vs,fs,tree=cache['Body_Tank'];raw=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(fs[i]).intersection(fs[j])]
    result['tank_self_intersection_candidates']=len(raw)
    result['limits']='Scoped geometry test only; no overall assembly or photo likeness certification'
    (ROOT/'qa/tank_r47_geometry.json').write_text(json.dumps(result,indent=2));return result


def render(tag='after'):
    """Render isolated tank and rider-facing perspective without saving blend."""
    scene=bpy.context.scene
    for o in scene.objects:
        if o.type in ('MESH','CURVE','FONT') and not (o.name=='Body_Tank' or o.name.startswith('FuelCap')):o.hide_render=True
    scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading
    sh.light='STUDIO';sh.studiolight_rotate_z=.5;sh.color_type='SINGLE';sh.single_color=(.4,.4,.4)
    sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
    scene.world.color=(.82,.82,.82);scene.view_settings.view_transform='Standard'
    scene.render.resolution_x=1000;scene.render.resolution_y=760;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.use_border=False;scene.render.film_transparent=False
    out=ROOT/'renders/tank_r47';out.mkdir(exist_ok=True)
    configs={'Side':((2,.08,.86),(0,.08,.86),.67),'Rider':((0,-.72,1.65),(0,.08,.87),.68),
             'Oblique':((.85,.76,1.50),(0,.08,.87),.69),'Top':((0,.08,2),(0,.08,.86),.68)}
    paths=[]
    for key,(eye,target,scale) in configs.items():
        data=bpy.data.cameras.new('TankR47_'+key);cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
        cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale
        scene.camera=cam;path=out/(tag+'_'+key+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);paths.append(str(path))
    return paths
