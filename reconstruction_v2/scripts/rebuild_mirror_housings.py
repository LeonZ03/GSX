"""Replace the six-point mirror proxies with closed, rounded housings.
Requires an explicit derived control file and a new output; does not edit cameras.
"""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(V/'scripts'))
from rebuild_body_stage_b import setup_helpers

def mesh(name,verts,faces,mat,col):
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata([[x*.001 for x in p] for p in verts],[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat)
 for f in me.polygons:f.use_smooth=True
 ob['revision']='r21';ob['acceptance']='photo_led_shell_depth_and_adjustable_pose_unverified'
 return ob

def apply(scene,control,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('revision')!='r20':raise ValueError('Use the frozen r20 source')
 a=json.loads(Path(control).read_text());b=setup_helpers(scene)
 assembly=scene.objects.get('Body_NoseAssembly');display=[(m,m.show_viewport) for m in assembly.modifiers] if assembly else []
 for m,enabled in display:m.show_viewport=False
 col=scene.objects['Mirror_R'].users_collection[0];mat=scene.objects['Mirror_R'].data.materials[0]
 for ob in list(scene.objects):
  if ob.name in ['Mirror_L','Mirror_R','Mirror_Stem_L','Mirror_Stem_R']:bpy.data.objects.remove(ob,do_unlink=True)
 cen=Vector(a['center_right']);n=Vector(a['normal_right']).normalized();u=Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
 coords=[Vector(p)-cen for p in a['rim_right_mm']];uv=[(p.dot(u),p.dot(v)) for p in coords]
 old=json.loads((V/'data/mirror_control.json').read_text())
 if a.get('left_pose'):old.update(center_left=a['left_pose']['center_mm'],normal_left=a['left_pose']['normal'])
 for lab in ['R','L']:
  if lab=='L':
   n=Vector(old['normal_left']).normalized();cen=Vector(old['center_left']);u=Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
   pts=[cen-u*x+v*y for x,y in uv]
  else:pts=[Vector(p) for p in a['rim_right_mm']]
  ring=len(pts);verts=[]
  for scale,depth in [(.94,-3),(1,0),(.985,5),(.87,15),(.57,22),(.16,25)]:
   verts += [cen+(p-cen)*scale+n*depth for p in pts]
  faces=[tuple(reversed(range(ring)))]+[(j*ring+i,j*ring+(i+1)%ring,(j+1)*ring+(i+1)%ring,(j+1)*ring+i) for j in range(5) for i in range(ring)]+[tuple(range(5*ring,6*ring))]
  ob=mesh('Mirror_'+lab,verts,faces,mat,col);md=ob.modifiers.new('Editable_Housing_Subdivision','SUBSURF');md.levels=1;md.render_levels=1
  glass=bpy.data.materials.get('MAT_Gray_MirrorInset') or bpy.data.materials.new('MAT_Gray_MirrorInset');glass.diffuse_color=(.22,.22,.22,1)
  glass.use_nodes=True;bs=next((n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or glass.node_tree.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(.22,.22,.22,1);bs.inputs['Roughness'].default_value=.6
  vv=[cen+(p-cen)*.905-n*3.7 for p in pts];vv += [p+n*.7 for p in vv]
  ff=[tuple(reversed(range(ring))),tuple(range(ring,2*ring))]+[(i,(i+1)%ring,(i+1)%ring+ring,i+ring) for i in range(ring)]
  mesh('Mirror_Glass_'+lab,vv,ff,glass,col)
  sign=1 if lab=='R' else -1;b.COL=col;b.M['black']=mat
  mount=cen-v*38-n*4
  stem=b.tube('Mirror_Stem_'+lab,[(sign*139,604,915),(sign*218,594,970),mount],8,'black',False,False);stem.data.use_fill_caps=True
  ob['shell_depth_mm']=25;ob['depth_is_estimate']=True
 scene['revision']='r21';scene.name='GSX250R_Reconstruction_V2_Gray_r21';scene['visual_acceptance']='NOT_PASSED'
 for m,enabled in display:m.show_viewport=enabled
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(output))
 return {'output':str(output),'objects':len(scene.objects),'camera_changes':False,'status':'CANDIDATE_NOT_ACCEPTED'}
