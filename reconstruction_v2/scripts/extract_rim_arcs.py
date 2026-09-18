"""Extract actually observed fluorescent rim stripe arc samples, never hidden arcs."""
from pathlib import Path
import sys,json,shutil
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'));import cv2,numpy as np
from PIL import Image,ImageDraw
BOXES={62:{'rear':(45,1000,362,1314),'front':(1020,980,1280,1315)},63:{'rear':(70,1015,292,1293),'front':(829,1118,1186,1505)},64:{'front':(0,1330,189,1475),'rear':(780,1287,1148,1620)}}

def main():
 for k,boxes in BOXES.items():
  p=V2/f'annotations/photo_{k}.json';a=json.loads(p.read_text());backup=V2/f'annotations/manual_v2/photo_{k}.json';backup.parent.mkdir(exist_ok=True)
  if not backup.exists():shutil.copy2(p,backup)
  im=Image.open(next((ROOT/'IMG').glob(f'*_{k}_97.jpg'))).convert('RGB');rgb=np.array(im);hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV);draw=ImageDraw.Draw(im)
  for name,(x0,y0,x1,y1) in boxes.items():
   roi=hsv[y0:y1,x0:x1];mask=cv2.inRange(roi,np.array([24,125,140]),np.array([48,255,255]))
   n,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
   valid=np.zeros_like(mask)
   for i,stat in enumerate(stats[1:],1):
    if stat[4]>40:valid[labels==i]=255
   yy,xx=np.where(valid);pts=np.column_stack((xx+x0,yy+y0)).astype(np.float32)
   if len(pts)<80:continue
   ellipse=cv2.fitEllipse(pts);center=np.array(ellipse[0]);ang=np.arctan2(pts[:,1]-center[1],pts[:,0]-center[0]);samples=[]
   for theta in np.arange(-np.pi,np.pi,.13):
    d=np.arctan2(np.sin(ang-theta),np.cos(ang-theta));sl=pts[abs(d)<.022]
    if len(sl)>7:samples.append(np.median(sl,axis=0).round(2).tolist())
   if len(samples)>=5:
    a['wheels'][name]['rim_points']=samples;a['wheels'][name]['rim_radius_mm']=220;a['wheels'][name]['arc_method']='HSV isolated fluorescent stripe pixels; medians in angular bins; visible samples only';a['wheels'][name]['estimated_stripe_radius_mm']=220;a['wheels'][name]['radius_uncertainty_mm']=5
    for u,v in samples:draw.ellipse((u-3,v-3,u+3,v+3),fill=(255,20,30))
    print(k,name,len(samples),'ellipse',ellipse)
  for e in a['exclude_polygons']:
   if e['polygon']:draw.polygon([tuple(p) for p in e['polygon']],fill=(55,55,55))
  im.save(V2/f'renders/stripe_samples_{k}.jpg',quality=90)
  a['annotation_review']='Automated observed stripe arc extraction replaces hand-traced rim edges. Metric stripe radius remains estimated.'
  p.write_text(json.dumps(a,indent=2))
if __name__=='__main__':main()
