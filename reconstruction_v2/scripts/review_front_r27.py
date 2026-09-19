"""Private open-rail comparison, never a whole silhouette or keypoint score."""
from pathlib import Path
import json,sys
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V.parent/'.tools/calibration'))
import numpy as np
from scipy.spatial import cKDTree

def dense(p):
    p=np.array(p);q=[]
    for a,b in zip(p,p[1:]):q.extend(np.linspace(a,b,max(2,int(np.linalg.norm(a-b)*3))))
    return np.array(q)
def run():
    qa=V/'qa/front_r27';g=json.loads((qa/'geometry.json').read_text());ref=json.loads((qa/'fairing_ridge.local.json').read_text())['front_segments'];metrics={}
    for k in [62,63,69]:
        c=json.loads((V/f'calibration/camera_{k}.json').read_text());R=np.array(c['R_cv']);t=np.array(c['t_cv_m']);K=np.array(c['K_px']);target=dense(ref[str(k)]);entry={}
        for label,key in [('r26','baseline_diagnostics'),('r27','candidate_diagnostics')]:
            w=np.array(g[key]['evaluated_upper_rail_m']);w=w[np.argsort(w[:,1])]
            i=np.searchsorted(w[:,1],.300);a,b=w[i-1],w[i];start=a+(b-a)*(.300-a[1])/(b[1]-a[1]);w=np.vstack([start,w[i:]])
            if k==69:w[:,0]*=-1
            q=w@R.T+t;p=q@K.T;p=p[:,:2]/p[:,2,None];p=dense(p)
            d=np.r_[cKDTree(target).query(p)[0],cKDTree(p).query(target)[0]]
            entry[label]={'median_px':float(np.median(d)),'p95_px':float(np.percentile(d,95)),'max_px':float(d.max())}
        metrics[str(k)]=entry
    report={'scope':'Evaluated open forward upper rail only. Approximate matched start at Y=300 mm; hand-traced uncertainty +/-5 px; all three angles used in fitting. No closed mask, independent holdout, keypoint or whole-bike accuracy claim.','metrics':metrics}
    (qa/'upper_rail_metrics.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
