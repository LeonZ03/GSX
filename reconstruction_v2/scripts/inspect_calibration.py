"""Inspect projected wheel constraints and triangulate candidate visible body points.
Triangulations are diagnostics, not automatic surface vertices or metric certification.
"""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'))
import numpy as np,cv2
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
from fit_cameras import wheel,project,CENTERS

def main():
 cams={};anns={}
 for k in [62,63]:
  c=json.loads((V2/f'calibration/camera_{k}.json').read_text());a=json.loads((V2/f'annotations/photo_{k}.json').read_text());cams[k]=c;anns[k]=a
  im=Image.open(next((ROOT/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB');d=ImageDraw.Draw(im)
  for reg in a['exclude_polygons']:
   if reg['polygon']:d.polygon([tuple(p) for p in reg['polygon']],fill=(55,55,55))
  for name,ann in a['wheels'].items():
   cen,u,v=wheel(name,math.radians(c['front_steer_deg']))
   ps=[cen+(c['rim_radius_mm']/1000)*(u*math.cos(t)+v*math.sin(t)) for t in np.linspace(0,2*math.pi,181)]
   pix=project(ps,np.array(c['R_cv']),np.array(c['t_cv_m']),np.array(c['K_px']))
   d.line([tuple(p) for p in pix],fill=(0,255,255),width=3)
   for x,y in ann['rim_points']:d.ellipse((x-3,y-3,x+3,y+3),fill=(255,80,30))
   x,y=ann['center'];d.line((x-10,y,x+10,y),fill='yellow',width=2);d.line((x,y-10,x,y+10),fill='yellow',width=2)
  im.save(V2/f'renders/camera_fit_{k}.jpg',quality=91)
 out={}
 for name in anns[62]['landmarks']:
  obs=[anns[k]['landmarks'][name]['xy'] for k in [62,63]]
  def fun(p):return np.concatenate([project([p],np.array(cams[k]['R_cv']),np.array(cams[k]['t_cv_m']),np.array(cams[k]['K_px']))[0]-xy for k,xy in zip([62,63],obs)])
  o=least_squares(fun,[.16,0,.8]);out[name]={'point_mm':(o.x*1000).tolist(),'residuals_px':fun(o.x).tolist()}
 (V2/'calibration/body_point_candidates.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
