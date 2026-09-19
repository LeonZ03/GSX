"""Photo/catalogue-led rear chain case and pillion brackets, r35 -> r36.
Hidden depths and folded-peg pose remain review candidates, not measured data.
"""
from pathlib import Path
import bpy,bmesh,math,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_clutch_r30 import loft,mesh,cylinder

def hide(o):
 o.hide_render=True;o.hide_set(True);o.display_type='WIRE';o['export_exclude']=True;return o

def boolean(o,tool,operation='DIFFERENCE'):
 m=o.modifiers.new('Editable_'+tool.name,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=hide(tool)

def bevel(o,w=1):
 m=o.modifiers.new('Cast_edge_radius','BEVEL');m.width=w*.001;m.segments=3

def hull(points):
 pts=sorted(set(points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 halves=[]
 for pp in [pts,list(reversed(pts))]:
  hh=[]
  for p in pp:
   while len(hh)>=2 and cross(hh[-2],hh[-1],p)<=0:hh.pop()
   hh.append(p)
  halves.append(hh[:-1])
 return halves[0]+halves[1]

def tube(scene,name,points,radius,mat):
 d=bpy.data.curves.new(name+'_Curve','CURVE');d.dimensions='3D';d.bevel_depth=radius*.001;d.bevel_resolution=3;d.use_fill_caps=True;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,q in zip(sp.points,points):p.co=tuple(x*.001 for x in q)+(1,)
 o=bpy.data.objects.new(name,d);next(c for c in scene.collection.children if c.name.startswith('Collection_Details')).objects.link(o);d.materials.append(mat);m=o.modifiers.new('Cap_Seam_Weld','WELD');m.merge_threshold=.000001;return o

def peg(scene,name,a,b,mat):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=Vector((0,1,0)) if abs(axis.x)>.9 else Vector((1,0,0));v=axis.cross(u).normalized();profile=[(-8,-5),(-5,-8),(5,-8),(8,-5),(8,5),(5,8),(-5,8),(-8,5)]
 o=loft(scene,name,[[list(c+u*x+v*y) for x,y in profile] for c in [a,b]],mat,.8)
 for j in range(1,9):
  c=a.lerp(b,j/10);ends=[c+u*(-8)+v*8,c+u*8+v*8];tube(scene,name+f'_Grip_{j}',ends,1.3,mat)
 return o

def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('revision')!='r35':raise ValueError('Requires r35')
 d=json.loads((V/'data/revisions/r36_rear_hardware/control.json').read_text());gun=scene.objects['Engine_ClutchCover'].data.materials[0];plastic=scene.objects['ChainGuard'].data.materials[0];silver=scene.objects['Footpeg_L'].data.materials[0];steel=scene.objects['BrakeDisc_Front'].data.materials[0]
 for n in ['ChainGuard','PassengerPeg_L','PassengerPeg_R','PassengerPegHanger_L','PassengerPegHanger_R']:bpy.data.objects.remove(scene.objects[n],do_unlink=True)
 outline=d['chain_case_outline'];case=loft(scene,'ChainGuard',[[[p[0]+dx,p[1],p[2]] for p in outline] for dx in [-2,2]],plastic)
 for i,slot in enumerate(d['chain_case_slots']):boolean(case,loft(scene,f'Tool_ChainVent_{i}',[[[x,p[1],p[2]] for p in slot] for x in [-170,-80]],plastic))
 roof=loft(scene,'Tool_ChainGuardRoof',[[[x,p[1],p[2]+z] for x,z in [(-118.8,-1),(-75.5,-1),(-75.5,2),(-118.8,2)]] for p in outline[:6]],plastic);boolean(case,roof,'UNION')
 # OEM FIG541A chain case includes a forward wheel-hugging arch.
 rows=[]
 for i in range(25):
  t=math.radians(22+61*i/24);row=[]
  for j in range(13):
   x=-95+190*j/12;r=343-20*(x/95)**2;row.append([x,-715+r*math.cos(t),313.9+r*math.sin(t)])
  rows.append(row)
 verts=sum(rows,[]);faces=[(i*13+j,i*13+j+1,(i+1)*13+j+1,(i+1)*13+j) for i in range(24) for j in range(12)]
 hug=mesh(scene,'Tool_ChainGuardHugger',verts,[tuple(reversed(f)) for f in faces],plastic);m=hug.modifiers.new('Moulded_shell','SOLIDIFY');m.thickness=.0025;m.offset=-1;boolean(case,hug,'UNION');case['evidence']='Owner69 outline and vents, Suzuki FIG541A 63110-20K00';case['unverified']='Hugger transverse crown, hidden arc and mounting thickness'
 points={k:Vector(p) for k,p in d['hanger_points'].items()}
 for side,lab in [(-1,'L'),(1,'R')]:
  source=points if side<0 else {k:Vector(p) for k,p in d['hanger_points_R'].items()}
  A,B,C,E=[source[n].copy() for n in ['hanger_mount_front','hanger_mount_rear','hanger_pivot','folded_peg_tip']]
  for p in [A,B,C,E]:p.x=side*abs(p.x)
  normal=(B-A).cross(C-A)
  def x_at(y,z):return A.x-(normal.y*(y-A.y)+normal.z*(z-A.z))/normal.x
  poly=hull([(p.y+10*math.cos(j*math.tau/12),p.z+10*math.sin(j*math.tau/12)) for p in [A,B,C] for j in range(12)])
  o=loft(scene,'PassengerPegHanger_'+lab,[[[x_at(y,z)+dx,y,z] for y,z in poly] for dx in [-4,4]],gun)
  bevel(o,1)
  center=(A+B+C)/3;inner=[center+(p-center)*.53 for p in [A,B,C]];tool=loft(scene,'Tool_PillionWindow_'+lab,[[[x,p.y,p.z] for p in inner] for x in [-300,300]],gun);boolean(o,tool)
  for j,p in enumerate([A,B]):
   tool=cylinder(scene,f'Tool_PillionBoltHole_{lab}_{j}',p,4.3,50,gun,32);boolean(o,tool)
   cylinder(scene,f'PassengerPegMountBolt_{lab}_{j}',[p.x+side*6,p.y,p.z],6.5,4,steel,6)
   # Welded mounting tab meets the existing subframe instead of floating.
   frame=scene.objects['Frame_Subframe_'+lab];ev=frame.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();target=min((ev.matrix_world@v.co*1000 for v in me.vertices),key=lambda v:(v-p).length);ev.to_mesh_clear()
   vv=Vector((0,target.y-p.y,target.z-p.z));perp=Vector((0,-vv.z,vv.y)).normalized()*9
   pp=[p+perp,p-perp,target-perp,target+perp];tab=loft(scene,f'PassengerPegFrameTab_{lab}_{j}',[[[q.x+dx,q.y,q.z] for q in pp] for dx in [-6,6]],gun,1);tab['unverified']='Welded tab footprint inferred between observed bolts and current frame; hidden extent provisional.'
  peg(scene,'PassengerPeg_'+lab,C,E,silver);tube(scene,'PassengerPegPivot_'+lab,[C+Vector((0,-12,0)),C+Vector((0,12,0))],4,steel)
  o['evidence']='Suzuki FIG415A, owner69 mounting triangle; owner70 right-hand structure';o['part_number']=d['part_numbers']['pillion_bracket_'+lab]
  if side==1:
   mount=Vector(d['exhaust_eye_R']);armpts=[C+Vector((0,8,3)),C+Vector((0,-7,-3)),mount+Vector((0,-12,-6)),mount+Vector((0,12,-6))]
   arm=loft(scene,'PassengerPegExhaustEar_R',[[[p.x+dx,p.y,p.z] for p in armpts] for dx in [-5,5]],gun,1);cylinder(scene,'Exhaust_HangerBolt',mount,8,24,steel,6);arm['unverified']='Right-only catalogue-supported exhaust ear; final muffler clamp and fit remain unverified.'
 import rebuild_exhaust_r29 as ex
 axis,u,v=ex._basis();rx,rz,bias=ex._muffler_section(.46);q=2.35;rr=1+bias*math.sin(q)+.018*math.cos(2*q);foot=ex._centre(.46)+u*((rx*rr-2)*math.cos(q))+v*((rz*rr-2)*math.sin(q));mount=Vector(d['exhaust_eye_R'])
 pp=[mount+Vector((0,13,0)),mount-Vector((0,13,0)),foot-Vector((0,13,0)),foot+Vector((0,13,0))]
 support=loft(scene,'Exhaust_MufflerHangerTab',[[[p.x+dx,p.y,p.z] for p in pp] for dx in [-3,3]],gun,1);support['unverified']='Visible connection reproduced; hidden weld and clamp depth provisional.'
 for obj in scene.objects:
  if obj.name.startswith(('PassengerPeg','Tool_Pillion','Tool_Chain','Exhaust_Hanger','Exhaust_MufflerHanger')) or obj.name=='ChainGuard':obj['stage_c_owner']='rear_hardware_r36'
 scene['revision']='r36';scene.name='GSX250R_Reconstruction_V2_Gray_r36';scene['stage_C']='NOT_PASSED';scene['rear_hardware_candidate']='Photo-led chain case and pillion supports; mounts require evaluated clearance and multi-view review.'
 bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True);return {'saved':str(output),'objects':len(scene.objects),'stage_C':'NOT_PASSED'}
