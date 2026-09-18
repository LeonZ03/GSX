"""Initialize editable control cages once. Never silently replaces hand edits.
All points in millimetres. Photo 62 rays set Y/Z; X widths remain provisional.
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'.tools/calibration'))
import numpy as np
c=json.loads((V2/'calibration/camera_62.json').read_text());R=np.array(c['R_cv']);t=np.array(c['t_cv_m']);K=np.array(c['K_px']);eye=-R.T@t

def ray(uv,x):
 d=R.T@np.linalg.inv(K)@np.array([*uv,1]);return ((eye+d*((x/1000-eye[0])/d[0]))*1000).round(3).tolist()

def ruled(top,bottom,widths,bottom_widths=None,cols=7):
 rows=[]
 for i,(a,b) in enumerate(zip(top,bottom)):
  pa=np.array(ray(a,widths[i]));pb=np.array(ray(b,(bottom_widths or widths)[i]));row=[]
  for u in np.linspace(0,1,cols):
   p=pa*(1-u)+pb*u;p[0]+=4*np.sin(u*np.pi);row.append(p.round(3).tolist())
  rows.append(row)
 return rows

def write(name,grid,material='shell',mirror=True,sub=2,thickness=3,notes=''):
 p=V2/'data/control_cages'/f'{name}.json'
 if p.exists():raise RuntimeError(f'Protected editable cage already exists: {p.name}')
 p.write_text(json.dumps({'name':name,'units':'mm','grid':grid,'mirror_x':mirror,'subdivision':sub,'thickness_mm':thickness,'material':material,'evidence':['owner_photo_62','owner_photo_63','official_turntable_05'],'status':'provisional_multiview_review_required','notes':notes},indent=2))

def main():
 # Transverse points deliberately describe shoulder, ridge and knee scallop separately.
 tank=[]
 sections=[[-156,52,804,778],[-143,61,823,781],[-102,94,873,784],[-42,151,927,781],[45,188,952,771],[130,191,960,767],[210,180,948,775],[285,151,923,798],[340,86,878,812],[350,76,866,816]]
 for y,w,top,bot in sections:
  tank.append([[0,y,top],[w*.28,y,top-1],[w*.67,y,top-12],[w*.93,y,top-37],[w,y,top-65],[w*.84,y,bot+40],[w*.62,y,bot],[0,y,bot]])
 write('Body_Tank',tank,'tank',notes='Distinct crown, shoulders and knee indentation. Widths need cockpit/left-side validation; not metric-certified.')
 # Rider seat saddle: official nominal low point 790 mm, side contour checked against photo.
 rows=[]
 for y,w,z in [[-530,96,853],[-520,112,851],[-468,137,819],[-365,151,791],[-265,142,789],[-158,109,802],[-89,60,826],[-80,46,829]]:
  rows.append([[0,y,z+5],[w*.42,y,z+3],[w*.86,y,z],[w,y,z-12],[w*.91,y,z-31],[0,y,z-32]])
 write('Seat_Rider',rows,'seat',thickness=0)
 rows=[]
 for y,w,z in [[-922,30,925],[-913,54,928],[-831,95,916],[-739,105,899],[-631,109,874],[-571,100,858],[-564,87,854]]:
  rows.append([[0,y,z],[w*.6,y,z-1],[w*.95,y,z-5],[w,y,z-18],[w*.82,y,z-31],[0,y,z-33]])
 write('Seat_Pillion',rows,'seat',thickness=0)
 rows=[]
 for y,w,zt,zb in [[-954,18,918,890],[-937,55,926,878],[-869,99,912,851],[-749,131,890,802],[-626,146,855,753],[-497,159,806,707],[-360,150,781,698],[-211,105,782,727],[-174,89,790,750]]:
  rows.append([[0,y,zt],[w*.76,y,zt],[w,y,zt-22],[w*.91,y,zb+9],[w*.72,y,zb],[0,y,zb+3]])
 write('Body_Tail',rows,'shell',notes='Tail hidden by luggage in fit views; official profile supplies only initial topology. Not accepted.')
 top=[[628,940],[710,923],[805,901],[913,875],[1018,853],[1110,836],[1180,831],[1219,850]]
 bottom=[[649,965],[751,1001],[859,1020],[972,1008],[1052,959],[1145,909],[1202,874],[1219,855]]
 write('Body_SideFairing',ruled(top,bottom,[183,212,235,257,249,221,143,64],[185,213,233,228,206,173,106,64]),notes='Side shell top/bottom rails selected from actual panel edges, not decal edges.')
 # The down-swept blade is a separate editable patch joined visually beneath side panel.
 write('Body_FairingBlade',ruled([[859,1018],[873,1060],[899,1137],[976,1205],[982,1210]],[[1052,957],[1010,1032],[979,1116],[985,1204],[986,1210]],[233,213,182,150,147],[206,196,164,150,147]),notes='Wheel opening and rear engine aperture must be evaluated independently.')
 write('Body_BellyPan',ruled([[610,1198],[683,1160],[793,1174],[895,1202],[982,1210]],[[592,1224],[698,1231],[807,1237],[908,1235],[986,1219]],[120,150,163,163,147],[113,131,136,140,147]),sub=1)
 # Black tank surround and intake strip, modelled as discrete shells.
 write('Body_TankSideTrim',ruled([[696,791],[762,812],[842,844],[906,850]],[[723,856],[809,885],[861,899],[906,874]],[190,207,215,218],[182,202,213,218]),'trim',sub=1)
 # Fairing shoulders run from cockpit side to nose. Each row is inner / ridge / outer.
 rows=[]
 for inner,outer,wi,wo in [([911,780],[939,800],110,248),([945,758],[1020,806],117,265),([1025,723],[1103,818],126,256),([1090,750],[1160,832],121,217),([1161,786],[1200,847],97,142),([1204,826],[1219,850],42,65)]:
  a=np.array(ray(inner,wi));b=np.array(ray(outer,wo));rows.append([(a*(1-u)+b*u+np.array([3*np.sin(np.pi*u),0,8*np.sin(np.pi*u)])).tolist() for u in [0,.12,.4,.73,.93,1]])
 write('Body_UpperCowling',rows,'shell')
 # Central lamp surround: shield silhouette from owner front view 66, surface depth provisional.
 rows=[]
 for z,w,y in [[895,91,738],[884,114,758],[849,112,784],[803,95,811],[761,66,822],[725,31,820],[714,0.8,816]]:
  rows.append([[0,y+15,z],[w*.55,y+10,z],[w*.88,y+2,z],[w,y,z]])
 write('Headlight_Surround',rows,'trim',sub=1,thickness=4)
 rows=[]
 for z,w,y in [[878,83,759],[870,100,775],[839,97,795],[805,82,817],[769,58,830],[744,28,829],[738,1,826]]:
  rows.append([[0,y+13,z],[w*.5,y+11,z],[w*.85,y+5,z],[w,y,z]])
 write('Headlight_Lens',rows,'lamp',sub=1,thickness=2)
 rows=[]
 for z,y,w in [[893,739,72],[909,707,107],[957,642,129],[1020,554,146],[1074,493,169],[1082,483,175]]:
  rows.append([[0,y+25,z],[w*.4,y+21,z+2],[w*.76,y+9,z+4],[w,y,z]])
 write('Windscreen',rows,'wind',sub=2,thickness=3,notes='Opaque light gray for shape comparison; transparent material postponed.')
 # Front fender: central ridge and side flanges are explicit cage columns.
 rows=[]
 for y,z,w in [[422,528,61],[441,559,69],[510,612,76],[625,640,79],[760,640,77],[895,614,69],[944,595,57],[951,592,51]]:
  rows.append([[0,y,z],[w*.43,y,z-2],[w*.89,y,z-16],[w,y,z-31]])
 write('Fender_Front',rows,'shell',sub=2)
 print('Created editable cages; rerun is intentionally refused to preserve refinements.')
if __name__=='__main__':main()
