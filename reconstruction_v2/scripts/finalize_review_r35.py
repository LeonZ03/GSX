"""Finalize r35 review checkpoint; caps seat into castings, controls stay editable."""
from pathlib import Path
import bpy,json,hashlib
V=Path(__file__).resolve().parents[1]

def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('revision')!='r34':raise ValueError('Requires r34')
 for n,casting,side in [('Engine_CoverInset_R','Engine_ClutchCover',1),('Engine_CoverInset_L','Engine_AlternatorCover',-1)]:
  o=scene.objects[n];target=(max(v.co.x for v in scene.objects[casting].data.vertices)-.0005) if side==1 else (min(v.co.x for v in scene.objects[casting].data.vertices)+.0005)
  inner=min(v.co.x for v in o.data.vertices) if side==1 else max(v.co.x for v in o.data.vertices)
  for v in o.data.vertices:
   if abs(v.co.x-inner)<1e-6:v.co.x=target
  o.data.update();o['mounting_note']='Rear cap face seated 0.5mm into the cover; nominal construction fit, not measured.'
 folder=V/'data/revisions/r35_controls';folder.mkdir(exist_ok=True);manifest={}
 for o in scene.objects:
  path=o.get('control_cage_source')
  if o.type!='MESH' or not path:continue
  source=V.parent/str(path)
  if not source.exists():continue
  d=json.loads(source.read_text(encoding='utf-8-sig'))
  if 'grid' not in d:continue
  count=sum(len(row) for row in d['grid'])
  if count!=len(o.data.vertices):raise ValueError(f'{o.name}: control source vertex mismatch {count} vs {len(o.data.vertices)}')
  nc=len(d['grid'][0]);d['grid']=[[list(v.co*1000) for v in o.data.vertices[i:i+nc]] for i in range(0,len(o.data.vertices),nc)];d['faces']=[list(p.vertices) for p in o.data.polygons];d['revision']='r35';d['status']='REVIEW_CHECKPOINT_NOT_PASSED';d['superseded_by']=o.get('superseded_by');d['source_revision_file']=str(path)
  file=folder/(o.name+'.json');file.write_text(json.dumps(d,indent=2));o['control_cage_source']=str(file.relative_to(V.parent)).replace('\\','/');manifest[o.name]={'file':str(file.relative_to(V.parent)).replace('\\','/'),'construction_only':bool(o.get('construction_control_only')),'superseded_by':o.get('superseded_by'),'vertices':len(o.data.vertices),'faces':len(o.data.polygons)}
 (folder/'manifest.json').write_text(json.dumps({'revision':'r35','acceptance':'B_AND_C_NOT_PASSED','objects':manifest},indent=2))
 scene['revision']='r35';scene.name='GSX250R_Reconstruction_V2_Gray_r35';scene['stage_B']='NOT_PASSED';scene['stage_C']='NOT_PASSED';scene['control_manifest']='reconstruction_v2/data/revisions/r35_controls/manifest.json';scene['review_note']='New front connection, lamps, exhaust, bilateral engine castings. Appearance and independent-view gates outstanding.'
 bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True)
 return {'saved':str(output),'objects':len(scene.objects),'controls':len(manifest),'active_controls':sum(not d['superseded_by'] for d in manifest.values()),'Blender':bpy.app.version_string,'B':'NOT_PASSED','C':'NOT_PASSED'}
