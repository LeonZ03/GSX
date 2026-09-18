"""Apply r03 source corrections to a V2-only scene and save a normal Blender file.
No baseline scene is removed or overwritten.
"""
from pathlib import Path
import bpy,json,sys,re
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2'
s=next(s for s in bpy.data.scenes if s.name.startswith('GSX250R_Reconstruction_V2_Gray'));bpy.context.window.scene=s
for o in s.objects:
 if o.get('control_cage_source'):
  a=json.loads((ROOT/o['control_cage_source']).read_text());rows=a['grid'];nr=len(rows);nc=len(rows[0]);d=bpy.data.meshes.new(a['name']+'_r03')
  d.from_pydata([[x*.001 for x in p] for row in rows for p in row],[],[(j*nc+i,j*nc+i+1,(j+1)*nc+i+1,(j+1)*nc+i) for j in range(nr-1) for i in range(nc-1)])
  d.materials.append(o.data.materials[0]);o.data=d
  for p in d.polygons:p.use_smooth=True
  if a['name']=='Body_Tank':
   creases=d.attributes.new('crease_edge','FLOAT','EDGE')
   for e in d.edges:
    i,j=e.vertices
    if i%nc==j%nc and i%nc in [2,3,5]:creases.data[e.index].value=.28
 if o.name.startswith('Tire_') and not o.get('nominal_width_corrected'):
  for v in o.data.vertices:v.co.x/=1.02
  o['nominal_width_corrected']=True
 if not o.get('placement_r03'):
  if o.name.startswith('Engine_'):o.location.y+=.135;o.location.z-=.030
  if o.name.startswith(('Footpeg','Rearset')):o.location.y+=.140;o.location.z-=.050
  if o.name.startswith('Radiator'):o.location.y+=.080
  o['placement_r03']=True
 # Keep names human-readable in this isolated file; no original source scene is present.
 base=re.sub(r'\.\d{3}$','',o.name)
 if bpy.data.objects.get(base) in (None,o):o.name=base
for o in s.objects:
 if o.type=='CAMERA' and o.get('image_id') in [62,63,64]:
  c=json.loads((V2/f"calibration/camera_{o['image_id']}.json").read_text());R=Matrix(c['R_cv']);t=Vector(c['t_cv_m']);T=Matrix.Identity(4);rot=R.transposed()@Matrix.Diagonal(Vector((1,-1,-1)))
  T.col[0].xyz=rot.col[0];T.col[1].xyz=rot.col[1];T.col[2].xyz=rot.col[2];T.translation=-(R.transposed()@t);o.matrix_world=T;o.data.lens=c['K_px'][0][0]*36/c['image_size'][0];o['fit_status']=c['status']
for o in s.objects:
 if o.name.startswith('GuardBar_') and o.type=='CURVE':
  sign=1 if '_R' in o.name else -1
  if 'Slider' not in o.name:
   pts=[(sign*185,-116,522),(sign*314,-92,536),(sign*335,282,519),(sign*308,302,478),(sign*308,213,386),(sign*283,-12,416),(sign*185,-116,522)]
   if len(o.data.splines[0].bezier_points)==len(pts):
    for p,co in zip(o.data.splines[0].bezier_points,pts):p.co=Vector(co)*.001
s.camera=next(o for o in s.objects if o.type=='CAMERA' and o.get('image_id')==63)
s['revision']='r03';s['visual_acceptance']='NOT_PASSED';bpy.context.view_layer.update()
# Only empty startup scenes created while opening a library-only checkpoint may be removed.
for other in list(bpy.data.scenes):
 if other!=s and len(other.objects)==0 and other.name=='Scene':bpy.data.scenes.remove(other)
bpy.ops.wm.save_as_mainfile(filepath=str(V2/'blends/03_gray_review.blend'))
print('NORMAL_SOURCE_SAVED',len(s.objects))
