"""Rebuild r37/r38 from an isolated r36 source; refuses output overwrite."""
from pathlib import Path
import bpy,sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))

def run(prefix):
    if not prefix or Path(prefix).name!=prefix:raise ValueError('Use a simple unique output prefix')
    if bpy.context.scene.get('revision')!='r36':raise ValueError('Open an isolated r36 source')
    a=V/'blends'/f'{prefix}_37.blend';b=V/'blends'/f'{prefix}_38.blend'
    for p in [a,b]:
        if p.exists():raise FileExistsError(p)
    import rebuild_tail_assembly_r37 as tail,rebuild_fuel_cap_r38 as cap
    tail.apply(bpy.context.scene,a);cap.apply(bpy.context.scene,b)
    return {'source':str(b),'revision':bpy.context.scene.get('revision')}
