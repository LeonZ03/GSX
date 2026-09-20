"""Evidence-led r45 tank control edit for the mirrored 10x8 half grid."""
from __future__ import annotations
import copy, json
from pathlib import Path
from typing import Any, Dict, Optional
ROOT=Path(__file__).resolve().parents[1]; BASIS=ROOT/"data/current_controls/r39_shape_basis.json"
ROW_PROFILE={0:(0,0,0,0,0,0),1:(0,0,0,0,0,0),2:(4,5,5,1,1.5,.5),3:(8,9,11,2.5,3,1),4:(10,10,14,4,4,1.5),5:(10,8,16,5,5,2),6:(7,5,14,4,5,2),7:(4,2,9,2,3,1),8:(0,0,0,0,0,0),9:(0,0,0,0,0,0)}
SHOULDER_COL={0:0,1:.20,2:1,3:.75,4:.20,5:0,6:0,7:0}; HOLLOW_COL={0:0,1:0,2:.05,3:.35,4:.90,5:1,6:.30,7:0}; GROOVE_COL={0:0,1:0,2:0,3:0,4:.20,5:.85,6:1,7:0}
def _load_basis(path:Path=BASIS)->Dict[str,Any]:
 data=json.loads(path.read_text(encoding="utf-8")); body=data.get("Body_Tank",data)
 if body.get("mirror_x") is not True: raise ValueError("Body_Tank must be mirrored positive-X half")
 grid=body.get("grid")
 if len(grid)!=10 or any(len(r)!=8 for r in grid): raise ValueError("expected 10x8 Body_Tank grid")
 return body
def build_grid(source:Optional[Path]=None):
 body=_load_basis(source or BASIS); grid=copy.deepcopy(body["grid"]); changes=[]
 for ri,row in enumerate(grid):
  sr,sz,hr,hz,gr,gz=ROW_PROFILE[ri]
  for ci,p in enumerate(row):
   if ci in (0,7): continue
   sw,hw,gw=SHOULDER_COL[ci],HOLLOW_COL[ci],GROOVE_COL[ci]; dx=sr*sw-hr*hw-gr*gw; dz=sz*sw-hz*hw-gz*gw
   if abs(dx)+abs(dz)>1e-9: p[0]=round(p[0]+dx,6); p[2]=round(p[2]+dz,6); changes.append({"row":ri,"col":ci,"dx_mm":round(dx,3),"dz_mm":round(dz,3)})
 return grid,{"revision":"r45_tank_product_reference","basis":"r39_shape_basis.json","grid_shape":[10,8],"mirror_x":True,"changed_points":len(changes),"changes":changes,"protected":["columns 0 and 7 centreline closures","rows 0,1,8,9 end interfaces","all Y coordinates, fuel-cap and seat interface objects"],"evidence":["local product tank photo 20260920","owner IMG65","owner IMG62","owner IMG69"],"uncertainty":"proportional shape controls; no physical measurements inferred"}
def apply(*,tank_obj:Any=None,bpy_module:Any=None,write_path:Optional[str]=None,dry_run:bool=True):
 grid,report=build_grid()
 if write_path:
  out=Path(write_path); out.parent.mkdir(parents=True,exist_ok=True); body=_load_basis(); body["grid"]=grid; body["revision"]="r45_tank_product_reference"; body["source_basis"]="r39_shape_basis.json"; body["notes"]="Product-photo shoulder/knee/lower-groove control; acceptance pending multiview review."; out.write_text(json.dumps(body,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); report["derived_control_path"]=str(out)
 if not dry_run:
  if tank_obj is None: raise ValueError("tank_obj required when dry_run=False")
  verts=getattr(getattr(tank_obj,"data",tank_obj),"vertices",None)
  if verts is None or len(verts)!=80: raise ValueError("expected 80-vertex Body_Tank control mesh")
  for i,p in enumerate(p for row in grid for p in row): verts[i].co.x,verts[i].co.y,verts[i].co.z=p[0]*.001,p[1]*.001,p[2]*.001
  tank_obj.data.update(); report["applied_to_object"]=getattr(tank_obj,"name","<unnamed>")
 report["dry_run"]=dry_run; return report
if __name__=="__main__": print(json.dumps(apply(),indent=2,ensure_ascii=False))


def apply_supported(scene=None):
    """Integrate photo-led cross sections and support bands into current tank."""
    import bpy,sys
    from mathutils import Vector
    sys.path.insert(0,str(ROOT/'scripts'))
    from rebuild_owner_shapes import get,put
    import build_gray as bg
    scene=scene or bpy.context.scene
    obj=scene.objects['Body_Tank']
    if len(obj.data.vertices)!=80: raise ValueError('Requires r45 80-point tank; do not replay on refined source')
    before=copy.deepcopy(_load_basis())
    before['grid']=[[list(v.co*1000) for v in obj.data.vertices[i:i+8]] for i in range(0,80,8)]
    grid,report=build_grid()
    # Actual current cap-centre/crown points, not a bbox-derived protection mask.
    for i,row in enumerate(grid):
        row[0]=before['grid'][i][0][:];row[1]=before['grid'][i][1][:]
    out=[]
    for i,row in enumerate(grid):
        weight=[0,0,.20,.75,1,1,.65,.20,0,0][i]
        a,b=Vector(row[4]),Vector(row[5]);c=Vector(row[6])
        # Mid-flank bowl below the shoulder. Two added rings resolve curvature
        # separately from the top ridge and the lower pressed lip.
        mid1=a.lerp(b,.36);mid1.x-=15*weight
        mid2=a.lerp(b,.73);mid2.x-=12*weight
        lip1=b.lerp(c,.25);lip1.x-=4*weight
        lip2=b.lerp(c,.62);lip2.x+=3*weight
        out.append(row[:5]+[list(mid1),list(mid2),row[5],list(lip1),list(lip2)]+row[6:])
    before['grid']=out;before['crease_columns']={'2':.18,'3':.45,'4':.42,'7':.38,'8':.18,'9':.25}
    before['faces']=bg.cage_faces(before)
    obj=put(scene,before)
    # The pre-existing saddle clearance Boolean also creates a disconnected
    # closed chip below the rear tip. Keep the dominant shell after Booleans.
    from prune_geometry_islands import apply as keep_main
    keep_main(obj,'Tank_MainShellOnly')
    obj['product_reference_refinement']='r46 shoulder ridge / knee bowl / low pressed groove; inferred dimensions'
    report.update(grid_shape=[10,12],cap_centre_control_unchanged=True,source='r39 envelope with protected r45 cap region',acceptance='NOT_PASSED')
    target=ROOT/'data/current_controls/tank_product_reference_r45.json'
    target.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
