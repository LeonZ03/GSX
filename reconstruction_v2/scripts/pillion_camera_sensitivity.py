"""Propagate isolated wheel-camera candidates into a fixed pillion mesh.
Body boundaries are used only AFTER camera fitting, never to select a camera.
Optional vertical offsets are diagnostics; they never mutate mesh or camera files.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np,cv2
from scipy.spatial import cKDTree
from scipy.optimize import minimize_scalar
from fit_cameras import project

def outline(geo,camera,dz=0):
 xyz=np.array(geo['vertices']);xyz[:,2]+=dz
 uv=project(xyz,np.array(camera['R_cv']),np.array(camera['t_cv_m']),np.array(camera['K_px']))
 lo=np.floor(uv.min(axis=0)).astype(int)-3;hi=np.ceil(uv.max(axis=0)).astype(int)+3
 if np.any(hi-lo>3000):raise ValueError('Implausible projected mesh extent')
 mask=np.zeros(tuple((hi-lo)[::-1]+1),np.uint8);pixels=np.rint(uv-lo).astype(np.int32)
 for face in geo['triangles']:cv2.fillConvexPoly(mask,pixels[face],1)
 edges,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
 return np.concatenate([e[:,0,:]+lo for e in edges]).astype(float)

def dense_poly(points):
 p=np.asarray(points,float);p=np.vstack([p,p[:1]]);out=[]
 for a,b in zip(p,p[1:]):
  n=max(1,int(np.ceil(np.linalg.norm(b-a))));out.extend(a+(b-a)*np.arange(n)[:,None]/n)
 return np.asarray(out)

def compare(edge,target):
 values=np.r_[cKDTree(target).query(edge)[0],cKDTree(edge).query(target)[0]]
 return {'median_px':float(np.median(values)),'p95_px':float(np.percentile(values,95)),'mean_px':float(np.mean(values))}

def main():
 source=V2/'calibration/camera69_sensitivity_r12_refined.json';a=json.loads(source.read_text());annpath=V2/'annotations/seat_tail_r09.json'
 ann=next(x for x in json.loads(annpath.read_text())['boundaries'] if x['image_id']==69 and x['part']=='Seat_Pillion');ref=dense_poly(ann['points'])
 geos={tag:json.loads((V2/f'qa/tail_mesh_{tag}.json').read_text())['Seat_Pillion'] for tag in ['r08','r11']}
 cameras=[a['frozen_camera']]+[c for c in a['candidates'] if c['low_residual_diagnostic']]
 results=[]
 for c in cameras:
  row={'name':c['name'],'family':c['family'],'wheel_rms_px':c['wheel_rms_px'],'focal_px':c['K_px'][0][0],'radius_mm':c['radius_mm'],'cx':c['cx'],'cy':c['cy'],'parts':{}}
  for tag,geo in geos.items():
   edge=outline(geo,c);before=compare(edge,ref)
   def objective(dz):return compare(outline(geo,c,dz),ref)['mean_px']
   grid=np.linspace(-.18,.18,19);costs=[objective(x) for x in grid];idx=int(np.argmin(costs));left=grid[max(0,idx-1)];right=grid[min(len(grid)-1,idx+1)]
   opt=minimize_scalar(objective,bounds=(left,right),method='bounded',options={'xatol':.0005});best=min([(objective(0),0),(costs[idx],float(grid[idx])),(opt.fun,float(opt.x))])[1]
   row['parts'][tag]={'fixed_mesh':before,'diagnostic_offset_z_mm':best*1000,'diagnostic_max_height_mm':(max(p[2] for p in geo['vertices'])+best)*1000,'after_vertical_offset':compare(outline(geo,c,best),ref),'offset_on_scan_boundary':abs(best)>.179}
  # Same actual mesh centroid, seen through each candidate; not a new landmark annotation.
  center=np.mean(geos['r11']['vertices'],axis=0);row['fixed_mesh_centroid_px']=project([center],np.array(c['R_cv']),np.array(c['t_cv_m']),np.array(c['K_px']))[0].tolist()
  results.append(row);print(c['name'],'r11 dz',round(row['parts']['r11']['diagnostic_offset_z_mm'],1),'r08 dz',round(row['parts']['r08']['diagnostic_offset_z_mm'],1),flush=True)
 screened=results[1:];stats={'low_residual_variants':len(screened),'fixed_r11_centroid_axis_span_px':np.ptp([x['fixed_mesh_centroid_px'] for x in screened],axis=0).tolist()}
 for tag in geos:
  stats[tag+'_diagnostic_offset_range_mm']=[min(x['parts'][tag]['diagnostic_offset_z_mm'] for x in screened),max(x['parts'][tag]['diagnostic_offset_z_mm'] for x in screened)]
  stats[tag+'_fixed_mean_error_range_px']=[min(x['parts'][tag]['fixed_mesh']['mean_px'] for x in screened),max(x['parts'][tag]['fixed_mesh']['mean_px'] for x in screened)]
 out={'status':'NOT_PASSED','scope':'Sampled assumption sensitivity of a fitting view, not independent validation or a statistical confidence interval. Offsets are diagnostic only.','source_profile':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'annotation_sha256':hashlib.sha256(annpath.read_bytes()).hexdigest(),'annotation_uncertainty_px':4,'geometry_revision':'r11 unchanged','metric':'Symmetric nearest silhouette-boundary distances on isolated evaluated part; no inter-part occlusion. Not named landmark errors.','summary':stats,'results':results}
 path=V2/'qa/pillion_camera_sensitivity_r12.json'
 if path.exists():raise FileExistsError(path)
 path.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(stats,indent=2),flush=True)
if __name__=='__main__':main()