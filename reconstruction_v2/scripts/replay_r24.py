"""Replay the reviewed r24 increment from the preserved r20 source.
Run in Blender via MCP or CLI. Refuses reused output files and other baselines.
Photo annotation and camera-fitting scripts are deliberately not rerun.
"""
from pathlib import Path
import bpy,json,sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
D=V/'data/revisions/r24'
if bpy.context.scene.get('revision')!='r20':raise ValueError('Requires preserved r20 source')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];prefix=args[0] if args else 'replay_r24'
if not prefix or not all(c.isalnum() or c in '_-' for c in prefix):raise ValueError('Output prefix must contain only letters, digits, dash or underscore')
outputs=[V/f'blends/{prefix}_{n}.blend' for n in ['mirrors','shock','covers','interfaces']]
if any(p.exists() for p in outputs):raise FileExistsError('Replay output already exists; preserve existing files')
import rebuild_mirror_housings as mirrors
import rebuild_mounts_r21 as shock
import add_missing_side_covers as covers
import repair_cover_interfaces as interfaces
s=bpy.context.scene;mirrors.apply(s,D/'mirror_housing.json',outputs[0])
a=json.loads((D/'Windscreen.json').read_text());o=s.objects['Windscreen']
for v,p in zip(o.data.vertices,[p for row in a['grid'] for p in row]):v.co=[x*.001 for x in p]
o.data.update();shock.apply(s,outputs[1]);covers.apply(s,D/'Body_FrameSidePanel.json',D/'sprocket_cover.json',outputs[2]);interfaces.apply(s,outputs[3])
print('Replay saved',outputs[-1])
