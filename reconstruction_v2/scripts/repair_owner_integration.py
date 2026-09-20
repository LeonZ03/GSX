"""r44 integration corrections discovered by rendered views and assembly audit."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_structure import init,purge,solid_tube,ring
from rebuild_owner_shapes import get,put,remove
from rebuild_clutch_r30 import loft

def run():
 s=bpy.context.scene
 if s.get('revision')!='r44':raise ValueError('Requires r44 candidate')
 b=init(s)
 d=get(s,'Headlight_Lens')
 for row in d['grid']:
  w=row[-1][0];y=row[0][1];z=row[0][2]
  for p in row:
   t=p[0]/w;p[1]=y-15*(w/121)**2*t*t;p[2]=z+10*(w/121)*t*t
 put(s,d);g=d['grid']
 contour=[Vector(p) for p in reversed(g[0])]+[Vector((-p[0],p[1],p[2])) for p in g[0][1:]]
 contour += [Vector((-r[-1][0],r[-1][1],r[-1][2])) for r in g[1:]]
 contour += [Vector((-p[0],p[1],p[2])) for p in reversed(g[-1][:-1])]+[Vector(p) for p in g[-1][1:]]+[Vector(r[-1]) for r in reversed(g[1:-1])]
 outer=[p+Vector((p.x,0,p.z-812)).normalized()*4+Vector((0,-1,0)) for p in contour]
 purge(s,('Headlight_Housing','Headlight_Surround','Headlight_Reflector'))
 ring(s,b,'Headlight_Surround',outer,contour,(0,-7,0),'black')
 N=len(outer);back=[Vector((p.x*.65,715,812+(p.z-812)*.65)) for p in outer]
 vs=[p+Vector((0,-10,0)) for p in outer]+back+[Vector((0,715,812))]
 fs=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[(2*N,N+(i+1)%N,N+i) for i in range(N)]
 o=b.mesh('Headlight_Housing',vs,fs,'black',smo=True);m=o.modifiers.new('Housing_wall','SOLIDIFY');m.thickness=.002;m.offset=-1
 # Faceted bowl drawn inside the housing; closed annular thickness at socket.
 vs=[];center=Vector((0,775,812))
 for t in [0,.08,.38,.68,.82]:
  for p in contour:
   q=p.lerp(center,t);q.y-=18*math.sin(math.pi*t);vs.append(q)
 fs=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(4) for j in range(N)]
 o=b.mesh('Headlight_Reflector',vs,fs,'silver');m=o.modifiers.new('Reflector_wall','SOLIDIFY');m.thickness=.001;m.offset=-1
 # Pipe drops ahead of crankcase before turning under sump; endpoints retained.
 for lab in ['L','R']:
  o=s.objects['Exhaust_Header_'+lab];pts=o.data.splines[0].bezier_points
  pts[2].co.y=.380;pts[3].co.y=.250
  for p in pts:p.handle_left_type=p.handle_right_type='AUTO'
 # Reject automatic long rods. Replace with short mounting tabs at actual ray hits.
 purge(s,('Fairing_InnerBoss','Fairing_RubberGrommet'))
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();created=[]
 for side,lab in [(-1,'L'),(1,'R')]:
  frame=s.objects['Frame_Main_'+lab];ev=frame.evaluated_get(dg);me=ev.to_mesh();fps=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
  for k,(y,z) in enumerate([(.25,.73),(.17,.70),(.07,.68)]):
   origin=Vector((0,y,z));direction=Vector((side,0,0));best=None
   for name in ['Body_SideFairing','Body_UpperSideCowl','Body_SeatSide']:
    ob=s.objects.get(name)
    if not ob:continue
    ev=ob.evaluated_get(dg);inv=ev.matrix_world.inverted();hit,p,n,idx=ev.ray_cast(inv@origin,inv.to_3x3()@direction)
    if hit:
     p=ev.matrix_world@p;target=min(fps,key=lambda q:(q-p).length);length=(target-p).length
     if length<.080 and (best is None or length<best[0]):best=(length,p,target)
   if best:
    length,p,target=best;p*=1000;target*=1000;u=Vector((0,0,8));poly=[p+u,p-u,target-u,target+u]
    ob=b.panel('Fairing_MountTab_'+lab+str(k),poly,'black',4,1);ob['unverified']='Mount footprint inferred behind shell; hidden placement unmeasured';created.append((ob.name,round(length*1000,1)))
 # The visible long rear tube was a generic AUTO spline below bodywork.
 for side,lab in [(-1,'L'),(1,'R')]:
  old=s.objects['Frame_SeatRail_'+lab];r=old.data.bevel_depth*1000;remove(s,old.name)
  solid_tube(b,'Frame_SeatRail_'+lab,[(side*85,-199,744),(side*75,-420,776),(side*64,-610,876),(side*35,-900,983)],r,'black',False)
 # Small collapsed bevel strips come from bevel radius exceeding thin panel depth.
 for o in s.objects:
  if o.name.startswith('Grip_Rib_'):
   for m in list(o.modifiers):
    if m.type=='BEVEL':m.width=.00015
  if o.name in ['Dashboard_Bezel','Dashboard_LCD','PhoneMount_RubberPad']:
   for m in o.modifiers:
    if m.type=='BEVEL':m.width=.0003
 # Bring colour-independent workbench inspection into readable neutral range.
 for mat in bpy.data.materials:
  if mat.name.startswith('MAT_Gray_'):mat.diffuse_color=(.4,.4,.4,1)
 # No edit of official/photo cameras; source remains the one working file.
 s['revision']='r45';s.name='GSX250R_Reconstruction_V2_Gray_r45'
 bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
 return {'short_fairing_tabs_mm':created,'status':'RECHECK_REQUIRED'}
