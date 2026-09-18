"""Generate isolated evaluated tank-rear candidates from r11; never save a scene.
Only three smooth section parameters change; production cage JSON stays frozen.
All trial meshes, parameters and quality diagnostics remain in ignored qa/.
"""
from pathlib import Path
import bpy,bmesh,json,itertools,math,sys
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];V2=ROOT/'reconstruction_v2';s=bpy.context.scene
if s.get('revision')!='r11':raise RuntimeError('Expected isolated r11 source')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
refine='--small' in args
out=V2/('qa/interface_candidates_r13_small' if refine else 'qa/interface_candidates_r13')
if out.exists():raise FileExistsError('Preserve existing candidate run; choose a new revision')
out.mkdir()
template=json.loads((V2/'data/control_cages/Body_Tank.json').read_text());base=template['grid'];tank=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Body_Tank.json'));seat=next(o for o in s.objects if o.get('control_cage_source','').endswith('/Seat_Rider.json'))
if max(math.dist([float(c)*1000 for c in vert.co],point) for vert,point in zip(tank.data.vertices,[p for row in base for p in row]))>.01:raise RuntimeError('Scene cage differs from canonical JSON; restore the explicitly frozen r11 inputs before running this historical migration')
yweight=[.35,.5,1.,1.,.35,0,0,0,0,0];xweight=[.3,.5,1.,1.,.3,0,0,0,0,0];zweight=[1,1,.5,.3,.1,0,0,0,0,0]

def evaluate(obj):
 e=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();verts=[e.matrix_world@v.co for v in m.vertices];faces=[list(f.vertices) for f in m.loop_triangles];tree=BVHTree.FromPolygons(verts,faces,all_triangles=True);bm=bmesh.new();bm.from_mesh(m);non=sum(not x.is_manifold for x in bm.edges);bm.free();e.to_mesh_clear();return verts,faces,tree,non
bpy.context.view_layer.update();_,_,seat_tree,_=evaluate(seat);results=[]
trials=list(itertools.product([10,15,20],[0,6],[0,5])) if refine else [(0,0,0)]+list(itertools.product([25,40,55],[0,12,24],[0,10]))
for ext,narrow,lift in trials:
 name=f'e{ext}_w{narrow}_z{lift}';grid=json.loads(json.dumps(base));maxmove=0
 for j,row in enumerate(grid):
  xmax=max(p[0] for p in base[j])
  for i,p in enumerate(row):
   p[0]-=narrow*xweight[j]*base[j][i][0]/xmax;p[1]-=ext*yweight[j];p[2]+=lift*zweight[j]
   maxmove=max(maxmove,math.dist(p,base[j][i]));tank.data.vertices[j*len(row)+i].co=[x*.001 for x in p]
 tank.data.update();bpy.context.view_layer.update();verts,faces,tree,non=evaluate(tank);selfpairs=sum(1 for i,j in tree.overlap(tree) if i<j and not set(faces[i]).intersection(faces[j]));overlap=len(tree.overlap(seat_tree))
 cage=dict(template,grid=grid,revision='r13',acceptance='candidate_only_not_applied')
 data={'name':name,'parameters_mm':{'rear_extension':ext,'rear_width_reduction':narrow,'rear_lift':lift},'geometry':{'vertices':[list(v) for v in verts],'triangles':faces},'cage':cage,'max_control_move_mm':maxmove,'quality':{'nonmanifold_edges':non,'nonadjacent_self_intersection_candidates':selfpairs,'seat_triangle_overlap_pairs':overlap}}
 (out/f'{name}.json').write_text(json.dumps(data),encoding='utf8');results.append({k:v for k,v in data.items() if k not in ['geometry','cage']});print('INTERFACE_CANDIDATE',name,data['quality'],flush=True)
(out/'index.json').write_text(json.dumps({'source':'11_gray_review.blend','blender_version':bpy.app.version_string,'source_scene_saved':False,'candidates':results},indent=2),encoding='utf8')
result={'candidate_count':len(results),'geometry_clean':sum(all(v==0 for v in r['quality'].values()) for r in results),'source_saved':False}