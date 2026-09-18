"""Validate the local CPU visibility renderer against actual Cycles color labels.
This internal implementation agreement is not a photo similarity measurement.
Also resolves Blender's subpixel crop rounding against its own full-frame output.
"""
from pathlib import Path
import sys,json,itertools
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np
from PIL import Image
from interface_projection import raster,measure
mesh=json.loads((V2/'qa/interface_mesh_r13.json').read_text());mesh['Other_Occluders']=json.loads((V2/'qa/interface_occluders_r13.json').read_text());ann=json.loads((V2/'annotations/tank_interface_r13.json').read_text());report={}
def label(rgb):return np.where(rgb.max(axis=2)>127,rgb.argmax(axis=2)+1,0).astype(np.uint8)
for k,a in ann['views'].items():
 full=np.array(Image.open(V2/f'renders/interface_r13/crop_r13_ids_full_{k}.png').convert('RGB'));crop=np.array(Image.open(V2/f'renders/interface_r13/crop_r13_ids_{k}.png').convert('RGB'));h,w=crop.shape[:2];x0,y0,_,_=a['crop'];attempts=[]
 for dx,dy in itertools.product(range(-2,3),repeat=2):
  x=x0+dx;y=y0+dy;diff=np.mean(label(full[y:y+h,x:x+w])!=label(crop));attempts.append((float(diff),x,y))
 mismatch,x,y=min(attempts)
 if mismatch>1e-5:raise RuntimeError('Cropped ID render cannot be located exactly in full frame')
 actual=[x,y,x+w,y+h];cam=json.loads((V2/f'calibration/camera_{k}.json').read_text());cpu=raster(mesh,cam,a['crop']);X,Y,XX,YY=a['crop'];labels=label(full[Y:YY,X:XX]);rows={}
 for name,part in [('tank',1),('seat',2),('trim',3)]:
  ra=labels==part;rb=cpu==part;rows[name]=float(np.count_nonzero(ra&rb)/max(1,np.count_nonzero(ra|rb)))
 if min(rows.values())<.995:raise RuntimeError('Visibility calculation needs review')
 report[k]={'crop_actual_pixels':actual,'cropped_vs_full_id_mismatch_fraction':mismatch,'full_render_vs_cpu_part_mask_iou':rows,'actual_full_render_boundary_metrics':measure(labels,a)}
(V2/'qa/interface_raster_validation_r13.json').write_text(json.dumps({'scope':'Implementation cross-check against Cycles color labels; NOT photo IoU or appearance acceptance','views':report},indent=2),encoding='utf8');print('Visibility implementation verified against full native Cycles output; no photo acceptance implied.')