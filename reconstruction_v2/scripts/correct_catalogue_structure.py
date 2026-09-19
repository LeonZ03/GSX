"""Incremental catalogue corrections on the preserved r20 fairing candidate.

Rebuild only chain/sprockets, rotor carriers and sensor rings. Real mounting
depths remain unaccepted. This is not a whole-scene regeneration command.
"""
from pathlib import Path
import bpy,sys,json,math,bmesh
from mathutils import Vector
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
import rebuild_mechanics_stage_c as m

def remove_prefixes(scene,prefixes):
    for o in list(scene.objects):
        if o.name.startswith(prefixes):bpy.data.objects.remove(o,do_unlink=True)

def gear(name,center,teeth,radius,pins):
    x,y,z=center
    angles=[math.atan2(p[0]-y,p[1]-z) for p in pins if abs(math.hypot(p[0]-y,p[1]-z)-radius)<.001]
    phase=math.atan2(sum(math.sin(teeth*a) for a in angles),sum(math.cos(teeth*a) for a in angles))/teeth
    # Valleys centred on roller pins; flank shape remains a visual approximation.
    n=teeth*8;vs=[]
    for xx in [x-2.6,x+2.6]:
        for j in range(n):
            a=phase+j*math.tau/n;rr=radius-5.1+8.0*(.5-.5*math.cos(teeth*(a-phase)))
            vs.append((xx,y+rr*math.sin(a),z+rr*math.cos(a)))
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    o=m._mesh(name,vs,fs,'steel',0,False)
    cutters=[m._cyl('C_tmp',(x,y,z),17 if teeth==46 else 11,14,'black',(1,0,0),48)]
    if teeth==46:
        for j in range(5):
            a=j*math.tau/5
            cutters.append(m._cyl('C_tmp',(x,y+74*math.sin(a),z+74*math.cos(a)),17,14,'black',(1,0,0),32))
    m._cut(o,cutters,'Hub_and_lightening_openings')
    o['tooth_count']=teeth;o['pitch_radius_mm']=radius;o['tooth_profile_status']='visual approximation; roller pitch positions constrained'
    return o

def chain(scene,data):
    m._COL=m._collection(scene,'Collection_Engine')
    remove_prefixes(scene,('Chain_Link','Chain_Roller','Sprocket_Rear','Sprocket_Front','Sprocket_Tooth','Sprocket_Bolt'))
    old=scene.objects.get('Chain')
    if old:bpy.data.objects.remove(old,do_unlink=True)
    x=data['chain_plane_x'];pins=data['pins_yz'];n=len(pins)
    front=gear('Sprocket_Front',(x,*data['front_center_yz']),data['front_teeth'],data['front_pitch_radius'],pins)
    rear=gear('Sprocket_Rear',(x,*data['rear_center_yz']),data['rear_teeth'],data['rear_pitch_radius'],pins)
    # A hub between the retained axle centre and the new common chain plane.
    ry,rz=data['rear_center_yz'];m._cyl('Sprocket_Rear_Hub',(-70.5,ry,rz),42,65,'gun',(1,0,0),64,1)
    for j in range(5):
        a=j*math.tau/5;m._cyl(f'Sprocket_Bolt_{j}',(x-5,ry+57*math.sin(a),rz+57*math.cos(a)),6,5,'steel',(-1,0,0),6,.4)
    # Linked mesh prototypes: alternating inner/outer side plates, rollers and pins.
    plate=m._cube('Chain_PlatePrototype',(0,0,0),(1.6,25.0,12.0),'steel',3.0)
    bpy.ops.object.select_all(action='DESELECT');plate.select_set(True);bpy.context.view_layer.objects.active=plate
    bpy.ops.object.modifier_apply(modifier=plate.modifiers[0].name)
    pm=plate.data;pm.use_fake_user=True;bpy.data.objects.remove(plate,do_unlink=True)
    roller=m._cyl('Chain_RollerPrototype',(0,0,0),5.08,6.35,'gun',(1,0,0),20,0)
    rm=roller.data;rm.use_fake_user=True;rotation=roller.rotation_quaternion.copy();bpy.data.objects.remove(roller,do_unlink=True)
    pin=m._cyl('Chain_PinPrototype',(0,0,0),2.55,17.5,'steel',(1,0,0),12,0)
    pinmesh=pin.data;pinmesh.use_fake_user=True;bpy.data.objects.remove(pin,do_unlink=True)
    root=bpy.data.objects.new('Chain',None);m._COL.objects.link(root);root['pitch_mm']=data['chain_pitch'];root['link_count']=n
    for j,(y,z) in enumerate(pins):
        y2,z2=pins[(j+1)%n];mid=Vector((x,(y+y2)/2,(z+z2)/2))*.001
        # Inner width 6.35 mm; alternating plate pairs are separated in X.
        for side in [-1,1]:
            o=bpy.data.objects.new(f'Chain_Link_{j:03}_{"L" if side<0 else "R"}',pm);m._COL.objects.link(o)
            o.location=mid+Vector((side*(3.975 if j%2==0 else 5.875)*.001,0,0));o.rotation_euler.x=math.atan2(z2-z,y2-y);o.parent=root
            o['link_index']=j
        for key,mesh in [('Roller',rm),('Pin',pinmesh)]:
            o=bpy.data.objects.new(f'Chain_{key}_{j:03}',mesh);m._COL.objects.link(o);o.location=Vector((x,y,z))*.001
            o.rotation_mode='QUATERNION';o.rotation_quaternion=rotation;o.parent=root;o['pin_index']=j
    # Clear the aft-left case at the catalogue-constrained output position.
    # Retain the editable crankcase and use an explicitly local Boolean recess.
    fy,fz=data['front_center_yz'];case=scene.objects['Engine_Crankcase']
    pocket=m._cyl('Tool_OutputSprocketClearance',(-139,fy,fz),data['front_pitch_radius']+13,143,'gun',(1,0,0),64,0)
    pocket.hide_render=True;pocket.hide_set(True);pocket['export_exclude']=True
    for c in list(pocket.users_collection):c.objects.unlink(pocket)
    next(c for c in scene.collection.children if c.name.startswith('Collection_Blockout')).objects.link(pocket)
    md=case.modifiers.new('Editable_OutputSprocketClearance','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=pocket
    exit_tool=m._cube('Tool_OutputChainExit',(-139,fy-70,fz),(143,140,110),'gun',0)
    exit_tool.hide_render=True;exit_tool.hide_set(True);exit_tool['export_exclude']=True
    for c in list(exit_tool.users_collection):c.objects.unlink(exit_tool)
    next(c for c in scene.collection.children if c.name.startswith('Collection_Blockout')).objects.link(exit_tool)
    md=case.modifiers.new('Editable_OutputChainExit','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=exit_tool
    m._cyl('Engine_OutputShaft',(-86,fy,fz),11,45,'steel',(1,0,0),32,.5)
    m._cyl('Sprocket_Front_Nut',(x-7,fy,fz),16,7,'steel',(-1,0,0),6,.8)
    scene['stage_c_drive_rebuilt']='FIG206A / FIG550B:14T46T116L; retained output height/chain plane are assumptions'

def wheels(scene):
    m._COL=m._collection(scene,'Collection_Wheels')
    remove_prefixes(scene,('RotorCarrier_','ABS_Ring_','ABS_Mount_','ABS_Bolt_'))
    for name,y,z,x,r in [('Front',715,303.9,-65,145),('Rear',-715,313.9,83,120)]:
        start=set(scene.objects)
        m._lathe('RotorCarrier_'+name,y,z,[(x-2,25),(x-2,41),(x+2,41),(x+2,25)],'gun',96)
        for j in range(5):
            a=j*math.tau/5
            poly=[(x,y+rr*math.sin(t),z+rr*math.cos(t)) for rr,t in [(33,a-.16),(r*.68,a-.10),(r*.68,a+.10),(33,a+.16)]]
            m._solid_plate(f'RotorCarrier_{name}_Arm_{j}',poly,4,'gun')
            m._cyl(f'RotorCarrier_{name}_Bolt_{j}',(x-4,y+r*.65*math.sin(a),z+r*.65*math.cos(a)),4.5,4,'steel',(1,0,0),6,.4)
        ax=x*.72;ring=m._lathe('ABS_Ring_'+name,y,z,[(ax-1,63),(ax-1,75),(ax+1,75),(ax+1,63)],'steel',200)
        cutters=[]
        for j in range(50):
            a=j*math.tau/50;o=m._cube('C_tmp',(ax,y+69*math.sin(a),z+69*math.cos(a)),(10,2.4,7),'black',0);o.rotation_euler.x=-a;cutters.append(o)
        m._cut(ring,cutters,'Fifty_sensing_slots');ring['sensor_teeth']=50;ring['catalogue_part']='54162-44H00'
        for j in range(3):
            a=j*math.tau/3
            poly=[(ax,y+rr*math.sin(t),z+rr*math.cos(t)) for rr,t in [(32,a-.15),(64,a-.09),(64,a+.09),(32,a+.15)]]
            m._solid_plate(f'ABS_Mount_{name}_{j}',poly,2,'steel')
            m._cyl(f'ABS_Bolt_{name}_{j}',(ax-2,y+37*math.sin(a),z+37*math.cos(a)),4,3,'steel',(1,0,0),6,.3)
        for o in set(scene.objects)-start:o['steer_with_front']=name=='Front'

def main():
    if Path(bpy.data.filepath).name!='20_fairing_checked.blend':raise RuntimeError('Use the preserved candidate only')
    out=V/'blends/20_drive_candidate.blend'
    if out.exists():raise FileExistsError(out)
    s=bpy.context.scene;m._materials();d=json.loads((V/'data/drive_layout.json').read_text(encoding='utf8'))
    chain(s,d);wheels(s);s['revision']='r20_candidate';s['stage_c_status']='NOT_PASSED'
    bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out))
    return {'candidate':str(out),'objects':len(s.objects),'link_count':d['link_count'],'front_sprocket_yz_mm':d['front_center_yz'],'status':'NOT_PHOTO_ACCEPTED'}
if __name__=='__main__':result=main()
