"""Clean revised seat interfaces and seat new position lamps on actual front shell."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector,Matrix
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_shapes import get,put,setup_helpers

def clearance(s,source,name,targets,gap):
 seat=s.objects[source];helper=seat.copy();helper.data=seat.data;helper.name=name
 next(c for c in s.collection.children if c.name.startswith('Collection_Blockout')).objects.link(helper)
 for k in list(helper.keys()):del helper[k]
 helper.hide_render=True;helper.hide_set(True);helper['export_exclude']=True;helper['construction_role']=source+'_clearance';helper['clearance_mm']=gap
 con=helper.constraints.new('COPY_TRANSFORMS');con.target=seat
 m=helper.modifiers.new('Construction_clearance','DISPLACE');m.direction='NORMAL';m.strength=gap*.001;m.mid_level=0
 for n in targets:
  o=s.objects[n];m=o.modifiers.new('Editable_'+source+'_Clearance','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=helper
  m=o.modifiers.new('Interface_numerical_weld','WELD');m.merge_threshold=.000002

def run():
 s=bpy.context.scene
 if s.get('revision')!='r40':raise ValueError('Requires r40 candidate')
 b=setup_helpers(s)
 for key,n in {'black':'Body_TankSideTrim','rubber':'Seat_Rider'}.items():b.M[key]=s.objects[n].data.materials[0]
 # More pronounced upholstered crown on the pillion, without moving its base.
 d=get(s,'Seat_Pillion')
 for i,row in enumerate(d['grid']):
  w=[0,2,7,10,12,7,1][i]
  for j,f in enumerate([1,.8,.15,0,0,0]):row[j][2]+=w*f
 put(s,d)
 clearance(s,'Seat_Rider','Tool_RiderTankClearance',['Body_Tank'],1.5)
 clearance(s,'Seat_Pillion','Tool_PillionClearance',['Body_Tail'],1.5)
 # A thin seam follows the evaluated upholstered face, not a floating curve.
 bpy.context.view_layer.update();o=s.objects['Seat_Pillion'];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[]
 for x in [-99,-85,-65,-40,-15,0,15,40,65,85,99]:
  ok,p,n,idx=ev.ray_cast(Vector((x*.001,-.559,2)),Vector((0,0,-1)))
  if ok:pts.append((p+n*.0007)*1000)
 b.COL=b.C['Body'];seam=b.tube('Seat_Pillion_FrontSeam',pts,.65,'black',False,True);seam.data.use_fill_caps=True
 # Match depth to the evaluated cowling; the previous broad lens crossed it.
 ev=s.objects['Body_NoseAssembly'].evaluated_get(bpy.context.evaluated_depsgraph_get())
 for name,offset in [('Headlight_PositionLens',4.0),('Headlight_PositionSurround',2.2)]:
  d=get(s,name)
  for row in d['grid']:
   for p in row:
    hit,co,n,idx=ev.ray_cast(Vector((p[0]*.001,2,p[2]*.001)),Vector((0,-1,0)))
    if hit:p[1]=co.y*1000+offset
  d['thickness_mm']=.8;d['crease_boundary']=.35;put(s,d)
  for m in s.objects[name].modifiers:
   if m.type=='SOLIDIFY':m.thickness=.0008;m.use_even_offset=True;m.thickness_clamp=.5
 # Close open ends of new visible tubular parts; retain live curves.
 for o in s.objects:
  if o.type=='CURVE' and o.name.startswith(('Guard','SideStand')):
   o.data.use_fill_caps=True
   m=o.modifiers.new('Tube_cap_weld','WELD');m.merge_threshold=.000001
 # Phone mount's larger back plate and jaws are visible in cockpit photo65.
 origin=Vector((-.188,.399,.997));u=Vector((1,0,0));v=Vector((0,.2955,.9553)).normalized();n=u.cross(v)
 B=Matrix((u,v,n)).transposed();T=Matrix.Translation(origin)@(B@Matrix.Diagonal(Vector((1.17,1.28,1)))@B.transposed()).to_4x4()@Matrix.Translation(-origin)
 for o in s.objects:
  if o.name=='PhoneMount' or o.name.startswith(('PhoneMount_Jaw','PhoneMount_Contact')):o.matrix_world=T@o.matrix_world
 s['revision']='r41';s.name='GSX250R_Reconstruction_V2_Gray_r41';s['visual_acceptance']='NOT_PASSED';bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'revision':'r41','changes':['pillion crown and seam','rider/tank and pillion/tail 1.5mm modeled clearances','position lamp depth and shell thickness','closed guard/stand tubes','cockpit phone holder envelope'],'dimensions_measured':False}
