"""r31 headlamp bowl/black chin candidate from owner front detail and OEM front.
Fixed photo cameras. Shape estimates remain subject to multi-view review.
"""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));import build_gray as bg

def apply(scene,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    if scene.get('revision')!='r30':raise ValueError('Requires isolated r30')
    host=scene.objects['Body_NoseAssembly'];flags=[m.show_viewport for m in host.modifiers]
    for m in host.modifiers:m.show_viewport=False
    names=['Headlight_Lens','Headlight_Surround','Body_NoseCheek','Body_NoseSideReturn'];data={}
    for n in names:
        d=json.loads((V/'data/control_cages'/f'{n}.json').read_text());o=scene.objects[n];nc=len(d['grid'][0]);d['grid']=[[list(v.co*1000) for v in o.data.vertices[i:i+nc]] for i in range(0,len(o.data.vertices),nc)];data[n]=d
    for n,widths in [('Headlight_Lens',[83,105,115,105,85,50,18]),('Headlight_Surround',[91,120,128,118,98,60,22])]:
        for row,w in zip(data[n]['grid'],widths):
            old=row[-1][0]
            for p in row:p[0]*=w/old
    cheek=data['Body_NoseCheek'];g=cheek['grid'][:6]
    rim=data['Headlight_Surround']['grid']
    for i in range(1,6):
        p=Vector(rim[i-1][-1])+Vector((0,-1.8,0));q=Vector(g[i][-1])
        if i==5:q.x=124
        g[i]=[list(p.lerp(q,t)) for t in [0,.035,.18,.5,.82,.965,1]]
    cheek['grid']=g;cheek['notes']+=' r31 remove blue central underside; black lamp surround remains visible below U-shaped lens.'
    ret=data['Body_NoseSideReturn']['grid']
    for i,p,q in [(6,[124,831,755],[190,746,707]),(7,[100,837,719],[190,746,699])]:ret[i]=[list(Vector(p).lerp(Vector(q),t)) for t in [0,.035,.18,.5,.82,.965,1]]
    dst=V/'data/revisions/r31_front_candidate';dst.mkdir(exist_ok=True)
    for n,d in data.items():
        o=scene.objects[n];old=o.data;me=bpy.data.meshes.new(n+'_r31');me.from_pydata([[x*.001 for x in p] for row in d['grid'] for p in row],[],bg.cage_faces(d));me.update()
        for mat in old.materials:me.materials.append(mat)
        for f in me.polygons:f.use_smooth=True
        o.data=me;bg.apply_creases(o,d);d['revision']='r31';d['status']='SHAPE_CANDIDATE_NOT_PASSED';o['control_cage_source']=f'reconstruction_v2/data/revisions/r31_front_candidate/{n}.json';(dst/f'{n}.json').write_text(json.dumps(d,indent=2))
    for m,f in zip(host.modifiers,flags):m.show_viewport=f
    scene['revision']='r31';scene.name='GSX250R_Reconstruction_V2_Gray_r31';scene['stage_B']='NOT_PASSED'
    bpy.data.libraries.write(str(output),{scene},fake_user=True);return {'saved':str(output),'changed':names,'stage_B':'NOT_PASSED'}
