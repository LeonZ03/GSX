"""Create private rider-control comparisons from fixed photo renders."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
V=Path(__file__).resolve().parents[1];R=V/'renders';TAG=sys.argv[1] if len(sys.argv)>1 else 'r26'
f=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);out=Image.new('RGB',(1800,1515),'white')
for row,(k,box) in enumerate([(62,(430,990,720,1210)),(63,(300,1020,540,1260)),(69,(920,770,1140,985))]):
 photo=Image.open(next((V.parent/'IMG').glob(f'*_{k}_*.jpg'))).convert('RGB');panels=[photo]
 for tag in ['r25',TAG]:
  gray=Image.open(R/f'gray_{tag}_{k}.png').convert('RGBA').resize(photo.size);bg=Image.new('RGB',photo.size,(220,220,220));bg.paste(gray,(0,0),gray);panels.append(bg)
 for col,im in enumerate(panels):
  crop=im.crop(box);scale=min(580/crop.width,455/crop.height);crop=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS);out.paste(crop,(col*600+10,row*505+42));ImageDraw.Draw(out).text((col*600+10,row*505+7),f'{k} '+['实车局部','r25',TAG+' 局部重建'][col],font=f,fill='black')
out.save(R/f'rearset_{TAG}_comparison.jpg',quality=94)
