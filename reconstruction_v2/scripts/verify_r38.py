"""Compare independent replay geometry, cameras, curve shape and selected modifiers."""
from pathlib import Path
import bpy,json,sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from audit_stage_bc import signature

def snapshot(scene):
    out={}
    for o in scene.objects:
        mods=[]
        for m in o.modifiers:
            d={'name':m.name,'type':m.type}
            for k in ['operation','solver','width','segments','levels','render_levels','thickness','offset','merge_threshold','show_viewport','show_render']:
                if hasattr(m,k):d[k]=getattr(m,k)
            if hasattr(m,'object'):d['object']=m.object.name if m.object else None
            mods.append(d)
        value={'signature':signature(o),'modifiers':mods,'hide_render':o.hide_render,'hidden':o.hide_get()}
        if o.type=='CURVE':
            value['curve']={'bevel':o.data.bevel_depth,'resolution':o.data.resolution_u,'caps':o.data.use_fill_caps,'handles':[[[list(p.handle_left),list(p.handle_right),p.handle_left_type,p.handle_right_type] for p in s.bezier_points] for s in o.data.splines]}
        out[o.name]=value
    return out

def verify(reference):
    replay=bpy.data.filepath;now=snapshot(bpy.context.scene)
    bpy.ops.wm.open_mainfile(filepath=str(reference));old=snapshot(bpy.context.scene)
    missing=sorted(set(old)-set(now));extra=sorted(set(now)-set(old));different=[n for n in old if n in now and old[n]!=now[n]]
    r={'replay':replay,'reference':str(reference),'objects':len(now),'missing':missing,'extra':extra,'different':different,'scope':'Source geometry/transforms/camera/curve handles/selected modifiers/visibility, not full material or evaluated mesh equivalence.'}
    (V/'qa/replay_r38.json').write_text(json.dumps(r,indent=2));return r
