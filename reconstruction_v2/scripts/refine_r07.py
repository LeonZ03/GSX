"""Explicit headlight position-lamp and mirror envelope cage additions.
Observed in photos 63/66/69; dimensions remain provisional until camera review.
"""
from pathlib import Path
import json,shutil
V=Path(__file__).resolve().parents[1];D=V/'data/control_cages';A=V/'calibration/r06_frozen';A.mkdir(exist_ok=True)
if not (A/'control_cages').exists():shutil.copytree(D,A/'control_cages')
sections=[((161,744,885),(172,733,895)),((112,792,852),(159,753,875)),((103,814,822),(125,796,841)),((105,815,817),(113,806,827))]
for name,mat,expand in [('Headlight_PositionSurround','trim',1.12),('Headlight_PositionLens','lamp',1.)]:
 g=[]
 for a,b in sections:
  mid=[(x+y)/2 for x,y in zip(a,b)];aa=[m+(v-m)*expand for v,m in zip(a,mid)];bb=[m+(v-m)*expand for v,m in zip(b,mid)]
  row=[]
  for u in [0,.04,.33,.67,.96,1]:
   p=[x*(1-u)+y*u for x,y in zip(aa,bb)];p[1]+=1.5 if mat=='lamp' else -1;row.append(p)
  g.append(row)
 a={'name':name,'units':'mm','grid':g,'mirror_x':True,'subdivision':1,'thickness_mm':2,'material':mat,'crease_boundary':.8,'revision':'r07','evidence':['owner_photo_63','owner_photo_66','owner_photo_69'],'status':'provisional_multiview_review_required','notes':'Observed diagonal position-light envelopes beside the central lamp; optical reflector detail deferred. Photo 66 is therefore a used reference, not an independent holdout.'}
 (D/(name+'.json')).write_text(json.dumps(a,indent=2))
mirrors={'revision':'r07','units':'mm','status':'provisional_pose_and_shell_review','evidence':['owner_photo_63','owner_photo_66'],'center_right':[310,610,1049],'center_left':[-310,610,1049],'normal_right':[.55,.83,.08],'normal_left':[-.10,.99,.08],'outline_uv_mm':[[-70,60],[-20,48],[35,20],[60,-30],[36,-57],[-57,-45]],'notes':'Back-shell outline based on visible 63 silhouette. Separate left yaw reflects independently adjustable mirror; no symmetry claim for adjusted mirror pose.'}
(V/'data/mirror_control.json').write_text(json.dumps(mirrors,indent=2))