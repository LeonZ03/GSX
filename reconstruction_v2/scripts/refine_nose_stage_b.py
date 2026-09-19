"""Second front-shell candidate: align shared rims and remove floating crown wings."""
from pathlib import Path
import json,sys,bpy
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_body_stage_b import setup_helpers,supported_rows,data
import build_gray as bg

def apply(scene):
 if scene.objects.get('Body_NoseAssembly'):raise ValueError('Historical pass must not replace live assembly controls')
 setup_helpers(scene);D=V/'calibration/r15_body_frozen/control_cages';candidates={}
 if not D.exists():raise FileNotFoundError('Historical r15 frozen controls required')
 lamp=json.loads((D/'Headlight_Surround.json').read_text())['grid'];wind=json.loads((D/'Windscreen.json').read_text())['grid']
 # Screen's lower edge and lamp's upper rim now share a short physical bridge.
 a=lamp[0];b=wind[0];grid=[]
 for t in [0,.04,.25,.75,.96,1]:grid.append([list(Vector(p).lerp(Vector(q),t)+Vector((0,-2,1))) for p,q in zip(a,b)])
 candidates['Body_NoseCrown']=data('Body_NoseCrown',grid,crease=.5)
 # Preserve the visible lamp frame; re-use the first candidate's cheek, whose
 # outer rail supplies identical endpoints for the side return and screen wing.
 cheek=json.loads((V/'qa/stage_b_r16/Body_NoseCheek.json').read_text());candidates['Body_NoseCheek']=cheek
 outer=[row[-1] for row in cheek['grid']]
 upper=[[149,550,935],[156,630,925]]+outer[1:7]
 lower=[[137,610.8441,826.2559],[135,611.2848,829.5119],[103,677.4546,798.273],[104,746.8559,728.0377],
        [87,765.7084,744.6254],[58,778.4583,731.1846],[40,810,713],[34,820,711]]
 candidates['Body_NoseSideReturn']=data('Body_NoseSideReturn',supported_rows(upper,lower,0),sub=2,crease=.65)
 inside=[wind[0][-1],wind[1][-1],wind[2][-1]]
 outside=[outer[2],outer[1],[156,630,925]]
 candidates['Body_WindscreenSeat']=data('Body_WindscreenSeat',supported_rows(inside,outside,0),sub=2,crease=.65)
 # Front boundary of the black inner shroud meets the raised mirror-base return.
 d=json.loads((D/'Cockpit_InnerPanel.json').read_text());p=Vector((149,550,935));q=Vector(d['grid'][-1][-1]);nc=len(d['grid'][-1])
 d['grid'][-1]=[list(p.lerp(q,j/(nc-1))) for j in range(nc)];d['crease_boundary']=.65;candidates['Cockpit_InnerPanel']=d
 out=V/'qa/stage_b_r18';out.mkdir(exist_ok=True)
 for name,d in candidates.items():
  d['revision']='r18';d['status']='CANDIDATE_REQUIRES_MULTIVIEW_REVIEW'
  old=scene.objects.get(name)
  if old:bpy.data.objects.remove(old,do_unlink=True)
  ob=bg.cage(d);ob['stage_b_revision']='r18';(out/(name+'.json')).write_text(json.dumps(d,indent=2),encoding='utf8')
 bpy.context.view_layer.update();return {'changed':list(candidates),'camera_changes':False}
