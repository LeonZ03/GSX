"""Geometric audit of evaluated meshes, not copied construction constants."""
from pathlib import Path
import bpy,json,math,re
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_Reconstruction_V2_Gray'));bpy.context.window.scene=s;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def obj(name):return next(o for o in s.objects if re.sub(r'\.\d{3}$','',o.name)==name)
def bounds(o):
 ev=o.evaluated_get(dg);m=ev.to_mesh();pts=[ev.matrix_world@v.co for v in m.vertices];ev.to_mesh_clear();lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);return lo,hi
out={'source':bpy.data.filepath,'status':'M1_NOT_PASSED','blender_version':bpy.app.version_string,'objects':len(s.objects),'scene_names':[x.name for x in bpy.data.scenes],'units':'mm','measurements':{},'unaccepted':['all photo camera intrinsics','main body silhouette and local part matching','two effective heldout cameras','mechanical proxies and attachment mounts','all markings and materials']}
centers={}
for name in ['Front','Rear']:
 lo,hi=bounds(obj('Hub_'+name));centers[name]=(lo+hi)*.5
 lo,hi=bounds(obj('Tire_'+name));out['measurements']['tire_'+name]={'width':(hi.x-lo.x)*1000,'diameter_y':(hi.y-lo.y)*1000,'diameter_z':(hi.z-lo.z)*1000}
 lo,hi=bounds(obj('BrakeDisc_'+name));out['measurements']['disc_'+name]={'diameter_y':(hi.y-lo.y)*1000,'diameter_z':(hi.z-lo.z)*1000}
out['measurements']['wheelbase_from_evaluated_hub_centers']=abs(centers['Front'].y-centers['Rear'].y)*1000
out['measurements']['hub_centers']={k:[v*1000 for v in p] for k,p in centers.items()}
out['construction_dimension_checks']={'wheelbase_within_1mm':abs(out['measurements']['wheelbase_from_evaluated_hub_centers']-1430)<1,'front_disc_within_1mm':abs(out['measurements']['disc_Front']['diameter_y']-290)<1,'rear_disc_within_1mm':abs(out['measurements']['disc_Rear']['diameter_y']-240)<1}
out['construction_dimension_checks']['note']='Only model geometry versus documented nominal dimensions. Not a measurement of the real motorcycle.'
quads={}
for o in s.objects:
 if o.get('control_cage_source'):quads[o.name]={'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'all_quads':all(len(p.vertices)==4 for p in o.data.polygons),'subdivision_retained':any(m.type=='SUBSURF' for m in o.modifiers),'source':o['control_cage_source']}
out['control_cages']=quads
out['cameras']=[{'name':o.name,'photo':o.get('image_id'),'status':o.get('fit_status')} for o in s.objects if o.type=='CAMERA']
plate=obj('LicensePlate');out['privacy']={'plate_is_blank_gray_proxy':plate.type=='MESH','no_text_objects':not any(o.type=='FONT' for o in s.objects)}
(V2/f"qa/geometry_{s.get('revision','r03')}.json").write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out['measurements'],indent=2));print('CONTROL_CAGES',len(quads),'ALL_QUADS',all(x['all_quads'] for x in quads.values()))
