"""Synchronize the protected control cage JSON into an isolated V2 source file."""
from pathlib import Path
import bpy,json,sys,re
from datetime import datetime
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
 expected={tuple(sorted(f)) for f in ns['cage_faces'](a)}
 if len(o.data.vertices)!=len(verts) or {tuple(sorted(f.vertices)) for f in o.data.polygons}!=expected:raise RuntimeError('Topology changed: explicit mesh migration required for '+a['name'])
 for v,pco in zip(o.data.vertices,verts):v.co=[x*.001 for x in pco]
 ns['apply_creases'](o,a)
 sub=next((m for m in o.modifiers if m.name=='Editable_Subdivision'),None)
 if sub:sub.levels=a['subdivision'];sub.render_levels=a['subdivision']
 solid=next((m for m in o.modifiers if m.name=='Shell_Thickness'),None)
 if solid and not a.get('thickness_mm'):o.modifiers.remove(solid)
 elif a.get('thickness_mm'):
  if solid is None:solid=o.modifiers.new('Shell_Thickness','SOLIDIFY');solid.offset=-1
  solid.thickness=a['thickness_mm']*.001
 o.data.update()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
name=args[0] if args else 'working_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend'
if Path(name).name!=name or not name.endswith('.blend'):raise ValueError('Output must be a local .blend filename')
target=V2/'blends'/name
if target.exists() or target.resolve()==Path(bpy.data.filepath).resolve():raise FileExistsError('Choose a new output filename; existing source files are protected')
stem=Path(name).stem;match=re.match(r'^(?:r)?(\d+)(?:_|$)',stem)
revision=args[1] if len(args)>1 else ('r'+match.group(1).zfill(2) if match else s.get('revision','working'))
if not re.fullmatch(r'r\d+|working',revision):raise ValueError('Revision must be rNN or working')
s['revision']=revision
s['visual_acceptance']='NOT_PASSED';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(V2/'blends'/name));print('CAGE_SYNC_SAVED',name)
