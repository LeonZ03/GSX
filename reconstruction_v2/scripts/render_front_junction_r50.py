"""Freeze expensive evaluated shells only in a disposable inspection process."""
import bpy,json
from pathlib import Path
V=Path(__file__).resolve().parents[1]

def run(tag='r50',keys=('Nose','FrontSymmetry','NoseSide')):
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();frozen={}
 for name in ['Body_NoseAssembly','Body_SideFairing','Body_SeatSide','Cockpit_InnerPanel','Headlight_InnerMask','Body_BellyPan','Body_PillionSidePanel','Body_PillionBase']:
  o=s.objects[name];e=o.evaluated_get(dg);frozen[name]=bpy.data.meshes.new_from_object(e,preserve_all_data_layers=True,depsgraph=dg)
 # Snapshot all dependent outputs BEFORE replacing any live input.
 for name,data in frozen.items():s.objects[name].modifiers.clear();s.objects[name].data=data
 bpy.context.view_layer.update()
 from render_owner_assembly import render
 return render(keys,tag)
