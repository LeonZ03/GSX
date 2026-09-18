"""Read evaluated local interface meshes/occluders from an isolated V2 scene.
No model is saved. Crop evidence and geometry dumps remain in ignored qa/.
"""
from pathlib import Path
import bpy,json,numpy as np
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene;tag=s.get('revision');dg=bpy.context.evaluated_depsgraph_get();ann=json.loads((V2/'annotations/tank_interface_r13.json').read_text());views=[]
for k,a in ann['views'].items():
 c=json.loads((V2/f'calibration/camera_{k}.json').read_text());views.append((np.array(c['R_cv']),np.array(c['t_cv_m']),np.array(c['K_px']),a['crop']))
parts=['Body_Tank','Seat_Rider','Body_TankSideTrim','Body_SeatSide','Body_PillionBase','Body_Tail'];data={};vv=[];ff=[];counts={}
for o in s.objects:
 if o.type not in ['MESH','CURVE','FONT'] or o.hide_render or any(c.hide_render for c in o.users_collection) or o.get('export_exclude'):continue
 key=Path(o.get('control_cage_source','')).stem;e=o.evaluated_get(dg);m=e.to_mesh()
 if m is None:continue
 m.calc_loop_triangles();xyz=np.array([list(e.matrix_world@p.co) for p in m.vertices]);tri=np.array([list(t.vertices) for t in m.loop_triangles],dtype=int)
 if key in parts:data[key]={'vertices':xyz.tolist(),'triangles':tri.tolist()};e.to_mesh_clear();continue
 if not len(tri):e.to_mesh_clear();continue
 keep=np.zeros(len(tri),bool)
 for R,t,K,box in views:
  cp=(R@xyz.T).T+t;hp=(K@cp.T).T;uv=(hp[:,:2]/hp[:,2,None])[tri];z=cp[tri,2];x0,y0,x1,y1=box
  keep|=(z.min(axis=1)>0)&(uv[:,:,0].max(axis=1)>=x0-3)&(uv[:,:,0].min(axis=1)<=x1+3)&(uv[:,:,1].max(axis=1)>=y0-3)&(uv[:,:,1].min(axis=1)<=y1+3)
 selected=tri[keep]
 if len(selected):
  counts[o.name]=len(selected)
  for f in selected:start=len(vv);vv.extend(xyz[f].tolist());ff.append([start,start+1,start+2])
 e.to_mesh_clear()
if set(data)!=set(parts):raise RuntimeError('Missing required interface part')
(V2/f'qa/interface_mesh_{tag}.json').write_text(json.dumps(data),encoding='utf8')
(V2/f'qa/interface_occluders_{tag}.json').write_text(json.dumps({'vertices':vv,'triangles':ff,'object_triangle_counts':counts}),encoding='utf8')
result={'revision':tag,'source_saved':False,'parts':len(data),'other_objects':len(counts),'other_triangles':len(ff)}