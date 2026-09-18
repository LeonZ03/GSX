"""Export evaluated meshes with consistent UVs, PBR approximations and round-trip QA."""
import bpy,bmesh,json,math,sys,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
window=bpy.context.window_manager.windows[0];window.scene=source
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
export_scene=bpy.data.scenes.new('GSX250R_Export');export_scene.unit_settings.system='METRIC';export_scene.unit_settings.scale_length=1
export_col=bpy.data.collections.new('GSX250R');export_scene.collection.children.link(export_col)
matmap={};mapping=[];bad=[]
for old in list(source.objects):
    if old.type not in {'MESH','CURVE','FONT'} or old.name.startswith('Studio') or old.hide_render:continue
    ev=old.evaluated_get(deps);data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
    if len(data.vertices)==0:bpy.data.meshes.remove(data);bad.append(old.name);continue
    # World transforms are baked once; real metre units are kept in each export.
    data.transform(old.matrix_world);ob=bpy.data.objects.new(old.name+'_Export',data);export_col.objects.link(ob)
    ob['source_name']=old.name;mapping.append((ob,old.name));ob.name=old.name+'_EXPORT'
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    if not data.uv_layers:data.uv_layers.new(name='UVMap')
    uv=data.uv_layers.active
    # Box projection normalized per object, useful for uniform PBR surfaces. Artwork is geometry.
    lo=[min(v.co[i] for v in data.vertices) for i in range(3)];hi=[max(v.co[i] for v in data.vertices) for i in range(3)]
    for p in data.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            co=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=tuple((co[i]-lo[i])/max(hi[i]-lo[i],1e-6) for i in axes)
    for i,mat in enumerate(list(data.materials)):
        if not mat:continue
        if mat.name not in matmap:
            copy=mat.copy();copy.name=mat.name+'_Export'
            if any(n.type=='BSDF_GLASS' for n in copy.node_tree.nodes):
                copy.node_tree.nodes.clear();out=copy.node_tree.nodes.new('ShaderNodeOutputMaterial');p=copy.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.94,.97,1,1);p.inputs['Roughness'].default_value=.055;p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46;copy.node_tree.links.new(p.outputs[0],out.inputs['Surface'])
            matmap[mat.name]=copy
        data.materials[i]=matmap[mat.name]
window.scene=export_scene
# Lay out a separate UV tile per editable part; unrelated parts may reuse the tile.
# Materials are procedural or solid colors, so this does not alter the rendered paint.
bpy.ops.object.select_all(action='DESELECT')
uv_invalid=[]
for index,(ob,source_name) in enumerate(mapping):
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015,margin_method='FRACTION',correct_aspect=True,scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
    if any(not math.isfinite(c) or c<-.0001 or c>1.0001 for item in ob.data.uv_layers.active.data for c in item.uv):uv_invalid.append(source_name)
    if index%100==0:print('UV_UNWRAP',index,len(mapping),flush=True)
assert not uv_invalid, 'UV coordinates outside the normalized tile'
for o in export_col.objects:o.select_set(True)
bpy.context.view_layer.objects.active=next(iter(export_col.objects))
# Preserve exact readable names, then restore source names after saving/exporting.
for o,name in mapping:bpy.data.objects[name].name=name+'_Source';o.name=name
out=ROOT/'exports';out.mkdir(exist_ok=True)
report={'source_version':bpy.app.version_string,'objects':len(mapping),'vertices':sum(len(o.data.vertices) for o,n in mapping),'polygons':sum(len(o.data.polygons) for o,n in mapping),'uv_missing':sum(not o.data.uv_layers for o,n in mapping),'materials_missing':sum(not len(o.data.materials) for o,n in mapping),'empty_objects_removed':bad,'formats':{},'uv_layout':'Smart UV Project, separate 0-1 tile per object, 0.015 island margin','uv_invalid':uv_invalid}
pts=[v.co for o,n in mapping for v in o.data.vertices];report['bounds_mm']=[(max(p[i] for p in pts)-min(p[i] for p in pts))*1000 for i in range(3)]
# A separate evaluated .blend accompanies the editable source.
bpy.ops.wm.save_as_mainfile(filepath=str(out/'GSX250R_evaluated.blend'),compress=True,copy=True)
start=time.time();bpy.ops.export_scene.gltf(filepath=str(out/'GSX250R.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=False);report['formats']['GLB']={'bytes':(out/'GSX250R.glb').stat().st_size,'seconds':time.time()-start}
start=time.time();bpy.ops.export_scene.fbx(filepath=str(out/'GSX250R.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,global_scale=1,axis_forward='Y',axis_up='Z',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='COPY');report['formats']['FBX']={'bytes':(out/'GSX250R.fbx').stat().st_size,'seconds':time.time()-start}
start=time.time();bpy.ops.wm.obj_export(filepath=str(out/'GSX250R.obj'),export_selected_objects=True,forward_axis='Y',up_axis='Z',export_materials=True,export_uv=True,export_normals=True);report['formats']['OBJ']={'bytes':(out/'GSX250R.obj').stat().st_size,'seconds':time.time()-start}
(ROOT/'qa/export_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('GSX_EXPORT_COMPLETE',json.dumps(report))

# Keep only the evaluated vehicle in the companion .blend; editable source is a separate file.
for scene in list(bpy.data.scenes):
    if scene!=export_scene:
        for ob in list(scene.objects):
            if ob.name not in export_scene.objects:bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.scenes.remove(scene)
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'GSX250R_evaluated.blend'),compress=True,copy=True)
