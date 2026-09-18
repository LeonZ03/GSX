"""Import each delivered format in a fresh scene and check units, bounds and materials."""
import bpy,json,sys,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
formats=['GLB','FBX','OBJ'];report={}
for fmt in formats:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    start=time.time();p=ROOT/'exports'/('GSX250R.'+fmt.lower())
    if fmt=='GLB':bpy.ops.import_scene.gltf(filepath=str(p))
    elif fmt=='FBX':bpy.ops.import_scene.fbx(filepath=str(p),use_anim=False)
    else:bpy.ops.wm.obj_import(filepath=str(p),forward_axis='Y',up_axis='Z')
    obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(co) for o in obs for co in o.bound_box]
    report[fmt]={'meshes':len(obs),'bounds_mm':[round((max(v[i] for v in pts)-min(v[i] for v in pts))*1000,3) for i in range(3)],'vertices':sum(len(o.data.vertices) for o in obs),'missing_materials':sum(len(o.data.materials)==0 for o in obs),'missing_uv':sum(not o.data.uv_layers for o in obs),'seconds':round(time.time()-start,2)}
    (ROOT/'qa/roundtrip.json').write_text(json.dumps(report,indent=2))
print('GSX_ROUNDTRIP_COMPLETE',json.dumps(report))
