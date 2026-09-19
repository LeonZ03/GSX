"""r33 position-light strip topology and inner-cowl assembly seam."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));import build_gray as bg

def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('revision')!='r32':raise ValueError('Requires r32')
 # Four monotonic stations replace the folded old tip rows. Same observed area.
 ends=[([168,735,895],[174,739,889]),([153,757,880],[173,767,857]),([136,781,860],[159,790,835]),([128,795,850],[136,800,834])]
 for pair in ends:
  for p in pair:p[1]=735-1.1*(p[2]-895)-.26*(p[0]-168)
 lens=[[list(Vector(p).lerp(Vector(q),t)) for t in [0,.06,.32,.68,.94,1]] for p,q in ends]
 center=Vector((149,768,864));sur=[]
 for row in lens:
  sur.append([list(center+(Vector(p)-center)*1.08+Vector((0,-4,0))) for p in row])
 dst=V/'data/revisions/r33_front_candidate';dst.mkdir(exist_ok=True)
 for n,g in [('Headlight_PositionLens',lens),('Headlight_PositionSurround',sur)]:
  d=json.loads((V/'data/control_cages'/f'{n}.json').read_text());d['grid']=g;d['revision']='r33';d['thickness_mm']=1.5;d['notes']='Nonfolding diagonal position light candidate; unseen optical assembly not certified.'
  o=scene.objects[n];old=o.data;me=bpy.data.meshes.new(n+'_r33');me.from_pydata([[x*.001 for x in p] for row in g for p in row],[],bg.cage_faces(d));me.update()
  for mat in old.materials:me.materials.append(mat)
  for f in me.polygons:f.use_smooth=True
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o.data=me;bg.apply_creases(o,d)
  for m in o.modifiers:
   if m.type=='SOLIDIFY':m.thickness=.0015
  o['control_cage_source']=f'reconstruction_v2/data/revisions/r33_front_candidate/{n}.json';(dst/f'{n}.json').write_text(json.dumps(d,indent=2))
 # Separate the coincident rear return rail from the inner-panel front rail.
 n='Body_NoseSideReturn';o=scene.objects[n];d=json.loads((V/'data/revisions/r32_front_candidate'/f'{n}.json').read_text())
 for p in d['grid'][0]:p[1]+=4.5
 for v,p in zip(o.data.vertices,[p for row in d['grid'] for p in row]):v.co=Vector(p)*.001
 o.data.update();d['revision']='r33';d['notes']+=' Rear seam offset 4.5mm in Y for shell thickness; construction gap, not measured.'
 o['control_cage_source']=f'reconstruction_v2/data/revisions/r33_front_candidate/{n}.json';(dst/f'{n}.json').write_text(json.dumps(d,indent=2))
 scene['revision']='r33';scene.name='GSX250R_Reconstruction_V2_Gray_r33';bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True);return {'saved':str(output),'acceptance':'NOT_PASSED'}
