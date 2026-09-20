"""Photo-led saddle with a continuous downturned upholstery skirt.
Run once on the checkpointed r47 source, after the r48 assembly migration.
No source save. The cross section is estimated, not a measured foam thickness.
"""
import bpy,json
from pathlib import Path
V=Path(__file__).resolve().parents[1]

def apply(scene=None):
 s=scene or bpy.context.scene;o=s.objects['Seat_Rider'];tool=s.objects['Tool_SeatClearance']
 if s.get('revision') not in ('r47','r48') or o.get('saddle_r48_applied'):raise RuntimeError('Requires unapplied r47 saddle')
 if len(o.data.vertices)!=48:raise RuntimeError('Expected eight by six source cage')
 old=[[list(v.co*1000) for v in o.data.vertices[i:i+6]] for i in range(0,48,6)]
 g=[]
 for row_index,row in enumerate(old):
  y=row[0][1];w=row[3][0];top=row[0][2]+8;bottom=row[4][2]-[3,3,14,24,24,24,20,20][row_index];under=row[5][2]
  h=top-bottom
  # Top rolls over both shoulders, continues down a vertical outer wall,
  # then turns inward under the cushion. Ten points per half section.
  profile=[(0,top),(.45*w,top-1),(.8*w,top-5),(.96*w,top-.28*h),(w,top-.53*h),(w,bottom+.14*h),(.95*w,bottom),(.85*w,bottom-1),(.45*w,under),(0,under)]
  g.append([[x,y,z] for x,z in profile])
 d=json.loads((V/'data/current_controls/Seat_Rider.json').read_text())
 d.update(grid=g,cap_ends=True,crease_columns={},crease_boundary=.35,revision='r48',current_snapshot='r48',source_revision_file='r47 checkpoint Seat_Rider',units='mm')
 d.pop('faces',None)
 from rebuild_owner_shapes import put
 put(s,d)
 s.objects['Tool_RiderTankClearance'].data=o.data
 d['revision']='r48';d['faces']=[list(p.vertices) for p in o.data.polygons]
 d['evidence']='Owner 62/69/70: rolled shoulder and downturned upholstery side, section depths unmeasured'
 (V/'data/current_controls/Seat_Rider.json').write_text(json.dumps(d,indent=2))
 for obj in (o,tool):
  obj['saddle_r48_applied']=True;obj['control_cage_source']='reconstruction_v2/data/current_controls/Seat_Rider.json'
 report={'revision':'r48','units':'mm','profile':'ten-point half section with downturned side and underside return','control_drop_top_to_outer_bottom_mm':[round(r[0][2]-r[6][2],3) for r in g],'thickness_measured':False,'source':'reconstruction_v2/data/current_controls/Seat_Rider.json'}
 (V/'data/current_controls/saddle_r48_control.json').write_text(json.dumps(report,indent=2))
 return report
