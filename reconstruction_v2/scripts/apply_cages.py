"""Synchronize the protected control cage JSON into an isolated V2 source file."""
from pathlib import Path
import bpy,json,sys
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_Reconstruction_V2_Gray'));bpy.context.window.scene=s
ns={'__name__':'gsx_api','__file__':str(V2/'scripts/build_gray.py')};exec(compile((V2/'scripts/build_gray.py').read_text(encoding='utf8'),ns['__file__'],'exec'),ns)
ns['C'].update({k:next(c for c in s.collection.children if c.name.startswith('Collection_'+k)) for k in ['Body','FrontEnd']})
existing={Path(o['control_cage_source']).stem:o for o in s.objects if o.get('control_cage_source')}
for name,o in existing.items():
 a=json.loads((V2/f'data/control_cages/{name}.json').read_text());ns['M'][a['material']]=o.data.materials[0]
for p in sorted((V2/'data/control_cages').glob('*.json')):
 a=json.loads(p.read_text())
 if a['name'] not in existing:ns['cage'](a);continue
 o=existing[a['name']];rows=a['grid'];nr=len(rows);nc=len(rows[0]);verts=[v for row in rows for v in row]
 # Preserve sculpted source only when the cage shape/count still agrees; JSON is explicit authority for this command.
 if len(o.data.vertices)!=len(verts):raise RuntimeError('Topology changed: explicit mesh migration required for '+a['name'])
 for v,pco in zip(o.data.vertices,verts):v.co=[x*.001 for x in pco]
 o.data.update()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
name=args[0] if args else '04_gray_review.blend'
if Path(name).name!=name or not name.endswith('.blend'):raise ValueError('Output must be a local .blend filename')
s['revision']='r04';s['visual_acceptance']='NOT_PASSED';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(V2/'blends'/name));print('CAGE_SYNC_SAVED',name)
