"""Wing sidelights and nonfolding solid backing, actual cowling depth sampled."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_owner_shapes import get,put

def build(s):
 ev=s.objects['Body_NoseAssembly'].evaluated_get(bpy.context.evaluated_depsgraph_get())
 # A common fitted plane avoids discontinuities when rays switch from the
 # outer fairing to the deeper headlight rim. Three supported outer samples.
 samples=[]
 for x,z in [(184,881),(150,850),(128,799)]:
  ok,p,n,i=ev.ray_cast(Vector((x*.001,2,z*.001)),Vector((0,-1,0)))
  if not ok:raise RuntimeError('No front-shell mounting sample')
  samples.append((x,z,p.y*1000))
 from mathutils import Matrix
 coeff=Matrix([[x,z,1] for x,z,y in samples]).inverted()@Vector([y for x,z,y in samples])
 def depth(x,z):return coeff.x*x+coeff.y*z+coeff.z
 pairs=[((183,881),(181,880)),((175,866),(126,852)),((151,834),(116,814)),((119,802),(112,797))]
 d=get(s,'Headlight_PositionLens');g=[]
 for a,b in pairs:
  row=[]
  for t in [0,.05,.28,.72,.95,1]:
   x=a[0]*(1-t)+b[0]*t;z=a[1]*(1-t)+b[1]*t;row.append([x,depth(x,z)+4,z])
  g.append(row)
 d['grid']=g;d['crease_boundary']=.55;d['thickness_mm']=.8;put(s,d)
 # Convex boundary avoids the acute narrow radial ring's crossed offset strips.
 points=sorted(set((p[0],p[2]) for row in g for p in row))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 halves=[]
 for seq in [points,list(reversed(points))]:
  h=[]
  for p in seq:
   while len(h)>=2 and cross(h[-2],h[-1],p)<=1e-7:h.pop()
   h.append(p)
  halves.extend(h[:-1])
 center=Vector((sum(p[0] for p in halves)/len(halves),sum(p[1] for p in halves)/len(halves)))
 outline=[]
 for p in halves:
  v=Vector(p);v+=(v-center).normalized()*2.6;outline.append([v.x,depth(v.x,v.y)+2,v.y])
 N=len(outline);verts=[[x,y+dy,z] for dy in [-.8,0] for x,y,z in outline]
 faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
 o=s.objects['Headlight_PositionSurround'];mat=o.data.materials[0];me=bpy.data.meshes.new('Sidelight_Bezel_Closed');me.from_pydata([[v*.001 for v in p] for p in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);o.data=me;o.modifiers.clear();m=o.modifiers.new('Symmetry_X','MIRROR');m.use_clip=True
 o['control_cage_source']='reconstruction_v2/data/current_controls/position_lamp_bezel.json'
 (V/'data/current_controls/position_lamp_bezel.json').write_text(json.dumps({'vertices_mm':verts,'faces':faces,'mirror_x':True,'evidence':'Owner66 wing lamp and evaluated front-shell mounting depth; unmeasured sizes'},indent=2))
 for old in ['position_lamp_ring.json','Headlight_PositionSurround.json']:
  p=V/'data/current_controls'/old
  if p.exists():p.unlink()
 return {'bezel_boundary_vertices':N}
if __name__=='__main__':
 result=build(bpy.context.scene);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(V/'model_history/GSX250R.blend'))
