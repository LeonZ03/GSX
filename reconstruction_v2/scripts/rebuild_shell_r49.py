"""Continuous folded seat-side shell and coherent front side-cowl boundaries.
Requires checkpointed r48. All dimensions are photo-led estimates in mm.
"""
import bpy,json,copy,math
from pathlib import Path
from mathutils import Vector
from rebuild_owner_shapes import put
V=Path(__file__).resolve().parents[1]
BASE=json.loads((V/'data/revisions/r48_shell_baseline/controls.json').read_text())

def control(s,n,g,**kw):
 d=copy.deepcopy(BASE[n]);d.update(grid=g,**kw);d.pop('faces',None);o=put(s,d)
 d.update(revision='r49',current_snapshot='r49');d['faces']=[list(p.vertices) for p in o.data.polygons]
 (V/'data/current_controls'/(n+'.json')).write_text(json.dumps(d,indent=2));return o

def section_lines(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();vs=[e.matrix_world@v.co*1000 for v in me.vertices];lines=[(vs[q.vertices[0]],vs[q.vertices[1]]) for q in me.edges];e.to_mesh_clear();return lines

def outer_low(lines,y):
 pts=[a.lerp(b,(y-a.y)/(b.y-a.y)) for a,b in lines if (a.y-y)*(b.y-y)<=0 and abs(b.y-a.y)>1e-7]
 pts=[p for p in pts if p.x>0]
 if not pts:raise ValueError('No section at '+str(y))
 mx=max(p.x for p in pts);return min((p for p in pts if p.x>mx*.94),key=lambda p:p.z)

def side_shell(s):
 old=BASE['Body_SeatSide']['grid'];ys=[r[0][1] for r in old]
 def interp(y):
  for i in range(len(ys)-1):
   if ys[i]<=y<=ys[i+1]:
    t=(y-ys[i])/(ys[i+1]-ys[i]);return [list(Vector(a).lerp(Vector(b),t)) for a,b in zip(old[i],old[i+1])]
  return copy.deepcopy(old[0] if y<ys[0] else old[-1])
 seat=section_lines(s.objects['Seat_Rider']);tank=section_lines(s.objects['Body_Tank']);trim=section_lines(s.objects['Body_TankSideTrim'])
 rows=[];targets=[]
 for y in [-489.7,-486,-465,-393,-267,-200,-160,-145,-133,-120,-105,-90,-76,-70,-68,-60,-38,30,68,115,121]:
  row=interp(y)
  if y<=-145:p=outer_low(seat,y)
  elif y<-120:
   a=outer_low(seat,y);b=outer_low(tank,y);p=a.lerp(b,(y+145)/25)
  elif y<-70:p=outer_low(tank,y)
  elif y<-60:
   a=outer_low(tank,y);b=outer_low(trim,max(-69,y));p=a.lerp(b,(y+70)/10)
  else:p=outer_low(trim,y)
  p+=Vector((-1.8,0,-.8));a=Vector(row[0]);a.x=max(a.x,p.x+6);a.z=min(a.z,p.z-1.5)
  delta=a-Vector(row[0])
  for j,q in enumerate(row):row[j]=list(Vector(q)+delta*(1-j/(len(row)-1))**1.5)
  # Folded upper return and descending visible face are one quad surface.
  upper=[list(p.lerp(a,t)) for t in [0,.07,.32,.72,1]]
  rows.append(upper+row[1:]);targets.append(list(p))
 o=control(s,'Body_SeatSide',rows,crease_columns={'4':.25},crease_boundary=.85,solidify_mode='NON_MANIFOLD',use_even_offset=True,thickness_clamp=.5,use_thickness_angle_clamp=True)
 for m in o.modifiers:
  if m.type=='SOLIDIFY':m.solidify_mode='NON_MANIFOLD';m.use_even_offset=True;m.thickness_clamp=.5;m.use_thickness_angle_clamp=True
 m=o.modifiers.new('R49_TankInterface','BOOLEAN');m.operation='DIFFERENCE';m.solver='MANIFOLD';m.object=s.objects['Tool_R47TankTrimClearance']
 for m in o.modifiers:
  if m.type=='BOOLEAN':m.solver='MANIFOLD'
 return {'upper_lip_targets_mm':targets,'section_sources':'evaluated rider-seat / tank / trim; outer fold remains editable','nominal_inset_mm':1.8}

def front_shell(s):
 cg=copy.deepcopy(BASE['Body_NoseCheek']['grid'])
 for i,a,c in [(6,(141,844,788),(169,822,795)),(7,(137,856,744),(151,844,746)),(8,(143,869,712),(147,861,709))]:
  cg[i]=[list(Vector(a).lerp(Vector(c),t)) for t in [0,.06,.25,.5,.75,.94,1]]
 control(s,'Body_NoseCheek',cg,crease_columns={},crease_boundary=.65)
 outer=[r[-1] for r in cg]
 back=[(0,694,919),(130,610,930),(162,557,916),(187,575,878),(203,611,829),(212,637,782),(213,642,749),(193,683,721),(166,727,705)]
 rg=[]
 for a,c in zip(outer,back):
  a=Vector(a);c=Vector(c);rg.append([list(a.lerp(c,t)+Vector((3*math.sin(math.pi*t),0,0))) for t in [0,.06,.25,.5,.75,.94,1]])
 control(s,'Body_NoseSideReturn',rg,crease_columns={},crease_boundary=.65)
 # Both surfaces now share a single front cross-section. The old r35 cowl
 # continued underneath the r47 face, causing a buckled double surface.
 tops=[(133,279.8,821.7),(166,337.1,807.1),(190,408.9,801),(199,481.6,799.9),(196,552.6,827),back[3]]
 bottoms=[(208,259.8,754.3),(219,348.8,722.3),(228,455.3,723.6),(210.2,576.4,726.4),(199.5,633.7,714.9),back[-1]]
 front=[Vector(q) for q in back[3:]];ts=[0,.035,.10,.2,.3,.4,.5,.6,.7,.8,.9,.965,1]
 last=[]
 for t in ts:
  f=t*(len(front)-1);i=min(int(f),len(front)-2);last.append(front[i].lerp(front[i+1],f-i))
 g=[]
 for i,(a,c) in enumerate(zip(tops,bottoms)):
  if i==len(tops)-1:g.append([list(p) for p in last]);continue
  a=Vector(a);c=Vector(c);g.append([list(a.lerp(c,t)+Vector((8*math.sin(math.pi*t),0,0))) for t in ts])
 control(s,'Body_UpperSideCowl',g,crease_columns={'5':.12},crease_boundary=.65)
 black=copy.deepcopy(BASE['Cockpit_InnerPanel']['grid'])
 for i,row in enumerate(black):
  target=Vector(tops[i])+Vector((0,-1.5,0));delta=target-Vector(row[-1])
  for j,q in enumerate(row):row[j]=list(Vector(q)+delta*j/(len(row)-1))
 black[-1]=[list(Vector(back[2]).lerp(Vector(back[3]),t)+Vector((0,-1.5,0))) for t in [0,.04,.2,.5,.8,.96,1]]
 control(s,'Cockpit_InnerPanel',black,crease_columns={},crease_boundary=.75)
 return {'shared_front_section_mm':back[3:],'cowling_top_mm':tops,'side_return_back_mm':back,'unverified':'photo-led shape and hidden dimensions; not metrology'}

def offset_tool(s,name,source,offset):
 if name in s.objects:bpy.data.objects.remove(s.objects[name],do_unlink=True)
 me=bpy.data.meshes.new(name);o=bpy.data.objects.new(name,me);source.users_collection[0].objects.link(o)
 ng=bpy.data.node_groups.new(name+'_LiveSurface','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 inf=ng.nodes.new('GeometryNodeObjectInfo');inf.inputs['Object'].default_value=source;inf.transform_space='ORIGINAL'
 normal=ng.nodes.new('GeometryNodeInputNormal');scale=ng.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=offset
 move=ng.nodes.new('GeometryNodeSetPosition');out=ng.nodes.new('NodeGroupOutput')
 ng.links.new(inf.outputs['Geometry'],move.inputs['Geometry']);ng.links.new(normal.outputs['Normal'],scale.inputs[0]);ng.links.new(scale.outputs['Vector'],move.inputs['Offset']);ng.links.new(move.outputs['Geometry'],out.inputs['Geometry'])
 m=o.modifiers.new('Live_neighbor_offset','NODES');m.node_group=ng;o.hide_render=True;o.hide_set(True);o['export_exclude']=True;return o

def finish_interfaces(s):
 nose=s.objects['Body_NoseAssembly'];m=nose.modifiers.new('R49_SurfaceRelax','SMOOTH');m.factor=.45;m.iterations=8
 nt=offset_tool(s,'Tool_R49NoseJoint',nose,.001)
 tt=offset_tool(s,'Tool_R49TrimJoint',s.objects['Body_TankSideTrim'],.001)
 tail=offset_tool(s,'Tool_R49TailJoint',s.objects['Body_Tail'],.001)
 for n,tool in [('Body_SeatSide',tt),('Body_SeatSide',tail),('Cockpit_InnerPanel',nt),('Body_SideFairing',nt)]:
  m=s.objects[n].modifiers.new('R49_PanelSeam','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT' if n=='Body_SideFairing' else 'MANIFOLD';m.object=tool
 m=s.objects['Body_SideFairing'].modifiers.new('R49_SeamMicroWeld','WELD');m.merge_threshold=.000001


def seam_finish(s):
 for n in ['Body_SeatSide','Cockpit_InnerPanel']:
  o=s.objects[n];m=o.modifiers.new('R49_ClosedSeamVolume','REMESH');m.mode='VOXEL';m.voxel_size=.00085;m.use_smooth_shade=True
  m=o.modifiers.new('R49_SeamRelax','SMOOTH');m.factor=.1;m.iterations=2
  ng=bpy.data.node_groups.new(n+'_RejectDetachedCutChips','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
  inp=ng.nodes.new('NodeGroupInput');out=ng.nodes.new('NodeGroupOutput');island=ng.nodes.new('GeometryNodeInputMeshIsland');acc=ng.nodes.new('GeometryNodeAccumulateField');acc.data_type='INT';acc.domain='POINT';acc.inputs['Value'].default_value=1
  less=ng.nodes.new('FunctionNodeCompare');less.data_type='INT';less.operation='LESS_THAN';less.inputs['B'].default_value=200;delete=ng.nodes.new('GeometryNodeDeleteGeometry');delete.domain='POINT';delete.mode='ALL'
  ng.links.new(island.outputs['Island Index'],acc.inputs['Group ID']);ng.links.new(acc.outputs['Total'],less.inputs['A']);ng.links.new(less.outputs['Result'],delete.inputs['Selection']);ng.links.new(inp.outputs['Geometry'],delete.inputs['Geometry']);ng.links.new(delete.outputs['Geometry'],out.inputs['Geometry'])
  m=o.modifiers.new('R49_RejectDetachedCutChips','NODES');m.node_group=ng


def apply(s):
 if s.get('revision')!='r48':raise RuntimeError('Requires checkpointed r48')
 report={'side_shell':side_shell(s),'front_shell':front_shell(s)}
 finish_interfaces(s);seam_finish(s)
 s['revision']='r49';s.name='GSX250R_Reconstruction_V2_Gray_r49';bpy.context.view_layer.update()
 (V/'data/current_controls/shell_r49_layout.json').write_text(json.dumps(report,indent=2));return report
