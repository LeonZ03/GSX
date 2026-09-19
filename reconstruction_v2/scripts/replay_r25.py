"""Replay the reviewed r25 result from r20 using a fresh local output prefix."""
from pathlib import Path
import bpy,sys,runpy
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];prefix=args[0] if args else 'replay_r25'
if not prefix or not all(c.isalnum() or c in '_-' for c in prefix):raise ValueError('Invalid output prefix')
final=V/f'blends/{prefix}_final.blend'
if final.exists():raise FileExistsError(final)
sys.argv=['replay_r24.py','--',prefix];runpy.run_path(str(V/'scripts/replay_r24.py'),run_name='__main__')
from resolve_midcover_duplicate import apply
apply(bpy.context.scene,final)
