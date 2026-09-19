"""Reconstruct missing nose wrapping and supported side-panel folds on isolated r15.

The new surfaces are editable quad cages. Coordinates are photo-led estimates,
not measured dimensions. Cameras and the accepted local tank/seat interface stay fixed.
Run via Blender MCP; this module does not publish or read private registration.
"""
from pathlib import Path
import bpy, json, sys, math, hashlib, shutil
from mathutils import Vector

V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
import build_gray as bg

def setup_helpers(scene):
    b=bg.b; b.SC=scene
    bg.C.clear()
    for key in ['Reference','Blockout','Wheels','FrontEnd','Engine','Body','Details','Materials','Lights','Cameras']:
        bg.C[key]=next(c for c in scene.collection.children if c.name.startswith('Collection_'+key))
    b.C=bg.C
    bg.M.clear()
    sources={'shell':'Body_SideFairing','tank':'Body_Tank','trim':'Body_TankSideTrim','seat':'Seat_Rider','lamp':'Headlight_Lens','wind':'Windscreen'}
    for key,name in sources.items():
        bg.M[key]=scene.objects[name].data.materials[0]
    return b

def supported_rows(a,b,bulge=0):
    """Close support rows preserve observed seams instead of rounding a loose sheet."""
    out=[]
    for p,q in zip(a,b):
        p,q=Vector(p),Vector(q)
        out.append([list(p.lerp(q,t)+Vector((bulge*math.sin(math.pi*t),0,0))) for t in [0,.035,.18,.5,.82,.965,1]])
    return out

def data(name,grid,mat='shell',sub=2,crease=.65):
    return dict(name=name,units='mm',grid=grid,mirror_x=True,subdivision=sub,
                thickness_mm=2.5,material=mat,crease_boundary=crease,
                revision='r16',status='PHOTO_LED_CANDIDATE_NOT_METRIC_ACCEPTED',
                evidence=['owner_photo_62','owner_photo_63','owner_photo_66','owner_photo_69'],
                notes='Editable quad surface; front wrapping and fold placement from visible assembly. Hidden depth is provisional.')

def apply(scene,output):
    if scene.get('revision')!='r15':raise ValueError('Requires an isolated r15 baseline')
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    b=setup_helpers(scene)
    archive=V/'calibration/r15_body_frozen'
    D=archive/'control_cages'
    if not D.exists():raise FileNotFoundError('Historical r15 frozen controls required; never substitute current cages')
    if not (archive/'manifest.json').exists():
        paths=list((V/'calibration').glob('camera_*.json'))+list((V/'annotations').glob('*.json'))
        (archive/'manifest.json').write_text(json.dumps({str(p.relative_to(V)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))
    candidates={}
    # Missing front-facing blue cheek surrounding the central headlamp. The
    # inner rail follows the existing lamp rim; the outer rail wraps to side lips.
    lamp=json.loads((D/'Headlight_Surround.json').read_text())['grid']
    inner=[lamp[0][0]]+[r[-1] for r in lamp]+[lamp[-1][0]]
    outer=[[0,753,897],[177,706,932],[193,737,895],[183,776,850],
           [149,807,800],[99,831,755],[48,837,719],[4,837,704],[0,837,704]]
    # A supported margin remains visible around the lens, with no rear floating plane.
    inner=[[p[0],p[1]-1.8,p[2]] for p in inner]
    candidates['Body_NoseCheek']=data('Body_NoseCheek',supported_rows(inner,outer,1.0),sub=2,crease=.85)
    # Side return bridges the front cheek to the established cockpit blue lip.
    upper=[[168,498,902],[156,585,938],[177,706,932],[193,737,895],[183,776,850],[149,807,800],[99,831,755],[48,837,719]]
    lower=[[197,491,802],[179,560,811],[135,611,830],[117,658,812],
           [103,677,798],[83,722,756],[58,779,733],[34,810,711]]
    candidates['Body_NoseSideReturn']=data('Body_NoseSideReturn',supported_rows(upper,lower,3),sub=2,crease=.75)
    # A short crown joins the windscreen base to the headlamp brow; separate
    # from the side cheek, so the screen remains an editable removable component.
    wind=json.loads((D/'Windscreen.json').read_text())['grid']
    brow=[[0,753,897],[45,752,898],[86,737,908],[130,724,917],[177,706,932]]
    back=[[0,747,904],[40,738,912],[81,713,916],[124,666,947],[156,585,938]]
    # Full-width surface grid begins on X=0; mirror welds only this real seam.
    grid=[]
    for t in [0,.05,.25,.75,.95,1]:grid.append([list(Vector(p).lerp(Vector(q),t)) for p,q in zip(brow,back)])
    candidates['Body_NoseCrown']=data('Body_NoseCrown',grid,sub=2,crease=.65)
    # Side fairing has a distinct shoulder/fold, not a uniformly inflated ribbon.
    # Keep both observed edge rails; reshape only interior controls and preserve
    # the lower engine opening. Supporting columns preserve the shoulder crease.
    for name in ['Body_SideFairing','Body_TankSideTrim','Body_SeatSide']:
        d=json.loads((D/f'{name}.json').read_text());g=d['grid']
        for row in g:
            p,q=Vector(row[0]),Vector(row[-1])
            # Three-plane transverse profile, restrained inward return below fold.
            for j,t in enumerate([0,.04,.20,.46,.74,.96,1]):
                co=p.lerp(q,t)
                if name=='Body_SideFairing':co.x+=math.sin(math.pi*t)*4
                elif name=='Body_TankSideTrim':co.x+=math.sin(math.pi*t)*2
                else:co.x+=math.sin(math.pi*t)*2
                row[j]=list(co)
        d['grid']=g;d['crease_columns']={'2':.45,'4':.25};d['revision']='r16'
        d['notes']+=' r16: flattened inflated interior; observed edge rails unchanged.'
        candidates[name]=d
    for name,d in candidates.items():
        old=scene.objects.get(name)
        if old:
            # Existing topology stays unchanged; preserve interface modifiers.
            if len(old.data.vertices)!=sum(len(r) for r in d['grid']):raise ValueError(name+' topology mismatch')
            for v,p in zip(old.data.vertices,sum(d['grid'],[])):v.co=Vector(p)*.001
            bg.apply_creases(old,d);old.data.update();o=old
        else:o=bg.cage(d)
        o['stage_b_revision']='r16';o['acceptance']='NOT_PASSED'
    # Distinct neutral values make seams reviewable; this is diagnostic gray,
    # not an attempted final paint/plastic calibration.
    for key,value in [('shell',.28),('tank',.28),('trim',.07),('seat',.095),('lamp',.20),('wind',.21)]:
        m=bg.M[key];m.diffuse_color=(value,value,value,1)
        next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(value,value,value,1)
    scene['revision']='r16';scene.name='GSX250R_Reconstruction_V2_Gray_r16'
    scene['stage_B']='IN_PROGRESS';scene['visual_acceptance']='NOT_PASSED'
    bpy.context.view_layer.update()
    dest=V/'qa/stage_b_r16';dest.mkdir(exist_ok=True)
    for name,d in candidates.items():(dest/f'{name}.json').write_text(json.dumps(d,indent=2),encoding='utf8')
    bpy.data.libraries.write(str(output),{scene},fake_user=True)
    return {'source':str(output),'changed':list(candidates),'cameras_changed':False,'gate':'NOT_PASSED'}

if __name__=='__main__':
    result=apply(bpy.context.scene,V/'blends/16_body_candidate.blend')
