"""Stage C mechanical rebuild for the GSX250R gray scene.

This module is intentionally an integration step: ``apply(scene)`` edits an
already-built Blender scene and never saves it.  Coordinates are millimetres
at the API boundary and metres in Blender, matching build_motorcycle.py.
It only owns exposed mechanical parts; body, seat, camera and control-cage
objects are outside its removal and creation lists.
"""
import math
from math import sin, cos, pi
import bpy,bmesh
from mathutils import Vector

MM = .001
_COL = None
_MAT = {}

REMOVE_PREFIXES = (
    'Spoke_', 'BrakeDisc_', 'Caliper_', 'RotorCarrier_', 'ABS_',
    'Engine_ClutchCover', 'Engine_AlternatorCover', 'Engine_CoverInset_', 'Crankcase_Bolt_',
    'Exhaust_HeatShield', 'Engine_BoltBoss_',
)

def _v(p): return Vector(p) * MM

def _collection(scene, name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); scene.collection.children.link(c)
    return c

def _materials():
    global _MAT
    s=bpy.context.scene
    sources={'black':'Body_TankSideTrim','gloss':'Wheel_Front','gun':'Engine_Crankcase','rubber':'Tire_Front','steel':'BrakeDisc_Front','silver':'Exhaust_HeatShield','chrome':'FuelCap','bronze':'Exhaust_Muffler','white':'Seat_Rider'}
    _MAT={k:s.objects[n].data.materials[0] for k,n in sources.items()}

def _link(o, name, mat=None):
    o.name = name
    for c in list(o.users_collection): c.objects.unlink(o)
    _COL.objects.link(o)
    if mat and hasattr(o.data, 'materials'):
        o.data.materials.append(_MAT[mat])
    o['stage_c_owner'] = 'rebuild_mechanics_stage_c'
    o['units'] = 'millimetres_input_metres_scene'
    return o

def _mat(name, kind):
    if hasattr(name, 'data'): return _link(name, name.name, kind)

def _smooth(o):
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
    return o

def _bevel(o, width=1.5):
    if width:
        m=o.modifiers.new('StageC_edge_radius','BEVEL'); m.width=width*MM; m.segments=2
    return o

def _mesh(name, verts, faces, mat, bevel=0, smooth=False):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata([_v(x) for x in verts], [], faces); me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name, me); _link(o,name,mat)
    if smooth: _smooth(o)
    if bevel: _bevel(o,bevel)
    return o

def _cube(name, p, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=_v(p)); o=_link(bpy.context.object,name,mat)
    o.scale=_v(size); bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.select_set(False)
    return _bevel(o,bevel)

def _cyl(name, p, radius, depth, mat, axis=(0,0,1), n=48, bevel=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=radius*MM, depth=depth*MM, location=_v(p))
    o=_link(bpy.context.object,name,mat); o.rotation_mode='QUATERNION'; o.rotation_quaternion=Vector(axis).to_track_quat('Z','Y')
    return _smooth(_bevel(o,bevel))

def _rod(name, a, b, r, mat):
    a,b=Vector(a),Vector(b); return _cyl(name,(a+b)/2,r,(b-a).length,mat,b-a,24,min(r*.12,1.2))

def _tube(name, points, r, mat, cyclic=False):
    d=bpy.data.curves.new(name+'_Curve','CURVE'); d.dimensions='3D'; d.resolution_u=8; d.bevel_depth=r*MM; d.bevel_resolution=2
    s=d.splines.new('POLY'); s.points.add(len(points)-1)
    for q,p in zip(s.points,points): q.co=(*_v(p),1)
    s.use_cyclic_u=cyclic; o=bpy.data.objects.new(name,d); return _link(o,name,mat)

def _remove_old(scene):
    for o in list(scene.objects):
        if any(o.name.startswith(p) for p in REMOVE_PREFIXES): bpy.data.objects.remove(o, do_unlink=True)

def _wheel(name,y,r,width,disc_x,disc_r):
    start={o.name for o in bpy.context.scene.objects}
    half=42 if name=='Front' else 55
    for k in range(10):
        vs=[]
        for rr,da,wide,depth in [(31,-.17,15,half*.48),(75,-.08,13,half*.43),(125,0,11,half*.38),(170,.06,10,half*.35),(216,.09,9,half*.32)]:
            a=k*math.tau/10+da
            for j in range(8):
                q=j*math.tau/8;xx=depth*cos(q);du=wide*.5*sin(q)
                vs.append((xx,y+rr*sin(a)+du*cos(a),r+rr*cos(a)-du*sin(a)))
        fs=[tuple(reversed(range(8))),tuple(range(32,40))]+[(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(4) for i in range(8)]
        _mesh('Spoke_'+name+f'_{k:02}',vs,fs,'gloss',.4,True)
    disc=_lathe('BrakeDisc_'+name,y,r,[(disc_x-2,disc_r*.62),(disc_x-2,disc_r),(disc_x+2,disc_r),(disc_x+2,disc_r*.62)],'steel',192)
    cutters=[];count=18 if name=='Front' else 15
    for j in range(count):
        for q,rr in [(0,disc_r*.91),(.42,disc_r*.78)]:
            a=(j+q)*math.tau/count;cutters.append(_cyl('C_tmp',(disc_x,y+rr*sin(a),r+rr*cos(a)),3.5,14,'black',(1,0,0),16,0))
    _cut(disc,cutters,'Ventilation_through_holes')
    disc['hole_layout_status']='family-photo pattern approximation; exact count unverified'
    # Cast carrier has open sectors and physical attachment to the disc annulus.
    _lathe('RotorCarrier_'+name,y,r,[(disc_x-2,25),(disc_x-2,41),(disc_x+2,41),(disc_x+2,25)],'gun',96)
    for j in range(6):
        a=j*math.tau/6;poly=[]
        for rr,ang in [(33,a-.16),(disc_r*.68,a-.10),(disc_r*.68,a+.10),(33,a+.16)]:poly.append((disc_x,y+rr*sin(ang),r+rr*cos(ang)))
        _solid_plate('RotorCarrier_'+name+f'_Arm_{j}',poly,4,'gun')
        _cyl('RotorCarrier_'+name+f'_Bolt_{j}',(disc_x-4,y+disc_r*.65*sin(a),r+disc_r*.65*cos(a)),4.5,4,'steel',(1,0,0),6,.4)
    cy=y-105;cz=r+72
    _cube('Caliper_'+name,(disc_x-14,cy,cz),(27,51,88),'gun',6)
    _cube('Caliper_'+name+'_Outboard',(disc_x+15,cy,cz),(17,48,82),'gun',5)
    for zz in [-30,30]:
        _cube('Caliper_'+name+'_Bridge',(disc_x,cy,cz+zz),(44,43,10),'gun',3)
        _cyl('Caliper_'+name+'_PistonBoss',(disc_x-29,cy,cz+zz*.60),16,9,'gun',(1,0,0),32,1.2)
    _cyl('Caliper_'+name+'_BleedNipple',(disc_x-20,cy,cz+51),3,9,'steel',(0,0,1),6,.4)
    ax=disc_x*.72;absring=_lathe('ABS_Ring_'+name,y,r,[(ax-1,63),(ax-1,75),(ax+1,75),(ax+1,63)],'steel',144)
    cutters=[]
    for j in range(48):
        a=j*math.tau/48;cc=_cube('C_tmp',(ax,y+69*sin(a),r+69*cos(a)),(10,2.4,7),'black',0);cc.rotation_euler.x=-a;cutters.append(cc)
    _cut(absring,cutters,'ABS_radial_slots')
    a=math.radians(34);_rod('Valve_'+name,(0,y+204*sin(a),r+204*cos(a)),(0,y+226*sin(a),r+226*cos(a)),3.5,'rubber')
    for o in bpy.context.scene.objects:
        if o.name not in start:
            o['steer_with_front']=name=='Front'
            o['mechanical_accuracy']='nominal fit; detailed visual gate pending'


def _cut(target,cutters,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in cutters:o.select_set(True)
    bpy.context.view_layer.objects.active=cutters[0];bpy.ops.object.join();operand=bpy.context.object
    bpy.ops.object.select_all(action='DESELECT');target.select_set(True);bpy.context.view_layer.objects.active=target
    mod=target.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=operand
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(operand,do_unlink=True)

def _lathe(name,y,z,profile,mat,segments=128):
    m=len(profile); vs=[(x,y+rr*sin(2*pi*j/segments),z+rr*cos(2*pi*j/segments)) for j in range(segments) for x,rr in profile]
    fs=[(j*m+k,((j+1)%segments)*m+k,((j+1)%segments)*m+(k+1)%m,j*m+(k+1)%m) for j in range(segments) for k in range(m)]
    return _mesh(name,vs,fs,mat,0,True)


def _engine():
    global _COL
    _COL=_collection(bpy.context.scene,'Collection_Engine')
    # Preserve the r15 relocated engine centre. Old bolt locations had not
    # followed that relocation and visibly floated behind the covers.
    for s,lab,rr in [(-1,'L',88),(1,'R',101)]:
        y,z=66,380;N=64;verts=[]
        for xx,scale in [(s*143,1.0),(s*157,1.01),(s*176,.93),(s*179,.86)]:
            for j in range(N):
                a=j*math.tau/N;shape=1+.025*cos(3*a)
                verts.append((xx,y+rr*sin(a)*scale*shape,z+rr*cos(a)*scale*shape))
        fs=[tuple(reversed(range(N))),tuple(range(3*N,4*N))]+[(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for k in range(3) for j in range(N)]
        _mesh('Engine_AlternatorCover' if s<0 else 'Engine_ClutchCover',verts,fs,'gun',.8,True)
        _cyl('Engine_CoverInset_'+lab,(s*181,y,z),rr*.73,3,'gun',(s,0,0),64,1)
        for j in range(10):
            a=j*math.tau/10;py=y+rr*.90*sin(a);pz=z+rr*.90*cos(a)
            _cyl('Engine_BoltBoss_'+lab+f'_{j}',(s*170,py,pz),8,8,'gun',(s,0,0),24,1)
            _cyl('Crankcase_Bolt_'+lab+f'_{j}',(s*176,py,pz),4,4,'steel',(s,0,0),6,.4)
    # Restore physical head/header connection after the earlier engine relocation.
    for o in bpy.context.scene.objects:
        if o.name.startswith('Exhaust_Header') and o.type=='CURVE':
            pts=o.data.splines[0].bezier_points
            if len(pts)>=3:
                pts[0].co.y=.343;pts[0].co.z=.618;pts[1].co.y=.357;pts[1].co.z=.563
                o['attachment_revision']='matched relocated cylinder-head front'
        if o.name.startswith('Exhaust_Flange'):o.location.y=.341;o.location.z=.618

def _solid_plate(name, points, thickness, mat):
    # Closed thin plate with an explicit side wall; points are ordered outline.
    vs=[(x-thickness/2,y,z) for x,y,z in points]+[(x+thickness/2,y,z) for x,y,z in points]; n=len(points)
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    return _mesh(name,vs,fs,mat,1.2,False)

def _radiator_exhaust():
    global _COL
    _COL = _collection(bpy.context.scene, 'Collection_Engine')
    # Existing radiator, headers, collector and异形 muffler stay untouched.
    pts=[(306,-344,287),(313,-403,338),(324,-749,538),(312,-827,521),(291,-756,411),(291,-435,268)]
    _solid_plate('Exhaust_HeatShield',pts,5,'silver')['heat_shield_profile']='faceted_plate_from_existing_outline'

def _drive():
    # Existing swingarm, shock, sprockets, chain, chain links, footpegs and
    # side stand remain untouched in this incremental pass.
    return

def apply(scene):
    """Replace the stage-C mechanical proxy set in ``scene``; returns created objects."""
    global _COL
    if scene is None: raise ValueError('apply(scene) requires a Blender scene')
    if scene.get('stage_c_drive_rebuilt'):raise ValueError('Do not replay the historical pre-catalogue mechanics pass on corrected sources')
    _COL=_collection(scene,'Collection_Wheels'); _materials(); _remove_old(scene)
    _wheel('Front',715,303.9,110,-65,145); _wheel('Rear',-715,313.9,140,83,120)
    _engine(); _radiator_exhaust(); _drive()
    for o in list(scene.objects):
        if o.get('stage_c_owner') == 'rebuild_mechanics_stage_c':
            o['acceptance']='stage_c_proxy_requires_photo_review'
            o['evidence_basis']='GSX250R family geometry; local photos; official family specs'
    scene['stage_c_rebuild']='mechanical_exposed_parts_only'
    scene['stage_c_status']='NOT_PASSED'
    scene['stage_c_no_body_seat_camera_cage_mutation']=True
    bpy.context.view_layer.update()
    return [o for o in scene.objects if o.get('stage_c_owner')=='rebuild_mechanics_stage_c']









