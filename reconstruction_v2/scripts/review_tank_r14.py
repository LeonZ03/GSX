"""Actual Cycles before/after tank review; all photo-containing outputs stay local.
R14 uses three fitting views, not independent validation. Open boundary distance
must not be presented as closed-mask IoU or whole-bike accuracy.
"""
from pathlib import Path
import sys,json,itertools,hashlib
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageOps
from interface_projection import measure
before='r13';after=sys.argv[1] if len(sys.argv)>1 else 'r14';ann=json.loads((V2/'annotations/tank_crown_r14.json').read_text());out=V2/'renders/interface_r14';font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
board=Image.new('RGB',(1800,1280),'#f6f8fa');draw=ImageDraw.Draw(board);draw.text((18,12),'r14 油箱曲面重修：整段上缘、后部体量与封闭收口',font=font,fill='#213547');draw.text((18,52),'相机固定；62 / 63 / 69均参与拟合。灰模未通过；照片只保存在本地。',font=small,fill='#874331');metrics={};origins={}
def labels(im):
 rgb=np.asarray(im.convert('RGB'));return np.where(rgb.max(axis=2)>127,rgb.argmax(axis=2)+1,0).astype(np.uint8)
for row,(key,a) in enumerate(ann['views'].items()):
 labelmaps={};metrics[key]={};photo=Image.open(next((ROOT/'IMG').glob(f'*_{key}_97.jpg'))).convert('RGB');boxes={}
 for tag in [before,after]:
  full=labels(Image.open(out/f'crop_{tag}_ids_full_{key}.png'));crop=labels(Image.open(out/f'crop_{tag}_ids_{key}.png'));h,w=crop.shape;x0,y0,_,_=a['crop'];attempts=[]
  for dx,dy in itertools.product(range(-2,3),repeat=2):
   x=x0+dx;y=y0+dy;attempts.append((float(np.mean(full[y:y+h,x:x+w]!=crop)),x,y))
  mismatch,x,y=min(attempts)
  if mismatch>1e-5:raise RuntimeError(('Crop not aligned',tag,key,mismatch))
  boxes[tag]=[x,y,x+w,y+h];X,Y,XX,YY=a['crop'];metrics[key][tag]=measure(full[Y:YY,X:XX],a);labelmaps[tag]=full
 if boxes[before]!=boxes[after]:raise RuntimeError('Before/after crops differ')
 box=boxes[after];origins[key]=box;original=photo.crop(box);panels=[original]
 for tag in [before,after]:
  im=Image.open(out/f'crop_{tag}_{key}.png').convert('RGBA');assert im.size==original.size;bg=Image.new('RGBA',im.size,(228,228,228,255));bg.alpha_composite(im);panels.append(bg.convert('RGB'))
 overlay=np.asarray(photo).copy()
 for tag,color in [(before,(220,60,150)),(after,(0,190,210))]:
  mask=(labelmaps[tag]==1).astype(np.uint8);edge=mask-cv2.erode(mask,np.ones((3,3),np.uint8));overlay[edge>0]=color
 for kind,line in a['boundaries'].items():cv2.polylines(overlay,[np.array(line,np.int32)],False,(255,180,20),1)
 panels.append(Image.fromarray(overlay).crop(box));y=126+row*365
 for col,(im,title) in enumerate(zip(panels,['实车局部','改前 r13','改后 r14','黄=参考  紫=改前  青=改后'])):
  im=ImageOps.contain(im,(442,285));board.paste(im,(col*450+(450-im.width)//2,y+(285-im.height)//2));draw.text((col*450+8,y-32),key+'：'+title,font=small,fill='#243b4c')
 m0=metrics[key][before];m1=metrics[key][after];text=f"后缘均值 {m0['rear_outline']['mean_px']:.1f} → {m1['rear_outline']['mean_px']:.1f}px；接缝 {m0['contact']['mean_px']:.1f} → {m1['contact']['mean_px']:.1f}px"
 if 'crown' in m0:text+=f"；上缘 {m0['crown']['mean_px']:.1f} → {m1['crown']['mean_px']:.1f}px"
 draw.text((18,y+298),text,font=small,fill='#243b4c')
draw.text((18,1230),'开放边界距离来自实际渲染；人工标注约±4–5px。不是整车还原率，未通过独立角度复核。',font=small,fill='#874331')
board.save(V2/'renders/tank_crown_r14_comparison.jpg',quality=94)
report={'status':'M1_NOT_PASSED','before':before,'after':after,'fit_views':[62,63,69],'independent_holdout':False,'metric':'one-way reference-to-visible-part-edge from native full-frame Cycles ID output','uncertainty_px':{'old_lines':4,'new_crown':5},'crop_actual_pixels':origins,'measurements':metrics,'annotation_sha256':hashlib.sha256((V2/'annotations/tank_crown_r14.json').read_bytes()).hexdigest()}
(V2/'qa/tank_review_r14.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:{tag:{kind:round(v['mean_px'],2) for kind,v in m.items()} for tag,m in val.items()} for k,val in metrics.items()},indent=2))
