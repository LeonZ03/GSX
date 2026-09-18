"""Photo-led GSX250R reconstruction. Built and verified with the installed Blender 5.2.1 or via Blender MCP.

All construction coordinates are millimetres; mesh datablocks store metres.
Private registration is loaded only from config/user.local.json.
"""
from pathlib import Path
import bpy, math, json, os, sys, bmesh
from mathutils import Vector, Matrix
from math import sin, cos, pi

ROOT = Path(os.environ.get('GSX_ROOT', Path(__file__).resolve().parents[1]))
MM = .001
C = {}
M = {}
SC = None
COL = None
PRIVATE = json.loads((ROOT/'config/user.local.json').read_text('utf-8')) if (ROOT/'config/user.local.json').exists() else {'plate_top':'LOCAL','plate_bottom':'GSX250'}

def V(p): return Vector(p)*MM
def select(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active=o
def assign(o,name,mat=None,col=None):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    (col or COL).objects.link(o)
    if mat: o.data.materials.append(M[mat])
    o['gsx_generated']=True
    return o
def smooth(o):
    if o.type=='MESH':
        for p in o.data.polygons: p.use_smooth=True
    return o
def bevel(o,w=2,segments=3):
    m=o.modifiers.new('Edge radii','BEVEL'); m.width=w*MM; m.segments=segments
    m.limit_method='ANGLE'
    return o
def weighted(o):
    m=o.modifiers.new('Surface normals','WEIGHTED_NORMAL'); m.keep_sharp=True
    return o
def mesh(name,verts,faces,mat=None,bev=0,smo=False):
    data=bpy.data.meshes.new(name+'_Mesh'); data.from_pydata([V(p) for p in verts],[],faces); data.update()
    bm=bmesh.new(); bm.from_mesh(data); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(data); bm.free()
    o=bpy.data.objects.new(name,data); assign(o,name,mat)
    # Exportable base UVs: dominant-axis planar projection per polygon.
    uv=data.uv_layers.new(name='UVMap')
    for p in data.polygons:
        axis=max(range(3),key=lambda i: abs(p.normal[i])); axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            co=data.vertices[data.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]],co[axes[1]])
    if smo: smooth(o)
    if bev: bevel(o,bev); weighted(o)
    return o
def cube(name,p,size,mat,bev=2):
    bpy.ops.mesh.primitive_cube_add(size=1,location=V(p)); o=assign(bpy.context.object,name,mat); o.scale=V(size)
    select(o); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev: bevel(o,bev); weighted(o)
    return o
def cyl(name,p,r,depth,mat,axis=(0,0,1),n=48,bev=1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r*MM,depth=depth*MM,location=V(p))
    o=assign(bpy.context.object,name,mat); o.rotation_mode='QUATERNION'; o.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
    if bev: bevel(o,bev)
    return smooth(o)
def rod(name,a,b,r,mat,n=24):
    a=Vector(a); b=Vector(b); return cyl(name,(a+b)/2,r,(b-a).length,mat,b-a,n,min(r*.15,1))
def sphere(name,p,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=V(p)); o=assign(bpy.context.object,name,mat); o.scale=V(size)
    select(o); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return smooth(o)
def tube(name,pts,r,mat,cyclic=False,curved=True):
    d=bpy.data.curves.new(name+'_Curve','CURVE'); d.dimensions='3D'; d.resolution_u=12; d.bevel_depth=r*MM; d.bevel_resolution=3
    s=d.splines.new('BEZIER' if curved else 'POLY')
    if curved:
        s.bezier_points.add(len(pts)-1)
        for p,co in zip(s.bezier_points,pts): p.co=V(co); p.handle_left_type=p.handle_right_type='AUTO'
    else:
        s.points.add(len(pts)-1)
        for p,co in zip(s.points,pts): p.co=(*V(co),1)
    s.use_cyclic_u=cyclic
    o=bpy.data.objects.new(name,d); return assign(o,name,mat)
def panel(name,verts,mat,thick=3,bev=3):
    o=mesh(name,verts,[tuple(range(len(verts)))],mat)
    if thick:
        m=o.modifiers.new('Shell thickness','SOLIDIFY'); m.thickness=thick*MM; m.offset=0
    if bev: bevel(o,bev); weighted(o)
    return o
def patch(name,grid,mat,thick=3,sub=1):
    rows=len(grid); cols=len(grid[0]); verts=sum(grid,[])
    faces=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(rows-1) for i in range(cols-1)]
    o=mesh(name,verts,faces,mat,smo=True)
    if sub:
        m=o.modifiers.new('Surface shaping','SUBSURF'); m.levels=sub; m.render_levels=sub
    if thick: m=o.modifiers.new('Shell thickness','SOLIDIFY'); m.thickness=thick*MM
    return o
def loft(name,sections,mat,sub=2,power=.85):
    # (Y, half width, bottom Z, top Z), transverse superellipse sections.
    n=16; verts=[]
    for y,w,z0,z1 in sections:
        for j in range(n):
            a=2*pi*j/n; x=w*math.copysign(abs(cos(a))**power,cos(a)); z=(z0+z1)/2+(z1-z0)/2*math.copysign(abs(sin(a))**power,sin(a))
            verts.append((x,y,z))
    faces=[tuple(reversed(range(n)))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(len(sections)-1) for j in range(n)]+[tuple(range((len(sections)-1)*n,len(sections)*n))]
    o=mesh(name,verts,faces,mat,smo=True)
    if sub: m=o.modifiers.new('Sculpted subdivision','SUBSURF'); m.levels=sub; m.render_levels=sub
    return o
def lathe(name,y,z,profile,mat,segments=128):
    n=len(profile); verts=[(x,y+r*sin(2*pi*j/segments),z+r*cos(2*pi*j/segments)) for j in range(segments) for x,r in profile]
    faces=[(j*n+k,((j+1)%segments)*n+k,((j+1)%segments)*n+(k+1)%n,j*n+(k+1)%n) for j in range(segments) for k in range(n)]
    return mesh(name,verts,faces,mat,smo=True)
def ring(name,p,r,width,mat,axis='X',tube_r=2):
    x,y,z=p
    pts=[(x,y+r*sin(i*2*pi/96),z+r*cos(i*2*pi/96)) if axis=='X' else (x+r*cos(i*2*pi/96),y+r*sin(i*2*pi/96),z) for i in range(96)]
    return tube(name,pts,tube_r,mat,True,False)
def bolt(name,p,r=4,axis=(1,0,0),mat='steel'):
    o=cyl(name,p,r,2.5,mat,axis,n=6,bev=.4)
    return o
def text_obj(name,body,p,size,mat,normal=(1,0,0),right=(0,1,0),font=None,extrude=.15):
    d=bpy.data.curves.new(name+'_Letters','FONT'); d.body=body; d.size=size*MM; d.align_x='CENTER'; d.align_y='CENTER'; d.extrude=extrude*MM; d.bevel_depth=.05*MM
    if font: d.font=font
    o=bpy.data.objects.new(name,d); assign(o,name,mat); o.location=V(p)
    a=Vector(right).normalized(); c=Vector(normal).normalized(); b=c.cross(a).normalized()
    o.rotation_euler=Matrix((a,b,c)).transposed().to_euler()
    return o
def mat(key,name,color,metal=0,rough=.4,coat=0,trans=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    for nm,value in [('Coat Weight',coat),('Coat Roughness',.15),('Transmission Weight',trans),('IOR',1.46)]:
        if nm in p.inputs: p.inputs[nm].default_value=value
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    M[key]=m; return m
def materials():
    mat('blue','MAT_Paint_UserCustom',(.005,.205,.65),.58,.23,.65)
    mat('black','MAT_Plastic_MatteBlack',(.013,.018,.024),0,.39)
    mat('gloss','MAT_Plastic_GlossBlack',(.009,.012,.018),.2,.21,.4)
    mat('gun','MAT_Engine_Graphite',(.06,.069,.078),.7,.35)
    mat('rubber','MAT_Tire_Rubber',(.016,.019,.022),0,.64)
    mat('leather','MAT_Seat_GrainedVinyl',(.022,.026,.032),0,.52)
    mat('steel','MAT_BrakeDisc_Steel',(.38,.43,.48),.85,.27)
    mat('silver','MAT_Aluminium_Brushed',(.48,.54,.59),.82,.31)
    mat('chrome','MAT_Chrome',(.72,.8,.86),.97,.12)
    mat('guard','MAT_GuardBar_Metal',(.032,.037,.043),.6,.4)
    mat('yellow','MAT_Decal_FluoroYellow',(.72,.95,.006),.12,.27)
    mat('white','MAT_Decal_White',(.91,.94,.98),.1,.3)
    mat('plate','MAT_Plate_Metal',(.98,.55,.012),.32,.32)
    mat('ink','MAT_Decal_Black',(.003,.004,.006),0,.4)
    mat('amber','MAT_Indicator_Amber',(.95,.22,.005),.1,.22,.3,0,.5)
    mat('red','MAT_Lamp_Red',(.6,.003,.008),.1,.2,.3,0,1.0)
    mat('glass','MAT_Headlight_Glass',(.91,.98,1),0,.09,.4,.94)
    mat('wind','MAT_Windscreen_PC',(.65,.73,.79),0,.11,.35,.92)
    mat('bronze','MAT_Exhaust_TemperedSteel',(.22,.15,.10),.86,.34)
    mat('lcd','MAT_Dashboard_LCD',(.08,.2,.22),.1,.22,0,0,.15)
    mat('ground','MAT_Studio_Floor',(.16,.19,.23),.05,.39)
    for key,scale,strength,distance in [('rubber',190,.24,.001),('leather',450,.35,.0004),('gun',280,.1,.0004)]:
        m=M[key]; nodes=m.node_tree.nodes; links=m.node_tree.links; p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        noise=nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=scale
        bump=nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=strength; bump.inputs['Distance'].default_value=distance
        links.new(noise.outputs['Fac'],bump.inputs['Height']); links.new(bump.outputs['Normal'],p.inputs['Normal'])

def setup():
    global SC,COL
    for scene in list(bpy.data.scenes):
        if scene.name.startswith('GSX250R_User_Reconstruction'):
            for o in list(scene.objects): bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.scenes.remove(scene)
    for c in list(bpy.data.collections):
        if c.name.startswith('Collection_') and not c.objects: bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.name.startswith('MAT_') and m.users==0: bpy.data.materials.remove(m)
    # New scene avoids deleting unrelated work in the connected Blender session.
    SC=bpy.data.scenes.new('GSX250R_User_Reconstruction'); bpy.context.window.scene=SC
    SC.unit_settings.system='METRIC'; SC.unit_settings.scale_length=1; SC.unit_settings.length_unit='METERS'
    for n in ['Reference','Blockout','Wheels','FrontEnd','Engine','Body','Details','Materials','Lights','Cameras']:
        c=bpy.data.collections.new('Collection_'+n); SC.collection.children.link(c); C[n]=c
    COL=C['Body']; materials()
    SC.render.engine='CYCLES'; SC.cycles.samples=96; SC.cycles.use_denoising=True
    SC.render.resolution_x=1600; SC.render.resolution_y=1100; SC.render.resolution_percentage=100
    SC.render.image_settings.file_format='PNG'; SC.render.image_settings.color_mode='RGBA'
    SC.view_settings.view_transform='AgX'
    SC.world=bpy.data.worlds.new('GSX_Studio_World'); SC.world.use_nodes=True
    next(n for n in SC.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.32,.4,.52,1); next(n for n in SC.world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.35
    SC['source_units']='millimetres converted by 0.001'; SC['coordinate_system']='+X right, +Y forward, +Z up'; SC['accuracy']='Photo-led approximation; no metrology claim'
    for d in ['blends','renders/checks','renders/final','exports','qa','references/local']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    cameras(); lights()

def camera(name,p,target,ortho=None,lens=65):
    d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); C['Cameras'].objects.link(o)
    o.location=V(p); o.rotation_euler=(V(target)-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=lens; d.clip_start=.01
    if ortho: d.type='ORTHO'; d.ortho_scale=ortho*MM
    return o
def cameras():
    camera('Camera_Front_3Q',(2900,3400,1750),(0,0,550),lens=60)
    camera('Camera_Rear_3Q',(2700,-3200,1600),(0,-120,530),lens=60)
    camera('Camera_Left_3Q',(-2900,3300,1700),(0,0,560),lens=60)
    camera('Camera_Right_Ortho',(4500,0,620),(0,0,620),2700)
    camera('Camera_Left_Ortho',(-4500,0,620),(0,0,620),2700)
    camera('Camera_Front_Ortho',(0,4500,560),(0,0,560),1600)
    camera('Camera_Rear_Ortho',(0,-4500,560),(0,0,560),1600)
    camera('Camera_Top_Ortho',(0,0,5000),(0,0,0),2600)
    camera('Camera_Wheel_Detail',(1150,1640,700),(0,715,320),lens=65)
    camera('Camera_Cockpit',(-900,-400,1850),(0,375,920),lens=62)
    camera('Camera_Engine_Detail',(1500,70,690),(0,-50,440),lens=60)
    SC.camera=bpy.data.objects['Camera_Front_3Q']
def lights():
    global COL
    COL=C['Lights']
    for name,p,power,size,color in [('Key',(1600,1600,3000),700,2500,(.87,.94,1)),('Fill',(-1800,500,1600),500,2100,(.7,.82,1)),('Rim',(400,-2200,2500),950,1800,(1,.91,.78)),('Top',(-100,0,3500),600,2000,(1,1,1))]:
        d=bpy.data.lights.new('Light_'+name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size*MM; d.color=color
        o=bpy.data.objects.new('Light_'+name,d); COL.objects.link(o); o.location=V(p); o.rotation_euler=(V((0,0,450))-o.location).to_track_quat('-Z','Y').to_euler()
    cube('Studio_Ground',(0,0,-16),(200000,200000,30),'ground',0)
    COL=C['Body']
def save(stage):
    SC['stage']=stage; bpy.context.view_layer.update(); SC.camera=bpy.data.objects['Camera_Front_3Q']
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blends'/f'{stage}.blend'),compress=True)
    (ROOT/'qa/progress.json').write_text(json.dumps({'stage':stage,'objects':len(SC.objects),'blender':bpy.app.version_string}),encoding='utf-8')

def references():
    global COL
    COL=C['Reference']
    specs={'wheelbase':1430,'length':2085,'width':740,'height':1110,'seat_height':790,'front_tire_outer_radius':303.9,'rear_tire_outer_radius':313.9}
    for name,a,b in [('Wheelbase',(450,-715,314),(450,715,314)),('Length',(500,-1066,50),(500,1019,50)),('SeatHeight',(450,-360,0),(450,-360,790)),('Height',(-480,400,0),(-480,400,1110))]:
        tube('Dimension_'+name,[a,b],1.2,'yellow',curved=False)
        for p in [a,b]: sphere('DimensionPoint_'+name,p,(4,4,4),'yellow')
    # Photos retain their perspective. Side reference approximately scaled using wheel centres.
    for suffix,p,rot,scale in [('_62_97.jpg',(0,0,805),(pi/2,0,pi/2),2550),('_66_97.jpg',(0,0,690),(pi/2,0,pi),1760),('_57_97.jpg',(0,0,705),(pi/2,0,0),1890),('_64_97.jpg',(0,0,740),(pi/2,0,-pi/2),2390)]:
        paths=list((ROOT/'IMG').glob('*'+suffix))
        if not paths: continue
        o=bpy.data.objects.new('Reference_'+suffix[1:3],None); COL.objects.link(o); o.empty_display_type='IMAGE'; o.data=bpy.data.images.load(str(paths[0]),check_existing=True); o.empty_display_size=scale*MM; o.location=V(p); o.rotation_euler=rot; o.color[3]=.4; o.empty_image_depth='BACK'; o.hide_render=True
        o['alignment']='Perspective photograph, approximate axle calibration; not orthographic blueprint'
    SC['dimensions_mm']=json.dumps(specs)
    (ROOT/'references/local/dimensions.json').write_text(json.dumps(specs,indent=2))
    save('01_reference'); C['Reference'].hide_render=True; C['Reference'].hide_viewport=True

def blockout():
    global COL
    COL=C['Blockout']
    for n,y,r,w in [('Front',715,303.9,110),('Rear',-715,313.9,140)]: cyl('Blockout_Wheel_'+n,(0,y,r),r,w,'rubber',(1,0,0),64)
    cube('Blockout_Tank',(0,25,815),(360,570,230),'blue',60)
    cube('Blockout_Engine',(0,-40,455),(350,400,360),'gun',30)
    cube('Blockout_Seat',(0,-415,765),(290,370,50),'leather',25)
    cube('Blockout_Tail',(0,-795,845),(260,390,100),'blue',25)
    cube('Blockout_Fairing',(0,375,590),(430,650,480),'blue',80)
    for s in [-1,1]:
        rod('Blockout_Fork', (s*94,715,304),(s*94,449,890),24,'chrome')
        tube('Blockout_Guard',[(s*180,-230,410),(s*340,80,460),(s*310,275,580)],14,'guard')
    cube('Blockout_PhoneMount',(-160,420,1005),(85,30,165),'black')
    cube('Blockout_LicensePlate',(0,-1040,580),(220,5,140),'plate')
    rod('Blockout_Exhaust',(230,-90,210),(240,-785,495),65,'silver')
    save('02_blockout'); C['Blockout'].hide_render=True; C['Blockout'].hide_viewport=True

def tire(name,y,r,width):
    # True geometric tread recesses across a rounded tire crown, not painted strips.
    profile=[(-width*.47,217),(-width*.51,240),(-width*.5,r-25)]
    for j in range(41):
        u=-1+2*j/40; profile.append((u*width*.47,r-20*abs(u)**2.2))
    profile += [(width*.5,r-25),(width*.51,240),(width*.47,217)]
    n=len(profile); N=480; verts=[]
    for k in range(N):
        a=k*2*pi/N
        for j,(x,rr) in enumerate(profile):
            if 3<=j<=43:
                u=x/(width*.47); phase=(a/(2*pi)*40 + .42*abs(u)+.12*u)%1
                dist=min(phase,1-phase); fade=min(1,(1.1-abs(u))*5)
                rr-=3.2*max(0,1-dist/.072)**.7*fade
            verts.append((x,y+rr*sin(a),r+rr*cos(a)))
    faces=[(k*n+j,((k+1)%N)*n+j,((k+1)%N)*n+(j+1)%n,k*n+(j+1)%n) for k in range(N) for j in range(n)]
    return mesh('Tire_'+name,verts,faces,'rubber',smo=True)
def disc(name,y,z,x,r):
    o=lathe(name,y,z,[(x-2,r*.62),(x-2,r),(x+2,r),(x+2,r*.62)],'steel',160)
    # Combined cutters produce real drilled perforations.
    cutters=[]
    for j in range(36):
        a=2*pi*j/36
        for rr,da in [(r*.91,0),(r*.78,.028)]: cutters.append(cyl('Drill', (x,y+rr*sin(a+da),z+rr*cos(a+da)),3.1,12,'ink',(1,0,0),12,0))
    bpy.ops.object.select_all(action='DESELECT')
    for c in cutters:c.select_set(True)
    bpy.context.view_layer.objects.active=cutters[0]; bpy.ops.object.join(); cutter=bpy.context.object
    select(o); mod=o.modifiers.new('Drilled rotor','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name); bpy.data.objects.remove(cutter,do_unlink=True)
    for j in range(6):
        a=j*pi/3; rod(name+'_Carrier', (x,y+38*sin(a),z+38*cos(a)),(x,y+r*.71*sin(a+.12),z+r*.71*cos(a+.12)),7,'gun')
        bolt(name+'_Button',(x+3,y+r*.64*sin(a),z+r*.64*cos(a)),5)
    return o
def wheels():
    global COL
    COL=C['Wheels']
    for name,y,r,w,disc_r,disc_x in [('Front',715,303.9,110,145,-65),('Rear',-715,313.9,140,120,83)]:
        tire(name,y,r,w)
        half=w*.36
        lathe('Wheel_'+name,y,r,[(-half,202),(-half,216),(-half+5,221),(-half+8,212),(half-8,212),(half-5,221),(half,216),(half,202)],'gloss')
        cyl('Hub_'+name,(0,y,r),35,w*.73,'gun',(1,0,0))
        cyl('Axle_'+name,(0,y,r),10,w+94,'steel',(1,0,0))
        for side in [-1,1]:
            bolt('AxleNut_'+name,(side*(w/2+45),y,r),12,(side,0,0))
            for k in range(4):
                pts=[(side*(half+1),y+216*sin(a),r+216*cos(a)) for a in [(k*90+8+j*74/48)*pi/180 for j in range(49)]]
                tube('RimTape_'+name,pts,2.7,'yellow',curved=False)
        for k in range(10):
            a=k*2*pi/10
            # Paired slender cast spokes have a swept edge at the rim.
            yy=y+128*sin(a+.035); zz=r+128*cos(a+.035)
            a0=Vector((0,y+31*sin(a-.13),r+31*cos(a-.13))); a1=Vector((0,y+207*sin(a+.075),r+207*cos(a+.075)))
            o=cube('Spoke_'+name+f'_{k:02}',(a0+a1)/2,(half*1.15,16,(a1-a0).length),'gloss',3)
            o.rotation_euler=(a1-a0).to_track_quat('Z','Y').to_euler()
        cyl('Valve_'+name,(half,y+192,r),3.5,22,'rubber',(0,1,0),16)
        disc('BrakeDisc_'+name,y,r,disc_x,disc_r)
        cal=cube('Caliper_'+name,(disc_x, y-106 if name=='Front' else y+94,r+70),(41,65,90),'gun',12)
        for zz in [-22,22]: bolt('CaliperBolt_'+name,(disc_x+24,y-106 if name=='Front' else y+94,r+70+zz),5)
        for i in range(48):
            a=i*2*pi/48
            o=cube('ABS_Tooth_'+name,(disc_x*.72,y+76*sin(a),r+76*cos(a)),(2,6,8),'steel',.3); o.rotation_euler.x=-a
        lathe('ABS_Ring_'+name,y,r,[(disc_x*.72-1,63),(disc_x*.72-1,70),(disc_x*.72+1,70),(disc_x*.72+1,63)],'steel',96)
    save('03_wheels')

def front_end():
    global COL
    COL=C['FrontEnd']
    for s in [-1,1]:
        label='L' if s<0 else 'R'
        a=(s*92,715,304); b=(s*92,581,610); c=(s*92,454,892)
        rod('Fork_Lower_'+label,a,b,22,'gloss'); rod('Fork_Stanchion_'+label,b,c,18.5,'chrome')
        rod('Fork_DustSeal_'+label,(s*92,581,610),(s*92,591,588),25,'rubber')
        cyl('Fork_Cap_'+label,c,21,8,'silver',(0,-.41,.91))
        cyl('Fork_Reflector_'+label,(s*119,628,528),22,5,'amber',(s,0,0))
        tube('Handlebar_'+label,[(s*88,451,886),(s*155,390,910),(s*290,353,913)],12,'gloss')
        rod('Grip_'+label,(s*215,376,913),(s*330,339,913),16,'rubber')
        for j in range(18):
            p=(s*(220+j*5.6),374-j*1.8,913); cyl('Grip_Rib_'+label,p,16.5,1.2,'rubber',(s,-.32,0),24,.2)
        rod('BarEnd_'+label,(s*328,339,913),(s*349,332,913),17,'gun')
        cube('SwitchHousing_'+label,(s*205,378,915),(42,43,48),'black',7)
        cube('KillSwitch_'+label,(s*216,370,943),(13,16,8),'red',2)
        tube('Lever_'+label,[(s*186,402,926),(s*233,416,926),(s*293,387,921),(s*346,365,918)],5,'silver')
        sphere('Lever_End_'+label,(s*346,365,918),(7,7,7),'silver')
        tube('Mirror_Stem_'+label,[(s*175,623,903),(s*235,638,966),(s*290,648,1028)],9,'gloss')
        o=sphere('Mirror_'+label,(s*306,655,1060),(63,22,42),'black'); o.rotation_euler.y=s*.25
        o=sphere('Mirror_Glass_'+label,(s*306,638,1060),(55,5,34),'chrome'); o.rotation_euler.y=s*.25
        cube('Mirror_Foot_'+label,(s*175,623,903),(48,46,16),'black',6)
        for yy in [-14,14]:bolt('MirrorMountBolt',(s*175,623+yy,915),5,(0,0,1))
    cube('TripleClamp_Upper',(0,456,870),(250,83,25),'gun',12)
    cube('TripleClamp_Lower',(0,538,686),(244,75,32),'gun',10)
    cyl('SteeringStem_Nut',(0,447,890),15,10,'chrome',n=6)
    cube('BrakeReservoir',(171,436,952),(61,45,33),'black',4)
    for x in [151,191]:bolt('Reservoir_Screw',(x,436,970),3,(0,0,1))
    dash=cube('Dashboard',(0,558,967),(188,37,115),'black',24); dash.rotation_euler.x=math.radians(23)
    screen=cube('Dashboard_Glass',(0,535,971),(153,4,80),'lcd',15); screen.rotation_euler.x=math.radians(23)
    text_obj('Dashboard_Readout','0',(5,530,974),41,'white',(0,-1,.42),(1,0,0))
    text_obj('Dashboard_Label','SUZUKI',(0,528,1006),7,'white',(0,-1,.42),(1,0,0))
    text_obj('Dashboard_Gear','N',(-56,531,981),17,'yellow',(0,-1,.42),(1,0,0))
    cyl('Ignition',(0,485,913),24,10,'black',(0,-.3,1)); cube('KeySlot',(0,483,920),(4,16,2),'silver',1)
    # Left-hand four-corner clamping phone holder and ball-joint mount, photo 65.
    tube('PhoneMount_Arm',[(-143,409,905),(-157,419,961),(-168,438,989)],9,'black')
    sphere('PhoneMount_Ball',(-157,419,961),(15,15,15),'black')
    o=cube('PhoneMount',(-168,426,1030),(78,20,142),'black',13); o.rotation_euler.x=.23
    cube('PhoneMount_Pad',(-168,413,1030),(62,6,111),'rubber',10)
    for sx in [-1,1]:
        for sz in [-1,1]:
            x=-168+sx*39; z=1030+sz*60
            tube('PhoneMount_Jaw',[(x-sx*9,426,z-sz*7),(x,406,z),(x-sx*8,399,z)],5,'rubber')
    cyl('PhoneMount_Adjuster',(-218,423,1030),10,15,'black',(1,0,0),24)
    rod('SteeringDamper_Body',(-104,363,907),(65,363,907),12,'gun')
    rod('SteeringDamper_Rod',(65,363,907),(154,363,907),4,'bronze')
    for x in [-68,142]:cyl('SteeringDamper_Clamp',(x,363,907),17,12,'gloss',(1,0,0))
    # Curved front fender follows the tire and wraps the shoulders.
    grid=[]
    for a in [-.68,-.62,-.4,-.1,.2,.48,.72,.88,.93]:
        row=[]
        for t in [-1,-.94,-.68,0,.68,.94,1]:
            rr=325-13*abs(t)**2; row.append((t*81,715+rr*sin(a),304+rr*cos(a)))
        grid.append(row)
    patch('Fender_Front',grid,'blue',3,2)
    for s in [-1,1]:
        panel('Fender_Mount',[(s*82,585,560),(s*82,680,613),(s*74,741,570),(s*74,630,490)],'blue',4,5)
        for y,z in [(622,552),(685,578)]:bolt('Fender_Bolt',(s*84,y,z),4,(s,0,0))
    save('04_front_end')

def mechanical():
    global COL
    COL=C['Engine']
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        tube('Frame_Main_'+lab,[(s*75,452,791),(s*155,224,716),(s*159,-160,557),(s*115,-265,390)],17,'gloss')
        tube('Frame_Cradle_'+lab,[(s*117,268,629),(s*145,244,341),(s*142,50,269),(s*113,-233,358)],14,'gloss')
        tube('Frame_Subframe_'+lab,[(s*133,-226,570),(s*108,-631,758),(s*74,-911,841)],14,'gloss')
        tube('Frame_SeatRail_'+lab,[(s*134,-199,698),(s*147,-500,734),(s*85,-882,836)],14,'gloss')
        cube('Swingarm_'+lab,(s*114,-490,329),(49,536,67),'gun',6)
        cyl('Swingarm_Pivot_'+lab,(s*142,-221,350),23,16,'steel',(s,0,0))
        cube('AxleAdjuster_'+lab,(s*141,-715,321),(13,60,31),'silver',3)
        rod('AxleAdjuster_Screw_'+lab,(s*136,-739,331),(s*136,-779,331),4,'steel')
        panel('Rearset_'+lab,[(s*176,-215,462),(s*181,-322,417),(s*190,-237,331),(s*193,-136,359)],'silver',12,6)
        rod('Footpeg_'+lab,(s*181,-245,360),(s*275,-245,360),12,'gun')
        for j in range(9):cyl('Footpeg_Ridge_'+lab,(s*(201+j*8),-245,360),12.5,2,'rubber',(1,0,0),16,.2)
        rod('PassengerPeg_'+lab,(s*110,-590,631),(s*212,-610,608),11,'silver')
        tube('PassengerPegHanger_'+lab,[(s*104,-510,738),(s*146,-592,634),(s*114,-704,759)],10,'gloss')
    cube('Swingarm_Brace',(0,-413,338),(246,70,50),'gun',5)
    cube('Engine_Crankcase',(0,-27,424),(285,335,223),'gun',40)
    for s in [-1,1]:
        lab='L' if s<0 else 'R'; rr=101 if s>0 else 88
        cyl('Engine_ClutchCover' if s>0 else 'Engine_AlternatorCover',(s*159,-69,410),rr,31,'gun',(s,0,0),64,6)
        cyl('Engine_CoverInset_'+lab,(s*177,-69,410),rr-13,4,'gun',(s,0,0),64,2)
        for j in range(10):
            a=j*2*pi/10; bolt('Crankcase_Bolt_'+lab,(s*178,-69+(rr-4)*sin(a),410+(rr-4)*cos(a)),4,(s,0,0))
    cube('Engine_Cylinders',(0,94,563),(250,193,136),'gun',14)
    cube('Engine_CylinderHead',(0,104,649),(287,213,74),'silver',15)
    cube('Engine_HeadCover',(0,108,692),(289,212,33),'gun',14)
    for k in range(5):cube('Cylinder_CastingRib',(0,96,518+k*23),(259,204,5),'gun',2)
    for s in [-1,1]:
        for y in [36,168]:bolt('HeadBolt',(s*142,y,665),5,(s,0,0))
    cube('Airbox',(0,-41,700),(246,213,106),'black',15)
    rad=cube('Radiator',(0,330,557),(326,47,234),'gun',9); rad.rotation_euler.x=.12
    for j in range(30): cube('Radiator_Fin',(0,358,458+j*6.6),(291,3,2),'steel',0)
    for x in range(-140,141,20):cube('Radiator_Core',(x,359,557),(2,4,197),'gun',0)
    for s in [-1,1]:tube('CoolantHose',[(s*146,323,637),(s*156,220,650),(s*136,145,605)],12,'rubber')
    for x in [-64,64]:
        tube('Exhaust_Header',[(x,199,630),(x,262,578),(x,276,401),(x,184,222),(x,-42,203)],19,'bronze')
        cyl('Exhaust_Flange',(x,206,630),28,8,'gun',(0,1,0))
    tube('Exhaust_Collector',[(0,10,202),(80,-137,197),(194,-291,237),(237,-403,294)],26,'bronze')
    # Faceted oval muffler, tapering towards rear, with a separate brushed shield.
    a=Vector((242,-340,278)); b=Vector((251,-819,496)); axis=(b-a).normalized(); u=Vector((1,0,0)); v=axis.cross(u).normalized()
    def exhaust_shell(name,radii,mat):
        verts=[]; n=12
        for t,rx,rz in radii:
            cen=a+(b-a)*t
            for k in range(n):verts.append(cen+u*cos(2*pi*k/n)*rx+v*sin(2*pi*k/n)*rz)
        faces=[tuple(reversed(range(n)))]+[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(radii)-1) for k in range(n)]+[tuple(range((len(radii)-1)*n,len(radii)*n))]
        return mesh(name,verts,faces,mat,3,True)
    exhaust_shell('Exhaust_Muffler',[(0,32,36),(.12,61,69),(.78,68,82),(1,56,67)],'gun')
    exhaust_shell('Exhaust_EndCap',[(.91,62,73),(1.015,55,64)],'silver')
    cyl('Exhaust_Outlet',b+axis*10,24,15,'ink',axis,48,2)
    panel('Exhaust_HeatShield',[(306,-344,287),(313,-403,338),(324,-749,538),(312,-827,521),(291,-756,411),(291,-435,268)],'silver',5,12)
    for y,z in [(-439,327),(-747,479)]:bolt('HeatShieldBolt',(322,y,z),5)
    rod('OxygenSensor',(22,236,325),(52,249,337),6,'steel')
    tube('OxygenSensorWire',[(52,249,337),(96,252,389),(132,218,451)],2,'black')
    rod('Shock_Piston',(0,-392,374),(0,-269,665),12,'chrome')
    rod('Shock_Body',(0,-307,586),(0,-264,682),25,'gun')
    start=Vector((0,-381,402)); end=Vector((0,-290,618)); axis=(end-start).normalized(); u=Vector((1,0,0)); v=axis.cross(u)
    pts=[start+(end-start)*i/210+u*31*cos(i/210*2*pi*10)+v*31*sin(i/210*2*pi*10) for i in range(211)]
    tube('RearShock_Spring',pts,5,'white',False,False)
    # Rear sprocket and full roller chain run on vehicle left.
    y=-715; z=313.9; x=-88
    lathe('Sprocket_Rear',y,z,[(x-3,35),(x-3,104),(x+3,104),(x+3,35)],'steel',100)
    for j in range(46):
        a=j*2*pi/46; o=cube('Sprocket_Tooth',(x,y+107*sin(a),z+107*cos(a)),(6,6,10),'steel',1); o.rotation_euler.x=-a
    for j in range(6):
        a=j*pi/3;bolt('Sprocket_Bolt',(x-6,y+57*sin(a),z+57*cos(a)),6,(-1,0,0))
    cyl('Sprocket_Front',(-90,-225,370),38,10,'gun',(1,0,0))
    pts=[]
    for j in range(34):
        a=pi/2+j*pi/33; pts.append(Vector((-101,-715+110*cos(a),313.9+110*sin(a))))
    for j in range(1,40):pts.append(Vector((-101,-715+490*j/40,203.9+(370-40-203.9)*j/40)))
    for j in range(17):
        a=-pi/2+j*pi/16;pts.append(Vector((-101,-225+40*cos(a),370+40*sin(a))))
    for j in range(1,40):pts.append(Vector((-101,-225-490*j/40,410+(423.9-410)*j/40)))
    tube('Chain',pts,5,'gun',True,False)
    for j,p in enumerate(pts):
        nxt=pts[(j+1)%len(pts)]; o=cube('Chain_Link',p,(4,15,9),'steel',2); o.rotation_euler.x=math.atan2(nxt.z-p.z,nxt.y-p.y)
        cyl('Chain_Roller',p,3.8,16,'gun',(1,0,0),12,.2)
    cube('ChainGuard',(-102,-550,464),(40,411,14),'black',5)
    tube('SideStand',[(-131,-242,340),(-205,-347,144),(-261,-395,16)],12,'gun')
    cube('SideStand_Foot',(-265,-400,10),(70,65,13),'gun',8)
    tube('SideStand_Spring',[(-159,-265,308),(-183,-300,202)],5,'steel',False,False)
    save('05_engine_frame_exhaust')

def bodywork():
    global COL
    COL=C['Body']
    loft('Body_Tank',[(-324,65,750,784),(-306,100,721,818),(-250,141,708,867),(-110,181,711,938),(40,184,730,960),(183,155,752,946),(289,113,779,888),(321,83,803,845)],'blue',2,.77)
    loft('Seat_Rider',[(-611,129,774,807),(-583,143,751,791),(-458,148,754,790),(-350,117,765,795),(-311,88,771,806)],'leather',2,.58)
    loft('Seat_Pillion',[(-943,57,867,902),(-912,90,863,913),(-810,122,836,910),(-658,132,803,875),(-634,118,800,851)],'leather',2,.6)
    loft('Body_Tail',[(-987,37,860,887),(-947,71,824,882),(-813,136,780,871),(-646,151,746,823),(-571,128,739,782)],'blue',2,.64)
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        def pp(name,points,mat='blue',th=3,bev=5):return panel(name+'_'+lab,[(s*x,y,z) for x,y,z in points],mat,th,bev)
        pp('Body_SeatSide',[(143,-588,748),(159,-356,763),(176,-196,769),(205,-50,710),(180,-141,640),(147,-364,622)],'blue')
        pp('Body_FrameCover',[(145,-358,617),(181,-137,645),(179,17,671),(170,-15,531),(148,-223,471)],'black')
        pp('Body_TankTrim',[(178,-213,775),(210,13,802),(225,228,807),(219,377,766),(199,238,713),(194,47,692)],'gun')
        # Upper cowling wrapping cockpit into a sharp nose.
        grid=[[(s*119,391,911),(s*166,554,936),(s*164,682,898),(s*119,827,823)],[(s*200,373,840),(s*227,545,858),(s*216,706,812),(s*124,898,718)],[(s*218,341,777),(s*246,544,797),(s*239,731,731),(s*114,886,678)]]
        patch('Body_UpperCowling_'+lab,grid,'blue',3,1)
        pp('Cockpit_Inner',[(102,378,891),(152,481,924),(183,576,922),(206,453,834),(195,324,808),(173,283,818)],'black',4,4)
        # Main side fairing perimeter: upper graphic blade, forward shin, lower keel.
        pp('Body_SideFairing',[(199,-165,642),(226,56,721),(247,305,737),(257,533,784),(260,728,733),(240,810,662),(220,532,576),(192,381,376),(155,306,222),(139,415,205),(198,519,384),(244,664,654),(217,265,671),(188,-121,572)],'blue',4,7)
        pp('Body_FairingForward',[(258,529,759),(244,737,713),(231,782,659),(213,527,541),(174,409,257),(144,315,226),(189,401,477),(211,453,665)],'blue',4,7)
        pp('Body_BellyPan',[(141,-259,206),(158,-160,228),(158,156,260),(166,333,222),(140,417,203),(121,245,169),(117,-192,170)],'blue',4,4)
        pp('Body_BellyGraphic',[(161,-237,209),(164,-145,221),(171,154,250),(167,313,220),(125,233,179),(122,-179,183)],'white',.5,0)
        pp('SideVent',[(215,91,697),(220,276,698),(230,423,667),(214,339,632),(209,207,659)],'ink',3,2)
        for k in range(3):tube('VentFin_'+lab,[(s*218,154+k*55,662),(s*239,231+k*55,679)],2,'gun')
        for y,z,x in [(-144,617,201),(69,715,227),(549,777,259),(514,397,200),(-191,205,167),(-415,735,153)]:bolt('Fairing_Bolt_'+lab,(s*(x+3),y,z),4,(s,0,0))
        # Amber stalk indicators, clear aerodynamic housings.
        rod('IndicatorStem_Front_'+lab,(s*228,715,797),(s*270,716,798),7,'rubber')
        sphere('Indicator_Front_'+lab,(s*283,718,800),(34,17,18),'glass')
        sphere('IndicatorBulb_Front_'+lab,(s*283,719,800),(23,11,11),'amber')
    # Central angular halogen headlamp and its triangular black bezel.
    bezel=[(-119,869,841),(0,904,858),(119,869,841),(154,884,775),(117,935,685),(0,952,654),(-117,935,685),(-154,884,775)]
    panel('Headlight_Bezel',bezel,'gloss',14,6)
    lens=[(-81,896,836),(0,924,844),(81,896,836),(109,917,778),(68,952,708),(0,961,693),(-68,952,708),(-109,917,778)]
    panel('Headlight_Reflector',[(x,y+1,z) for x,y,z in lens],'chrome',4,3)
    # Reflector flutes capture the real headlamp's vertical faceting.
    for k in range(-7,8):
        x=k*11; z0=704+abs(x)*.38; tube('Headlight_Flute',[(x,954-abs(x)*.26,z0),(x,940-abs(x)*.2,772),(x,923-abs(x)*.23,831)],1,'silver')
    cyl('Headlight_Bulb',(0,945,770),23,19,'chrome',(0,1,0)); sphere('Headlight_BulbLens',(0,956,770),(16,8,16),'glass')
    panel('Headlight',[(x*1.015,y+9,z) for x,y,z in lens],'glass',2,4)
    for s in [-1,1]:
        panel('PositionLamp',[(s*88,901,833),(s*196,816,860),(s*149,872,781)],'chrome',3,2)
    # Windscreen with width changes and cylindrical transverse curvature.
    grid=[]
    for y,z,w in [(846,839,70),(821,868,99),(747,955,132),(650,1072,136),(641,1085,135)]:
        grid.append([(w*t,y-35*t*t,z+10*t*t) for t in [-1,-.94,-.5,0,.5,.94,1]])
    patch('Windscreen',grid,'wind',3,2)
    for s in [-1,1]:
        for y,z,x in [(813,875,93),(755,946,119)]:bolt('Windscreen_Fastener',(s*x,y-15,z),5,(0,1,.5))
    cyl('FuelCap_Ring',(0,121,950),63,6,'silver')
    cyl('FuelCap',(0,121,955),48,5,'gloss')
    cube('FuelCap_Latch',(0,101,959),(35,39,4),'gun',4)
    for j in range(6):
        a=j*pi/3;bolt('FuelCap_Bolt',(55*cos(a),121+55*sin(a),955),3.5,(0,0,1))
    # Rear lamp, mudguard, turn indicators and local-only number plate.
    panel('Taillight',[(0,-1002,817),(-48,-968,880),(48,-968,880)],'red',12,7)
    tube('Taillight_LED',[(-36,-979,866),(-21,-1003,832),(0,-1009,824),(21,-1003,832),(36,-979,866)],4,'red')
    panel('Fender_Rear', [(-58,-885,808),(58,-885,808),(64,-1034,665),(47,-1024,622),(-47,-1024,622),(-64,-1034,665)],'black',7,7)
    cube('Rear_Reflector',(0,-1040,697),(91,13,33),'red',4)
    for s in [-1,1]:
        rod('IndicatorStem_Rear',(s*54,-960,758),(s*133,-963,758),8,'rubber')
        sphere('Indicator_Rear',(s*148,-965,758),(32,17,18),'glass'); sphere('IndicatorBulb_Rear',(s*148,-967,758),(23,12,11),'amber')
    o=cube('LicensePlate',(0,-1039,587),(220,4,140),'plate',5); o.rotation_euler.x=-.16
    tube('LicensePlate_Rim',[(-104,-1054,522),(104,-1054,522),(105,-1032,652),(-105,-1032,652)],1.4,'ink',True,False)
    font=None
    for fp in ['C:/Windows/Fonts/msyh.ttc','C:/Windows/Fonts/simhei.ttf']:
        if Path(fp).exists():font=bpy.data.fonts.load(fp);break
    text_obj('LicensePlate_Region',PRIVATE['plate_top'],(0,-1040,620),49,'ink',(0,-1,.16),(1,0,0),font)
    text_obj('LicensePlate_Number',PRIVATE['plate_bottom'],(0,-1050,555),57,'ink',(0,-1,.16),(1,0,0))
    for s in [-1,1]:bolt('LicensePlate_Bolt',(s*90,-1034,643),7,(0,-1,.16),'chrome')
    save('06_body')

def details():
    global COL
    COL=C['Details']
    for s in [-1,1]:
        lab='L' if s<0 else 'R'; right=(0,s,0)
        # Three mounting zones and symmetrical 25 mm tube guard cage, photo 62/63.
        tube('GuardBar_'+lab,[(s*182,-209,437),(s*290,-96,526),(s*336,163,602),(s*321,244,606),(s*295,161,438),(s*244,32,428),(s*182,-209,437)],12.5,'guard')
        tube('GuardBar_Brace_'+lab,[(s*183,234,498),(s*307,218,498),(s*321,244,606)],12.5,'guard')
        tube('GuardBar_LowerBrace_'+lab,[(s*181,-15,368),(s*247,44,411),(s*307,218,498)],12.5,'guard')
        for y,z,x in [(-209,437,184),(234,498,184),(-15,368,182)]:
            cube('GuardBar_Mount_'+lab,(s*x,y,z),(10,40,35),'guard',4);bolt('GuardBar_MountBolt_'+lab,(s*(x+8),y,z),7,(s,0,0))
        cyl('GuardBar_Slider_'+lab,(s*337,238,605),21,27,'rubber',(s,0,0)); cyl('GuardBar_SliderCap_'+lab,(s*353,238,605),17,5,'gun',(s,0,0))
        # White livery is authored geometry; no reference photos become final textures.
        # Side reading direction differs physically on opposite vehicle sides.
        def side_decal(name,points,key='white'):
            return panel(name+'_'+lab,[(s*x,y,z) for x,y,z in points],key,.35,0)
        side_decal('Tank_WhiteFlash',[(171,-165,834),(184,-44,814),(180,22,835),(168,-80,870)])
        side_decal('Tank_YellowFlash',[(184,-19,820),(186,83,837),(178,27,837)],'yellow')
        # Bold letter fragments follow the separated fairing blades, as in the photos.
        t=text_obj('Decal_Side_SUZUKI_'+lab,'UKI' if s>0 else 'SU',(s*247,268,688),145,'white',(s,0,0),right); t.data.shear=.18
        t=text_obj('Decal_Seat_SUZUKI_'+lab,'SU' if s>0 else 'ZU',(s*174,-342,707),115,'white',(s,0,0),right); t.data.shear=.15
        text_obj('Decal_Tail_'+lab,'SUZUKI',(s*141,-735,812),36,'white',(s,0,0),right)
        text_obj('Decal_Belly_'+lab,'SUZUKI',(s*171,34,211),25,'ink',(s,0,0),right)
        text_obj('Decal_Model_'+lab,'GSX250R',(s*256,565,754),22,'white',(s,0,0),right)
        text_obj('Decal_TankBadge_'+lab,'S',(s*218,165,763),35,'chrome',(s,0,0),right)
        o=cube('Decal_MotulBase_'+lab,(s*264,498,683),(1,76,23),'red',.5)
        text_obj('Decal_Motul_'+lab,'MOTUL',(s*265,498,683),17,'white',(s,0,0),right)
        # Yellow eye-shaped patches visible on the owner's front photographs.
        side_decal('Nose_YellowAccent',[(237,705,811),(242,730,757),(225,779,765),(230,737,792)],'yellow')
        tube('BrakeHose_'+lab,[(s*94,574,646),(s*138,607,555),(s*91,638,448),(s*68,609,373)],3,'rubber')
        tube('ControlCable_'+lab,[(s*203,385,933),(s*180,469,945),(s*98,476,812),(s*144,229,695)],3,'rubber')
        for y,z in [(-315,454),(-224,373)]:bolt('Rearset_Bolt',(s*199,y,z),6,(s,0,0))
    text_obj('Decal_Windscreen','SUZUKI',(0,833,879),18,'white',(0,1,.72),(-1,0,0))
    text_obj('Decal_Engine','SUZUKI',(181,-69,410),19,'gun',(1,0,0),(0,1,0))
    text_obj('Tire_Marking_Front','110/80 - 17',(56,715,554),12,'gun',(1,0,0),(0,1,0))
    text_obj('Tire_Marking_Rear','140/70 - 17',(71,-715,574),12,'gun',(1,0,0),(0,1,0))
    save('07_details_decals')
    save('08_materials')

def finalize_source():
    # The reference and blockout remain in earlier stage files, not in final deliverables.
    for key in ['Reference','Blockout']:
        for o in list(C[key].objects):bpy.data.objects.remove(o,do_unlink=True)
    SC.render.resolution_x=3840;SC.render.resolution_y=2160;SC.cycles.samples=128
    save('09_lighting_render')
    SC['private_output']='Contains owner registration; local use only, excluded from Git'
    save('10_final')

def main():
    setup();references();blockout();wheels();front_end();mechanical();bodywork();details();finalize_source()
    return {'stage':SC['stage'],'objects':len(SC.objects),'filepath':bpy.data.filepath,'blender':bpy.app.version_string}

if __name__=='__main__':
    print(json.dumps(main(),ensure_ascii=False))
