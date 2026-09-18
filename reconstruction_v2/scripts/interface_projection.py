"""Local native-pixel visibility diagnostics for the tank/seat interface.
Rasterizes evaluated part triangles with perspective-correct depth; does not
claim full-scene masks, complete IoU or independent viewpoint validation.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np,cv2
from scipy.spatial import cKDTree
PARTS={'Body_Tank':1,'Seat_Rider':2,'Body_TankSideTrim':3,'Body_SeatSide':4,'Body_PillionBase':5,'Body_Tail':6,'Other_Occluders':7}

def raster(meshes,camera,box):
 x0,y0,x1,y1=box;w=x1-x0;h=y1-y0;depth=np.full((h,w),np.inf);labels=np.zeros((h,w),np.uint8)
 R=np.array(camera['R_cv']);t=np.array(camera['t_cv_m']);K=np.array(camera['K_px'])
 for name,partid in PARTS.items():
  if name not in meshes:continue
  mesh=meshes[name];cam=(R@np.asarray(mesh['vertices']).T).T+t;proj=(K@cam.T).T;uv=proj[:,:2]/proj[:,2,None]-[x0,y0]
  faces=np.asarray(mesh['triangles']);triangles=uv[faces];z=cam[faces,2];valid=(z.min(axis=1)>0)&(triangles[:,:,0].max(axis=1)>=0)&(triangles[:,:,0].min(axis=1)<w)&(triangles[:,:,1].max(axis=1)>=0)&(triangles[:,:,1].min(axis=1)<h)
  for tri,tz in zip(triangles[valid],z[valid]):
   a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-9:continue
   lo=np.maximum(np.floor(tri.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(tri.max(axis=0)).astype(int),[w-1,h-1]);xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;zv=1/np.maximum(u/tz[0]+v/tz[1]+(1-u-v)/tz[2],1e-12)
   sl=(slice(lo[1],hi[1]+1),slice(lo[0],hi[0]+1));accept=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(zv<depth[sl]);depth[sl][accept]=zv[accept];labels[sl][accept]=partid
 return labels

def dense(points):
 out=[];p=np.asarray(points,float)
 for a,b in zip(p[:-1],p[1:]):
  n=max(1,int(np.ceil(np.linalg.norm(b-a))));out.extend(a+(b-a)*np.arange(n)[:,None]/n)
 out.append(p[-1]);return np.array(out)

def edges(labels,part):
 mask=(labels==part).astype(np.uint8);edge=mask-cv2.erode(mask,np.ones((3,3),np.uint8));yy,xx=np.where(edge);return np.column_stack([xx+.5,yy+.5])

def measure(labels,annotation):
 out={};origin=np.array(annotation['crop'][:2]);seat_dist=cv2.distanceTransform((labels!=2).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
 for kind,points in annotation['boundaries'].items():
  edge=edges(labels,3 if kind=='trim_top' else 1)
  if kind=='contact' and len(edge):
   pix=edge.astype(int);edge=edge[seat_dist[pix[:,1],pix[:,0]]<=10]
  reference=dense(points);dist=cKDTree(edge+origin).query(reference)[0] if len(edge) else np.full(len(reference),999.)
  out[kind]={'median_px':float(np.median(dist)),'p95_px':float(np.percentile(dist,95)),'mean_px':float(np.mean(dist)),'samples':len(reference),'scope':'one_way_reference_to_visible_part_edge; contact within10px of seat'}
 return out