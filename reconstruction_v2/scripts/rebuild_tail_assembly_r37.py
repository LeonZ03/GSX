"""Independent r36 -> rear assembly candidate; hidden dimensions unverified."""
from pathlib import Path
import bpy,json,sys,math
from mathutils import Vector
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
from rebuild_clutch_r30 import loft,mesh
from rebuild_rear_hardware_r36 import tube,boolean

def capped_fan(scene,name,rings,material):
    n=len(rings[0]);verts=sum(rings,[])
    verts += [[sum(p[k] for p in ring)/n for k in range(3)] for ring in rings]
    faces=[(2*n,(i+1)%n,i) for i in range(n)]
    faces += [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    faces += [(2*n+1,n+i,n+(i+1)%n) for i in range(n)]
    return mesh(scene,name,verts,faces,material)

def apply(scene,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    if scene.get('revision')!='r36':raise ValueError('Requires isolated r36')
    d=json.loads((V/'data/revisions/r37_tail_assembly/control.json').read_text())
    black=scene.objects['Body_TankSideTrim'].data.materials[0]
    lens=scene.objects['Headlight_Lens'].data.materials[0]
    metal=scene.objects['BrakeDisc_Rear'].data.materials[0]
    before=set(scene.objects)
    bpy.data.objects.remove(scene.objects['LicensePlate_Bracket'],do_unlink=True)
    rings=[]
    for y,z,w in d['fender_sections_y_z_halfwidth']:
        rings.append([[-w,y,z-6],[-w,y,z],[0,y,z+7],[w,y,z],[w,y,z-6],[0,y,z+1]])
    top=loft(scene,'Fender_Rear_Crown',rings,black,1)
    for side,lab in [(-1,'L'),(1,'R')]:
        p=d['side_panel_yz'];x=side*d['side_panel_x']
        panel=loft(scene,'Fender_Rear_Side_'+lab,[[[x+dx,y,z] for y,z in p] for dx in [-2,2]],black)
        cut=[[-867,803],[-1008,775],[-1047,672],[-968,735]]
        tool=loft(scene,'Tool_FenderSlot_'+lab,[[[xx,y,z] for y,z in cut] for xx in [-100,100]],black)
        boolean(panel,tool)
        c=Vector(d['indicator_center_R']);c.x*=side
        tube(scene,'Indicator_Rear_Stem_'+lab,[c-Vector((side*47,0,0)),c-Vector((side*20,0,0))],8,black)
        rings=[]
        for dx,ry,rz in [(-29,5,5),(-22,21,15),(0,26,18),(24,16,12),(32,2,2)]:
            rings.append([[c.x+side*dx,c.y+ry*math.cos(k*math.tau/16),c.z+rz*math.sin(k*math.tau/16)] for k in range(16)])
        loft(scene,'Indicator_Rear_'+lab,rings,lens,.4)
        # Transverse connection between the fender shell and indicator stalk.
        tube(scene,'Indicator_Rear_Mount_'+lab,[[side*45,c.y,c.z],[c.x-side*45,c.y,c.z]],7,black)
    # A shallow housing sits ahead of the visible rearward-facing lens.
    outline=d['tail_lens_outline']
    capped_fan(scene,'Taillight_Housing',[[[x*1.05,y+dy,z] for x,y,z in outline] for dy in [3,24]],black)
    capped_fan(scene,'Taillight_Lens',[[[x,y+dy,z] for x,y,z in outline] for dy in [-1,2]],lens)
    cy=sum(p[1] for p in outline)/len(outline);cz=sum(p[2] for p in outline)/len(outline)
    aperture=capped_fan(scene,'Tool_TaillightAperture',[[[x*1.10,cy+(y-cy)*1.10+dy,cz+(z-cz)*1.10] for x,y,z in outline] for dy in [-5,29]],black)
    boolean(scene.objects['Body_Tail'],aperture)
    # Update the exposed legacy support layout to fit the reconstructed shell.
    # Hidden tube routing remains a packaging estimate, not a measured frame.
    for lab,side in [('L',-1),('R',1)]:
        for base,key in [('Frame_SeatRail_','frame_seat_rail_R'),('Frame_Subframe_','frame_subframe_R')]:
            rail=scene.objects[base+lab];rail.data=rail.data.copy();rail.data.use_fill_caps=True
            for sp in rail.data.splines:
                points=sp.bezier_points if sp.type=='BEZIER' else sp.points
                if len(points)!=3:raise ValueError('Unexpected inherited frame topology')
                for p,xyz in zip(points,d[key]):
                    q=Vector((side*xyz[0],xyz[1],xyz[2]))*.001
                    if sp.type=='BEZIER':p.co=q;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
                    else:p.co=tuple(q)+(1,)
            weld=rail.modifiers.new('Tube_cap_weld','WELD');weld.merge_threshold=.000001
            rail['unverified']='Routing fitted within body envelope; hidden frame dimensions unmeasured.'
    tail=scene.objects['Body_Tail'];tail.data=tail.data.copy()
    for index,z in d['tail_tip_z_mm'].items():tail.data.vertices[int(index)].co.z=z*.001
    tail.data.update()
    tail['control_cage_source']='reconstruction_v2/data/revisions/r37_tail_assembly/Body_Tail.json'
    for lab in ['L','R']:
        rail=scene.objects['Frame_Subframe_'+lab]
        tool=rail.copy();tool.data=rail.data.copy();tool.name='Tool_TailFrameClearance_'+lab
        tool.data.bevel_depth+=.002
        next(iter(rail.users_collection)).objects.link(tool)
        bpy.context.view_layer.update()
        me=bpy.data.meshes.new_from_object(tool.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        name=tool.name;matrix=tool.matrix_world.copy();bpy.data.objects.remove(tool,do_unlink=True)
        tool=bpy.data.objects.new(name,me);next(iter(rail.users_collection)).objects.link(tool);tool.matrix_world=matrix
        boolean(tail,tool)
        tool['unverified']='2 mm construction clearance at underside frame entry; not measured.'
    def box(name,c,size,mat,bevel=.5):
        x,y,z=c;w,dep,h=size
        return loft(scene,name,[[[x+a*w/2,y+dy,z+b*h/2] for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]] for dy in [-dep/2,dep/2]],mat,bevel)
    box('Reflector_Rear_Housing',[0,-1030,805],[84,16,30],black,2)
    box('Reflector_Rear',[0,-1040,805],[73,4,21],lens,1)
    box('LicensePlate_LampHousing',[0,-1033,783],[76,31,24],black,2)
    box('LicensePlate_LampLens',[0,-1047,777],[57,3,12],lens,.5)
    plate=scene.objects['LicensePlate'];plate.location=Vector(d['plate_center'])*.001;plate.rotation_euler.x=math.radians(-15)
    box('LicensePlate_Crossmember',[0,-1068,697],[182,9,22],black,1)
    for side in [-1,1]:
        tube(scene,'LicensePlate_Support_'+('L' if side<0 else 'R'),[[side*31,-1033,716],[side*75,-1068,697]],5,metal)
    col=next(c for c in scene.collection.children if c.name.startswith('Collection_Details'))
    for o in set(scene.objects)-before:
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o);o['stage_c_owner']='tail_assembly_r37';o['acceptance']='NOT_PASSED';o['evidence_control']='data/revisions/r37_tail_assembly/control.json'
    scene['revision']='r37';scene.name='GSX250R_Reconstruction_V2_Gray_r37';scene['stage_C']='NOT_PASSED'
    bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True)
    return {'saved':str(output),'objects':len(scene.objects),'status':'CANDIDATE_NOT_ACCEPTED'}
