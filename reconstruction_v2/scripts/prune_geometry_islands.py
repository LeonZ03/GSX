"""Discard disconnected Boolean/remesh fragments, retaining a majority shell."""
import bpy

def apply(obj,name):
    ng=bpy.data.node_groups.new(name,'GeometryNodeTree')
    ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    inp=ng.nodes.new('NodeGroupInput');outp=ng.nodes.new('NodeGroupOutput')
    islands=ng.nodes.new('GeometryNodeInputMeshIsland')
    acc=ng.nodes.new('GeometryNodeAccumulateField');acc.data_type='INT';acc.domain='POINT';acc.inputs['Value'].default_value=1
    size=ng.nodes.new('GeometryNodeAttributeDomainSize');size.component='MESH'
    half=ng.nodes.new('ShaderNodeMath');half.operation='MULTIPLY';half.inputs[1].default_value=.5
    less=ng.nodes.new('FunctionNodeCompare');less.data_type='INT';less.operation='LESS_THAN'
    delete=ng.nodes.new('GeometryNodeDeleteGeometry');delete.domain='POINT';delete.mode='ALL'
    ng.links.new(inp.outputs['Geometry'],size.inputs['Geometry']);ng.links.new(size.outputs['Point Count'],half.inputs[0])
    ng.links.new(islands.outputs['Island Index'],acc.inputs['Group ID'])
    ng.links.new(acc.outputs['Total'],less.inputs['A']);ng.links.new(half.outputs[0],less.inputs['B'])
    ng.links.new(inp.outputs['Geometry'],delete.inputs['Geometry']);ng.links.new(less.outputs['Result'],delete.inputs['Selection'])
    ng.links.new(delete.outputs['Geometry'],outp.inputs['Geometry'])
    mod=obj.modifiers.new('Dominant_connected_shell','NODES');mod.node_group=ng
