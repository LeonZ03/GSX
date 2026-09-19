"""Explicit r19 -> fairing-tip candidate; canonical controls remain untouched."""
from pathlib import Path
import bpy, json, sys, copy
from mathutils import Vector

V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V / 'scripts'))
from build_gray import cage_faces, apply_creases

def main():
    scene = bpy.context.scene
    if Path(bpy.data.filepath).name != '19_gray_review.blend':
        raise RuntimeError('Use the preserved r19 baseline only')
    output = V / 'blends/20_fairing_candidate.blend'
    if output.exists():
        raise FileExistsError(output)
    data = json.loads((V / 'data/archive/r19/Body_SideFairing.json').read_text(encoding='utf8'))
    observations = json.loads((V / 'qa/stage_b_tip_r20/tip.local.json').read_text(encoding='utf8'))
    rows = copy.deepcopy(data['grid'])
    old = Vector(rows[4][-1]); delta = Vector(observations['point_mm']) - old
    for j, row in enumerate(rows):
        longitudinal = {3: .15, 4: 1., 5: .15}.get(j, 0.)
        for i, p in enumerate(row):
            transverse = [0., 0., .01, .08, .3, .88, 1.][i]
            row[i] = list(Vector(p) + delta * longitudinal * transverse)
    # Support the photographed angular termination; preserve the top rail.
    def between(a, b, t):
        return [list(Vector(x).lerp(Vector(y), t)) for x,y in zip(a,b)]
    data['grid'] = rows[:4] + [between(rows[3],rows[4],.88), rows[4], between(rows[4],rows[5],.12)] + rows[5:]
    data['revision'] = 'r20_candidate'
    data['status'] = 'CANDIDATE_NOT_PHOTO_ACCEPTED'
    data['notes'] += ' Local angular blade-tip candidate: three approximate visible tip observations, fixed cameras, two added support rows. No independent validation.'
    data['crease_boundary'] = .85
    data.update(solidify_mode='NON_MANIFOLD',use_even_offset=True,thickness_clamp=.5,use_thickness_angle_clamp=True)
    obj = scene.objects.get(data['name'])
    oldmesh = obj.data
    mesh = bpy.data.meshes.new('Body_SideFairing_Control_r20')
    mesh.from_pydata([[v*.001 for v in p] for row in data['grid'] for p in row], [], cage_faces(data))
    mesh.update()
    for mat in oldmesh.materials: mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    obj.data = mesh
    apply_creases(obj, data)
    solid=next(m for m in obj.modifiers if m.type=='SOLIDIFY')
    solid.solidify_mode='NON_MANIFOLD';solid.use_even_offset=True;solid.thickness_clamp=.5;solid.use_thickness_angle_clamp=True
    scene['revision']='r20_candidate';scene['visual_acceptance']='NOT_PASSED'
    (V/'qa/stage_b_tip_r20/Body_SideFairing.json').write_text(json.dumps(data,indent=2),encoding='utf8')
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    return {'candidate':str(output),'changed_object':obj.name,'control_vertices':len(mesh.vertices),'old_tip_mm':list(old),'tip_mm':observations['point_mm'],'status':'UNACCEPTED_CANDIDATE'}

if __name__ == '__main__':result=main()
