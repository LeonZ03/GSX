"""Close the observed missing lateral transition below the pillion cushion."""
from mathutils import Vector
from rebuild_owner_shapes import get,put

def apply(scene):
 o=scene.objects['Body_PillionBase']
 if o.get('owner_side_transition_closed'):return
 d=get(scene,'Body_PillionBase');tail=get(scene,'Body_Tail');rail=[Vector(r[1]) for r in tail['grid']]
 def edge(y):
  for a,b in zip(rail,rail[1:]):
   if a.y<=y<=b.y:return a.lerp(b,(y-a.y)/(b.y-a.y))
  return min(rail,key=lambda p:abs(p.y-y)).copy()
 rows=[]
 for i,row in enumerate(d['grid']):
  p=Vector(row[-1]);q=edge(p.y)
  if i>=len(d['grid'])-2:q=p+Vector((1.5,0,-3))
  elif q.z>=p.z:q=p+Vector((2.5,0,-3))
  else:q+=Vector((1.5,0,-1.0));q.y=p.y
  rows.append(row+[list(p.lerp(q,t)) for t in [.15,.85,1]])
 d['grid']=rows;d['crease_columns']={'2':.2};d['crease_boundary']=.35;d['notes']='Lateral transition extended from cushion underside to tail shoulder; preserves front rider ramp. Hidden attachment not measured.';put(scene,d);o['owner_side_transition_closed']=True
