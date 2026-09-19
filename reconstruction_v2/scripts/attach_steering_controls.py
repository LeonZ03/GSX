"""Keep clip-ons, caps and mounted controls attached during photo-pose steering."""
def apply(scene):
 prefixes=('Handlebar','Grip_','Lever_','SwitchHousing','BrakeReservoir','ClutchPerch','PhoneMount','ForkCap','Ignition_','TripleClamp_','Tool_TripleClampFork','SteeringDamper')
 names=[]
 for o in scene.objects:
  if o.name.startswith(prefixes):o['steer_with_front']=True;names.append(o.name)
 return names
