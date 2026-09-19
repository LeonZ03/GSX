"""Replay the r35 review checkpoint from a frozen r26 source through Blender MCP.
Usage in an isolated process: sys.argv=['replay_r35.py','--','unique_prefix']; runpy...
"""
from pathlib import Path
import bpy,sys,runpy
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];prefix=args[0] if args else 'replay_r35'
if not prefix or not all(c.isalnum() or c in '_-' for c in prefix):raise ValueError('Invalid prefix')
s=bpy.context.scene
if s.get('revision')!='r26':raise ValueError('Requires isolated 26_gray_review.blend')
def out(n):return V/f'blends/{prefix}_{n}.blend'
for n in [27,28,30,31,32,33,34,35]:
 if out(n).exists():raise FileExistsError(out(n))
from apply_front_r27_candidate import apply as r27
from rebuild_front_join_r28 import apply as r28
from rebuild_exhaust_r29 import apply as r29
from rebuild_clutch_r30 import apply as r30
from rebuild_headlamp_r31 import apply as r31
from rebuild_front_frame_r32 import apply as r32
from rebuild_position_lamps_r33 import apply as r33
from rebuild_alternator_r34 import apply as r34
from finalize_review_r35 import apply as r35
r27(s,out(27));r28(s,out(28));r29(s);s['revision']='r29';r30(s,out(30));r31(s,out(31));r32(s,out(32));r33(s,out(33));r34(s,out(34));result=r35(s,out(35))
