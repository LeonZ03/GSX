"""Local inspection views only; never save this disposable render scene."""
import bpy
from mathutils import Vector
from pathlib import Path
V=Path(__file__).resolve().parents[1]
def run():
 from render_owner_assembly import render
 report=render(('RightSide','FrontSymmetry','CockpitTop','SeatProfile'),'r48')
 s=bpy.context.scene
 for o in s.objects:
  if o.type not in ('CAMERA','LIGHT'):o.hide_render=o.name!='Seat_Rider'
 d=bpy.data.cameras.new('Review_Saddle');cam=bpy.data.objects.new('Review_Saddle',d);s.collection.objects.link(cam);d.type='ORTHO';d.ortho_scale=.54;s.camera=cam
 s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100
 for tag,eye in [('Oblique',(1,.6,1.07)),('Underside',(1,.4,.61))]:
  cam.location=eye;cam.rotation_euler=(Vector((0,-.30,.80))-cam.location).to_track_quat('-Z','Y').to_euler()
  path=V/'renders/assembly_review'/('r48_Saddle'+tag+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);report['views'].append(str(path))
 return report
