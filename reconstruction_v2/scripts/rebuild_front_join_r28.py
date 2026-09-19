"""Unify the front shoulder control surface on an isolated r27 candidate.
Photo cameras stay fixed; editable controls remain in the saved source.
"""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
import build_gray as bg
from rebuild_body_stage_b import setup_helpers

def apply(scene,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    if scene.get('revision')!='r27':raise ValueError('Requires r27 candidate')
    setup_helpers(scene);host=scene.objects['Body_NoseAssembly'];flags=[m.show_viewport for m in host.modifiers]
    for m in host.modifiers:m.show_viewport=False
    D=V/'data/revisions/r27_front_candidate';a=json.loads((D/'Body_UpperCowling.json').read_text());b=json.loads((D/'Body_CowlingSide.json').read_text())
    assert len(a['grid'])==len(b['grid'])
    grid=[]
    for ar,br in zip(a['grid'],b['grid']):
        assert (Vector(ar[-1])-Vector(br[0])).length<.001
        grid.append(ar+br[1:])
    inner=json.loads((D/'Cockpit_InnerPanel.json').read_text())['grid']
    for i in range(6):
        p=Vector(inner[i][-1])+Vector((0,0,-1.0));q=Vector(grid[i][6])
        for j,t in enumerate([0,.04,.20,.46,.74,.96,1]):grid[i][j]=list(p.lerp(q,t))
    d=dict(name='Body_UpperSideCowl',units='mm',grid=grid,mirror_x=True,subdivision=1,thickness_mm=2.5,material='shell',crease_boundary=.35,crease_columns={'6':.35},revision='r28',status='NOT_PASSED',notes='Connected upper shoulder and side return quad controls, shared rail welded before subdivision. Hidden live contributor to front cowl assembly; no photo accuracy certification.')
    o=bg.cage(d);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if sum(f.normal.x*f.calc_area() for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free();o.hide_render=True;o['construction_control_only']=True;o['export_exclude']=True
    for n in ['Body_UpperCowling','Body_CowlingSide']:
        q=scene.objects[n];q.hide_render=True;q['construction_control_only']=True;q['export_exclude']=True;q['superseded_by']='Body_UpperSideCowl'
    tree=host.modifiers['Live_Editable_Quad_Controls'].node_group;join=next(n for n in tree.nodes if n.bl_idname=='GeometryNodeJoinGeometry');node=tree.nodes.new('GeometryNodeObjectInfo');node.transform_space='ORIGINAL';node.inputs['Object'].default_value=o;tree.links.new(node.outputs['Geometry'],join.inputs['Geometry'])
    host['control_dependencies']=json.dumps(['Body_NoseCheek','Body_NoseSideReturn','Body_WindscreenSeat','Body_UpperSideCowl'])
    host['assembly_method']='Live editable shoulder and nose shells unioned at 1 mm. Construction thickness provisional.'
    # Keep photographed boundary rails. Bow only interior control columns outward
    # where the pre-existing radiator side tank breaks through the fairing.
    fair=scene.objects['Body_SideFairing'];fd=json.loads((D/'Body_SideFairing.json').read_text())
    for row in fd['grid']:
        for j,p in enumerate(row):
            if j in [0,6]:continue
            if 340<p[1]<490 and 415<p[2]<645:
                p[0]=max(p[0],178+8*math.sin(math.pi*(p[2]-415)/230))
    for v,p in zip(fair.data.vertices,[p for r in fd['grid'] for p in r]):v.co=Vector(p)*.001
    fair.data.update();fd['revision']='r28';fd['notes']+=' Interior radiator clearance candidate; outer rails unchanged.'
    for m,f in zip(host.modifiers,flags):m.show_viewport=f
    scene['revision']='r28';scene.name='GSX250R_Reconstruction_V2_Gray_r28';scene['candidate_status']='ASSEMBLY_REVIEW_REQUIRED';scene['stage_B']='NOT_PASSED';scene['stage_C']='NOT_PASSED'
    out=V/'data/revisions/r28_front_candidate';out.mkdir(exist_ok=True)
    for data in [d,fd]:(out/(data['name']+'.json')).write_text(json.dumps(data,indent=2),encoding='utf8')
    bpy.data.libraries.write(str(output),{scene},fake_user=True)
    return {'source':str(output),'new_quad_controls':'Body_UpperSideCowl','photo_cameras_changed':False,'status':'NOT_PASSED'}
