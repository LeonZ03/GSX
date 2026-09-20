"""Explicit r45-to-r46 migration. Never replay on a refined work file."""
from pathlib import Path
import bpy,json,sys
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))

def run(save=True):
    from rebuild_guard_product_reference import apply as guard
    from refine_tank_product_reference import apply_supported as tank
    from audit_product_refinement import run as audit
    s=bpy.context.scene
    if s.get('revision')!='r45':raise ValueError('Requires checkpointed r45 source')
    changes={'guard':guard(s),'tank':tank(s)}
    s['revision']='r46';s.name='GSX250R_Reconstruction_V2_Gray_r46'
    s['stage_B']=s['stage_C']='NOT_PASSED'
    report=audit('r46')
    assert not any(q['nonmanifold'] or q['zero_area'] for q in report['quality'].values())
    assert all(report['quality'][n]['connected_components']==1 for n in ['GuardBar_L','GuardBar_R','Body_Tank'])
    assert report['guard_surface_mirror_max_mm']<.0001
    assert report['tank_self_intersection']['unresolved']==0
    assert all(v['intersection_pairs']==0 for v in report['clearance'].values())
    p=V/'data/current_controls/Body_Tank.json';d=json.loads(p.read_text());d.update(revision='r46',current_snapshot='r46',revision_note='Product shoulder, knee hollow and lower pressed lip; 10x12 control grid. Full modifier chain required, including majority-shell filter.')
    p.write_text(json.dumps(d,indent=2))
    if save:
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
    return changes
