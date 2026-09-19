"""Weld tube elbow volumes and clean the evaluated seat-base interface.
Control curves/quad cages and existing booleans remain editable.
"""
import bpy

def apply(scene):
 from rebuild_owner_shapes import get,put
 o=scene.objects['Fender_Front']
 if not o.get('owner_leading_beak'):
  d=get(scene,'Fender_Front')
  for row,amount in [(d['grid'][-3],3),(d['grid'][-2],12),(d['grid'][-1],18)]:
   for j,p in enumerate(row):
    weight=(1-j/(len(row)-1))**2;p[1]+=amount*weight;p[2]-=amount*weight
  put(scene,d);o['owner_leading_beak']=True
 for name,voxel in [('GuardBar_L',.0015),('GuardBar_R',.0015),('Body_PillionBase',.0015),('Fender_Front',.0007)]:
  o=scene.objects[name]
  if o.modifiers.get('Welded_surface_volume'):
   if name=='Body_PillionBase':o.modifiers['Welded_surface_volume'].voxel_size=voxel
   continue
  m=o.modifiers.new('Welded_surface_volume','REMESH');m.mode='VOXEL';m.voxel_size=voxel;m.use_smooth_shade=True
  m=o.modifiers.new('Submillimetre_surface_relax','SMOOTH');m.factor=.12;m.iterations=2
  o['construction_note']='Live volume union of tube elbow / seat interface; sampling '+str(voxel*1000)+' mm. Not a measured manufacturing tolerance.'
 o=scene.objects['Body_PillionBase']
 if not o.modifiers.get('Final_rider_clearance'):
  m=o.modifiers.new('Final_rider_clearance','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=scene.objects['Tool_RiderTankClearance']
  m=o.modifiers.new('Final_interface_weld','WELD');m.merge_threshold=.000002
 if not o.modifiers.get('Final_seat_base_surface'):
  m=o.modifiers.new('Final_seat_base_surface','REMESH');m.mode='VOXEL';m.voxel_size=.0012;m.use_smooth_shade=True
 return {'welded':['GuardBar_L','GuardBar_R','Body_PillionBase']}
