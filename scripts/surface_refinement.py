"""Continuous cowling surfaces fitted to owner photographs 62 and 66.

This is a visual refinement, not a scan or a calibrated measurement.
Coordinates below are millimetres in the established vehicle frame.
"""
from pathlib import Path
import bpy, bmesh, sys, math, json
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).parent))
import build_motorcycle as b
import fix_details as decals


def sample(points, u):
    u = max(0.0, min(float(len(points)-1), u))
    i = min(int(u), len(points)-2); t = u-i
    p0 = Vector(points[max(0,i-1)]); p1 = Vector(points[i])
    p2 = Vector(points[i+1]); p3 = Vector(points[min(len(points)-1,i+2)])
    return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)


def dense_grid(rows, steps=5):
    return [[sample([r[c] for r in rows], i/steps) for c in range(len(rows[0]))]
            for i in range((len(rows)-1)*steps+1)]


def shell(name, grids, material, thickness=3):
    verts=[]; faces=[]
    for grid in grids:
        nr=len(grid); nc=len(grid[0]); off=len(verts); verts.extend(sum(grid, []))
        faces.extend((off+j*nc+i,off+j*nc+i+1,off+(j+1)*nc+i+1,off+(j+1)*nc+i)
                     for j in range(nr-1) for i in range(nc-1))
    o=b.mesh(name, verts, faces, material, smo=True)
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free()
    m=o.modifiers.new('Moulded shell thickness', 'SOLIDIFY'); m.thickness=thickness*.001; m.offset=-1
    return o


def refine_surfaces():
    b.SC=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
    bpy.context.window.scene=b.SC
    b.C={n:bpy.data.collections['Collection_'+n] for n in ['Body','Details','FrontEnd','Lights','Cameras']}
    keys={'blue':'Paint_UserCustom','black':'Plastic_MatteBlack','gloss':'Plastic_GlossBlack','gun':'Engine_Graphite','rubber':'Tire_Rubber','leather':'Seat_GrainedVinyl','steel':'BrakeDisc_Steel','silver':'Aluminium_Brushed','chrome':'Chrome','guard':'GuardBar_Metal','yellow':'Decal_FluoroYellow','white':'Decal_White','plate':'Plate_Metal','ink':'Decal_Black','amber':'Indicator_Amber','red':'Lamp_Red','glass':'Headlight_Glass','wind':'Windscreen_PC','bronze':'Exhaust_TemperedSteel','lcd':'Dashboard_LCD','ground':'Studio_Floor'}
    b.M={k:bpy.data.materials['MAT_'+v] for k,v in keys.items()}
    prefixes=('Body_UpperCowling','Body_SideFairing','Fairing_UpperLip','Headlight','PositionLamp','Windscreen','SideVent','VentFin','Body_BellyPan','Body_BellyGraphic','Decal_Belly_')
    for o in list(b.SC.objects):
        if o.name.startswith(prefixes): bpy.data.objects.remove(o,do_unlink=True)
    b.COL=b.C['Body']
    # The top/side split shares exactly the same outer rail; no open assembly gap.
    stations=[(300,110,887,240,790),(360,121,904,249,802),(470,140,936,263,818),
              (590,144,942,271,820),(700,130,923,259,799),(780,113,896,243,764),
              (830,105,878,220,729),(870,89,859,186,697),(915,118,798,147,678),
              (948,70,735,100,661),(960,0,705,46,652)]
    outer=[(xo,y,zo) for y,xi,zi,xo,zo in stations]
    lower=[(239,300,604),(247,360,608),(255,470,615),(254,590,622),(240,700,638),
           (224,780,655),(208,830,670),(183,870,681),(146,915,669),(98,948,657),(46,960,652)]
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        upper=[]
        for y,xi,zi,xo,zo in stations:
            upper.append([(s*(xi+(xo-xi)*t+4*math.sin(math.pi*t)),y,zi+(zo-zi)*t+7*math.sin(math.pi*t)) for t in [j/10 for j in range(11)]])
        shell('Body_UpperCowling_'+lab,[dense_grid(upper)],'blue')
        top=[(184,-190,635),(207,-40,687),(229,110,740)]+outer
        low=[(176,-190,581),(196,-40,584),(216,110,594)]+lower
        rows=[]
        for a,z in zip(top,low):
            rows.append([(s*(a[0]*(1-t)+z[0]*t+4*math.sin(math.pi*t)),a[1]*(1-t)+z[1]*t,a[2]*(1-t)+z[2]*t) for t in [j/10 for j in range(11)]])
        # Broad sculpted forward leg, with the characteristic rear opening for the engine.
        blade=[]
        for level in range(6):
            row=[]
            for k in range(21):
                t=k/20
                if level==0:
                    p=sample(lower,t*4)
                else:
                    pairs=[((209,308,541),(231,610,557)),((184,304,435),(209,490,445)),
                           ((163,274,323),(182,379,329)),((147,241,224),(157,316,225)),
                           ((143,235,210),(151,304,210))]
                    a,z=pairs[level-1];p=Vector(a)*(1-t)+Vector(z)*t
                    p.x+=3*math.sin(math.pi*t)
                row.append((s*p.x,p.y,p.z))
            blade.append(row)
        ribbon=dense_grid(rows)
        for j in range(15,len(ribbon)):
            q=sample(outer,j/5-3);ribbon[j][0]=(s*q.x,q.y,q.z)
        shell('Body_SideFairing_'+lab,[ribbon,dense_grid(blade)],'blue')
        # Recessed outlet beneath the black tank surround, rather than a floating plate.
        b.panel('SideVent_'+lab,[(s*216,36,709),(s*240,267,770),(s*244,305,743),(s*224,126,690)],'ink',3,2)
        for j in range(3):b.tube('VentFin_'+lab,[(s*(225+j*3),110+j*44,707+j*10),(s*(230+j*4),148+j*44,729+j*10)],1.5,'gun')
        belly=[[(s*124,-263,176),(s*143,-263,205),(s*144,-263,224)],
               [(s*126,-136,169),(s*157,-136,201),(s*155,-136,236)],
               [(s*130,95,169),(s*161,95,209),(s*157,95,246)],
               [(s*134,236,178),(s*158,236,210),(s*149,236,227)],
               [(s*134,304,192),(s*151,304,210),(s*151,304,215)]]
        shell('Body_BellyPan_'+lab,[dense_grid(belly)],'blue')
        # A broad white lower graphic, separate from the structural shell.
        graphic=[[(s*145,-237,202),(s*146,-231,216)],[(s*158,-136,198),(s*157,-136,228)],
                 [(s*162,83,202),(s*159,83,237)],[(s*158,208,207),(s*151,227,220)],[(s*149,267,207),(s*151,281,215)]]
        shell('Body_BellyGraphic_'+lab,[dense_grid(graphic)],'white',.2)
        b.text_obj('Decal_Belly_'+lab,'SUZUKI',(s*166,1,215),24,'ink',(s,0,0),(0,s,0),None,0)
    # Black lower nose carries the clear central lamp; lamp and cowling share a flush perimeter.
    outline=[(-82,872,872),(0,888,866),(82,872,872),(106,909,813),(97,932,777),
             (62,957,718),(0,969,676),(-62,957,718),(-97,932,777),(-106,909,813)]
    def lamp_cap(name,points,key,offset=0,bulge=5):
        # Sample the silhouette explicitly so smoothing cannot round the shield into an oval.
        original=points;points=[]
        for i in range(len(original)):
            a=Vector(original[i]);z=Vector(original[(i+1)%len(original)])
            points.extend([a.lerp(z,j/5) for j in range(5)])
        center=Vector((0,(852 if name=='Headlight_Reflector' else 921)+offset,794));N=len(points);verts=[]
        for k in [1,.96,.82,.58,.3,.025]:
            for p in points:
                q=center+(Vector((p[0],p[1]+offset,p[2]))-center)*k;q.y+=bulge*(1-k*k);verts.append(q)
        faces=[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(5) for i in range(N)]+[tuple(range(5*N,6*N))]
        if name=='Headlight_Bezel':faces=faces[:2*N]
        o=b.mesh(name,verts,faces,key,smo=name!='Headlight_Reflector')
        if name!='Headlight_Reflector':
            m=o.modifiers.new('Optical surface','SUBSURF');m.levels=1;m.render_levels=1
        return o
    lamp_cap('Headlight_Bezel',[(x*1.14,y-4,786+(z-786)*1.2) for x,y,z in outline],'gloss',-3,3)
    lamp_cap('Headlight_Reflector',outline,'silver',-5,2)
    lamp_cap('Headlight',outline,'glass',0,3)
    b.sphere('Headlight_Bulb',(0,862,790),(17,9,17),'gun')
    b.sphere('Headlight_BulbLens',(0,870,790),(10,6,12),'glass')
    b.tube('Headlight_BulbRim',[(18*math.cos(j*math.tau/48),868,790+18*math.sin(j*math.tau/48)) for j in range(48)],1.2,'steel',True,False)
    for s in [-1,1]:
        lab='L' if s<0 else 'R'
        # Slender position-light triangles flare outward, as visible in photo 66.
        p=[(s*107,871,846),(s*191,833,835),(s*146,897,774)]
        b.panel('PositionLamp_Bezel_'+lab,[(x*1.045,y-2,815+(z-815)*1.09) for x,y,z in p],'gloss',4,2)
        b.panel('PositionLamp_Reflector_'+lab,p,'silver',1,1)
        b.panel('PositionLamp_'+lab,[(x,y+2,z) for x,y,z in p],'glass',1,1)
        # Chin sides close the lamp/fork region without blocking the radiator aperture.
        shell('Headlight_Undertray_'+lab,[dense_grid([[(s*123,916,743),(s*151,901,702),(s*163,850,640)],
                 [(s*71,954,708),(s*104,944,675),(s*116,863,628)],
                 [(0,970,698),(0,968,662),(0,869,623)]])],'black',3)
    # Bowed transparent PC screen sits above the headlamp, with a rubber mounting bead.
    wind=[]
    for y,z,w in [(869,879,91),(835,916,116),(754,1004,147),(676,1084,151),(665,1098,148)]:
        wind.append([(w*t,y-25*t*t,z-4*t*t) for t in [j/10 for j in range(-10,11)]])
    shell('Windscreen',[dense_grid(wind)],'wind',2.5)
    b.tube('Windscreen_BaseSeal',[(91*t,869-25*t*t,879-4*t*t) for t in [-1,-.75,-.5,-.25,0,.25,.5,.75,1]],3,'black')
    for s in [-1,1]:
        for x,y,z in [(105,814,917),(139,737,999)]:b.bolt('Windscreen_Fastener',(s*x,y,z),4.5,(0,1,.7))
    bpy.context.view_layer.update()
    # Regenerate artwork on the changed shell rather than moving old floating decals.
    decals.fix()
    paint=next(n for n in b.M['blue'].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    paint.inputs['Base Color'].default_value=(.0015,.052,.31,1);paint.inputs['Metallic'].default_value=.08;paint.inputs['Roughness'].default_value=.29;paint.inputs['Coat Weight'].default_value=.3
    for matname,ratio in [('MAT_Windscreen_PC',.018),('MAT_Headlight_Glass',.05)]:
        for node in bpy.data.materials[matname].node_tree.nodes:
            if node.type=='MIX_SHADER':node.inputs[0].default_value=ratio
    b.SC['revision']='r6.2: continuous fairing boundaries and recessed photo-based front assembly'
    b.SC['cowling_rail_join_gap_mm']=0.0
    bpy.ops.file.pack_all();b.save('09_lighting_render');b.save('10_final')
    return {'revision':b.SC['revision'],'objects':len(b.SC.objects),'cowling_rail_join_gap_mm':0}

if __name__=='__main__':print(refine_surfaces())
