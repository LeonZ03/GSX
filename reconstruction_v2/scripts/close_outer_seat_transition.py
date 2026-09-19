"""Outer lateral bridge from the pillion underside to the tail's outer shoulder."""
from mathutils import Vector
from pathlib import Path
import json
from rebuild_owner_shapes import get,setup_helpers
import build_gray as bg
V=Path(__file__).resolve().parents[1]
def apply(s):
 if s.objects.get('Body_PillionSidePanel'):return
 setup_helpers(s);base=get(s,'Body_PillionBase')['grid'];tail=get(s,'Body_Tail')['grid']
 def at(rows,col,y):
  pts=sorted([Vector(r[col]) for r in rows],key=lambda p:p.y)
  for a,b in zip(pts,pts[1:]):
   if a.y<=y<=b.y:return a.lerp(b,(y-a.y)/(b.y-a.y))
  return min(pts,key=lambda p:abs(p.y-y)).copy()
 grid=[]
 for y in [-750,-735,-690,-630,-570,-530,-510,-507]:
  a=at(base,2,y);b=at(tail,2,y);a.y=b.y=y;a.x+=1;a.z-=1.5;b.x+=.8;b.z+=1
  if b.z>=a.z:a=b+Vector((-4,0,3))
  grid.append([list(a.lerp(b,t)) for t in [0,.03,.2,.5,.8,.97,1]])
 d={'name':'Body_PillionSidePanel','grid':grid,'units':'mm','material':'trim','mirror_x':True,'subdivision':2,'thickness_mm':2,'crease_boundary':.5,'revision':'r42','notes':'Closes the outer lateral opening below the pillion, using existing cushion and tail control boundaries; paint split remains unverified.'}
 o=bg.cage(d);o['control_cage_source']='reconstruction_v2/data/current_controls/Body_PillionSidePanel.json';(V/'data/current_controls/Body_PillionSidePanel.json').write_text(json.dumps(d,indent=2))
