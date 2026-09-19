"""Unify overlapping front-cowl construction surfaces into a watertight shell.
The editable quad cages stay as hidden live dependencies. This repairs solid
assembly only; it does not certify photo similarity or real-world wall thickness.
"""
from pathlib import Path
import bpy,sys,json
V=Path(__file__).resolve().parents[1]

def apply(scene):
 names=['Body_NoseCheek','Body_NoseSideReturn','Body_WindscreenSeat']
 # The narrow trial crown is redundant with the windscreen seat and brow;
 # retain it only in historical files, never feed its folding ribbon to output.
 crown=scene.objects.get('Body_NoseCrown')
 if crown:bpy.data.objects.remove(crown,do_unlink=True)
 name='Body_NoseAssembly'
 if scene.objects.get(name):raise ValueError('Assembly exists; edit its source cages instead')
 me=bpy.data.meshes.new(name+'_Host');ob=bpy.data.objects.new(name,me)
 col=next(c for c in scene.collection.children if c.name.startswith('Collection_Body'));col.objects.link(ob)
 me.materials.append(scene.objects[names[0]].data.materials[0])
 tree=bpy.data.node_groups.new('GSX_Live_FrontCowl_Controls','GeometryNodeTree')
 tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
 tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 join=tree.nodes.new('GeometryNodeJoinGeometry');out=tree.nodes.new('NodeGroupOutput');tree.links.new(join.outputs['Geometry'],out.inputs['Geometry'])
 for n in names:
  src=scene.objects[n];node=tree.nodes.new('GeometryNodeObjectInfo');node.transform_space='ORIGINAL';node.inputs['Object'].default_value=src
  tree.links.new(node.outputs['Geometry'],join.inputs['Geometry']);src.hide_render=True;src['construction_control_only']=True;src['export_exclude']=True
 mod=ob.modifiers.new('Live_Editable_Quad_Controls','NODES');mod.node_group=tree
 rm=ob.modifiers.new('Joined_ThinShell_Solid','REMESH');rm.mode='VOXEL';rm.voxel_size=.001;rm.use_smooth_shade=True
 sm=ob.modifiers.new('Submillimetre_Surface_Relax','SMOOTH');sm.factor=.25;sm.iterations=2
 ob['control_dependencies']=json.dumps(names);ob['assembly_method']='Live source surfaces joined and voxel-unioned at 1 mm; not measured wall geometry'
 ob['acceptance']='PHOTO_GEOMETRY_NOT_PASSED';scene['revision']='r19';scene.name='GSX250R_Reconstruction_V2_Gray_r19'
 bpy.context.view_layer.update();return {'live_controls':names,'assembly':ob.name,'voxel_size_mm':1,'visual_acceptance':'NOT_PASSED'}
