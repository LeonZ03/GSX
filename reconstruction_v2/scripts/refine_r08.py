"""Correct the exposed rider-seat joint revealed by the new left-front view."""
from pathlib import Path
import json,shutil
import sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V.parent/'.tools/calibration'));import numpy as np
D=V/'data/control_cages';A=V/'calibration/r07_frozen';A.mkdir(exist_ok=True)
if not (A/'control_cages').exists():shutil.copytree(D,A/'control_cages')
p=D/'Body_SeatSide.json';a=json.loads(p.read_text());g=np.array(a['grid']);zt=[825,784,762,780,776,747];xt=[108,145,150,144,169,185]
for i in range(len(g)):
 dz=zt[i]-g[i,0,2];dx=xt[i]-g[i,0,0]
 for j in range(g.shape[1]):
  f=1-j/(g.shape[1]-1);g[i,j,2]+=dz*f;g[i,j,0]+=dx*f
# Meet the seat lower edge, keeping the observed lower seam independent.
a['grid']=g.round(4).tolist();a['revision']='r08';a['notes']+=' Raised upper joint to the rider-seat underside after new photo 69 revealed an open gap in r07. Lower observed rail preserved. No metric acceptance.';p.write_text(json.dumps(a,indent=2))
# Added pillion breadth is a provisional observation from the clear new photo.
p=D/'Seat_Pillion.json';a=json.loads(p.read_text());g=np.array(a['grid']);g[:,:,0]*=1.10;a['grid']=g.round(4).tolist();a['revision']='r08';a['notes']+=' Pillion breadth increased 10 percent from the newly visible photo 69 envelope; unmeasured.';p.write_text(json.dumps(a,indent=2))
p=V/'scripts/upgrade_r05.py';t=p.read_text();t=t.replace("('r05','r06','r07')","('r05','r06','r07','r08')");t=t.replace("print('R05_SAVED',len(s.objects))","print(revision+'_SAVED',len(s.objects))");p.write_text(t,encoding='utf8')