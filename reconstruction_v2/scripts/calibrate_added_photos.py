"""Extract observed fluorescent rim pixels and fit candidate cameras for photos 69/70."""
from pathlib import Path
import sys, json, hashlib, datetime
ROOT = Path(__file__).resolve().parents[2]; V2 = ROOT / "reconstruction_v2"
sys.path.insert(0, str(ROOT / ".tools" / "calibration"))
import cv2, numpy as np
from PIL import Image, ImageDraw
from fit_cameras import solve

CONFIG = {
  69: {"side":"left", "plate":[[1350,600],[1490,600],[1490,760],[1350,760]],
       "boxes":{"front":(300,810,655,1120),"rear":(1100,700,1390,975)}},
  70: {"side":"right", "plate":[[0,865],[125,865],[125,1050],[0,1050]],
       "boxes":{"rear":(160,1120,510,1400),"front":(1020,900,1210,1220)}}}

def path_for(n):
    ps = sorted((ROOT/'IMG').glob(f'*_{n}_97.jpg'))
    if len(ps) != 1: raise RuntimeError(f'expected one photo {n}, got {ps}')
    return ps[0]

def arc_points(hsv, box, n):
    x0,y0,x1,y1=box; roi=hsv[y0:y1,x0:x1]
    m=cv2.inRange(roi,np.array([24,125,140]),np.array([48,255,255]))
    N,L,S,C=cv2.connectedComponentsWithStats(m); pts=[]
    for i,s in enumerate(S[1:],1):
        x,y,w,h,a=s
        if a >= 100:
            yy,xx=np.where(L==i); pts.extend(np.c_[xx+x0,yy+y0])
    pts=np.asarray(pts,np.float32)
    if len(pts)<20: return [], None
    center=np.median(pts,axis=0)
    # Median samples by observed polar angle. Hidden angles remain absent.
    ang=np.arctan2(pts[:,1]-center[1],pts[:,0]-center[0]); out=[]
    for theta in np.arange(-np.pi,np.pi,.10):
        d=np.arctan2(np.sin(ang-theta),np.cos(ang-theta)); sl=pts[np.abs(d)<.025]
        if len(sl)>=4: out.append(np.median(sl,axis=0).round(2).tolist())
    return out, center

def main():
    qa={"schema":"gsx-added-photo-calibration-qa-v1","photos":{},"generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for n,cfg in CONFIG.items():
        if (V2/f'annotations/photo_{n}.json').exists() and '--extract-again' not in sys.argv:
            print(n,'existing annotation preserved; --extract-again required'); continue
        p=path_for(n); im=Image.open(p).convert('RGB'); rgb=np.asarray(im); h,w=rgb.shape[:2]
        qa["photos"][str(n)]={"file":str(p.relative_to(ROOT)).replace('\\','/'),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":[w,h],"exif":dict(im.getexif()),"status":"candidate","unconfirmed":["rim stripe radius is estimated 220 +/- 5 mm","no lens distortion or body-shape validation","occluded rim arc not inferred","plate mask and HSV threshold require manual review"]}
        hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV); ann={"schema":"gsx-photo-landmarks-v2","image_id":n,"image_size":[w,h],"side":cfg["side"],"role":"fit","coordinate_system":"native image pixels; top-left origin","wheels":{},"exclude_polygons":[{"label":"license_plate","polygon":cfg["plate"]}]}
        preview=im.copy(); draw=ImageDraw.Draw(preview); draw.polygon(cfg["plate"],fill=(0,0,0))
        for k,box in cfg["boxes"].items():
            pts,center=arc_points(hsv,box,n)
            if len(pts)<5: ann["wheels"][k]={"center":None,"rim_points":pts,"rim_radius_mm":220,"estimated_stripe_radius_mm":220,"radius_uncertainty_mm":5,"arc_method":"HSV observed pixels only"}; continue
            ann["wheels"][k]={"center":None,"rim_points":pts,"rim_radius_mm":220,"estimated_stripe_radius_mm":220,"radius_uncertainty_mm":5,"arc_method":"HSV isolated fluorescent stripe pixels; medians in angular bins; visible samples only"}
            for x,y in pts: draw.ellipse((x-2,y-2,x+2,y+2),fill=(255,20,30))
        draw.polygon(cfg["plate"],fill=(0,0,0)); preview.save(V2/'renders'/f'added_rim_check_{n}.jpg',quality=90)
        ann["annotation_review"]="Candidate automated observed stripe extraction; no hidden arc points or stand-spool centers."
        ap=V2/'annotations'/f'photo_{n}.json'; ap.write_text(json.dumps(ann,ensure_ascii=False,indent=2),encoding='utf-8')
        try:
            out=solve(ann); out['annotation_sha256']=hashlib.sha256(ap.read_bytes()).hexdigest()
            eye=out['camera_position_m']; pose_ok=(eye[0] < 0 and eye[1] > 0) if n == 69 else (eye[0] > 0 and eye[1] < 0)
            if not pose_ok or eye[2] < 0.3: raise RuntimeError(f'candidate_rejected: eye position {eye} violates required quadrant/height')
            if out['K_px'][0][0] <= w * 0.55 * 1.001 or abs(out['front_steer_deg']) > 15: raise RuntimeError('candidate_rejected: focal length at bound or implausible steering')
            (V2/'calibration'/f'camera_{n}.json').write_text(json.dumps(out,indent=2),encoding='utf-8'); qa['photos'][str(n)].update({'rms_px':out['rms_px'],'median_abs_px':out['median_abs_px'],'p95_abs_px':out['p95_abs_px'],'camera_position_m':out['camera_position_m'],'front_steer_deg':out['front_steer_deg']})
        except Exception as exc:
            (V2/'calibration'/f'camera_{n}_candidate_rejected.json').write_text(json.dumps({'status':'candidate_rejected','error':str(exc)},indent=2),encoding='utf-8'); qa['photos'][str(n)]['status']='candidate_rejected'; qa['photos'][str(n)]['error']=str(exc)
    (V2/'qa'/'added_photos_calibration.json').parent.mkdir(exist_ok=True); (V2/'qa'/'added_photos_extraction.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()



