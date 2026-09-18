"""Local-only seat/tail comparisons using frozen cameras and evaluated meshes.
Manual silhouette labels have 4 px uncertainty. These fitting-view diagnostics
are neither keypoint errors nor independent validation nor whole-bike IoU.
"""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from fit_cameras import project
ann=json.loads((V2/'annotations/seat_tail_r09.json').read_text());meshes={t:json.loads((V2/f'qa/tail_mesh_{t}.json').read_text()) for t in ['r08','r09']}
report={'status':'NOT_PASSED','annotation_sha256':hashlib.sha256((V2/'annotations/seat_tail_r09.json').read_bytes()).hexdigest(),'annotation_uncertainty_px':ann['uncertainty_px'],'metric_scope':'Symmetric silhouette boundary distance and visible part IoU in fitting views. Not keypoint error, not whole motorcycle, no held-out validation.','measurements':[]}
maskcache={}
for a in ann['boundaries']:
 k=a['image_id'];part=a['part'];c=json.loads((V2/f'calibration/camera_{k}.json').read_text());w,h=c['image_size'];target=np.zeros((h,w),np.uint8);cv2.fillPoly(target,[np.array(a['points'],np.int32)],1)
 def boundary(m):return m-cv2.erode(m,np.ones((3,3),np.uint8))
 refedge=boundary(target);refdist=cv2.distanceTransform(1-refedge,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
 for tag in meshes:
  geo=meshes[tag][part];uv=project(geo['vertices'],np.array(c['R_cv']),np.array(c['t_cv_m']),np.array(c['K_px']));model=np.zeros((h,w),np.uint8)
  for f in geo['triangles']:cv2.fillConvexPoly(model,np.round(uv[f]).astype(np.int32),1)
  edge=boundary(model);dist=cv2.distanceTransform(1-edge,cv2.DIST_L2,cv2.DIST_MASK_PRECISE);errors=np.r_[refdist[edge>0],dist[refedge>0]]
  measure={'image_id':k,'part':part,'revision':tag,'median_boundary_px':float(np.median(errors)),'p95_boundary_px':float(np.percentile(errors,95)),'mean_boundary_px':float(np.mean(errors)),'part_silhouette_iou':float(np.count_nonzero(model&target)/np.count_nonzero(model|target))}
  report['measurements'].append(measure);maskcache[(k,part,tag)]=edge
manifest=json.loads((V2/'calibration/r08_tail_frozen/manifest.json').read_text());checks={}
for p,sha in manifest.items():
 if '/calibration/camera_' in p.replace('\\','/') or '/annotations/' in p.replace('\\','/'):checks[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha
report['frozen_input_checks']=checks;report['all_frozen_inputs_unchanged']=all(checks.values())
(V2/'qa/seat_tail_r09.json').write_text(json.dumps(report,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
views={69:(960,465,1390,710),62:(330,760,675,895),63:(220,670,640,965)}
board=Image.new('RGB',(1560,955),'#eceff1');draw=ImageDraw.Draw(board)
for row,(k,box) in enumerate(views.items()):
 photo=Image.open(next((ROOT/'IMG').glob(f'*_{k}_*.jpg'))).convert('RGB')
 if k==69:ImageDraw.Draw(photo).rectangle((1340,580,1510,780),fill='#89929a')
 panels=[photo]
 for tag in ['r08','r09']:
  rgba=Image.open(V2/f'renders/gray_{tag}_{k}.png').convert('RGBA');bg=Image.new('RGBA',rgba.size,'#eeeeee');bg.alpha_composite(rgba);panels.append(bg.convert('RGB').resize(photo.size))
 overlay=photo.copy();arr=np.array(overlay)
 for a in ann['boundaries']:
  if a['image_id']!=k:continue
  cv2.polylines(arr,[np.array(a['points'],np.int32)],True,(255,176,20),2)
  for tag,color in [('r08',(238,70,100)),('r09',(0,208,220))]:
   edge=maskcache[(k,a['part'],tag)];arr[cv2.dilate(edge,np.ones((2,2),np.uint8))>0]=color
 panels.append(Image.fromarray(arr))
 for col,im in enumerate(panels):
  tile=im.crop(box);tile.thumbnail((380,215));board.paste(tile,(col*390+(380-tile.width)//2,42+row*300))
  draw.text((col*390+10,16+row*300),f'{k}: '+['实车照片（仅本地）','改前 r08','改后 r09（未验收）','橙：参考 / 红：改前 / 青：改后'][col],font=small,fill='#18232c')
 ms=[m for m in report['measurements'] if m['image_id']==k]
 parts=sorted(set(m['part'] for m in ms));segments=[]
 for part in parts:
  old=next(m for m in ms if m['part']==part and m['revision']=='r08');new=next(m for m in ms if m['part']==part and m['revision']=='r09')
  label='后座' if part=='Seat_Pillion' else '骑手座'
  segments.append(f"{label}轮廓距离：中位 {old['median_boundary_px']:.1f}→{new['median_boundary_px']:.1f}px，P95 {old['p95_boundary_px']:.1f}→{new['p95_boundary_px']:.1f}px")
 draw.text((10,270+row*300),'；'.join(segments) or '63：仅作外观复核，未建立可靠的完整分件轮廓标注。',font=small,fill='#18232c')
draw.text((10,925),'相机固定；人工描边约 ±4px；69 仍为候选镜头。以上为拟合视角的局部诊断，整体 M1 未通过。',font=font,fill='#7c2626')
board.save(V2/'renders/seat_tail_r09_comparison.jpg',quality=92)
print(json.dumps({'frozen':report['all_frozen_inputs_unchanged'],'measurements':report['measurements']},indent=2))