"""Catalogue-constrained 116-link 520 chain, with exact successive pin pitch.

This constrains model construction, not the owner's unknown chain adjustment,
sag, gearbox output height or modifications. Cameras never enter this solve.
"""
from pathlib import Path
import sys, json, math
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V.parent/'.tools/calibration'))
import numpy as np
from scipy.optimize import brentq

PITCH=15.875; LINKS=116; REAR_TEETH=46; FRONT_TEETH=14
RR=PITCH/(2*math.sin(math.pi/REAR_TEETH))
RF=PITCH/(2*math.sin(math.pi/FRONT_TEETH))
REAR=np.array([-715.,313.9]); FRONT_Z=370.

def layout(distance):
    front=np.array([REAR[0]+math.sqrt(distance**2-(FRONT_Z-REAR[1])**2),FRONT_Z])
    u=(front-REAR)/distance;v=np.array([-u[1],u[0]])
    theta=math.acos((RR-RF)/distance)
    rear_arc=RR*(2*math.pi-2*theta);straight=math.sqrt(distance**2-(RR-RF)**2);front_arc=2*RF*theta
    length=rear_arc+2*straight+front_arc
    def radial(a):return u*math.cos(a)+v*math.sin(a)
    ar=REAR+RR*radial(-theta);bf=front+RF*radial(-theta);bu=front+RF*radial(theta);au=REAR+RR*radial(theta)
    def point(s):
        s=s%length
        if s<rear_arc:return REAR+RR*radial(theta+s/RR)
        s-=rear_arc
        if s<straight:return ar+(bf-ar)*(s/straight)
        s-=straight
        if s<front_arc:return front+RF*radial(-theta+s/RF)
        return bu+(au-bu)*((s-front_arc)/straight)
    return point,length,front,rear_arc

def pins(distance):
    point,length,front,rear_arc=layout(distance)
    s=rear_arc*.5;start=s;points=[point(s)]
    for _ in range(LINKS):
        base=point(s)
        ds=brentq(lambda d:np.linalg.norm(point(s+d)-base)-PITCH,PITCH*.999,PITCH*1.08,xtol=1e-10)
        s+=ds;points.append(point(s))
    return s-start-length,np.array(points),front,length

def main():
    dest=V/'data/drive_layout.json'
    if dest.exists():raise FileExistsError(dest)
    distance=brentq(lambda d:pins(d)[0],650,710,xtol=1e-9)
    _,points,front,perimeter=pins(distance)
    p=points[:-1];d=np.linalg.norm(np.roll(p,-1,axis=0)-p,axis=1)
    result={'revision':'r20','units':'mm','chain_pitch':PITCH,'link_count':LINKS,
      'rear_teeth':REAR_TEETH,'front_teeth':FRONT_TEETH,'rear_pitch_radius':RR,'front_pitch_radius':RF,
      'rear_center_yz':REAR.tolist(),'front_center_yz':front.tolist(),'center_distance':distance,
      'chain_plane_x':-101.,'pins_yz':p.tolist(),'pitch_min':float(d.min()),'pitch_max':float(d.max()),
      'closure_error':float(np.linalg.norm(points[-1]-points[0])),
      'evidence':['Suzuki GSX250RAM1 parts FIG.206A: 14T front and 116-link DID520; FIG.550B:46T rear',
                  'DID motorcycle chain size table: 520 pitch15.875mm, inner width6.35mm'],
      'uncertain':['Family catalogue not owner teardown','Front output Z370 and chain X-101 retain old assumptions',
                   'Taut ideal layout; real sag, wear, adjuster and suspension state unmeasured',
                   'Approximate tooth flanks; not a transmission simulation'],
      'sources':['https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX250RAM1_GSX250RAZM1.pdf','https://didmc.com/chain/engine/']}
    dest.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:result[k] for k in ['center_distance','front_center_yz','pitch_min','pitch_max','closure_error']}))
if __name__=='__main__':main()
