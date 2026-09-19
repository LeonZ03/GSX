"""r34 left alternator casting from the visible owner-photo silhouette.
Single-view depth remains provisional; no claim of an unseen exact casting.
"""
from pathlib import Path
import bpy,json,sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_clutch_r30 import loft,cylinder

def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('revision')!='r33':raise ValueError('Requires isolated r33')
 d=json.loads((V/'data/revisions/r34_engine_candidate/alternator_cover.json').read_text());old=scene.objects['Engine_AlternatorCover'];mat=old.data.materials[0];steel=scene.objects['BrakeDisc_Front'].data.materials[0];outline=d['outline_mm'];cx,cy,cz=d['inset_center_mm']
 rings=[]
 for x,scale in [(-143,1),(-151,1),(-173,.97),(-177,.93)]:rings.append([[x,cy+(p[1]-cy)*scale,cz+(p[2]-cz)*scale] for p in outline])
 tmp=loft(scene,'Temporary_Alternator_r34',rings,mat,1.2);old.data=tmp.data;old.modifiers.clear();m=old.modifiers.new('Casting_edge_radius','BEVEL');m.width=.0012;m.segments=3;bpy.data.objects.remove(tmp,do_unlink=True)
 old['evidence']='owner69 visible outline, family FIG112A; depth remains provisional';old['control_cage_source']='reconstruction_v2/data/revisions/r34_engine_candidate/alternator_cover.json'
 helper=scene.objects['Tool_SprocketCoverClearance'];helper.data=old.data
 for m in helper.modifiers:
  if m.type=='BEVEL':m.width=.0012;m.segments=3
 for o in list(scene.objects):
  if o.name=='Engine_CoverInset_L' or o.name.startswith(('Engine_BoltBoss_L','Crankcase_Bolt_L')):bpy.data.objects.remove(o,do_unlink=True)
 cap=cylinder(scene,'Engine_CoverInset_L',[cx,cy,cz],d['inset_radius_mm'],5,mat,64)
 tool=cylinder(scene,'Tool_AlternatorHexSocket',[cx-2,cy,cz],4.0,4,mat,6);tool.hide_render=True;tool.hide_set(True);tool['export_exclude']=True;tool.display_type='WIRE'
 m=cap.modifiers.new('Access_HexSocket','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool
 for i,p in enumerate(d['visible_bolt_centers_mm']):
  cylinder(scene,f'Engine_BoltBoss_L_{i}',[-171,p[1],p[2]],7.5,10,mat,24)
  cylinder(scene,f'Crankcase_Bolt_L_{i}',[-178,p[1],p[2]],4.2,4,steel,6)
 scene['revision']='r34';scene.name='GSX250R_Reconstruction_V2_Gray_r34';scene['stage_C']='NOT_PASSED';bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True)
 return {'saved':str(output),'left_access_cap_radius_mm':d['inset_radius_mm'],'single_view_depth_unverified':True}
