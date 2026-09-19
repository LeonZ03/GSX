"""Photo-led right clutch casting reconstruction, isolated r29 -> r30.
The source contour and hidden support depth are provisional, not measurements.
"""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
V=Path(__file__).resolve().parents[1]

def mesh(scene,name,verts,faces,mat,bevel=0):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata([[c*.001 for c in p] for p in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);next(c for c in scene.collection.children if c.name.startswith('Collection_Engine')).objects.link(o);me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    if bevel:m=o.modifiers.new('Casting_edge_radius','BEVEL');m.width=bevel*.001;m.segments=3
    o['stage_c_owner']='clutch_r30';o['acceptance']='NOT_PASSED';return o

def loft(scene,name,rings,mat,bevel=0):
    n=len(rings[0]);verts=sum(rings,[]);faces=[tuple(reversed(range(n)))]+[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(rings)-1) for k in range(n)]+[tuple(range((len(rings)-1)*n,len(rings)*n))]
    return mesh(scene,name,verts,faces,mat,bevel)

def cylinder(scene,name,center,radius,depth,mat,n=48):
    x,y,z=center;rings=[[[x+dx,y+radius*math.cos(k*math.tau/n),z+radius*math.sin(k*math.tau/n)] for k in range(n)] for dx in [-depth/2,depth/2]]
    return loft(scene,name,rings,mat,.35)

def apply(scene,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    if scene.get('revision')!='r29':raise ValueError('Requires isolated r29 source')
    d=json.loads((V/'data/revisions/r30_engine_candidate/clutch_cover.json').read_text());mat=scene.objects['Engine_ClutchCover'].data.materials[0];steel=scene.objects['BrakeDisc_Front'].data.materials[0]
    for o in list(scene.objects):
        if o.name in ['Engine_ClutchCover','Engine_CoverInset_R'] or o.name.startswith(('Engine_BoltBoss_R','Crankcase_Bolt_R')):bpy.data.objects.remove(o,do_unlink=True)
    outline=d['outline_mm'];cx,cy,cz=d['inset_center_mm'];rr=d['inset_radius_mm'];rings=[]
    for x,scale in [(142.5,1),(148,1),(159,.97),(166,.93)]:rings.append([[x,cy+(p[1]-cy)*scale,cz+(p[2]-cz)*scale] for p in outline])
    cover=loft(scene,'Engine_ClutchCover',rings,mat,1.4);cover['evidence']='right cover outline; two-view raised rim; family FIG112A; hidden thickness unverified'
    cylinder(scene,'Engine_CoverInset_R',[cx,cy,cz],rr,5,mat,64)
    # Nonuniform visible bolt positions are traced, not equally spaced on a circle.
    for i,p in enumerate(d['visible_bolt_centers_mm']):
        cylinder(scene,f'Engine_BoltBoss_R_{i}',[161,p[1],p[2]],7.5,9,mat,24)
        cylinder(scene,f'Crankcase_Bolt_R_{i}',[168,p[1],p[2]],4.2,4,steel,6)
    # The original generic crankcase was too short rearward to support the cover.
    # Add a hidden editable casting-volume union; preserve the original body mesh.
    support=loft(scene,'Tool_TransmissionCaseSupport',[[[x,p[1],p[2]] for p in outline] for x in [-139,139]],mat,1.0)
    support.hide_render=True;support.hide_set(True);support.display_type='WIRE';support['export_exclude']=True;support['unverified']='back casting depth and hidden left footprint'
    m=scene.objects['Engine_Crankcase'].modifiers.new('Editable_TransmissionCasting','BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=support
    scene['revision']='r30';scene.name='GSX250R_Reconstruction_V2_Gray_r30';scene['stage_C']='NOT_PASSED';scene['clutch_r30']='photo-led candidate; five visible bolts only, remaining family hardware unverified'
    bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True)
    return {'saved':str(output),'rim_center_mm':[cx,cy,cz],'rim_radius_mm':rr,'acceptance':'NOT_PASSED'}
