"""Seat-interface candidates from actual cushion underside ray intersections.
The 3/4 mm construction clearances are modeling choices, not real measurements.
No canonical JSON or source blend is modified here.
"""
from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene
if s.get('revision')!='r10':raise RuntimeError('Expected rider candidate')
dg=bpy.context.evaluated_depsgraph_get();o=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'));e=o.evaluated_get(dg);m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[list(f.vertices) for f in m.polygons]);e.to_mesh_clear()
def underside(x,y):
 hit,_,_,_=tree.ray_cast(Vector((x*.001,y*.001,.4)),Vector((0,0,1)),.6)
 return hit.z*1000 if hit else None
report={'status':'candidate','clearance_note':'3/4 mm are construction gaps only, not measured from real motorcycle','changes':[]}
a=json.loads((V2/'calibration/r09_tail_frozen/Body_SeatSide.json').read_text())
for j,x in [(1,137),(2,134)]:
 row=a['grid'][j];old=list(row[0]);z=underside(x,old[1]);assert z is not None
 delta=[x-old[0],z-3-old[2]]
 for i,w in enumerate([1,.65,.25]):row[i][0]+=delta[0]*w;row[i][2]+=delta[1]*w
 report['changes'].append({'part':a['name'],'row':j,'old_mm':old,'new_mm':row[0],'underside_z_mm':z})
a['revision']='r10';a['acceptance']='pending_interface_review';a['revision_note']='Upper lip inset to the evaluated rider-seat underside; 3mm modeled clearance, hidden fit unverified.'
(V2/'qa/Body_SeatSide_r10_candidate.json').write_text(json.dumps(a,indent=2),encoding='utf8')
a=json.loads((V2/'calibration/r09_tail_frozen/Body_PillionBase.json').read_text())
for j in range(len(a['grid'])-2,len(a['grid'])):
 for i,p in enumerate(a['grid'][j]):
  z=underside(p[0],p[1]);old=list(p)
  if z is not None:p[2]=min(p[2],z-4)
  report['changes'].append({'part':a['name'],'row':j,'column':i,'old_mm':old,'new_mm':p,'underside_z_mm':z})
a['revision']='r10';a['revision_note']='Front ramp lowered beneath evaluated rider cushion where ray hits exist; 4mm modeled clearance, unseen bracket unverified.'
(V2/'qa/Body_PillionBase_r10_candidate.json').write_text(json.dumps(a,indent=2),encoding='utf8');(V2/'qa/seat_join_proposal_r10.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))