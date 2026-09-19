"""Independent r29 exhaust candidate for the GSX250R gray scene.

The public entry point is ``apply(scene)``.  It mutates only the supplied
candidate scene and never saves it.  Coordinates at this module boundary are
millimetres; Blender scene coordinates are metres.  The muffler is a closed
quad-section loft and the heat shield is a separate, rolled shell with open
ends and hardware.  This is a provisional photo-shaped candidate, not a
measurement claim.
"""
import math
import bpy
import bmesh
from mathutils import Vector

MM = 0.001
AXIS_A = Vector((242.0, -340.0, 278.0))
AXIS_B = Vector((251.0, -819.0, 496.0))
_COL = None
_MATS = {}

# Given muffler envelope, retained as the single source for loft and shield clearance.
MUFFLER_STATIONS = ((0.00,32.0,36.0,0.015),(0.12,61.0,69.0,0.030),(0.38,66.0,79.0,0.045),(0.78,68.0,82.0,0.055),(1.00,56.0,67.0,0.020))


def _v(p):
    return Vector(p) * MM


def _collection(scene):
    global _COL
    _COL = bpy.data.collections.get("Collection_Engine")
    if _COL is None:
        _COL = bpy.data.collections.new("Collection_Engine")
        scene.collection.children.link(_COL)
    return _COL


def _materials():
    # Reuse the scene's existing gray-stage materials; never invent final
    # paint or decals in this candidate.
    sources = {
        "black": "Body_TankSideTrim", "gun": "Engine_Crankcase",
        "silver": "Exhaust_HeatShield", "steel": "BrakeDisc_Front",
        "rubber": "Tire_Front",
    }
    for key, name in sources.items():
        o = bpy.data.objects.get(name)
        if o and getattr(o.data, "materials", None):
            _MATS[key] = o.data.materials[0]
    if "silver" not in _MATS:
        _MATS["silver"] = _MATS.get("steel")
    if "gun" not in _MATS:
        _MATS["gun"] = _MATS.get("black")


def _link(o, name, material=None):
    o.name = name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    _COL.objects.link(o)
    if material and hasattr(o.data, "materials") and _MATS.get(material):
        o.data.materials.append(_MATS[material])
    o["stage_c_owner"] = "rebuild_exhaust_r29"
    o["units"] = "millimetres_input_metres_scene"
    return o


def _mesh(name, verts, faces, material, smooth=False, bevel=0.0):
    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata([_v(p) for p in verts], [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    o = _link(bpy.data.objects.new(name, me), name, material)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        mod = o.modifiers.new("r29_small_edge_radius", "BEVEL")
        mod.width = bevel * MM
        mod.segments = 2
    return o


def _rod(name, a, b, radius, material, sides=20):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius * MM,
                                        depth=d.length * MM,
                                        location=_v((a + b) * 0.5))
    o = _link(bpy.context.object, name, material)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def _basis():
    axis = (AXIS_B - AXIS_A).normalized()
    u = Vector((1.0, 0.0, 0.0))
    v = axis.cross(u).normalized()
    return axis, u, v


def _centre(t):
    return AXIS_A.lerp(AXIS_B, t)


def _muffler_section(t):
    """Linear section interpolation including the loft harmonic bias."""
    if t <= MUFFLER_STATIONS[0][0]: return MUFFLER_STATIONS[0][1:]
    if t >= MUFFLER_STATIONS[-1][0]: return MUFFLER_STATIONS[-1][1:]
    for a,b in zip(MUFFLER_STATIONS, MUFFLER_STATIONS[1:]):
        if a[0] <= t <= b[0]:
            f=(t-a[0])/(b[0]-a[0])
            return tuple(x+(y-x)*f for x,y in zip(a[1:],b[1:]))
    raise ValueError("section interpolation failed")
def _section_loft(name, stations, material, n=12):
    """Closed loft with quad side faces and n-gon end caps.

    Each station is (t, half-width-X, half-height, shape-bias).  The mild
    third-harmonic bias gives the black can its visibly asymmetric cast shape.
    """
    axis, u, v = _basis()
    verts = []
    for t, rx, rz, bias in stations:
        c = _centre(t)
        for k in range(n):
            q = 2.0 * math.pi * k / n
            # Slightly flattened lower/front quadrant; dimensions remain near
            # the supplied source envelope rather than being reinterpreted.
            radial = 1.0 + bias * math.sin(q) + 0.018 * math.cos(2.0 * q)
            verts.append(c + u * (rx * radial * math.cos(q))
                         + v * (rz * radial * math.sin(q)))
    faces = [tuple(reversed(range(n)))]
    for j in range(len(stations) - 1):
        for k in range(n):
            faces.append((j*n+k, j*n+(k+1) % n,
                          (j+1)*n+(k+1) % n, (j+1)*n+k))
    last = (len(stations) - 1) * n
    faces.append(tuple(last + k for k in range(n)))
    return _mesh(name, verts, faces, material, smooth=True, bevel=1.2)


def _shield_shell(name, stations, material):
    """A real wrap shell: outer/inner quad strips plus rolled side rims.

    Angles are around the can section.  The changing arc centre makes the
    shield sweep from rear upper side toward the forward lower side.
    """
    axis, u, v = _basis()
    n = 20
    outer, inner = [], []
    samples = []
    # Densify between the five control stations while retaining their angle domains.
    for si in range(len(stations)-1):
        a, b = stations[si], stations[si+1]
        for j in range(8):
            f = j / 8.0
            samples.append(tuple(a[k] + (b[k]-a[k])*f for k in range(5)))
    samples.append(stations[-1])
    for t, rx_hint, rz_hint, amin, amax in samples:
        c = _centre(t)
        if 0.0 <= t <= 1.0:
            rx, rz, bias = _muffler_section(t)
        else:
            # The forward t<0 taper is outside the can loft and remains an
            # explicitly approximate reference continuation.
            rx, rz, bias = rx_hint, rz_hint, 0.0
        for k in range(n):
            q = amin + (amax - amin) * k / (n - 1)
            radial = 1.0 + bias * math.sin(q) + 0.018 * math.cos(2.0*q)
            # Offsets are divided by radial so the vector clearance is exact
            # at every angle, despite the harmonic section shape.
            inner_d = 3.0 / radial
            outer_d = 5.8 / radial
            outer.append(c + u * ((rx + outer_d) * radial * math.cos(q))
                         + v * ((rz + outer_d) * radial * math.sin(q)))
            inner.append(c + u * ((rx + inner_d) * radial * math.cos(q))
                         + v * ((rz + inner_d) * radial * math.sin(q)))
    verts = outer + inner
    count = len(outer)
    faces = []
    for j in range(len(samples) - 1):
        for k in range(n - 1):
            a = j*n+k; b = a+1; c = (j+1)*n+k+1; d = (j+1)*n+k
            faces.append((a, b, c, d))
            faces.append((count+d, count+c, count+b, count+a))
    # Rolled return edges at both longitudinal ends and along the arc ends.
    for j in [0, len(samples)-1]:
        for k in range(n-1):
            a=j*n+k; b=a+1; faces.append((a, count+a, count+b, b))
    for j in range(len(samples)-1):
        for k in [0, n-1]:
            a=j*n+k; b=(j+1)*n+k; faces.append((a, b, count+b, count+a))
    o = _mesh(name, verts, faces, material, smooth=True, bevel=0.7)
    o["shield_construction"] = "separate wrapped shell with rolled returns"
    o["clearance_mm_nominal"] = 3.0
    o["outer_shell_offset_mm"] = 5.8
    return o


def _remove_old(scene):
    prefixes = ("Exhaust_Muffler", "Exhaust_EndCap", "Exhaust_Outlet",
                "Exhaust_HeatShield", "HeatShieldBolt", "HeatShieldStandoff", "HeatShieldBand")
    for o in list(scene.objects):
        if o.name.startswith(prefixes):
            bpy.data.objects.remove(o, do_unlink=True)



def _ring_mesh(name, start, end, ro, ri, material):
    axis, u, v = _basis(); n=24; verts=[]
    for c, r in ((start, ro), (end, ro), (end, ri), (start, ri)):
        for k in range(n):
            q=2*math.pi*k/n; verts.append(Vector(c)+u*(r*math.cos(q))+v*(r*math.sin(q)))
    faces=[]
    # Outer wall, outlet annulus, inner wall, inlet annulus.
    for k in range(n):
        kn=(k+1)%n
        faces.append((k,kn,n+kn,n+k))
        faces.append((n+k,n+kn,2*n+kn,2*n+k))
        faces.append((2*n+k,2*n+kn,3*n+kn,3*n+k))
        faces.append((3*n+k,3*n+kn,kn,k))
    return _mesh(name, verts, faces, material, smooth=True, bevel=.5)

def _hollow_outlet(name, start, end, ro, ri, material):
    return _ring_mesh(name, start, end, ro, ri, material)

def _annular_endcap(name, material):
    axis,u,v=_basis(); n=24; verts=[]
    stations=[(.955,60,72),(1.0,58,69),(1.035,53,63)]
    for t,rx,rz in stations:
        c=_centre(t)
        for k in range(n):
            q=2*math.pi*k/n; verts.append(c+u*(rx*math.cos(q))+v*(rz*math.sin(q)))
    c=_centre(1.035)+axis*1.0
    for k in range(n):
        q=2*math.pi*k/n; verts.append(c+u*(22*math.cos(q))+v*(27*math.sin(q)))
    c2=_centre(0.985)
    for k in range(n):
        q=2*math.pi*k/n; verts.append(c2+u*(22*math.cos(q))+v*(27*math.sin(q)))
    faces=[]
    for j in range(2):
        for k in range(n):
            kn=(k+1)%n; faces.append((j*n+k,j*n+kn,(j+1)*n+kn,(j+1)*n+k))
    for k in range(n):
        kn=(k+1)%n; faces.append((2*n+k,2*n+kn,3*n+kn,3*n+k))
        faces.append((3*n+k,3*n+kn,4*n+kn,4*n+k))
    faces.append(tuple(reversed([4*n+k for k in range(n)])))
    faces.append(tuple(reversed([k for k in range(n)])))
    return _mesh(name, verts, faces, material, smooth=True, bevel=.7)
def _build_exhaust(scene):
    # Retain the given envelope: t=.12 and .78 carry the largest section.
    _section_loft("Exhaust_Muffler", MUFFLER_STATIONS, "gun")

    axis, u, v = _basis()
    # Separate spun rear cap, with a shoulder and a shallow outlet recess.
    _annular_endcap("Exhaust_EndCap", "silver")
    outlet_c = _centre(1.035) + axis * 9.0
    outlet_a = outlet_c - axis * 7.0
    outlet_b = outlet_c + axis * 7.0
    _hollow_outlet("Exhaust_Outlet", outlet_a, outlet_b, 23.0, 19.0, "gun")
    _hollow_outlet("Exhaust_Outlet_Lip", outlet_b-axis*2.0, outlet_b+axis*3.0, 27.0, 22.0, "silver")

    # The visible right-side shield wraps the can and tapers toward the
    # collector/front.  It is intentionally not one planar polygon.
    shield = _shield_shell("Exhaust_HeatShield", [
        (-0.06, 26, 28, math.radians(-35), math.radians(-8)),
        (0.08, 50, 52, math.radians(-65), math.radians(15)),
        (0.35, 65, 77, math.radians(-45), math.radians(65)),
        (0.62, 67, 80, math.radians(-5), math.radians(95)),
        (0.88, 63, 74, math.radians(30), math.radians(100)),
    ], "silver")
    shield["photo_shape_basis"] = "provisional supplied right-side silhouette guidance"
    shield["accuracy_status"] = "candidate_requires_render_review"
    shield["parameter_min_inner_clearance_mm"] = 3.0

    # One visible forward fastener; its stand-off follows the local shell normal.
    t=0.22; q=math.radians(-25.0); c=_centre(t); nrm=(u*math.cos(q)+v*math.sin(q)).normalized()
    rx,rz,bias=_muffler_section(t); radial=1.0+bias*math.sin(q)+0.018*math.cos(2.0*q); outer_d=5.8/radial; p=c+u*((rx+outer_d)*radial*math.cos(q))+v*((rz+outer_d)*radial*math.sin(q)); pin=p-nrm*7.0
    _rod("HeatShieldBolt_01", pin, p+nrm*4.0, 4.5, "steel", 12)
    _rod("HeatShieldStandoff_01", pin-nrm*4.0, pin, 6.0, "gun", 12)




def apply(scene):
    """Replace only the r29 exhaust candidate objects in ``scene``."""
    if scene is None:
        raise ValueError("apply(scene) requires a Blender scene")
    if scene.get("revision") != "r28":
        raise ValueError("Requires isolated r28 candidate scene")
    if scene.get("exhaust_r29_status"):
        raise ValueError("Refusing to replay an existing exhaust_r29 candidate")
    for window in bpy.context.window_manager.windows:
        window.scene = scene
        break
    _collection(scene)
    _materials()
    _remove_old(scene)
    _build_exhaust(scene)
    scene["exhaust_r29_status"] = "PROVISIONAL_CANDIDATE_NOT_PASSED"
    scene["exhaust_r29_kept_upstream"] = "headers_collector_engine_frame_cameras"
    scene["exhaust_r29_geometry_basis"] = "given centerline and envelope radii"
    bpy.context.view_layer.update()
    return [o for o in scene.objects if o.get("stage_c_owner") == "rebuild_exhaust_r29"]
