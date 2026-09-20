"""Clean finite-wall interfaces after r51 shape replacement, keep editable parents."""
import bpy
from rebuild_front_junction_r50 import largest_component

def remove_small(o,threshold=200):
 ng=bpy.data.node_groups.new(o.name+'_R51RemoveChips','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 inp=ng.nodes.new('NodeGroupInput');out=ng.nodes.new('NodeGroupOutput');island=ng.nodes.new('GeometryNodeInputMeshIsland');acc=ng.nodes.new('GeometryNodeAccumulateField');acc.data_type='INT';acc.domain='POINT';acc.inputs['Value'].default_value=1
 less=ng.nodes.new('FunctionNodeCompare');less.data_type='INT';less.operation='LESS_THAN';less.inputs['B'].default_value=threshold;delete=ng.nodes.new('GeometryNodeDeleteGeometry');delete.domain='POINT';delete.mode='ALL'
 ng.links.new(island.outputs['Island Index'],acc.inputs['Group ID']);ng.links.new(acc.outputs['Total'],less.inputs['A']);ng.links.new(less.outputs['Result'],delete.inputs['Selection']);ng.links.new(inp.outputs['Geometry'],delete.inputs['Geometry']);ng.links.new(delete.outputs['Geometry'],out.inputs['Geometry']);m=o.modifiers.new('R51_RemoveSeamChips','NODES');m.node_group=ng

def apply(s):
 o=s.objects['Body_NoseAssembly'];m=o.modifiers.new('R51_ApertureVolumeFinish','REMESH');m.mode='VOXEL';m.voxel_size=.0007;m.use_smooth_shade=True;largest_component(o)
 o=s.objects['Headlight_InnerMask'];m=o.modifiers.new('R51_FitAgainstPaint','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=s.objects['Tool_R49NoseJoint']
 m=o.modifiers.new('R51_RecessWallFinish','REMESH');m.mode='VOXEL';m.voxel_size=.00065;m.use_smooth_shade=True;largest_component(o)
 remove_small(s.objects['Body_SideFairing'])
