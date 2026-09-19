"""Rebuild side-specific rider footrest carriers from frozen photo-derived controls.
Only an isolated r25 is accepted. Cameras and existing frame geometry stay fixed.
Thickness, hidden bosses and linkage depths remain unverified construction estimates.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
import rebuild_mounts_r21 as geo


def prism(name,outline,depth,mat='metal',bevel=1.2):
    n=len(outline);pts=[Vector(p)+Vector((dx,0,0)) for dx in (-depth/2,depth/2) for p in outline]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=geo.mesh(name,pts,faces,mat,False)
    if bevel:
        m=o.modifiers.new('Cast_Edge_Radius','BEVEL');m.width=bevel*.001;m.segments=3
    return o


def box(name,center,size,mat='metal',bevel=1.2):
    c=Vector(center);sx,sy,sz=size
    out=[c+Vector((0,y,z)) for y,z in [(-sy/2,-sz/2),(sy/2,-sz/2),(sy/2,sz/2),(-sy/2,sz/2)]]
    return prism(name,out,sx,mat,bevel)


def hole(o,cutter,collection):
    for c in list(cutter.users_collection):c.objects.unlink(cutter)
    collection.objects.link(cutter);cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE';cutter['export_exclude']=True
    m=o.modifiers.new('Editable_Opening_'+cutter.name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter


def flat_link(name,a,b,width,depth,mat='metal'):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((1,0,0))).normalized();n=axis.cross(u).normalized();verts=[]
    count=26;faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    # Ordered semicircles produce a simple rounded strap outline.
    ring=[]
    for i in range(13):
        ang=-math.pi/2+i*math.pi/12;ring.append(b+axis*math.cos(ang)*width/2+u*math.sin(ang)*width/2)
    for i in range(13):
        ang=math.pi/2+i*math.pi/12;ring.append(a+axis*math.cos(ang)*width/2+u*math.sin(ang)*width/2)
    verts=[p+n*dz for dz in (-depth/2,depth/2) for p in ring]
    return geo.mesh(name,verts,faces,mat,False)


def apply(scene,control,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    if scene.get('revision')!='r25':raise ValueError('Requires isolated r25')
    d=json.loads(Path(control).read_text(encoding='utf8'))
    geo.COL=scene.objects['Rearset_R'].users_collection[0]
    geo.MAT={'metal':scene.objects['Rearset_R'].data.materials[0], 'dark':scene.objects['Footpeg_R'].data.materials[0], 'rubber':scene.objects['Footpeg_Ridge_R'].data.materials[0]}
    helpers=next(c for c in scene.collection.children if c.name.startswith('Collection_Blockout'))
    display=[(m,m.show_viewport) for m in scene.objects['Body_NoseAssembly'].modifiers]
    for m,_ in display:m.show_viewport=False
    removed=[]
    for o in list(scene.objects):
        if o.name.startswith(('Rearset_','Footpeg_')) or o.name in ['GuardMount_Rear_L','GuardMount_Rear_R','GuardMount_Bolt_rear_mount_L','GuardMount_Bolt_rear_mount_R']:
            removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
    created_before=set(scene.objects)
    for lab,side in d['sides'].items():
        sign=1 if lab=='R' else -1
        cast=prism('Rearset_'+lab,side['outer'],d['thickness_mm'])
        hole(cast,prism('Tool_Rearset_Slot_'+lab,side['slot'],42,bevel=0),helpers)
        for key in ['upper','lower','heel_top','heel_bottom']:
            if key not in side['mounts']:continue
            p=Vector(side['mounts'][key]);radius=4.8 if key.startswith('heel') else 5.3
            hole(cast,geo.tube('Tool_Rearset_Hole_'+lab+'_'+key,p+Vector((-22,0,0)),p+Vector((22,0,0)),radius),helpers)
            if key.startswith('heel'):continue
            geo.ring('Rearset_Washer_'+lab+'_'+key,p+Vector((sign*5,0,0)),5.3,9,2)
            geo.tube('Rearset_Bolt_'+lab+'_'+key,p+Vector((sign*4,0,0)),p+Vector((sign*12,0,0)),7.8,'metal',6)
            # Hidden boss connects to the retained frame; depth remains estimated.
            inner=p.copy();inner.x=sign*126
            geo.tube('Rearset_FrameBoss_'+lab+'_'+key,inner,p-Vector((sign*4,0,0)),10,'dark')
        weld=cast.modifiers.new('Join_Boolean_Seams','WELD');weld.merge_threshold=2e-6
        pivot=Vector(side['mounts']['peg']);root=pivot+Vector((sign*18,0,0));end=pivot+Vector((sign*109,0,0))
        # Folding pin runs fore/aft; rubber-topped cast bar extends outboard.
        for off in (-13,13):box('Footpeg_Clevis_'+lab+('_Front' if off>0 else '_Rear'),root+Vector((0,off,0)),(21,6,25),'metal',2)
        geo.tube('Footpeg_FoldPin_'+lab,root+Vector((0,-18,0)),root+Vector((0,18,0)),4,'metal',32)
        box('Footpeg_'+lab,(root+end)/2+Vector((sign*7,0,0)),(78,25,17),'metal',4)
        box('Footpeg_Rubber_'+lab,(root+end)/2+Vector((sign*9,0,12)),(78,28,12),'rubber',5)
        for j in range(9):box('Footpeg_Ridge_'+lab+'_'+str(j),root+Vector((sign*(20+j*7.4),0,19)),(2.8,25,2.5),'rubber',.8)
        geo.tube('Footpeg_Feeler_'+lab,end+Vector((0,0,-8)),end+Vector((0,0,-28)),4,'metal',24)
        # Distinct visible brake/shift controls, not a mirrored generic pedal.
        toe=Vector(side['toe']);lever_pivot=pivot+Vector((sign*18,4,-13))
        if lab=='R':
            elbow=Vector((sign*183,toe.y-18,toe.z-8))
            flat_link('BrakePedal_Arm_Rear',lever_pivot,elbow,14,7)
            flat_link('BrakePedal_Arm_Front',elbow,toe,13,7)
            box('BrakePedal_ToePad',toe,(31,30,7),'metal',2)
            for j in range(5):box('BrakePedal_ToeRidge_'+str(j),toe+Vector((0,(j-2)*5,5)),(29,1.8,2),'metal',.4)
            # Visible master cylinder body above the rear arm; no unobserved hose path invented.
            mc=pivot+Vector((-20,-35,65));geo.tube('BrakeMaster_RearBody',mc,mc+Vector((0,0,40)),12,'dark')
            geo.tube('BrakeMaster_RearPushrod',lever_pivot+Vector((-20,-32,0)),mc,3.5,'metal',24)
        else:
            elbow=Vector(side['link_lower']);flat_link('ShiftLever_Arm',lever_pivot,toe,12,7)
            geo.tube('ShiftLever_ToeRubber',toe+Vector((-20,0,0)),toe+Vector((10,0,0)),9,'rubber',32)
            a=Vector(side['link_upper']);b=Vector(side['link_lower']);geo.tube('ShiftLink_Rod',a,b,3.2,'metal',24)
            flat_link('ShiftLink_InputArm',side['shift_spindle'],a,12,6)
            flat_link('ShiftLink_OutputArm',lever_pivot,b,12,6)
            for key,p in [('Input',a),('Output',b)]:geo.ring('ShiftLink_Joint_'+key,p,3.2,7,9)
        # Both guard bars keep the same mirrored rear installation endpoint.
        p=Vector(d['sides']['R']['mounts']['upper']);p.x=(p.x+10)*sign
        flat_link('GuardMount_Rear_'+lab,p,Vector((218*sign,10,497)),25,8,'dark')
        geo.tube('GuardMount_Bolt_rear_mount_'+lab,p+Vector((-4,0,0)),p+Vector((4,0,0)),7,'metal',6)
    for o in set(scene.objects)-created_before:
        o['stage_r26_owner']='rearset_rebuild';o['dimension_status']='PHOTO_LED_NOT_METRIC_ACCEPTED'
    for m,enabled in display:m.show_viewport=enabled
    scene['revision']='r26';scene.name='GSX250R_Reconstruction_V2_Gray_r26';scene['stage_c_rearsets_rebuilt']=True;scene['stage_C']='NOT_PASSED';scene['stage_B']='NOT_PASSED'
    bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(output))
    return {'source':str(output),'objects':len(scene.objects),'removed':removed,'created':sorted(o.name for o in set(scene.objects)-created_before),'status':'CANDIDATE_NOT_ACCEPTED'}

if __name__=='__main__':result=apply(bpy.context.scene,V/'data/revisions/r26/rearset_control.json',V/'blends/26_rearset_candidate.blend')
