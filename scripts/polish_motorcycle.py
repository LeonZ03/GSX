from pathlib import Path
import bpy, bmesh, math, sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import refine_motorcycle as r
import build_motorcycle as b

def polish():
    b.SC=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
    b.C={n:bpy.data.collections['Collection_'+n] for n in ['Body','Details','Wheels','Engine','FrontEnd','Lights','Cameras','Reference','Blockout']}
    names={'blue':'Paint_UserCustom','black':'Plastic_MatteBlack','gloss':'Plastic_GlossBlack','gun':'Engine_Graphite','rubber':'Tire_Rubber','leather':'Seat_GrainedVinyl','steel':'BrakeDisc_Steel','silver':'Aluminium_Brushed','chrome':'Chrome','guard':'GuardBar_Metal','yellow':'Decal_FluoroYellow','white':'Decal_White','plate':'Plate_Metal','ink':'Decal_Black','amber':'Indicator_Amber','red':'Lamp_Red','glass':'Headlight_Glass','wind':'Windscreen_PC','bronze':'Exhaust_TemperedSteel','lcd':'Dashboard_LCD','ground':'Studio_Floor'}
    b.M={k:bpy.data.materials['MAT_'+v] for k,v in names.items()}
    for key,color,rough,spec in [('blue',(.001,.15,.64),.25,.25),('leather',(.005,.006,.008),.8,.08),('guard',(.006,.008,.011),.63,.12),('black',(.004,.005,.007),.58,.16),('rubber',(.009,.01,.012),.72,.18)]:
        p=next(n for n in b.M[key].node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Specular IOR Level'].default_value=spec
        if key in ['guard','leather']:p.inputs['Metallic'].default_value=0
    # HDRI bundled with this Blender installation. Packed into the local source file.
    hdr=Path(bpy.app.binary_path).parent/'5.2/datafiles/studiolights/world/studio.exr'
    if hdr.exists():
        world=b.SC.world;nodes=world.node_tree.nodes;bg=next(n for n in nodes if n.type=='BACKGROUND')
        env=next((n for n in nodes if n.type=='TEX_ENVIRONMENT'),None) or nodes.new('ShaderNodeTexEnvironment')
        env.image=bpy.data.images.load(str(hdr),check_existing=True);env.image.pack();world.node_tree.links.new(env.outputs['Color'],bg.inputs[0]);bg.inputs[1].default_value=.16
    b.SC.view_settings.exposure=-.6
    # Large floor leaves no horizon corner in the three-quarter camera.
    ground=bpy.data.objects['Studio_Ground'];ground.scale=(100,100,100)
    # Close front cowling seams and shorten the unsupported nose.
    b.COL=b.C['Body']
    r.remove(['Headlight','PositionLamp','Body_NoseBridge','Taillight'])
    outline=[(-84,850,858),(0,861,856),(84,850,858),(114,894,795),(84,928,729),(40,943,701),(0,951,688),(-40,943,701),(-84,928,729),(-114,894,795)]
    def cap(name,outline,mat,yoff=0):
        center=Vector((0,910+yoff,779));verts=[];N=len(outline)
        for k in [1,.96,.75,.38,.025]:
            for p in outline:
                q=center+(Vector((p[0],p[1]+yoff,p[2]))-center)*k;q.y+=10*(1-k*k);verts.append(q)
        faces=[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(4) for i in range(N)]+[tuple(range(4*N,5*N))]
        o=b.mesh(name,verts,faces,mat,smo=True);m=o.modifiers.new('Lamp surface refinement','SUBSURF');m.levels=1;m.render_levels=1
        m=o.modifiers.new('Lens thickness','SOLIDIFY');m.thickness=.0015
        return o
    cap('Headlight_Bezel',[(x*1.15,y-5,774+(z-774)*1.14) for x,y,z in outline],'gloss')
    cap('Headlight_Reflector',outline,'chrome',1)
    cap('Headlight',outline,'glass',6)
    for j in range(-8,9):
        x=j*9;b.tube('Headlight_Flute',[(x,926-abs(x)*.16,724+abs(x)*.25),(x,923-abs(x)*.16,779),(x,866-abs(x)*.12,846)],.7,'steel')
    b.sphere('Headlight_Bulb',(0,925,778),(18,7,18),'glass')
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        grid=[[(s*139,690,899),(s*101,799,885),(s*86,846,861)],[(s*205,704,841),(s*169,822,822),(s*117,887,796)],[(s*220,765,733),(s*170,870,706),(s*71,937,704)]]
        b.patch('Body_NoseBridge_'+lab,grid,'blue',3,0)
        b.panel('Headlight_SideTrim_'+lab,[(s*93,855,854),(s*188,806,854),(s*151,883,765),(s*57,946,689)],'gloss',5,6)
        b.panel('PositionLamp_'+lab,[(s*102,859,848),(s*180,820,843),(s*124,885,799)],'glass',2,5)
    # A larger original-style rear light with black trim. Luggage remains omitted.
    b.panel('Taillight_Housing',[(-65,-958,898),(65,-958,898),(53,-1007,823),(0,-1022,788),(-53,-1007,823)],'black',13,10)
    b.panel('Taillight',[(-49,-968,883),(49,-968,883),(37,-1015,829),(0,-1030,804),(-37,-1015,829)],'red',6,8)
    b.tube('Taillight_LED',[(-34,-980,873),(-29,-1018,836),(0,-1035,817),(29,-1018,836),(34,-980,873)],3,'red')
    # Font outline rescale and projection would accumulate errors: regenerate cleanly.
    r.remove(['Decal_MainLivery_','Decal_SeatLivery_'])
    font=bpy.data.fonts.load('C:/Windows/Fonts/arialbd.ttf')
    b.COL=b.C['Details']
    def decal(name,word,target,s,y,z,size,angle):
        o=b.text_obj(name,word,(s*500,y,z),size,'white',(s,0,0),(0,s,0),font,0);o.data.shear=.13;o.rotation_euler.rotate_axis('Z',angle)
        b.select(o);bpy.ops.object.convert(target='MESH');bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=7,use_grid_fill=True);bm.to_mesh(o.data);bm.free()
        bpy.context.view_layer.update();ev=target.evaluated_get(bpy.context.evaluated_depsgraph_get());inv=ev.matrix_world.inverted();valid={}
        for v in o.data.vertices:
            p=o.matrix_world@v.co;hit,co,no,idx=ev.ray_cast(inv@Vector((s*.6,p.y,p.z)),Vector((-s,0,0)));valid[v.index]=hit
            if hit:v.co=o.matrix_world.inverted()@(ev.matrix_world@co+Vector((s*.0015,0,0)))
        bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if not valid[v.index]],context='VERTS');bm.to_mesh(o.data);bm.free()
    for s in [-1,1]:
        lab='L' if s<0 else 'R';decal('Decal_MainLivery_'+lab,'UKI' if s>0 else 'SU',bpy.data.objects['Body_SideFairing_'+lab],s,269,634,382,-s*.31)
        decal('Decal_SeatLivery_'+lab,'SU' if s>0 else 'ZU',bpy.data.objects['Body_SeatSide_'+lab],s,-310,741,295,-s*.15)
        o=bpy.data.objects['Body_FrameCover_'+lab]
        for v in o.data.vertices:v.co.x*=1.2
    # Friendly modeling viewport and fixed dimensions stored for downstream verification.
    b.SC['revision']='r3 photo refinement';b.SC['plate_confirmation']='User selected Beijing B; actual characters stored locally only'
    # Keep clean final source: old default startup scene is not part of this deliverable.
    for s in list(bpy.data.scenes):
        if s!=b.SC and s.name=='Scene':
            for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.scenes.remove(s)
    b.save('09_lighting_render');b.save('10_final')
    return {'revision':b.SC['revision'],'objects':len(b.SC.objects)}
if __name__=='__main__':print(polish())
