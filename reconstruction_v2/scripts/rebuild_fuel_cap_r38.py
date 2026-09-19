"""Owner65 cap structure and evaluated tank mounting; sizes remain provisional."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_clutch_r30 import mesh,loft
from rebuild_rear_hardware_r36 import boolean

def apply(scene,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    if scene.get('revision')!='r37':raise ValueError('Requires r37')
    silver=scene.objects['FuelCap'].data.materials[0];black=scene.objects['FuelCap_Core'].data.materials[0]
    tank=scene.objects['Body_Tank'];ev=tank.evaluated_get(bpy.context.evaluated_depsgraph_get())
    samples=[]
    for y in [.178,.188,.198]:
        ok,p,n,idx=ev.ray_cast(Vector((0,y,2)),Vector((0,0,-1)))
        if not ok:raise ValueError('No tank mounting surface')
        samples.append(p)
    center=samples[1]*1000;u=Vector((1,0,0));v=(samples[2]-samples[0]).normalized();normal=u.cross(v).normalized()
    def xyz(x,y,z):return list(center+u*x+v*y+normal*z)
    before=set(scene.objects)
    for name in ['FuelCap','FuelCap_Core']:bpy.data.objects.remove(scene.objects[name],do_unlink=True)
    def cylinder(name,r,z0,z1,material,n=80,cx=0,cy=0):
        return loft(scene,name,[[xyz(cx+r*math.cos(j*math.tau/n),cy+r*math.sin(j*math.tau/n),z) for j in range(n)] for z in [z0,z1]],material)
    profile=[(40,-2),(57,-2),(57,1.5),(55.5,2.5),(40,2.5)];n=96;k=len(profile)
    verts=[xyz(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n) for r,z in profile]
    faces=[(i*k+j,((i+1)%n)*k+j,((i+1)%n)*k+(j+1)%k,i*k+(j+1)%k) for i in range(n) for j in range(k)]
    rim=mesh(scene,'FuelCap',verts,faces,silver)
    cylinder('FuelCap_Gasket',57,-7,-2.2,black)
    cylinder('FuelCap_Core',39.5,-5,1.6,black)
    cut=cylinder('Tool_FuelCapRecess',57.8,-17,18,black);boolean(tank,cut)
    # Five visible fasteners in owner65; no invented branding or concealed text.
    for j in range(5):
        a=math.radians(90-j*72);x,y=47*math.cos(a),47*math.sin(a)
        bore=cylinder('Tool_FuelCapBore_'+str(j),3.9,-5,6,silver,32,x,y);boolean(rim,bore)
        head=cylinder('FuelCap_Bolt_'+str(j),3.5,-1,2.8,silver,32,x,y)
        socket=cylinder('Tool_FuelCapHex_'+str(j),1.6,1.9,4,black,6,x,y);boolean(head,socket)
    weld=rim.modifiers.new('Boolean_seam_weld','WELD');weld.merge_threshold=.000002
    poly=[(-22,-14),(-25,3),(-14,21),(14,21),(25,3),(22,-14)]
    loft(scene,'FuelCap_LockCover',[[xyz(x,y,z) for x,y in poly] for z in [1.7,3.2]],black,.6)
    loft(scene,'FuelCap_Hinge',[[xyz(x,y,z) for x,y in [(-14,-30),(14,-30),(14,-23),(-14,-23)]] for z in [1.8,4]],black,.5)
    col=next(c for c in scene.collection.children if c.name.startswith('Collection_Details'))
    for o in set(scene.objects)-before:
        for c in list(o.users_collection):c.objects.unlink(o)
        col.objects.link(o);o['stage_c_owner']='fuel_cap_r38';o['acceptance']='NOT_PASSED'
    scene['revision']='r38';scene.name='GSX250R_Reconstruction_V2_Gray_r38';scene['stage_C']='NOT_PASSED'
    bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True)
    report={'center_mm':list(center),'normal':list(normal),'five_bolts':'owner65 visual evidence','outer_diameter_mm':114,'unverified':['Nominal 114mm inherited diameter, screw circle and recess depth not measured','Fixed XY inherited; image65 is structural evidence, not a calibrated acceptance camera'],'source':str(output)}
    (V/'qa'/f'fuel_cap_mount_{output.stem}.json').write_text(json.dumps(report,indent=2));return report
