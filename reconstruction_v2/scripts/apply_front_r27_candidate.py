"""Replay the explicitly UNACCEPTED r27 front candidate on an isolated r26 scene.
The canonical control_cages directory remains r26. This does not certify stage B.
"""
from pathlib import Path
import json,sys,bpy
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
import build_gray as bg
NAMES=('Body_SideFairing','Body_UpperCowling','Body_CowlingSide','Cockpit_InnerPanel')
def apply(scene,output):
    output=Path(output)
    if scene.get('revision')!='r26':raise ValueError('Requires isolated r26 baseline')
    if output.exists():raise FileExistsError(output)
    for n in NAMES:
        d=json.loads((V/'data/revisions/r27_front_candidate'/f'{n}.json').read_text())
        o=scene.objects[n];old=o.data;me=bpy.data.meshes.new(n+'_r27_QuadControls')
        me.from_pydata([[x*.001 for x in p] for r in d['grid'] for p in r],[],bg.cage_faces(d));me.update()
        for m in old.materials:me.materials.append(m)
        for p in me.polygons:p.use_smooth=True
        o.data=me;bg.apply_creases(o,d)
        o['control_source']=f'data/revisions/r27_front_candidate/{n}.json';o['acceptance']='UNACCEPTED_REVIEW_CANDIDATE'
    scene['revision']='r27';scene.name='GSX250R_Reconstruction_V2_Gray_r27'
    scene['stage_B']='NOT_PASSED';scene['stage_C']='NOT_PASSED';scene['candidate_status']='UNACCEPTED_ASSEMBLY_OVERLAPS'
    bpy.data.libraries.write(str(output),{scene},fake_user=True)
    return {'source':str(output),'changed':list(NAMES),'acceptance':'NOT_PASSED','canonical_controls':'r26 retained'}
