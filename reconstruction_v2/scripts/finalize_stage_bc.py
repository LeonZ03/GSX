"""Remove isolated output points without baking away editable front controls."""
from pathlib import Path
import bpy
V=Path(__file__).resolve().parents[1]

def apply(scene):
 o=scene.objects['Body_NoseAssembly'];tree=bpy.data.node_groups.new('GSX_Remove_Isolated_Output_Points','GeometryNodeTree')
 tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 inp=tree.nodes.new('NodeGroupInput');out=tree.nodes.new('NodeGroupOutput');nb=tree.nodes.new('GeometryNodeInputMeshVertexNeighbors')
 compare=tree.nodes.new('ShaderNodeMath');compare.operation='LESS_THAN';compare.inputs[1].default_value=.5
 delete=tree.nodes.new('GeometryNodeDeleteGeometry');delete.domain='POINT'
 tree.links.new(inp.outputs['Geometry'],delete.inputs['Geometry']);tree.links.new(nb.outputs['Face Count'],compare.inputs[0]);tree.links.new(compare.outputs[0],delete.inputs['Selection']);tree.links.new(delete.outputs['Geometry'],out.inputs['Geometry'])
 mod=o.modifiers.new('Remove_Isolated_Output_Points','NODES');mod.node_group=tree
 path=V/'blends/19_gray_review.blend'
 if path.exists():raise FileExistsError(path)
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(path))
 return {'source':str(path),'geometry_status':'CANDIDATE','stage_B':'NOT_PASSED','stage_C':'NOT_PASSED'}
if __name__=='__main__':result=apply(bpy.context.scene)
