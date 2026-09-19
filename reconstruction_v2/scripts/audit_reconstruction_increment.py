"""Read-only local geometry, source protection and fit-control checks."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils.bvhtree import BVHTree
V=Path(__file__).resolve().parents[1];sys.path.insert(0,str(V/'scripts'))
from audit_stage_bc import signature,cap_wall_vertex_contact

def audit(scene):
 dg=bpy.context.evaluated_depsgraph_get();trees={};quality={}
 targets=[o for o in scene.objects if o.type in ('MESH','CURVE') and o.name.startswith(('Mirror','Windscreen','Body_FrameSidePanel','Body_MidSideCover','Engine_SprocketCover','Shock_','ShockMount_','RearShock_','Rearset_','Footpeg_','BrakePedal_','BrakeMaster_Rear','ShiftLever_','ShiftLink_','GuardMount_Rear','GuardMount_Bolt_rear_mount'))]
 def tree(o):
  ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();verts=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(f.vertices) for f in me.loop_triangles];bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True);return ev,me,verts,faces,bvh
 for o in targets:
  ev,me,v,f,bvh=tree(o);bm=bmesh.new();bm.from_mesh(me);pairs=[(a,b) for a,b in bvh.overlap(bvh) if a<b and not set(f[a]).intersection(f[b])];contact=sum(cap_wall_vertex_contact(a,b,v,f) for a,b in pairs)
  quality[o.name]={'verts':len(v),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(p.area<1e-13 for p in me.polygons),'self_candidates':len(pairs)-contact,'raw_self_pairs':len(pairs)};trees[o.name]=bvh;bm.free();ev.to_mesh_clear()
 for n in ['Frame_Main_L','Frame_Main_R','Frame_SeatRail_L','Frame_SeatRail_R','Swingarm_L','Swingarm_R','Engine_AlternatorCover','Engine_Crankcase','Seat_Rider','Body_SeatSide','Tire_Rear','Exhaust_Muffler']:
  if n in scene.objects:
   ev,me,v,f,bvh=tree(scene.objects[n]);trees[n]=bvh;ev.to_mesh_clear()
 panel='Body_MidSideCover' if scene.get('stage_b_mid_cover_replaced') else 'Body_FrameSidePanel'
 pairs=[(panel,n) for n in ['Frame_Main_L','Frame_Main_R','Body_SeatSide','Engine_AlternatorCover']]+[('Engine_SprocketCover',n) for n in ['Engine_AlternatorCover','Engine_Crankcase']]+[('RearShock_Spring',n) for n in ['Tire_Rear','Seat_Rider',panel]]+[('ShockMount_UpperCrossmember',n) for n in ['Frame_SeatRail_L','Frame_SeatRail_R']]+[('ShockMount_LowerCrossmember',n) for n in ['Swingarm_L','Swingarm_R']]
 overlaps={a+' / '+b:len(trees[a].overlap(trees[b])) for a,b in pairs if a in trees and b in trees}
 sync={}
 for o in scene.objects:
  if not o.get('control_cage_source'):continue
  p=V/'data/control_cages'/ (o.name+'.json')
  # Canonical controls are synchronized for accepted local r24 geometry.

  a=json.loads(p.read_text());pts=[p for row in a['grid'] for p in row]
  sync[o.name]={'vertices_match':len(pts)==len(o.data.vertices),'max_mm':max((v.co-__import__('mathutils').Vector(p)*.001).length*1000 for v,p in zip(o.data.vertices,pts))}
 source=bpy.data.filepath;revision=scene.get('revision');now={o.name:signature(o) for o in scene.objects};newnames=set(now)
 expected={'Windscreen','Mirror_L','Mirror_R','Mirror_Stem_L','Mirror_Stem_R','Shock_Piston','Shock_Body','RearShock_Spring'}
 if scene.get('stage_b_mid_cover_replaced'):expected.add('Body_MidSideCover')
 if scene.get('stage_c_rearsets_rebuilt'):
  expected.update(n for n in now if n.startswith(('Rearset_','Footpeg_','GuardMount_Rear','GuardMount_Bolt_rear_mount')))
  # Old numbered ridge proxies are intentionally removed by the replacement.
  expected.update('Footpeg_Ridge_'+side+suffix for side in ('L','R') for suffix in ['']+[f'.{j:03}' for j in range(1,9)])
 bpy.ops.wm.open_mainfile(filepath=str(V/'blends/20_gray_review.blend'));old={o.name:signature(o) for o in bpy.context.scene.objects};changes=[n for n in old if old[n]!=now.get(n)];unexpected=[n for n in changes if n not in expected]
 report={'source':source,'revision':revision,'stage_B':'NOT_PASSED','stage_C':'NOT_PASSED','quality':quality,'surface_intersections':overlaps,'control_sync':sync,'changed_old_objects':changes,'unexpected_old_changes':unexpected,'added_objects':sorted(newnames-set(old)),'note':'Mating crossmember/frame intersections are intentional. Other overlaps require review; zero surface intersections is not volumetric collision proof.'}
 (V/f'qa/increment_{revision}.json').write_text(json.dumps(report,indent=2));return report

if __name__=='__main__':result=audit(bpy.context.scene)
