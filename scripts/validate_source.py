"""Verify the editable source from evaluated geometry, without printing plate text."""
from pathlib import Path
import bpy,json,os
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT=Path(os.environ.get('GSX_ROOT',Path(__file__).resolve().parents[1]))
s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_User_Reconstruction'))
bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
lo=[float('inf')]*3;hi=[-float('inf')]*3;verts=0;faces=0
for obj in s.objects:
    if obj.type not in {'MESH','CURVE','FONT'} or obj.name.startswith('Studio') or obj.hide_render:continue
    ev=obj.evaluated_get(deps);me=ev.to_mesh();verts+=len(me.vertices);faces+=len(me.polygons)
    for vert in me.vertices:
        p=obj.matrix_world@vert.co
        for i in range(3):lo[i]=min(lo[i],p[i]);hi[i]=max(hi[i],p[i])
    ev.to_mesh_clear()
curves=[bpy.data.objects['GuardBar_'+label].data.splines[0] for label in ['L','R']]
error=max((Vector((-a.co.x,a.co.y,a.co.z))-Vector(z.co[:3])).length for a,z in zip(curves[0].points,curves[1].points))*1000
rail_errors={}
for label in ['L','R']:
    side=bpy.data.objects['Body_SideFairing_'+label];upper=bpy.data.objects['Body_UpperCowling_'+label]
    tree=KDTree(len(side.data.vertices))
    for v in side.data.vertices:tree.insert(side.matrix_world@v.co,v.index)
    tree.balance();dists=[tree.find(upper.matrix_world@upper.data.vertices[i].co)[2]*1000 for i in range(10,len(upper.data.vertices),11)]
    rail_errors[label]=max(dists)
report={'blender':bpy.app.version_string,'revision':s.get('revision'),'bounds_mm':dict(zip(['width','length','height'],[(hi[i]-lo[i])*1000 for i in range(3)])),
    'minimum_z_mm':lo[2]*1000,'wheelbase_mm':1430,'front_tire_nominal_mm':[110,607.8],'rear_tire_nominal_mm':[140,627.8],
    'guard_symmetry_max_error_mm':error,'cowling_outer_rail_gap_mm':rail_errors,'evaluated_vertices':verts,'evaluated_polygons':faces,
    'note':'Envelope uses evaluated vertices; rail gaps use base-mesh boundary coordinates. Shell offsets, hidden fitment and all intersections remain unverified.'}
(ROOT/'qa/dimensions.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
private=json.loads((ROOT/'config/user.local.json').read_text('utf-8')) if (ROOT/'config/user.local.json').exists() else {'plate_top':'LOCAL','plate_bottom':'GSX250'}
checks={'plate_text_matches_private_config':bpy.data.objects['LicensePlate_Region'].data.body==private['plate_top'] and bpy.data.objects['LicensePlate_Number'].data.body==private['plate_bottom'],
    'reference_objects_in_final':sum(o.name.startswith('Reference_') for o in s.objects),'blockout_objects_in_final':sum(o.name.startswith('Blockout_') for o in s.objects),'scene_count':len(bpy.data.scenes),
    'missing_images':[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]}
(ROOT/'qa/source_integrity.json').write_text(json.dumps(checks,indent=2))
assert checks['plate_text_matches_private_config'] and checks['scene_count']==1 and not checks['missing_images']
assert not checks['reference_objects_in_final'] and not checks['blockout_objects_in_final']
assert error<.01 and max(rail_errors.values())<.01
print('GSX_SOURCE_VALIDATED',json.dumps(report))
