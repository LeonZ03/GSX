"""Compare replay and protected baseline, without mutating either file."""
from pathlib import Path
import bpy,json,sys,hashlib
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));from audit_stage_bc import signature

def capture():
 bpy.context.view_layer.update();s=bpy.context.scene
 return {'objects':{o.name:signature(o) for o in s.objects},'cameras':{o.name:signature(o) for o in s.objects if o.type=='CAMERA' and o.get('image_id')},'modifiers':{o.name:[(m.name,m.type,m.show_viewport,m.show_render,[(key,getattr(m,key)) for key in ['width','segments','levels','render_levels','thickness','offset','merge_threshold','operation','solver','voxel_size'] if hasattr(m,key)],getattr(m,'object',None).name if getattr(m,'object',None) else None) for m in o.modifiers] for o in s.objects},'visibility':{o.name:(o.hide_render,bool(o.get('export_exclude')),bool(o.get('construction_control_only'))) for o in s.objects}}

def run():
 current=capture();bpy.ops.wm.open_mainfile(filepath=str(V/'blends/verify_r35_35.blend'));replay=capture();bpy.ops.wm.open_mainfile(filepath=str(V/'blends/26_gray_review.blend'));base=capture()
 report={'objects':len(current['objects']),'replay_geometry_differences':[n for n,h in current['objects'].items() if replay['objects'].get(n)!=h],'replay_modifier_differences':[n for n,h in current['modifiers'].items() if replay['modifiers'].get(n)!=h],'replay_visibility_differences':[n for n,h in current['visibility'].items() if replay['visibility'].get(n)!=h],'replay_extra':sorted(set(replay['objects'])-set(current['objects'])),'baseline_camera_differences':[n for n,h in base['cameras'].items() if current['cameras'].get(n)!=h],'changed_from_r26':[n for n,h in base['objects'].items() if current['objects'].get(n)!=h],'added':sorted(set(current['objects'])-set(base['objects'])),'scope':'Object control geometry, transforms, camera intrinsics, selected modifier properties and visibility. Not complete evaluated-mesh/material equality.'}
 (V/'qa/replay_r35.json').write_text(json.dumps(report,indent=2));return report
