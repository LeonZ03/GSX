"""Explicit topology migration into an isolated r04 blend, saving r05 separately."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
sys.path.insert(0,str(ROOT/'scripts'));import build_motorcycle as b
s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_Reconstruction_V2_Gray'));bpy.context.window.scene=s
if Path(bpy.data.filepath).name not in ('04_gray_review.blend','05_gray_review.blend'):raise RuntimeError('Use an isolated r04/r05 file; live scenes are not a migration target')
C={key:next(c for c in s.collection.children if c.name.startswith('Collection_'+key)) for key in ['Body','FrontEnd','Details']}
M={key:next(m for m in bpy.data.materials if m.name.startswith('MAT_Gray_'+key)) for key in ['shell','tank','trim','seat','lamp','wind']}
for o in list(s.objects):
 if o.get('control_cage_source') and Path(o['control_cage_source']).stem=='Body_FairingBlade':bpy.data.objects.remove(o,do_unlink=True)
for p in sorted((V2/'data/control_cages').glob('*.json')):
 a=json.loads(p.read_text());rows=a['grid'];nr=len(rows);nc=len(rows[0]);d=bpy.data.meshes.new(a['name']+'_Cage_r05')
 d.from_pydata([[x*.001 for x in co] for row in rows for co in row],[],[(j*nc+i,j*nc+i+1,(j+1)*nc+i+1,(j+1)*nc+i) for j in range(nr-1) for i in range(nc-1)])
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();d.materials.append(M[a['material']])
 for f in d.polygons:f.use_smooth=True
 o=next((o for o in s.objects if o.get('control_cage_source') and Path(o['control_cage_source']).stem==a['name']),None)
 if o is None:
  o=bpy.data.objects.new(a['name'],d);C['Body' if a['name'].startswith(('Body','Seat')) else 'FrontEnd'].objects.link(o)
 else:o.data=d
 o['control_cage_source']='reconstruction_v2/data/control_cages/'+p.name;o['editable_quads']=True;o['acceptance']='pending'
 o.modifiers.clear()
 if a['mirror_x']:
  md=o.modifiers.new('Symmetry_X','MIRROR');md.use_clip=True;md.merge_threshold=.0001
 md=o.modifiers.new('Editable_Subdivision','SUBSURF');md.levels=md.render_levels=a['subdivision']
 if a['thickness_mm']:
  md=o.modifiers.new('Shell_Thickness','SOLIDIFY');md.thickness=a['thickness_mm']*.001;md.offset=-1
 if a.get('crease_columns') or a.get('crease_boundary'):
  cr=d.attributes.new('crease_edge','FLOAT','EDGE')
  for e in d.edges:
   i,j=e.vertices
   if i%nc==j%nc:cr.data[e.index].value=a.get('crease_columns',{}).get(str(i%nc),0)
   if (i//nc==j//nc and i//nc in [0,nr-1]) or (i%nc==j%nc and i%nc in [0,nc-1]):cr.data[e.index].value=max(cr.data[e.index].value,a.get('crease_boundary',0))
for k in [69,70]:
 if (V2/f'calibration/camera_{k}.json').exists() and not any(o.type=='CAMERA' and o.get('image_id')==k for o in s.objects):
  d=bpy.data.cameras.new('Camera_Photo_'+str(k));d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.clip_start=.05;o=bpy.data.objects.new(d.name,d);next(c for c in s.collection.children if c.name.startswith('Collection_Cameras')).objects.link(o);o['image_id']=k;o.lock_location=(True,)*3;o.lock_rotation=(True,)*3
for o in s.objects:
 if o.type=='CAMERA' and o.get('image_id') in [62,63,64,69,70]:
  c=json.loads((V2/f"calibration/camera_{o['image_id']}.json").read_text());R=Matrix(c['R_cv']);t=Vector(c['t_cv_m']);T=Matrix.Identity(4);rot=R.transposed()@Matrix.Diagonal(Vector((1,-1,-1)))
  for i in range(3):T.col[i].xyz=rot.col[i]
  T.translation=-(R.transposed()@t);o.matrix_world=T;o.data.lens=c['K_px'][0][0]*36/c['image_size'][0];o['fit_status']=c['status'];o['camera_evidence']='rim_arcs_and_reviewed_real_two_view_features' if o.get('image_id') in [62,63] else 'provisional_partial_wheel_arcs'
# Rebuild only the failed guard objects in this isolated copy.
for o in list(s.objects):
 if o.name.startswith(('GuardBar','GuardMount')):bpy.data.objects.remove(o,do_unlink=True)
b.COL=C['FrontEnd'];b.M={'guard':M['trim'],'rubber':M['seat'],'steel':M['trim']}
g=json.loads((V2/'data/guard_control.json').read_text());n={k:Vector(v) for k,v in g['right_nodes'].items()}
def rounded_triangle(ps,r=20):
 result=[]
 for i,p in enumerate(ps):
  prev=ps[(i-1)%3];nxt=ps[(i+1)%3];a=p+(prev-p).normalized()*r;c=p+(nxt-p).normalized()*r
  for j in range(7):
   u=j/6;result.append(a*(1-u)**2+p*(2*u*(1-u))+c*u*u)
 return result
for sign in [-1,1]:
 lab='R' if sign>0 else 'L'
 def pt(v):return (sign*v[0],v[1],v[2])
 o=b.tube('GuardBar_'+lab,[pt(v) for v in rounded_triangle([n['rear'],n['upper'],n['lower']])],g['tube_radius_mm'],'guard',True,False);o['evidence']='photo_62_63_observed_nodes';o['acceptance']='mount_depths_unverified'
 b.rod('GuardMount_Rear_'+lab,pt(n['rear_mount']),pt(n['rear']),10,'guard')
 b.rod('GuardMount_Lower_'+lab,pt(n['lower_mount']),pt(n['lower']),10,'guard')
 b.rod('GuardMount_Upper_'+lab,pt(Vector((145,265,545))),pt(n['upper']),11,'guard')
 for key,r,length in [('upper',18,42),('lower',16,25),('rear',15,30)]:
  v=n[key];b.rod('GuardBar_Slider_'+key+'_'+lab,pt(v-Vector((4,0,0))),pt(v+Vector((length,0,0))),r,'rubber')
 for key in ['rear_mount','lower_mount']:
  b.bolt('GuardMount_Bolt_'+key+'_'+lab,pt(n[key]),6,(sign,0,0),'steel')
# Mirror silhouette revision: actual back-shell envelope, independent left/right yaw.
if (V2/'data/mirror_control.json').exists():
 for o in list(s.objects):
  if o.name.startswith(('Mirror_Stem_','Mirror_L','Mirror_R')):bpy.data.objects.remove(o,do_unlink=True)
 m=json.loads((V2/'data/mirror_control.json').read_text());b.M['black']=M['trim']
 for sign in [-1,1]:
  lab='R' if sign>0 else 'L';key='right' if sign>0 else 'left';cen=Vector(m['center_'+key]);normal=Vector(m['normal_'+key]).normalized();u=Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u).normalized()
  coords=[cen+u*x+v*z for x,z in m['outline_uv_mm']]
  o=b.panel('Mirror_'+lab,coords,'black',20,6);o['acceptance']='photo_pose_provisional'
  mount=cen-v*48
  b.tube('Mirror_Stem_'+lab,[(sign*139,604,915),(sign*208,595,964),mount],8,'black',False,False)
s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.get('image_id')==63);args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];revision=args[0] if args else 'r05'
if revision not in ('r05','r06','r07','r08'):raise ValueError('Unsupported revision')
s['revision']=revision;s['visual_acceptance']='NOT_PASSED'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(V2/'blends'/(revision[1:]+'_gray_review.blend')));print(revision+'_SAVED',len(s.objects))