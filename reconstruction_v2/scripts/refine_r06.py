from pathlib import Path
import sys,json,shutil
sys.path.insert(0,'.tools/calibration');import numpy as np
V=Path('reconstruction_v2');D=V/'data/control_cages';A=V/'calibration/r05_frozen';A.mkdir(exist_ok=True)
if not (A/'control_cages').exists():shutil.copytree(D,A/'control_cages')
c=json.loads((V/'calibration/camera_62.json').read_text());R=np.array(c['R_cv']);K=np.array(c['K_px']);eye=-R.T@np.array(c['t_cv_m'])
def ray(uv,x):
 d=R.T@np.linalg.inv(K)@[*uv,1];return (eye+d*((x*.001-eye[0])/d[0]))*1000
p=D/'Body_UpperCowling.json';a=json.loads(p.read_text());top=[[850,789],[900,795],[958,800],[1028,798],[1074,793],[1104,784],[1146,807],[1194,837]];width=[130,155,182,197,179,135,103,63];g=np.array(a['grid']);us=[0,.04,.20,.46,.74,.96,1]
for i,(uv,x) in enumerate(zip(top,width)):
 pa=ray(uv,x);pb=g[i,-1];g[i]=[pa*(1-u)+pb*u+np.array([np.sin(u*np.pi),0,0]) for u in us]
a['grid']=g.round(4).tolist();a['revision']='r06';a['notes']+=' Corrected blue lip to LOWER edge of black insert; previous iteration mistakenly covered the insert.';a['crease_boundary']=.35;p.write_text(json.dumps(a,indent=2))
# Keep distinctive tips/joins when subdividing, instead of rounding off all four edges.
for n,w in [('Body_SideFairing',.65),('Body_TankSideTrim',.75),('Body_SeatSide',.55),('Body_MidSideCover',.50),('Body_BellyPan',.65)]:
 p=D/(n+'.json');a=json.loads(p.read_text());a['crease_boundary']=w;a['revision']='r06';p.write_text(json.dumps(a,indent=2))