"""Reproducible neutral assembly views; renders without saving source edits."""
from pathlib import Path
import bpy,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from cache_review_geometry import cache_review_assembly
from render_stage_bc import cameras

def render(keys=('CockpitTop','FrontSymmetry','SeatProfile','Underside'),tag='r45'):
 s=bpy.context.scene;cache_review_assembly(s);cams=cameras(s);col=next(c for c in s.collection.children if c.name.startswith('Collection_Cameras'))
 for n,eye,tar,scale in [('Underside',(1,-1,-2.4),(0,0,.37),2.1),('RightSide',(3,-.1,1),(0,-.1,.58),2.5),('PhoneMount',(-.55,-.4,1.4),(-.185,.408,1),.27)]:
  d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);col.objects.link(o);o.location=eye;o.rotation_euler=(Vector(tar)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;cams[n]=o
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.23,.23,.23)
 s.view_settings.view_transform='Standard';s.view_settings.exposure=0
 s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=80;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.render.use_border=False
 out=V/'renders/assembly_review';out.mkdir(exist_ok=True)
 for key in keys:
  s.camera=cams[key];s.render.filepath=str(out/(tag+'_'+key+'.png'));bpy.ops.render.render(write_still=True)
 return {'views':[str(out/(tag+'_'+key+'.png')) for key in keys]}
