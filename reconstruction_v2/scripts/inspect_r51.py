import bpy,json
from pathlib import Path
s=bpy.context.scene
r={}
for o in s.objects:
 if o.name.startswith(('Body_Nose','Headlight','Windscreen','Mirror','TurnSignal','Indicator','Body_UpperSideCowl')):
  r[o.name]={'type':o.type,'location':list(o.location),'matrix':[list(r) for r in o.matrix_world],'bbox':[list(o.matrix_world@__import__('mathutils').Vector(p)) for p in o.bound_box],'hide_render':o.hide_render,'modifiers':[(m.name,m.type) for m in o.modifiers],'materials':[m.name if m else None for m in getattr(o.data,'materials',[])]}
Path('D:/Work/gadgets/GSX/reconstruction_v2/qa/inspect_r51.json').write_text(json.dumps(r,indent=2))
