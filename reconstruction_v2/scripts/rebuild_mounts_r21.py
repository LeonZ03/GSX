"""Photo-led rear shock and compact mounting assembly, isolated incremental pass.
Official FIG545A supports hardware topology, not hidden mounting dimensions.
All frame attachment depth and eye coordinates remain explicit construction estimates.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
V=Path(__file__).resolve().parents[1];COL=None;MAT={}
def mesh(name,points,faces,mat='metal',smooth=True):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata([Vector(p)*.001 for p in points],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);COL.objects.link(o);me.materials.append(MAT[mat])
 for f in me.polygons:f.use_smooth=smooth
 o['stage_r21_owner']='rear_shock_root_rebuild';o['dimension_status']='photo_led_construction_estimate';return o

def tube(name,a,b,r,mat='metal',n=48):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.1:u=axis.cross(Vector((0,1,0)))
 u.normalize();v=axis.cross(u);points=[c+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for c in (a,b) for i in range(n)]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,points,faces,mat)

def ring(name,center,ir,outer,depth,mat='metal',stretch=0,direction=1):
 x,y,z=center;n=64;points=[]
 for xx in (x-depth/2,x+depth/2):
  for inner in (True,False):
   for j in range(n):
    a=j*math.tau/n;rr=ir if inner else outer+stretch*max(0,direction*math.cos(a))**3
    points.append((xx,y+rr*math.sin(a),z+rr*math.cos(a)))
 faces=[]
 for j in range(n):
  k=(j+1)%n;faces.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
 return mesh(name,points,faces,mat)

def apply(scene,output):
 global COL,MAT
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('stage_c_shock_rebuilt'):raise ValueError('Do not replay on a refined suspension')
 old=scene.objects['Shock_Piston'];COL=old.users_collection[0];MAT={'metal':old.data.materials[0],'dark':scene.objects['Engine_Crankcase'].data.materials[0],'coil':scene.objects['RearShock_Spring'].data.materials[0]}
 assembly=scene.objects.get('Body_NoseAssembly');display=[(m,m.show_viewport) for m in assembly.modifiers]
 for m,_ in display:m.show_viewport=False
 removed=[]
 for o in list(scene.objects):
  if o.name in ('Shock_Piston','Shock_Body','RearShock_Spring') or o.get('stage_r21_owner')=='rebuild_mounts_r21':removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 lower=Vector((0,-392,374));upper=Vector((0,-264,674));axis=(upper-lower).normalized();u=Vector((1,0,0));v=axis.cross(u).normalized()
 def at(t):return lower.lerp(upper,t)
 tube('Shock_Piston',at(.04),at(.68),7,'metal');tube('Shock_Body',at(.48),at(.94),18,'dark')
 tube('Shock_BumpStop',at(.14),at(.23),14,'dark')
 # Owner70 visible coil pack is short with a few wide-spaced turns; the old
 # ten-turn full-length spring contradicted both the photo and family diagram.
 turns=5.25;steps=336;segments=10;centers=[]
 for j in range(steps+1):
  t=j/steps;angle=turns*math.tau*t;centers.append(at(.28+.40*t)+31*(u*math.cos(angle)+v*math.sin(angle)))
 points=[]
 for j,c in enumerate(centers):
  tangent=(centers[min(steps,j+1)]-centers[max(0,j-1)]).normalized();rad=(c-at(.28+.40*j/steps)).normalized();n=tangent.cross(rad).normalized()
  points.extend(c+4.6*(rad*math.cos(k*math.tau/segments)+n*math.sin(k*math.tau/segments)) for k in range(segments))
 faces=[tuple(reversed(range(segments))),tuple(range(steps*segments,(steps+1)*segments))]+[(j*segments+k,j*segments+(k+1)%segments,(j+1)*segments+(k+1)%segments,(j+1)*segments+k) for j in range(steps) for k in range(segments)]
 mesh('RearShock_Spring',points,faces,'coil')
 for name,t,r in [('Lower',.265,36),('Upper',.697,36),('Adjuster',.734,33)]:tube('Shock_SpringSeat_'+name,at(t-.012),at(t+.012),r,'dark')
 for name,center in [('Upper',upper),('Lower',lower)]:
  ring('ShockMount_'+name+'Eye',center,5.3,16,28,'dark');tube('ShockMount_'+name+'Pin',center+Vector((-26,0,0)),center+Vector((26,0,0)),5)
  for sign,lab in [(-1,'L'),(1,'R')]:
   p=center+Vector((sign*18,0,0));ring('ShockMount_'+name+'Ear_'+lab,p,5.3,16,6,'dark',19 if name=='Upper' else 12,1 if name=='Upper' else -1)
   ring('ShockMount_'+name+'Washer_'+lab,center+Vector((sign*22,0,0)),5.3,12,2)
   tube('ShockMount_'+name+('Nut_' if sign<0 else 'Head_')+lab,center+Vector((sign*23,0,0)),center+Vector((sign*30,0,0)),8.5,'metal',6)
 # Minimal hidden crossmembers join the current frame/swingarm; no unsupported
 # diagonal strut cage. Exact factory profiles remain unverified.
 tube('ShockMount_UpperCrossmember',(-136,-264,709),(136,-264,709),13,'dark')
 tube('ShockMount_LowerCrossmember',(-114,-392,347),(114,-392,347),13,'dark')
 scene['stage_c_shock_rebuilt']=True;scene['revision']='r22';scene.name='GSX250R_Reconstruction_V2_Gray_r22';scene['stage_c_status']='NOT_PASSED'
 for m,enabled in display:m.show_viewport=enabled
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(output))
 return {'removed':removed,'objects':len(scene.objects),'source':str(output),'spring_turns':turns,'coil_wire_diameter_mm':9.2,'note':'Coil pack, eye coordinates, bracket profile and hidden crossmembers are photo-led estimates, not measured approval.'}
