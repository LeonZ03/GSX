"""Local-only tank/seat contact sheet; crop rectangles never contain a plate.
This is an appearance diagnostic, not a silhouette or keypoint metric.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
ROOT=Path(__file__).resolve().parents[2]; V2=ROOT/'reconstruction_v2'
# 69's Blender float border expands left to x=924; retain native pixel alignment.
BOXES={62:(555,740,720,880),63:(470,780,635,920),69:(924,540,1090,680)}
FONT=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
SMALL=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
board=Image.new('RGB',(1440,1250),(248,249,251)); d=ImageDraw.Draw(board)
d.text((24,15),'r11 油箱—骑手座接口：穿插已消除，外形仍未通过',font=FONT,fill=(30,40,53))
d.text((24,55),'固定相机 / 同一 Blender 5.2.2 / 32采样局部图 / 本地照片，仅供诊断',font=SMALL,fill=(70,80,90))
labels=['实车局部','r10 修正前','r11 修正后','r11 半透明叠加']
for col,label in enumerate(labels):d.text((col*360+16,98),label,font=FONT,fill=(35,45,55))
report={'status':'NOT_PASSED','source':'11_gray_review.blend','metric':None,'views':{}}
for row,(k,box) in enumerate(BOXES.items()):
 photo=Image.open(next((ROOT/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB').crop(box)
 grays=[Image.open(V2/f'renders/interface_r11/crop_{tag}_{k}.png').convert('RGBA') for tag in ('r10','r11')]
 assert all(im.size==photo.size for im in grays),(k,photo.size,[im.size for im in grays])
 neutral=[]
 for im in grays:
  bg=Image.new('RGBA',im.size,(226,226,226,255));bg.alpha_composite(im);neutral.append(bg.convert('RGB'))
 overlay=photo.copy();overlay.paste(grays[1],(0,0),grays[1].getchannel('A').point(lambda v:round(v*.45)))
 y=138+row*354
 for col,im in enumerate([photo,*neutral,overlay]):
  board.paste(im.resize((352,299),Image.Resampling.LANCZOS),(col*360+4,y))
 note={62:'照片62：接口上沿仍有尖折，座垫前端与蓝色壳体边界待拟合。',63:'照片63：后缘曲率和黑饰板遮挡关系仍与实车不同。',69:'照片69：当前缺口形状仍需修正；镜头及后座高度尚无独立验证。'}[k]
 d.text((16,y+307),note,font=SMALL,fill=(154,54,39))
 report['views'][str(k)]={'native_crop':box,'pixels':photo.size,'camera_sha256':hashlib.sha256((V2/f'calibration/camera_{k}.json').read_bytes()).hexdigest()}
d.text((24,1208),'3 mm仅为构造间隙；零相交不代表实车尺寸或1:1外观通过。',font=SMALL,fill=(154,54,39))
board.save(V2/'renders/tank_seat_r11_comparison.jpg',quality=94)
(V2/'qa/tank_seat_r11_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('Created local tank_seat_r11_comparison.jpg; no similarity score claimed.')