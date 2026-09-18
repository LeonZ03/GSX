"""Refinements after photo/render inspection; reproducible, no private data embedded."""
from pathlib import Path
import bpy, bmesh, math, sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import build_motorcycle as b

def remove(prefixes):
    for o in list(b.SC.objects):
        if any(o.name.startswith(p) for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)

def refine():
    b.SC=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
    b.C={n:bpy.data.collections['Collection_'+n] for n in ['Body','Details','Wheels','Engine','FrontEnd','Lights','Cameras','Reference','Blockout']}
    keys={'blue':'Paint_UserCustom','black':'Plastic_MatteBlack','gloss':'Plastic_GlossBlack','gun':'Engine_Graphite','rubber':'Tire_Rubber','leather':'Seat_GrainedVinyl','steel':'BrakeDisc_Steel','silver':'Aluminium_Brushed','chrome':'Chrome','guard':'GuardBar_Metal','yellow':'Decal_FluoroYellow','white':'Decal_White','plate':'Plate_Metal','ink':'Decal_Black','amber':'Indicator_Amber','red':'Lamp_Red','glass':'Headlight_Glass','wind':'Windscreen_PC','bronze':'Exhaust_TemperedSteel','lcd':'Dashboard_LCD','ground':'Studio_Floor'}
    b.M={k:bpy.data.materials['MAT_'+v] for k,v in keys.items()}
    # Saturated lacquer and powder coated guards, based on the owner's daylight photographs.
    changes={'blue':((.001,.075,.42),.28,.25,.32),'guard':((.008,.011,.015),.15,.48,0),'leather':((.006,.008,.012),0,.56,0),'rubber':((.009,.011,.013),0,.66,0),'black':((.005,.007,.009),0,.5,0),'gloss':((.004,.006,.008),.15,.28,.2)}
    for key,(color,metal,rough,coat) in changes.items():
        m=b.M[key];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Coat Weight'].default_value=coat
        p.inputs['Specular IOR Level'].default_value=.32;m.diffuse_color=(*color,1)
    # A camera-visible soft studio, with physically separate key/rim highlights.
    for o in b.C['Lights'].objects:
        if o.type=='LIGHT':o.data.energy*=.72
    bg=next(n for n in b.SC.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[1].default_value=.22
    b.SC.view_settings.look='AgX - Medium High Contrast'
    remove(['Studio_Ground']);b.COL=b.C['Lights']
    b.mesh('Studio_Ground',[(-10000,-10000,-1),(10000,-10000,-1),(10000,10000,-1),(-10000,10000,-1)],[(0,1,2,3)],'ground')
    # Main fairing shells have continuous coverage around the engine opening.
    remove(['Body_SideFairing','Body_FairingForward','Headlight','PositionLamp','Decal_Side_','Decal_Seat_','Tank_WhiteFlash','Tank_YellowFlash','Exhaust_HeatShield','Mirror_L','Mirror_R','Mirror_Glass','GuardBar_L','GuardBar_R','GuardBar_Brace','GuardBar_LowerBrace','GuardBar_Slider','SideVent','VentFin'])
    b.COL=b.C['Body']
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        pts=[(184,-190,627),(227,95,725),(267,559,790),(250,829,685),(230,547,584),(163,368,218),(145,253,177),(135,200,218),(180,269,384),(207,292,528),(207,49,574),(174,-159,571)]
        # Explicit quad topology prevents n-gon diagonal artifacts across the large concavity.
        verts=[(s*x,y,z) for x,y,z in pts]+[(s*252,366,657),(s*223,416,496)]
        faces=[(0,1,12,10,11),(1,2,3,4,12),(4,13,9,10,12),(4,5,6,7,8,9,13)]
        o=b.mesh('Body_SideFairing_'+lab,verts,faces,'blue',smo=True)
        mod=o.modifiers.new('Fairing shell 3 mm','SOLIDIFY');mod.thickness=.003;b.bevel(o,2)
        # Edge crease / upper lip adds thickness and a controlled highlight.
        b.tube('Fairing_UpperLip_'+lab,[(s*184,-190,627),(s*227,95,725),(s*267,559,790),(s*250,829,685)],2,'blue')
        b.panel('SideVent_'+lab,[(s*210,38,695),(s*229,268,722),(s*228,384,690),(s*214,169,651)],'ink',3,3)
        for j in range(3):b.tube('VentFin_'+lab,[(s*220,124+j*65,667),(s*237,210+j*65,692)],2,'gun')
        # Nose wraps both sides of the central reflector rather than floating behind it.
        b.patch('Body_NoseBridge_'+lab,[[(s*117,788,901),(s*92,866,850),(s*74,894,838)],[(s*194,760,850),(s*163,853,815),(s*119,915,786)],[(s*221,784,742),(s*188,890,701),(s*99,942,689)]],'blue',3,1)
        b.panel('Headlight_SideTrim_'+lab,[(s*80,903,840),(s*175,858,841),(s*139,916,732),(s*29,968,680)],'gloss',4,3)
        b.panel('PositionLamp_'+lab,[(s*86,900,827),(s*165,864,827),(s*124,901,788)],'glass',3,2)
        # Angular mirror housings, not generic round mirrors.
        x=s*310
        verts=[(x-s*58,655,1041),(x-s*34,655,1078),(x+s*47,656,1104),(x+s*60,658,1079),(x+s*35,660,1028),(x-s*24,658,1023)]
        b.panel('Mirror_'+lab,verts,'black',22,8)
        b.panel('Mirror_Glass_'+lab,[(x+(a-x)*.87,y-13,1061+(z-1061)*.83) for a,y,z in verts],'chrome',2,5)
        # Replace angular decal placeholder with thin original geometric flashes on tank.
        b.panel('Tank_WhiteFlash_'+lab,[(s*174,-185,846),(s*186,-56,815),(s*184,6,829),(s*179,-74,867)],'white',.25,0)
        b.panel('Tank_YellowFlash_'+lab,[(s*187,-35,819),(s*184,61,837),(s*182,8,837)],'yellow',.25,0)
    # Fresnel clear lens with layered reflector: a lamp assembly under a curved shell.
    lens=[(-76,902,840),(0,924,844),(76,902,840),(105,923,785),(67,960,709),(0,970,687),(-67,960,709),(-105,923,785)]
    b.panel('Headlight_Bezel',[(x*1.16,y-8,765+(z-765)*1.12) for x,y,z in lens],'gloss',10,6)
    b.panel('Headlight_Reflector',lens,'chrome',3,3)
    for j in range(-7,8):
        x=j*10;b.tube('Headlight_Flute',[(x,958-abs(x)*.23,712+abs(x)*.3),(x,942-abs(x)*.18,779),(x,918-abs(x)*.15,834)],1,'steel')
    b.sphere('Headlight_Bulb',(0,952,778),(20,8,20),'chrome')
    o=b.panel('Headlight',[(x,y+5,z) for x,y,z in lens],'glass',1.5,3)
    # OpenPBR dielectric glass is represented by a dedicated Glass BSDF for predictable transmission.
    for key in ['glass','wind']:
        m=b.M[key];nodes=m.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');gl=nodes.new('ShaderNodeBsdfGlass');gl.inputs['Color'].default_value=(.94,.975,1,1);gl.inputs['Roughness'].default_value=.035 if key=='glass' else .055;gl.inputs['IOR'].default_value=1.46;m.node_tree.links.new(gl.outputs[0],out.inputs['Surface'])
    # Broad brushed muffler shield follows the stock silencer rather than a thin fin.
    b.COL=b.C['Engine']
    grid=[[(294,-367,289),(312,-414,354),(323,-746,548),(300,-824,511)],[(307,-380,266),(330,-472,326),(332,-728,466),(305,-825,494)],[(286,-422,248),(307,-502,292),(307,-710,398),(293,-795,452)]]
    b.patch('Exhaust_HeatShield',grid,'silver',4,1)
    # Powder-coated triangular cage seen in photos 62 and 63; both sides mirror exactly.
    b.COL=b.C['Details']
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        b.tube('GuardBar_'+lab,[(s*180,-205,437),(s*274,-141,505),(s*323,187,591),(s*322,237,592),(s*308,186,436),(s*228,62,435),(s*180,-205,437)],12.5,'guard',False,False)
        b.tube('GuardBar_Brace_'+lab,[(s*180,229,483),(s*308,186,436),(s*323,237,592)],12.5,'guard',False,False)
        for y,z in [(237,592),(186,436)]:b.sphere('GuardBar_Joint_'+lab,(s*323,y,z),(17,17,17),'guard')
        b.cyl('GuardBar_Slider_'+lab,(s*336,232,593),19,28,'rubber',(s,0,0))
    # Manufacture the large, bold livery as vector meshes projected and clipped to each fairing.
    # This keeps the letter silhouettes while respecting seams and cutouts.
    font=None
    for fp in ['C:/Windows/Fonts/arialbd.ttf','C:/Windows/Fonts/Arial.ttf']:
        if Path(fp).exists():font=bpy.data.fonts.load(fp);break
    def projected_text(name,body,target,s,center,size,tilt=0):
        o=b.text_obj(name,body,(s*400,center[0],center[1]),size,'white',(s,0,0),(0,s,0),font,0)
        o.data.shear=.13
        if tilt:o.rotation_euler.rotate_axis('Z',tilt)
        b.select(o);bpy.ops.object.convert(target='MESH')
        # Densify triangles before per-vertex projection so letters conform to the shell.
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=4,use_grid_fill=True);bm.to_mesh(o.data);bm.free()
        deps=bpy.context.evaluated_depsgraph_get();ev=target.evaluated_get(deps);inv=ev.matrix_world.inverted();valid={}
        for v in o.data.vertices:
            p=o.matrix_world@v.co;origin=Vector((s*.5,p.y,p.z));direction=Vector((-s,0,0))
            hit,co,no,ind=ev.ray_cast(inv@origin,inv.to_3x3()@direction)
            valid[v.index]=hit
            if hit:v.co=o.matrix_world.inverted()@(ev.matrix_world@co+Vector((s*.0012,0,0)))
        bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bad=[v for v in bm.verts if not valid[v.index]];bmesh.ops.delete(bm,geom=bad,context='VERTS');bm.to_mesh(o.data);bm.free()
        return o
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        projected_text('Decal_MainLivery_'+lab,'UKI' if s>0 else 'SU',bpy.data.objects['Body_SideFairing_'+lab],s,(260,642),254)
        projected_text('Decal_SeatLivery_'+lab,'SU' if s>0 else 'ZU',bpy.data.objects['Body_SeatSide_'+lab],s,(-316,725),209)
        # Smaller marks are also bold and attached to their own trim planes.
        for prefix in ['Decal_Tail_','Decal_Belly_','Decal_Model_','Decal_Motul_']:
            o=bpy.data.objects.get(prefix+lab)
            if o and o.type=='FONT' and font:o.data.font=font
    # Restore the photo's black cylinder casing proportions; side fairing masks the upper casting.
    b.SC['refinement']='r2: continuous fairing, projected vector livery, angular mirrors, powder coated triangular cage'
    for area in (bpy.context.screen.areas if bpy.context.screen else []):
        if area.type=='VIEW_3D':area.spaces.active.clip_end=100
    b.SC.camera=bpy.data.objects['Camera_Front_3Q'];b.SC.render.resolution_x=3840;b.SC.render.resolution_y=2160
    b.save('09_lighting_render');b.save('10_final')
    return {'objects':len(b.SC.objects),'revision':b.SC['refinement']}
if __name__=='__main__':print(refine())
