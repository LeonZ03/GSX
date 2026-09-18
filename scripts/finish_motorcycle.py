"""Final continuous nose topology, physical envelope checks and packing."""
from pathlib import Path
import bpy,sys,json
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import build_motorcycle as b
import refine_motorcycle as r

def finish():
    b.SC=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
    b.C={n:bpy.data.collections['Collection_'+n] for n in ['Body','Details','Wheels','Engine','FrontEnd','Lights','Cameras','Reference','Blockout']}
    for k,v in {'blue':'Paint_UserCustom','gloss':'Plastic_GlossBlack','glass':'Headlight_Glass','white':'Decal_White','yellow':'Decal_FluoroYellow','black':'Plastic_MatteBlack','silver':'Aluminium_Brushed'}.items():b.M[k]=bpy.data.materials['MAT_'+v]
    r.remove(['Body_UpperCowling','Body_NoseBridge','Headlight_SideTrim','PositionLamp'])
    b.COL=b.C['Body']
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        sections=[(330,111,883,192,795),(345,113,887,196,800),(475,142,934,225,819),(649,139,932,249,811),(783,91,884,227,768),(855,87,854,183,734),(904,106,786,145,706),(934,58,716,94,686),(941,42,707,69,683)]
        grid=[]
        for y,xi,zi,xo,zo in sections:
            grid.append([(s*(xi+(xo-xi)*t),y,zi+(zo-zi)*t+8*__import__('math').sin(t*3.14159)) for t in [0,.04,.35,.7,.96,1]])
        b.patch('Body_UpperCowling_'+lab,grid,'blue',3,1)
        b.panel('Headlight_SideTrim_'+lab,[(s*94,850,855),(s*184,815,848),(s*135,896,762),(s*61,943,708)],'gloss',4,5)
        b.panel('PositionLamp_'+lab,[(s*102,855,847),(s*176,825,837),(s*132,886,791)],'glass',2,4)
    ground=bpy.data.objects['Studio_Ground'];ground.scale=(100,100,1)
    # Seat and reference envelopes use evaluated vertices, not curve object bounding boxes.
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    allpts=[];poly_count=0;vertices=0
    for o in b.SC.objects:
        if o.type not in {'MESH','CURVE','FONT'} or o.name.startswith('Studio'):continue
        e=o.evaluated_get(deps);me=e.to_mesh();allpts.extend([o.matrix_world@v.co for v in me.vertices]);poly_count+=len(me.polygons);vertices+=len(me.vertices);e.to_mesh_clear()
    mn=[min(p[i] for p in allpts) for i in range(3)];mx=[max(p[i] for p in allpts) for i in range(3)]
    # Analytic reference anchors match tire construction, independent of artwork.
    guards=[]
    for lab in ['L','R']:
        o=bpy.data.objects['GuardBar_'+lab];spline=o.data.splines[0];guards.append([Vector(p.co[:3]) for p in spline.points])
    err=max((Vector((-a.x,a.y,a.z))-z).length for a,z in zip(*guards))*1000
    report={'blender':bpy.app.version_string,'bounds_mm':{'width':(mx[0]-mn[0])*1000,'length':(mx[1]-mn[1])*1000,'height':(mx[2]-mn[2])*1000},'minimum_z_mm':mn[2]*1000,'wheelbase_mm':1430,'front_tire_nominal_mm':[110,607.8],'rear_tire_nominal_mm':[140,627.8],'guard_symmetry_max_error_mm':err,'evaluated_vertices':vertices,'evaluated_polygons':poly_count,'note':'Envelope is measured from actual evaluated mesh vertices. Nominal tire section is not a measured branded carcass. No claim of zero intersections.'}
    (b.ROOT/'qa/dimensions.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    b.SC['accuracy_report']='qa/dimensions.json';b.SC['revision']='r4: continuous nose and photo-led livery'
    # Source includes packed HDRI, not original photographic reference images.
    for im in list(bpy.data.images):
        if im.users==0 and im.source=='FILE':bpy.data.images.remove(im)
    bpy.ops.file.pack_all()
    b.save('09_lighting_render');b.save('10_final')
    return report
if __name__=='__main__':print(finish())
