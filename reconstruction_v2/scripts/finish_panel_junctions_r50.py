"""Finish remaining visible body-panel interfaces after r50 front reconstruction."""
import bpy,bmesh,json
from pathlib import Path
from rebuild_shell_r49 import offset_tool
V=Path(__file__).resolve().parents[1]

def finish(o,tool,insert_before=None):
 m=o.modifiers.new('R50_AdjacentPanelFit','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=tool
 if insert_before:
  o.modifiers.move(len(o.modifiers)-1,list(o.modifiers).index(o.modifiers[insert_before]));return
 m=o.modifiers.new('R50_PanelJointVolume','REMESH');m.mode='VOXEL';m.voxel_size=.0008;m.use_smooth_shade=True
 m=o.modifiers.new('R50_PanelJointRelax','SMOOTH');m.factor=.12;m.iterations=2
 m=o.modifiers.new('R50_PanelJointReduction','DECIMATE');m.ratio=.2

def apply(s):
 if s.get('revision')!='r50' or s.get('r50_remaining_panel_joints'):raise RuntimeError('Requires r50 before remaining-panel finish')
 finish(s.objects['Body_SideFairing'],s.objects['Tool_R49TrimJoint'],'R50_JointVolumeFinish')
 tool=offset_tool(s,'Tool_R50FairingJoint',s.objects['Body_SideFairing'],.001)
 finish(s.objects['Body_BellyPan'],tool)
 for n in ['Body_PillionSidePanel','Body_PillionBase']:finish(s.objects[n],s.objects['Tool_R49TailJoint'])
 # The existing closed Seat_Pillion_Pan supplies the rear seat underside.
 # Keep the forward base; discard the obsolete aft strip severed by the tail
 # interface together with microscopic chips, not as floating extra panels.
 print('R50 checking rear pan',flush=True)
 pan=s.objects.get('Seat_Pillion_Pan')
 if pan is None:raise RuntimeError('Missing independent rear-seat pan')
 ev=pan.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);closed=bool(len(bm.verts)) and all(e.is_manifold for e in bm.edges);bm.free();ev.to_mesh_clear()
 if not closed:raise RuntimeError('Rear-seat pan is not closed')
 from rebuild_front_junction_r50 import largest_component
 print('R50 retaining main forward base',flush=True)
 largest_component(s.objects['Body_PillionBase'])
 s['r50_remaining_panel_joints']=True
 report={'revision':'r50','nominal_neighbor_clearance_mm':1.0,'measured':False,'changes':['SideFairing/TankSideTrim','BellyPan/SideFairing','PillionSidePanel/Tail','PillionBase/Tail'],'preserved':'Tank, seats, exterior tail cage, photograph cameras'}
 (V/'data/current_controls/panel_joints_r50.json').write_text(json.dumps(report,indent=2));bpy.context.view_layer.update();return report
