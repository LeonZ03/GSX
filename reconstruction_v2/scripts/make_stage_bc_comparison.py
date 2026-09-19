"""Local matched-gray before/after evidence board; private photos never published."""
from pathlib import Path
import sys,json
from PIL import Image,ImageDraw,ImageFont
V=Path(__file__).resolve().parents[1];R=V.parent;sys.path.insert(0,str(V/'scripts'))
from make_review_boards import masked
F=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);S=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
TAG=sys.argv[1] if len(sys.argv)>1 else 'r19'
BASE=sys.argv[2] if len(sys.argv)>2 else 'r15'
rows=[]
for k in [62,63,69]:
 photo=Image.open(next((R/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB');ann=json.loads((V/f'annotations/photo_{k}.json').read_text())
 before=Image.open(V/(f'renders/stage_bc_baseline/gray_r15_{k}.png' if BASE=='r15' else f'renders/gray_{BASE}_{k}.png')).convert('RGBA').resize(photo.size,Image.Resampling.LANCZOS)
 after=Image.open(V/f'renders/gray_{TAG}_{k}.png').convert('RGBA').resize(photo.size,Image.Resampling.LANCZOS)
 a,b=before.getchannel('A').getbbox(),after.getchannel('A').getbbox();box=(max(0,min(a[0],b[0])-25),max(0,min(a[1],b[1])-25),min(photo.width,max(a[2],b[2])+25),min(photo.height,max(a[3],b[3])+25))
 frames=[masked(photo,ann)]
 for im in [before,after]:
  bg=Image.new('RGB',photo.size,(228,228,228));bg.paste(im,(0,0),im);frames.append(bg)
 frames=[im.crop(box) for im in frames];h=round(580*frames[0].height/frames[0].width)
 row=Image.new('RGB',(1800,h+82),'white');d=ImageDraw.Draw(row)
 for i,(im,label) in enumerate(zip(frames,[f'实车 {k}（隐私遮蔽）',f'{BASE} 中性灰基线',f'{TAG} 结构重建'])):
  row.paste(im.resize((580,h)),(i*600+10,48));d.text((i*600+12,10),label,font=F,fill=(35,40,48))
 d.text((12,h+54),'固定照片相机；本轮形体检查仍未通过。主要灰阶统一；局部诊断材质变化不作外形验收。',font=S,fill=(140,55,35));rows.append(row)
out=Image.new('RGB',(1800,sum(r.height for r in rows)),'white');y=0
for row in rows:out.paste(row,(0,y));y+=row.height
p=V/f'renders/stage_bc_{TAG}_comparison.jpg';out.save(p,quality=93);print(p)
