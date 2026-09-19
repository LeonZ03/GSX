"""Replay r26 from the local frozen r20 source, refusing existing outputs."""
from pathlib import Path
import bpy,sys,runpy
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];prefix=args[0] if args else 'replay_r26'
if not prefix or not all(c.isalnum() or c in '_-' for c in prefix):raise ValueError('Invalid prefix')
final=V/f'blends/{prefix}_final.blend'
if final.exists():raise FileExistsError(final)
sys.argv=['replay_r25.py','--',prefix+'_r25'];runpy.run_path(str(V/'scripts/replay_r25.py'),run_name='__main__')
from rebuild_rearsets import apply
apply(bpy.context.scene,V/'data/revisions/r26/rearset_control.json',final)
