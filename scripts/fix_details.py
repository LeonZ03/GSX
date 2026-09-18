"""Correct decal double surfaces and thin optical elements found in final-render QA."""
from pathlib import Path
import bpy,bmesh,sys,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import build_motorcycle as b

def fix():
    b.SC=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
    b.C={n:bpy.data.collections['Collection_'+n] for n in ['Details','Body','Lights','Cameras']};b.COL=b.C['Details']
    for k,v in {'white':'Decal_White','yellow':'Decal_FluoroYellow','blue':'Paint_UserCustom','chrome':'Chrome','black':'Plastic_MatteBlack','ink':'Decal_Black'}.items():b.M[k]=bpy.data.materials['MAT_'+v]
    for o in list(b.SC.objects):
        if o.name.startswith(('Decal_MainLivery_','Decal_SeatLivery_','Tank_WhiteFlash_','Tank_YellowFlash_','Decal_TankBadge_','Decal_Yoshimura_')):bpy.data.objects.remove(o,do_unlink=True)
    font=bpy.data.fonts.load('C:/Windows/Fonts/arialbd.ttf')
    chinese=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
    def project(o,target,s,cuts=7):
        b.select(o)
        if o.type!='MESH':bpy.ops.object.convert(target='MESH')
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=cuts,use_grid_fill=True)
        # Refine long faces before ray projection, so artwork follows panel bends.
        for refinement in range(7):
            edges=[edge for edge in bm.edges if edge.calc_length()>.008]
            if not edges:break
            bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
        bm.to_mesh(o.data);bm.free()
        bpy.context.view_layer.update();ev=target.evaluated_get(bpy.context.evaluated_depsgraph_get());inv=ev.matrix_world.inverted();valid={}
        for v in o.data.vertices:
            p=o.matrix_world@v.co;hit,co,no,idx=ev.ray_cast(inv@Vector((s*.65,p.y,p.z)),Vector((-s,0,0)));valid[v.index]=hit
            if hit:v.co=o.matrix_world.inverted()@(ev.matrix_world@co+Vector((s*.002,0,0)))
        bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if not valid[v.index]],context='VERTS');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000005);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        return o
    def text(name,word,target,s,y,z,size,angle=0,ft=font,key='white'):
        o=b.text_obj(name,word,(s*500,y,z),size,key,(s,0,0),(0,s,0),ft,0)
        o.data.bevel_depth=0;o.data.extrude=0;o.data.shear=.13;o.rotation_euler.rotate_axis('Z',angle)
        return project(o,target,s,9)
    for s in [-1,1]:
        lab='L' if s<0 else 'R';fair=bpy.data.objects['Body_SideFairing_'+lab]
        text('Decal_MainLivery_'+lab,'UKI' if s>0 else 'SU',fair,s,269,634,382,-s*.31)
        text('Decal_SeatLivery_'+lab,'SU' if s>0 else 'ZU',bpy.data.objects['Body_SeatSide_'+lab],s,-310,741,295,-s*.15)
        for name,pts,key in [('Tank_WhiteFlash',[(-191,868),(-61,818),(2,830),(-66,867)],'white'),('Tank_YellowFlash',[(-34,820),(66,843),(10,843)],'yellow')]:
            o=b.mesh(name+'_'+lab,[(s*500,y,z) for y,z in pts],[tuple(range(len(pts)))],key)
            project(o,bpy.data.objects['Body_Tank'],s,12)
        # Stylized metallic Suzuki emblem redrawn as an angular S silhouette.
        outline=[(-.48,.36),(-.06,.56),(.43,.27),(.09,.06),(.43,-.15),(.01,-.56),(-.43,-.31),(-.08,-.08),(-.43,.14),(-.03,.34)]
        o=b.mesh('Decal_TankBadge_'+lab,[(s*500,166+s*u*44,764+v*50) for u,v in outline],[tuple(range(len(outline)))],'chrome')
        project(o,bpy.data.objects['Body_TankTrim_'+lab],s,5)
        if s>0:
            old=bpy.data.objects.get('Decal_Model_R')
            if old:bpy.data.objects.remove(old,do_unlink=True)
            text('Decal_Yoshimura_R','ヨシムラ',fair,s,638,730,23,0,chinese)
    # Thin optical panels: mostly straight transmission plus a restrained Fresnel reflection.
    for name,reflection in [('MAT_Windscreen_PC',.12),('MAT_Headlight_Glass',.17)]:
        m=bpy.data.materials[name];n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');trans=n.new('ShaderNodeBsdfTransparent');trans.inputs[0].default_value=(.92,.96,.98,1)
        glass=n.new('ShaderNodeBsdfGlass');glass.inputs['Color'].default_value=(.96,.98,1,1);glass.inputs['Roughness'].default_value=.05;glass.inputs['IOR'].default_value=1.46
        mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=reflection;m.node_tree.links.new(trans.outputs[0],mix.inputs[1]);m.node_tree.links.new(glass.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs[0])
    # Rich medium blue base with restrained metallic reflection.
    p=next(n for n in bpy.data.materials['MAT_Paint_UserCustom'].node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Metallic'].default_value=.12;p.inputs['Coat Weight'].default_value=.2;p.inputs['Base Color'].default_value=(.001,.125,.53,1)
    b.SC['revision']='r5: cleaned single-surface projected decals and optical corrections'
    bpy.ops.file.pack_all();b.save('09_lighting_render');b.save('10_final')
    return {'revision':b.SC['revision'],'decal_faces':sum(len(o.data.polygons) for o in b.SC.objects if o.type=='MESH' and o.name.startswith('Decal_MainLivery_'))}
if __name__=='__main__':print(fix())
