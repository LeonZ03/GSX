"""Build a replacement mid-side cover candidate and visible left sprocket cover.
The r25 resolve step removes the old duplicate mid-side cover.
No original frame, drivetrain, body control or camera is deleted or moved.
"""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from rebuild_body_stage_b import setup_helpers
import build_gray as bg
from rebuild_mirror_housings import mesh

def apply(scene,panel_control,sprocket_control,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 if scene.objects.get('Body_FrameSidePanel'):raise ValueError('Do not replace an edited frame side panel')
 setup_helpers(scene);display=[(m,m.show_viewport) for m in scene.objects['Body_NoseAssembly'].modifiers]
 for m,_ in display:m.show_viewport=False
 a=json.loads(Path(panel_control).read_text());ob=bg.cage(a)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
 d=json.loads(Path(sprocket_control).read_text());edge=[Vector(p) for p in d['world_mm']];cen=sum(edge,Vector())/len(edge);N=len(edge)
 # Closed outer thin cover with a shallow centre ridge, independently editable.
 verts=[p+Vector((2,0,0)) for p in edge]+[p for p in edge]+[cen+Vector((-6,0,0))]
 faces=[tuple(reversed(range(N)))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]+[(N+i,N+(i+1)%N,2*N) for i in range(N)]
 cover=mesh('Engine_SprocketCover',verts,faces,bg.M['trim'],bg.C['Engine']);cover['part_reference']='FIG112A item16 / 11360-20K00';cover['accuracy']='Visible left face from photo69; depth and concealed flange approximate'
 bevel=cover.modifiers.new('Moulded_Edge_Radius','BEVEL');bevel.width=.001;bevel.segments=3
 scene['revision']='r23';scene.name='GSX250R_Reconstruction_V2_Gray_r23';scene['visual_acceptance']='NOT_PASSED'
 for m,enabled in display:m.show_viewport=enabled
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(output))
 return {'output':str(output),'objects':len(scene.objects),'new_parts':['Body_FrameSidePanel','Engine_SprocketCover'],'cameras_changed':False}
