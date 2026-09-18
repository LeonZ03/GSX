"""Score local evaluated tank candidates against fixed open photo boundaries.
Uses photos62/63 to rank; 69 is an additional regression check, not a holdout.
No model or canonical control JSON is changed by this script.
"""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';sys.path[:0]=[str(ROOT/'.tools/calibration'),str(V2/'scripts')]
from interface_projection import raster,measure
ann=json.loads((V2/'annotations/tank_interface_r13.json').read_text());base=json.loads((V2/'qa/interface_mesh_r11.json').read_text());small='--small' in sys.argv;folder=V2/('qa/interface_candidates_r13_small' if small else 'qa/interface_candidates_r13');index=json.loads((folder/'index.json').read_text());base['Other_Occluders']=json.loads((V2/'qa/interface_occluders_r13.json').read_text());cameras={k:json.loads((V2/f'calibration/camera_{k}.json').read_text()) for k in ann['views']};rows=[]
for candidate in index['candidates']:
 data=json.loads((folder/(candidate['name']+'.json')).read_text());meshes=dict(base,Body_Tank=data['geometry']);metrics={k:measure(raster(meshes,cameras[k],a['crop']),a) for k,a in ann['views'].items()};score=sum(m['contact']['mean_px']+m['rear_outline']['mean_px']+.25*m['trim_top']['mean_px'] for k,m in metrics.items() if k in ['62','63'])
 row=dict(candidate,metrics=metrics,fit_score=score);rows.append(row);print(candidate['name'],'score',round(score,2),'69',round(metrics['69']['contact']['mean_px'],1),round(metrics['69']['rear_outline']['mean_px'],1),flush=True)
rows.sort(key=lambda r:r['fit_score']);report={'status':'NOT_PASSED','fit_views':[62,63],'additional_check_view':69,'independent_holdout':False,'rows':rows,'limitations':'One-way open visible-part edge distance; not full silhouette, named keypoints or whole-bike similarity. Other render-visible geometry intersecting the three review crops supplies occlusion; partial local boundaries only.'}
(V2/('qa/interface_fit_r13_small.json' if small else 'qa/interface_fit_r13.json')).write_text(json.dumps(report,indent=2),encoding='utf8');print('TOP',[(r['name'],round(r['fit_score'],2)) for r in rows[:5]],flush=True)