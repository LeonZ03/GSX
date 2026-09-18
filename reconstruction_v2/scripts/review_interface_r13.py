"""Local before/after interface board and actual Cycles-label boundary metrics.
No whole-motorcycle similarity or named-keypoint accuracy is inferred.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageOps
from interface_projection import measure
ann=json.loads((V2/'annotations/tank_interface_r13.json').read_text());validation=json.loads((V2/'qa/interface_raster_validation_r13.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17);board=Image.new('RGB',(1440,1220),'#f6f8fa');d=ImageDraw.Draw(board);metrics={}
d.text((20,12),'r13 油箱后缘小幅修正：固定相机；仅局部候选，整体仍未通过',font=font,fill='#1b2f40')
d.text((20,48),'实车接缝开放标注约±4px；排除较大改形和自交候选；后座／座垫／饰板未改。',font=small,fill='#8e392c')
for row,(k,a) in enumerate(ann['views'].items()):
 photo=Image.open(next((ROOT/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB');box=validation['views'][k]['crop_actual_pixels'];origin=np.array(box[:2]);y=118+row*352;metrics[k]={};labelmaps={}
 for tag in ['r11','r13']:
  rgb=np.array(Image.open(V2/f'renders/interface_r13/crop_{tag}_ids_full_{k}.png').convert('RGB'));labels=np.where(rgb.max(axis=2)>127,rgb.argmax(axis=2)+1,0).astype(np.uint8);x0,y0,x1,y1=a['crop'];metrics[k][tag]=measure(labels[y0:y1,x0:x1],a);labelmaps[tag]=labels
 original=photo.crop(box);panels=[original]
 for tag in ['r11','r13']:
  im=Image.open(V2/f'renders/interface_r13/crop_{tag}_{k}.png').convert('RGBA');assert im.size==original.size,(k,tag,im.size,original.size);bg=Image.new('RGBA',im.size,(228,228,228,255));bg.alpha_composite(im);panels.append(bg.convert('RGB'))
 overlay=np.array(photo.copy())
 for tag,color in [('r11',(230,65,140)),('r13',(0,199,215))]:
  mask=(labelmaps[tag]==1).astype(np.uint8);edge=mask-cv2.erode(mask,np.ones((3,3),np.uint8));overlay[edge>0]=color
 for kind,line in a['boundaries'].items():cv2.polylines(overlay,[np.asarray(line,np.int32)],False,(255,180,20),1)
 panels.append(Image.fromarray(overlay).crop(box))
 for col,(im,title) in enumerate(zip(panels,['实车局部','改前 r11','改后 r13','黄＝参考 / 紫＝改前 / 青＝改后'])):
  tile=ImageOps.contain(im,(352,294));board.paste(tile,(col*360+(360-tile.width)//2,y+(294-tile.height)//2));d.text((col*360+10,y-30),f'{k}：'+title,font=small,fill='#243b4c')
 before=metrics[k]['r11'];after=metrics[k]['r13'];d.text((18,y+299),f"后缘平均距离 {before['rear_outline']['mean_px']:.1f}→{after['rear_outline']['mean_px']:.1f}px；接缝平均距离 {before['contact']['mean_px']:.1f}→{after['contact']['mean_px']:.1f}px。",font=small,fill='#243b4c')
 if k=='69':d.text((760,y+299),'69仅作交叉检查，非独立验收。',font=small,fill='#8e392c')
d.text((20,1176),'一侧开放参考边界到实际渲染分件边缘的距离，不是完整轮廓IoU或整车还原率。',font=small,fill='#8e392c')
board.save(V2/'renders/tank_interface_r13_comparison.jpg',quality=94)
report={'status':'M1_NOT_PASSED','source':'13_gray_review.blend','selected_candidate':'e10_w0_z0','fit_views':[62,63],'cross_check':[69],'independent_holdout':False,'annotation_uncertainty_px':4,'annotation_sha256':hashlib.sha256((V2/'annotations/tank_interface_r13.json').read_bytes()).hexdigest(),'metric':'One-way reference-to-visible-part edge distance from full native Cycles color-label renders. Contact edges restricted to10px proximity to visible seat; this is an image-space selection rule, not a physical clearance.','measurements':metrics,'warning':'Small local geometric correction; significant shape errors and camera uncertainty remain.'}
(V2/'qa/interface_review_r13.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(metrics,indent=2))