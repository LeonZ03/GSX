"""r32 front returns and an open headlamp surround. Candidate, not acceptance."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'));import build_gray as bg

def apply(scene,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.get('revision')!='r31':raise ValueError('Requires r31')
 host=scene.objects['Body_NoseAssembly'];flags=[m.show_viewport for m in host.modifiers]
 for m in host.modifiers:m.show_viewport=False
 d=json.loads((V/'data/revisions/r31_front_candidate/Body_NoseSideReturn.json').read_text())
 bottoms=[[137,610.8,825.3],[150,651,815],[180,705,775],[200,737,748],[200,752,730],[195,752,715],[190,746,707],[190,746,699]]
 for row,q in zip(d['grid'],bottoms):
  p=Vector(row[0]);row[:]=[list(p.lerp(Vector(q),t)) for t in [0,.035,.18,.5,.82,.965,1]]
 data={'Body_NoseSideReturn':d}
 ld=json.loads((V/'data/revisions/r31_front_candidate/Headlight_Lens.json').read_text());sd=json.loads((V/'data/revisions/r31_front_candidate/Headlight_Surround.json').read_text())
 def border(g):return g[0]+[r[-1] for r in g[1:]]+list(reversed(g[-1][:-1]))
 inner=[]
 for p in border(ld['grid']):
  v=Vector(p);dr=Vector((v.x,0,v.z-805));dr.normalize();v+=dr*2.0;v.y-=2.0
  if abs(p[0])<.001:v.x=0
  inner.append(v)
 outer=list(map(Vector,border(sd['grid'])))
 sd['grid']=[[list(a.lerp(b,t)) for a,b in zip(outer,inner)] for t in [0,.12,.88,1]]
 sd['crease_boundary']=.65;sd['notes']='Open editable quad ring; 2mm nominal lens clearance, not measured OEM gap.';data['Headlight_Surround']=sd
 dst=V/'data/revisions/r32_front_candidate';dst.mkdir(exist_ok=True)
 for n,d in data.items():
  o=scene.objects[n];old=o.data;me=bpy.data.meshes.new(n+'_r32');me.from_pydata([[x*.001 for x in p] for row in d['grid'] for p in row],[],bg.cage_faces(d));me.update()
  for mat in old.materials:me.materials.append(mat)
  for f in me.polygons:f.use_smooth=True
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o.data=me;bg.apply_creases(o,d)
  d['revision']='r32';d['status']='NOT_PASSED';o['control_cage_source']=f'reconstruction_v2/data/revisions/r32_front_candidate/{n}.json';(dst/f'{n}.json').write_text(json.dumps(d,indent=2))
 for m,f in zip(host.modifiers,flags):m.show_viewport=f
 for n in ['Body_UpperSideCowl','Body_SideFairing']:scene.objects[n]['control_cage_source']=f'reconstruction_v2/data/revisions/r28_front_candidate/{n}.json'
 scene['revision']='r32';scene.name='GSX250R_Reconstruction_V2_Gray_r32';scene['stage_B']='NOT_PASSED';scene['stage_C']='NOT_PASSED'
 bpy.context.view_layer.update();bpy.data.libraries.write(str(output),{scene},fake_user=True);return {'saved':str(output),'status':'NOT_PASSED'}
