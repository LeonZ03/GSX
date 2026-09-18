"""Explicit r05 cage migration from reviewed photo edges and two-view diagnostics.
Keeps the r04 data/cameras as a local immutable starting point. Never accumulates
transformations on an already migrated cage. All dimensions are provisional.
"""
from pathlib import Path
import json,sys,shutil
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'))
import numpy as np
from fit_cameras import project
D=V2/'data/control_cages';F=V2/'calibration/r04_frozen';F.mkdir(exist_ok=True)
if not (F/'control_cages').exists():shutil.copytree(D,F/'control_cages')
for k in [62,63,64]:
 if not (F/f'camera_{k}.json').exists():shutil.copy2(V2/f'calibration/camera_{k}.json',F/f'camera_{k}.json')
old=json.loads((F/'camera_62.json').read_text());new=json.loads((V2/'calibration/joint_candidate/camera_62.json').read_text())
R=np.array(new['R_cv']);t=np.array(new['t_cv_m']);K=np.array(new['K_px']);eye=-R.T@t

def ray(uv,x):
 d=R.T@np.linalg.inv(K)@np.r_[uv,1];return ((eye+d*((x*.001-eye[0])/d[0]))*1000).round(4)

def write(name,grid,material='shell',sub=1,mirror=True,thickness=2.5,notes='',creases=None):
 a={'name':name,'units':'mm','grid':np.array(grid).round(4).tolist(),'mirror_x':mirror,'subdivision':sub,'thickness_mm':thickness,'material':material,'evidence':['owner_photo_62','owner_photo_63'],'status':'provisional_multiview_review_required','revision':'r05','notes':notes}
 if creases:a['crease_columns']=creases
 (D/f'{name}.json').write_text(json.dumps(a,indent=2),encoding='utf8')

def ruled(top,bottom,wa,wb=None,bulge=0,columns=(0,.04,.20,.46,.74,.96,1)):
 out=[]
 for i,(a,b) in enumerate(zip(top,bottom)):
  pa=ray(a,wa[i]);pb=ray(b,(wb or wa)[i]);out.append([(pa*(1-u)+pb*u+np.array([bulge*np.sin(u*np.pi),0,0])).tolist() for u in columns])
 return out

# Reproject old evidence to the camera correction without keeping stale Y/Z.
for p in sorted((F/'control_cages').glob('*.json')):
 a=json.loads(p.read_text());g=np.array(a['grid']);flat=g.reshape((-1,3));uv=project(flat*.001,np.array(old['R_cv']),np.array(old['t_cv_m']),np.array(old['K_px']));a['grid']=np.array([ray(pix,point[0]) for pix,point in zip(uv,flat)]).reshape(g.shape).tolist();a['revision']='r05';a['notes']+=' Evidence preserved through joint camera correction; not metric certified.'
 (D/p.name).write_text(json.dumps(a,indent=2))

# Actual faceted trim boundary; the former tiny convex rounded panel was wrong.
write('Body_TankSideTrim',ruled([[644,823],[659,813],[700,804],[750,803],[803,812],[869,835],[933,853],[982,854]],[[644,827],[677,842],[732,852],[796,870],[838,889],[876,892],[938,870],[982,856]],[120,133,145,177,195,212,206,190],[120,149,175,193,220,233,225,190],bulge=3),'trim',notes='Manually read actual panel seams in photos 62/63. S-emblem two-view point constrains mid-panel width near 218 mm. Edge widths remain estimates.',creases={'2':.55,'4':.35})

# Main shell including the blade: a single continuous quad patch, no invented seam.
write('Body_SideFairing',ruled([[671,938],[750,919],[841,894],[926,870],[1008,850],[1090,829],[1169,828],[1214,849]],[[715,975],[840,1012],[880,1050],[906,1153],[982,1210],[1001,1048],[1119,919],[1214,854]],[170,196,220,232,228,210,152,58],[190,216,204,166,115,141,169,58],bulge=2),sub=2,notes='Continuous side fairing/blade control surface. Upper right decals triangulate near X 215-231 mm; bottom pan decals near X 100-160 mm. Near engine and fork openings remain under review.')
# Keep old blade data as a historical editable file, outside the active cage folder.
A=V2/'data/archive/r04';A.mkdir(parents=True,exist_ok=True)
if (D/'Body_FairingBlade.json').exists():
 shutil.copy2(F/'control_cages/Body_FairingBlade.json',A/'Body_FairingBlade.json')
 (D/'Body_FairingBlade.json').unlink()
write('Body_BellyPan',ruled([[610,1198],[683,1160],[793,1174],[895,1202],[982,1210]],[[592,1224],[698,1231],[807,1237],[908,1235],[986,1219]],[127,166,148,105,115],[120,142,117,96,115]),notes='Widths reduced to observed two-view decal points; does not certify unseen underside.')

# Tank knee edges must not fold upwards across themselves at the narrow ends.
p=D/'Body_Tank.json';a=json.loads(p.read_text());g=np.array(a['grid'])
for row in g:
 # Fixed ordered cross-section: shoulder -> knee -> lower lip; no inverted segment.
 row[5,2]=min(row[5,2],row[4,2]-6);row[6,2]=min(row[6,2],row[5,2]-8);row[7,2]=row[6,2]
 # Flatter crown and firmer shoulder break, with separate lower knee recess.
 row[2,2]=row[0,2]-8;row[3,2]=row[0,2]-27
rowcount=len(g);a['grid']=g.round(4).tolist();a['crease_columns']={'2':.35,'3':.25,'5':.3};a['notes']+=' Corrected self-folding end cross sections and shoulder transitions.';p.write_text(json.dumps(a,indent=2))
# Rear tail cover must end behind the rider saddle. Its old shell hid the separate side panel.
p=D/'Body_Tail.json';a=json.loads(p.read_text());a['grid']=a['grid'][:6];a['notes']+=' Forward blanket shell cut back to expose the separate SeatSide and MidSideCover components.';p.write_text(json.dumps(a,indent=2))

# Blue cockpit side shell follows the black insert boundary, not a generic wing.
write('Body_UpperCowling',ruled([[850,789],[900,777],[958,754],[1028,735],[1054,748],[1104,784],[1146,807],[1194,837]],[[878,814],[935,821],[998,827],[1063,829],[1125,839],[1162,846],[1195,853],[1210,853]],[130,132,148,168,162,135,103,63],[190,205,213,220,198,161,104,58],bulge=1),notes='Blue upper lip around actual black cockpit insert; edge rays taken from owner side view. Needs front-view gate.')
write('Body_CowlingSide',ruled([[878,814],[935,821],[998,827],[1063,829],[1125,839],[1162,846],[1195,853],[1210,853]],[[870,833],[933,853],[1008,850],[1090,829],[1127,831],[1169,828],[1205,843],[1210,854]],[190,205,213,220,198,161,104,58],[208,219,228,210,185,152,87,58],bulge=2),notes='Blue upper fairing side beneath insert; separate from main side shell as actual seam.')
write('Cockpit_InnerPanel',ruled([[872,786],[912,776],[965,754],[1028,735],[1054,748],[1104,784]],[[879,793],[920,799],[971,800],[1022,799],[1069,793],[1104,786]],[115,121,144,168,162,135],[133,166,190,199,180,137],bulge=0),'trim',notes='Black inner infill visible between tank front and upper fairing. Separate shell, no decals.')

# Explicit observed nodes instead of an auto-smoothed oval; left side mirrors right.
curves={'units':'mm','revision':'r05','status':'PROVISIONAL','notes':'Paired observed tube nodes 62/63; individual mounting depths still unmeasured. Sharp straights joined by short-radius bends.','right_nodes':{'rear':[218,10,497],'upper':[303,265,545],'lower':[297,222,433],'lower_mount':[210,261,343],'rear_mount':[145,-183,444]},'tube_radius_mm':12.5}
(V2/'data/guard_control.json').write_text(json.dumps(curves,indent=2))
for k in [62,63]:
 c=json.loads((V2/f'calibration/joint_candidate/camera_{k}.json').read_text());c['status']='r05_locked_joint_candidate_not_metric_certified'
 # Remove stale single-view residual summaries inherited from r04.
 for key in ['median_abs_px','p95_abs_px','residuals_px']:c.pop(key,None)
 (V2/f'calibration/camera_{k}.json').write_text(json.dumps(c,indent=2))
print('r05 editable cages prepared; old cameras and cages preserved in calibration/r04_frozen')