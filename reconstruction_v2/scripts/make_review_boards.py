"""Produce local evidence boards. All source photos remain local.
Contour panel compares evaluated render silhouette against observed open contours;
it deliberately does not invent a full segmentation mask or report a fake IoU.
"""
from pathlib import Path
import sys,json,math,hashlib
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'))
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
TAG=sys.argv[1] if len(sys.argv)>1 else 'r04'
if not (TAG.startswith('r') and TAG[1:].isdigit()):raise ValueError('Unknown review revision')
FONT=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
SMALL=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
EDGES={62:[[[588,807],[613,762],[668,720],[747,696],[802,705],[868,736],[900,762]],[[327,787],[402,824],[464,839],[521,839],[590,822],[637,813]],[[628,940],[710,923],[805,901],[913,875],[1018,853],[1110,836],[1180,831],[1219,850]],[[1219,855],[1145,909],[1052,959],[1010,1032],[979,1116],[986,1210],[908,1235],[807,1237],[698,1231],[592,1224]]],63:[[[483,852],[508,809],[553,776],[601,757],[628,750],[692,755],[737,769],[755,799]],[[297,818],[349,849],[406,879],[448,883],[487,868],[507,859]],[[521,985],[609,967],[730,940],[851,908],[936,936],[1042,975],[1106,982]],[[1106,982],[1060,1009],[1010,1043],[941,1100],[878,1165],[816,1240],[757,1347],[663,1334],[552,1301],[447,1276]]],64:[]}

def masked(im,ann):
 im=im.copy();d=ImageDraw.Draw(im)
 for reg in ann.get('exclude_polygons',[]):
  if reg.get('polygon'):d.polygon([tuple(p) for p in reg['polygon']],fill=(55,55,55))
 return im

def main():
 boards=[];report={'revision':TAG,'gate':'NOT_PASSED','scope':'neutral gray evidence review','silhouette_iou':None,'silhouette_iou_reason':'Full closed foreground and part masks have not passed annotation review. Observed open contours are visual diagnostics only.','views':{}}
 ids=[int(x) for x in sys.argv[2:] if x.isdigit()] or [62,63,64,69,70]
 for k in ids:
  ann=json.loads((V2/f'annotations/photo_{k}.json').read_text());cam=json.loads((V2/f'calibration/camera_{k}.json').read_text());photo=Image.open(next((ROOT/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB');gray=Image.open(V2/f'renders/gray_{TAG}_{k}.png').convert('RGBA').resize(photo.size,Image.Resampling.LANCZOS)
  ref=masked(photo,ann);neutral=Image.new('RGB',photo.size,(228,228,228));neutral.paste(gray,(0,0),gray);neutral=masked(neutral,ann)
  over=ref.copy();over.paste(gray,(0,0),gray.getchannel('A').point(lambda x:int(x*.52)));over=masked(over,ann)
  alpha=np.array(gray.getchannel('A'));binary=(alpha>127).astype(np.uint8);contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);diff=np.full((photo.height,photo.width,3),244,np.uint8);cv2.drawContours(diff,contours,-1,(0,145,183),3)
  for line in EDGES.get(k,[]):cv2.polylines(diff,[np.array(line,np.int32)],False,(242,116,33),4)
  # Stripe samples supply actual observed wheel curves. Do not fabricate hidden arcs.
  for wheel in ann['wheels'].values():
   for x,y in wheel['rim_points']:cv2.circle(diff,(round(x),round(y)),3,(242,116,33),-1)
  diff=masked(Image.fromarray(diff),ann)
  ph=round(640*photo.height/photo.width);step=ph+57;board=Image.new('RGB',(1280,step*2+36),'white');d=ImageDraw.Draw(board)
  labels=['原照片（固定排除区已遮蔽）','同相机灰模 / Cycles','半透明叠加','轮廓对照：青＝模型；橙＝已标注实物边缘']
  for i,im in enumerate([ref,neutral,over,diff]):
   im=im.resize((640,ph));x=(i%2)*640;y=(i//2)*step+43;board.paste(im,(x,y));d.text((x+12,y-32),labels[i],font=SMALL,fill=(30,30,30))
  message={62:'联合照片候选相机；外形未通过',63:'联合照片候选相机；外形未通过',64:'裁切轮圈；镜头欠约束',69:'倾斜转向轴候选；早期无三角护杠状态',70:'镜头拟合失败；仅展示诊断，不可验收'}[k]
  d.text((12,board.height-28),f'照片 {k} · {TAG} · '+message,font=SMALL,fill=(160,38,28))
  dest=V2/f'renders/review_{TAG}_{k}.jpg';board.save(dest,quality=93);boards.append(board)
  report['views'][str(k)]={'role':cam.get('role','fit'),'camera_status':cam['status'],'board':str(dest.relative_to(ROOT)).replace('\\','/'),'photo_dimensions':photo.size,'render_dimensions':Image.open(V2/f'renders/gray_{TAG}_{k}.png').size,'camera_sha256':hashlib.sha256((V2/f'calibration/camera_{k}.json').read_bytes()).hexdigest(),'annotation_sha256':hashlib.sha256((V2/f'annotations/photo_{k}.json').read_bytes()).hexdigest(),'body_adjustment_uses_this_view':k in [62,63],'visual_reference_used':k in [62,63,69,70],'pose_note':message}
 contact=Image.new('RGB',(1536,1480),'white')
 for i,b in enumerate(boards):
  thumb=b.copy();thumb.thumbnail((512,739));contact.paste(thumb,((i%3)*512,(i//3)*740))
 contact.save(V2/f'renders/review_{TAG}_contact_sheet.jpg',quality=90)
 contact.save(V2/'renders/review_contact_sheet.jpg',quality=90)
 report['reserved_unfit_views']=[61];report['reference_66_used_for_lamp_and_mirror_envelope']=True;report['heldout_gate']='NOT_PASSED: two reliable independent cameras are still required'
 report['known_shape_issues']=['Seat/tail curvature and joins are not accepted.','Nose, windscreen, mirror orientation and headlight shape still differ.','Mechanical placeholders, muffler heat shield and guard mounts remain provisional.','No livery/text/scratches or final materials made in V2.']
 (V2/f'qa/review_{TAG}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print('Created',len(boards),'four-panel boards with original aspect ratios; no unverified IoU reported.')
if __name__=='__main__':main()
