"""Secondary reference review: angular mirror casings and missing rear indicators."""
import bpy,math,json
from mathutils import Vector
from rebuild_owner_structure import init,purge,solid_tube
from rebuild_owner_shapes import rounded_path
from rebuild_clutch_r30 import loft
from rebuild_front_r51 import save_control

def apply(s):
 b=init(s);changed=[]
 # Existing insets determine each adjusted mirror's own orientation.
 import numpy as np
 for label,side in [('L',-1),('R',1)]:
  old=s.objects['Mirror_Glass_'+label];mat=old.data.materials[0];shellmat=s.objects['Mirror_'+label].data.materials[0]
  pts=np.array([list(old.matrix_world@v.co*1000) for v in old.data.vertices]);c=Vector(pts.mean(axis=0));val,vec=np.linalg.eigh(np.cov((pts-pts.mean(axis=0)).T))
  normal=Vector(vec[:,0]);normal*=1 if normal.y>0 else -1
  u=Vector(vec[:,2]);u*=1 if u.x*side>0 else -1
  v=normal.cross(u).normalized();v*=1 if v.z>0 else -1
  outline=rounded_path([(-65,0,-22),(-56,0,22),(35,0,36),(68,0,19),(55,0,-24),(-25,0,-34)],r=8)
  def contour(scale,d):return [list(c+u*(p.x*scale)+v*(p.z*scale)+normal*d) for p in outline]
  purge(s,('Mirror_'+label,'Mirror_Glass_'+label))
  o=loft(s,'Mirror_'+label,[contour(1.035,-.8),contour(1.05,3),contour(.97,18),contour(.72,27)],shellmat,1.2);save_control(o)
  for cc in list(o.users_collection):cc.objects.unlink(o)
  b.COL.objects.link(o)
  o=loft(s,'Mirror_Glass_'+label,[contour(.95,-.6),contour(.95,-2)],mat,.4);save_control(o)
  for cc in list(o.users_collection):cc.objects.unlink(o)
  b.COL.objects.link(o)
  # Retain the existing stalk end and bridge only inside the casing.
  stem=s.objects['Mirror_Stem_'+label];ev=stem.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();near=min((ev.matrix_world@p.co*1000 for p in me.vertices),key=lambda p:(p-c).length);ev.to_mesh_clear()
  solid_tube(b,'Mirror_InternalBallSeat_'+label,[near,c+normal*15-u*40-v*9],7,'black',False)
  changed += ['Mirror_'+label,'Mirror_Glass_'+label]
 # Both real photos show rear indicators on short stalks beside the carrier.
 # The old r45 prefix removal deleted these; restore connected assemblies.
 b.COL=b.C['Details'];purge(s,('Indicator_Rear',))
 for side,lab in [(-1,'L'),(1,'R')]:
  b.cube('Indicator_Rear_Bridge_'+lab,(side*65,-943,884),(54,19,18),'black',2)
  b.rod('Indicator_Rear_Stem_'+lab,(side*83,-943,884),(side*125,-943,884),8,'rubber',32)
  c=Vector((side*150,-947,884));outline=rounded_path([(-36,0,-9),(-32,0,12),(-10,0,17),(28,0,12),(37,0,0),(26,0,-13),(-13,0,-16)],r=6)
  def rr(scale,d):return [list(c+Vector((side*p.x*scale,d,p.z*scale))) for p in outline]
  o=loft(s,'Indicator_Rear_Housing_'+lab,[rr(.5,15),rr(.95,9),rr(1,0)],b.M['black'],1);save_control(o)
  for cc in list(o.users_collection):cc.objects.unlink(o)
  b.COL.objects.link(o)
  o=loft(s,'Indicator_Rear_Lens_'+lab,[rr(.95,.6),rr(.93,-6),rr(.80,-10)],b.M['glass'],.6);save_control(o)
  for cc in list(o.users_collection):cc.objects.unlink(o)
  b.COL.objects.link(o)
  b.sphere('Indicator_Rear_Bulb_'+lab,c+Vector((0,-1,0)),(8,5,7),'silver')
  changed += ['Indicator_Rear_Housing_'+lab,'Indicator_Rear_Lens_'+lab]
 # The real front fender has two shallow longitudinal stamped channels.
 # Preserve the outer footprint and fork mounting flanges; change only the crown.
 from rebuild_owner_shapes import get,put
 from rebuild_front_r51 import V
 d=json.loads((V/'data/revisions/r50_front_parent/Fender_Front.json').read_text());grid=[]
 for row in d['grid']:
  w=max(p[0] for p in row);rr=[]
  for u in [0,.20,.38,.48,.56,.64,.72,.78,.89,.96,1]:
   xx=w*u
   for j in range(len(row)-1):
    if row[j][0]-1e-6<=xx<=row[j+1][0]+1e-6:
     q=Vector(row[j]).lerp(Vector(row[j+1]),(xx-row[j][0])/(row[j+1][0]-row[j][0]));break
   q.z-=3.8*math.exp(-((u-.56)/.11)**2)*math.exp(-((q.y-705)/125)**4)
   rr.append(list(q))
  grid.append(rr)
 d.update(grid=grid,crease_columns={'7':.25,'8':.30});o=put(s,d);save_control(o);d['revision']='r51';(V/'data/current_controls/Fender_Front.json').write_text(json.dumps(d,indent=2));changed.append('Fender_Front')
 return changed
