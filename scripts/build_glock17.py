"""
Glock 17 Gen4 - procedural Blender model (mid-poly, < 30k triangles).

Run with Blender 4.2+ :   blender -b -P scripts/build_glock17.py -- [options]
or with the bpy module:   python scripts/build_glock17.py [options]
  (pip install "bpy==4.5.*"  - requires Python 3.11)

Options:
  --no-render       only build the model, save the .blend and export
  --quick           low resolution / low sample preview renders (no export)
  --views=a,b,...   render only the listed views (see VIEWS)

Outputs (repository root):
  glock17_gen4.blend, glock17_gen4.glb, glock17_gen4.fbx, renders/*.png
Textures are read from textures/ (generate them with make_textures.py).
"""
import json
import math
import os
import sys

import bpy  # must come first: the bpy module provides bmesh and mathutils
import bmesh
from mathutils import Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glock_data as G  # noqa: E402

ROOT = os.path.dirname(HERE)
TEX_DIR = os.path.join(ROOT, "textures")
RENDER_DIR = os.path.join(ROOT, "renders")

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
QUICK = "--quick" in ARGS
NO_RENDER = "--no-render" in ARGS


def _arg(name, default):
    for a in ARGS:
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return default


ONLY_VIEWS = _arg("--views", "")


# ==========================================================================
# Generic helpers
# ==========================================================================
def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def obj_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def apply_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg),
                                         preserve_all_data_layers=True,
                                         depsgraph=dg)
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    me.name = ob.name
    if old.users == 0:
        bpy.data.meshes.remove(old)


def prism(poly, axis, a0, a1, bm=None):
    """Extrude a closed 2D polygon along an axis.

    poly coordinates are (Y, Z) for axis X, (X, Z) for axis Y, (X, Y) for Z."""
    bm = bm or bmesh.new()

    def P(u, v, a):
        if axis == "X":
            return (a, u, v)
        if axis == "Y":
            return (u, a, v)
        return (u, v, a)

    va = [bm.verts.new(P(u, v, a0)) for u, v in poly]
    vb = [bm.verts.new(P(u, v, a1)) for u, v in poly]
    n = len(poly)
    faces = [bm.faces.new((va[i], va[(i + 1) % n], vb[(i + 1) % n], vb[i]))
             for i in range(n)]
    faces.append(bm.faces.new(va[::-1]))
    faces.append(bm.faces.new(vb))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def rrect(x0, x1, y0, y1, r=0.0, seg90=4):
    return G.rounded_poly([(x0, y0, r), (x1, y0, r), (x1, y1, r), (x0, y1, r)],
                          seg90)


def circle(cx, cy, r, n=16):
    return [(cx + r * math.cos(2 * math.pi * k / n),
             cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def curve_solid(name, loops_xz, half_width, bevel, res=2, y_center=0.0):
    """Outline(s) in the XZ plane extruded symmetrically along Y with rounded
    edges (Blender 2D curve with fill, extrude and bevel)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    for loop in loops_xz:
        sp = cu.splines.new("POLY")
        sp.points.add(len(loop) - 1)
        for p, (x, z) in zip(sp.points, loop):
            p.co = (x, z, 0.0, 1.0)
        sp.use_cyclic_u = True
    cu.extrude = max(half_width - bevel, 0.0)
    cu.bevel_depth = bevel
    cu.bevel_resolution = res
    cu.offset = -bevel
    tmp = link(bpy.data.objects.new(name + "_tmp", cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    me.transform(Matrix(((1, 0, 0, 0), (0, 0, -1, y_center),
                         (0, 1, 0, 0), (0, 0, 0, 1))))
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm(name, bm)
    ob["flat_axis"] = "Y"
    return ob


def lathe(profile, seg=16, bm=None):
    """Solid of revolution around the X axis; profile = [(x, r), ...] that
    starts and ends on the axis (r = 0)."""
    bm = bm or bmesh.new()
    rings = []
    for x, r in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((x, 0.0, 0.0))])
            continue
        rings.append([bm.verts.new((x, r * math.cos(2 * math.pi * k / seg),
                                    r * math.sin(2 * math.pi * k / seg)))
                      for k in range(seg)])
    faces = []
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(seg):
            k1 = (k + 1) % seg
            if len(a) == 1:
                faces.append(bm.faces.new((a[0], b[k1], b[k])))
            elif len(b) == 1:
                faces.append(bm.faces.new((a[k], a[k1], b[0])))
            else:
                faces.append(bm.faces.new((a[k], a[k1], b[k1], b[k])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def tube_along(name, path, radius, res=2):
    """Round tube following a 3D polyline (curve with circular bevel)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(path) - 1)
    for p, co in zip(sp.points, path):
        p.co = (*co, 1.0)
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    tmp = link(bpy.data.objects.new(name + "_tmp", cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)   # weld end caps
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm)


def boolean(target, cutter_bm, op="DIFFERENCE", self_overlap=False):
    cutter = obj_from_bm(target.name + "_cutter", cutter_bm)
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    m.use_self = self_overlap
    apply_modifiers(target)
    bpy.data.objects.remove(cutter)


def mag_loft(levels, uv=None):
    """Slanted prism with the magazine section; levels = [(z, grow), ...]
    from the bottom up (grow = clearance / flare in mm)."""
    bm = bmesh.new()
    rings = [[bm.verts.new((x, y, z)) for x, y in G.mag_section(z, grow)]
             for z, grow in levels]
    n = len(rings[0])
    faces = [bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
             for a, b in zip(rings[:-1], rings[1:]) for k in range(n)]
    faces += [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if uv is not None:                      # UVs handed to the new faces
        lay = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            for loop in f.loops:
                loop[lay].uv = uv
    return bm


def magwell_cutter(z0, z1, flare=0.0, flare_z=None, uv=None):
    """Magazine well (magazine section + clearance) from z0 up to z1; with
    flare, the mouth below flare_z is widened by `flare` mm."""
    c = G.MAG_WELL_CLEAR
    levels = [(z0, c), (z1, c)]
    if flare:
        levels = [(z0, c + flare), (flare_z, c + flare), (flare_z + 2.8, c),
                  (z1, c)]
    return mag_loft(levels, uv)


def bevel_mod(ob, width, segments=2, angle=35.0, limit="ANGLE"):
    m = ob.modifiers.new("bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = limit
    m.angle_limit = math.radians(angle)
    m.profile = 0.5
    m.miter_outer = "MITER_ARC"
    m.harden_normals = False
    return m


def join(objs, name):
    objs = [o for o in objs if o is not None]
    with bpy.context.temp_override(active_object=objs[0], object=objs[0],
                                   selected_objects=objs,
                                   selected_editable_objects=objs):
        bpy.ops.object.join()
    objs[0].name = name
    objs[0].data.name = name
    return objs[0]


def set_material(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


def harden_normals(ob, min_area=2.0, min_width=1.5, flat_deg=0.3):
    """Hard-surface custom normals.

    Flat regions get their exact plane normal, and faces touching exactly one
    such region (the first row of a bevel) take that normal at the shared
    corners.  This removes the shading streaks that long thin cap triangles
    show when their corner normals are averaged with the bevel next to them.

    Flat regions are wide coplanar regions (area >= min_area mm2, width >=
    min_width mm) and, when ob["flat_axis"] is set, every face perpendicular
    to that axis (the caps of extruded profiles).  ob["flat_width"] = False
    disables the width rule (the lofted grip must stay smooth)."""
    axis = ob.get("flat_axis")
    use_width = ob.get("flat_width", True)
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    nf = len(bm.faces)
    region = [-1] * nf
    rnorm, flat_region = [], []
    cos_t = math.cos(math.radians(flat_deg))
    for f in bm.faces:
        if region[f.index] >= 0:
            continue
        rid = len(rnorm)
        region[f.index] = rid
        n0 = f.normal.copy()
        stack, area = [f], 0.0
        lo = Vector((1e9, 1e9, 1e9))
        hi = Vector((-1e9, -1e9, -1e9))
        while stack:
            g = stack.pop()
            area += g.calc_area()
            for v in g.verts:
                for i in range(3):
                    lo[i] = min(lo[i], v.co[i])
                    hi[i] = max(hi[i], v.co[i])
            for e in g.edges:
                for h in e.link_faces:
                    if region[h.index] < 0 and h.normal.dot(n0) > cos_t:
                        region[h.index] = rid
                        stack.append(h)
        diag = max((hi - lo).length, 1e-6)
        rnorm.append(n0)
        is_flat = use_width and area >= min_area and area / diag >= min_width
        if axis and abs(n0["XYZ".index(axis)]) > 0.99995:
            is_flat = True
        flat_region.append(is_flat)
    flat = [flat_region[region[i]] for i in range(nf)]
    normals = [(0.0, 0.0, 0.0)] * len(me.loops)       # zero = automatic normal
    for poly, f in zip(me.polygons, bm.faces):
        for li, loop in zip(poly.loop_indices, f.loops):
            if flat[f.index]:
                normals[li] = tuple(rnorm[region[f.index]])
                continue
            cands = {region[g.index] for g in loop.vert.link_faces
                     if flat[g.index] and rnorm[region[g.index]].dot(f.normal) > 0.5}
            if len(cands) == 1:
                normals[li] = tuple(rnorm[cands.pop()])
    bm.free()
    me.normals_split_custom_set(normals)


def finish_shading(ob, angle=32.0, harden=True):
    me = ob.data
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(angle))
    if harden:
        harden_normals(ob)


def ensure_uv(ob, name="UVMap"):
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name=name)
    me.uv_layers[0].name = name


# ==========================================================================
# Materials
# ==========================================================================
def tex_path(name):
    p = os.path.join(TEX_DIR, name)
    return p if os.path.exists(p) else None


def principled(name, color, metallic, rough, spec=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = spec
    mat.diffuse_color = (*color, 1.0)
    return mat


def add_image(nt, path, colorspace, loc):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = img
    node.location = loc
    return node


def add_normal_map(mat, path, strength=1.0):
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = add_image(nt, path, "Non-Color", (-700, -300))
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.location = (-350, -300)
    nm.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])


def add_micro_bump(mat, scale, strength):
    """Fine procedural stipple (Blender render only)."""
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    if bsdf.inputs["Normal"].is_linked:
        return
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, -500)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-650, -500)
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 2.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-350, -500)
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.0001
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def make_materials():
    M = {}
    M["slide"] = principled("Slide_Nitride", (0.16, 0.16, 0.168), 1.0, 0.4)
    M["slide_marked"] = principled("Slide_Nitride_Markings",
                                   (0.16, 0.16, 0.168), 1.0, 0.4)
    M["barrel"] = principled("Barrel_Nitride", (0.09, 0.09, 0.095), 1.0, 0.26)
    M["steel"] = principled("Steel_Black", (0.07, 0.07, 0.075), 1.0, 0.38)
    M["polymer"] = principled("Polymer_Frame", (0.04, 0.04, 0.042), 0.0,
                              0.55, spec=0.5)
    M["grip"] = principled("Polymer_Grip_RTF", (0.044, 0.044, 0.046), 0.0,
                           0.6, spec=0.5)
    M["white"] = principled("Sight_White", (0.82, 0.82, 0.8), 0.0, 0.5)
    M["plate"] = principled("Serial_Plate", (0.55, 0.55, 0.55), 1.0, 0.35)
    M["bore"] = principled("Bore_Dark", (0.01, 0.01, 0.01), 1.0, 0.6)
    M["brass"] = principled("Brass_Case", (0.80, 0.55, 0.20), 1.0, 0.27)
    M["copper"] = principled("Copper_Jacket", (0.84, 0.40, 0.24), 1.0, 0.3)
    fl = principled("Muzzle_Flash", (1.0, 0.5, 0.12), 0.0, 1.0)
    bsdf = fl.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.45, 0.1, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 6.0
    fl.use_backface_culling = False
    M["flash"] = fl

    p = tex_path("slide_markings_normal.png")
    if p:
        add_normal_map(M["slide_marked"], p, 1.0)
    p = tex_path("slide_markings_color.png")
    if p:
        nt = M["slide_marked"].node_tree
        tex = add_image(nt, p, "sRGB", (-700, 200))
        nt.links.new(tex.outputs["Color"],
                     nt.nodes["Principled BSDF"].inputs["Base Color"])
    p = tex_path("slide_markings_rough.png")
    if p:
        nt = M["slide_marked"].node_tree
        tex = add_image(nt, p, "Non-Color", (-700, -50))
        nt.links.new(tex.outputs["Color"],
                     nt.nodes["Principled BSDF"].inputs["Roughness"])
    p = tex_path("grip_normal.png")
    if p:
        add_normal_map(M["grip"], p, 1.0)
    add_micro_bump(M["polymer"], 2500.0, 0.08)
    add_micro_bump(M["grip"], 2500.0, 0.08)
    add_micro_bump(M["slide"], 4000.0, 0.03)
    return M


# ==========================================================================
# Slide
# ==========================================================================
def build_slide(M):
    hw, th, H, L = G.SLIDE_HW, G.SLIDE_TOP_HW, G.SLIDE_H, G.SLIDE_LEN
    prof = [(-hw, -H), (-hw, G.SLIDE_CHAMFER_Z), (-th, 0.0), (th, 0.0),
            (hw, G.SLIDE_CHAMFER_Z), (hw, -H)]
    bm = prism(prof, "X", 0.0, L)
    bw = bm.edges.layers.float.new("bevel_weight_edge")
    for e in bm.edges:
        a, b = e.verts
        bottom = abs(a.co.z + H) < 1e-4 and abs(b.co.z + H) < 1e-4
        if abs(a.co.x) < 1e-4 and abs(b.co.x) < 1e-4:
            e[bw] = 0.35 if bottom else 1.0
        elif abs(a.co.x - L) < 1e-4 and abs(b.co.x - L) < 1e-4:
            e[bw] = 0.3 if bottom else 0.55
        else:
            e[bw] = 0.2 if abs(a.co.z + H) < 1e-4 else 0.16
    slide = obj_from_bm("Slide", bm)
    slide["flat_axis"] = "Y"
    bevel_mod(slide, 2.2, segments=3, limit="WEIGHT")
    apply_modifiers(slide)

    # ---- cutters: serrations, ejection port, barrel opening
    cut = bmesh.new()
    d = G.SERR_DEPTH
    for s in (-1, 1):
        for k in range(G.SERR_COUNT):
            x0 = G.SERR_X0 + k * G.SERR_PITCH
            x1 = x0 + G.SERR_W
            poly = [(x0 - 0.5, s * (hw + 1.0)), (x1 + 0.5, s * (hw + 1.0)),
                    (x1 - 0.42, s * (hw - d)), (x0 + 0.42, s * (hw - d))]
            prism(poly, "Z", -H - 1.5, 0.8, cut)
    port = G.rounded_poly([(G.PORT_X0, 3.0, 0.0), (G.PORT_X1, 3.0, 0.0),
                           (G.PORT_X1, G.PORT_Z_BOTTOM, 1.6),
                           (G.PORT_X0, G.PORT_Z_BOTTOM, 2.4)], 4)
    prism(port, "Y", -6.0, hw + 2.0, cut)
    prism(circle(0.0, G.BORE_Z, 7.05, 36), "X", -2.0, 16.0, cut)
    boolean(slide, cut)
    # hollow under the port: with the slide open you look into the chamber
    # and onto the magazine instead of onto a solid pocket floor
    x0, x1, hy, z0, z1 = G.SLIDE_CAVITY
    boolean(slide, prism(rrect(x0, x1, -hy, hy, 0.8), "Z", z0, z1))

    bevel_mod(slide, 0.18, segments=1, angle=50.0)
    apply_modifiers(slide)

    # ---- markings side: planar UV + material slot
    set_material(slide, M["slide"])
    slide.data.materials.append(M["slide_marked"])
    ensure_uv(slide)
    me = slide.data
    uvl = me.uv_layers[0].data
    S = G.SLIDE_TEX_W * G.SLIDE_TEX_MM_PER_PX
    Sv = G.SLIDE_TEX_H * G.SLIDE_TEX_MM_PER_PX
    for poly in me.polygons:
        c = poly.center
        if poly.normal.y < -0.985 and c.x < 140.0 and c.z < -1.0 \
                and c.y < -(hw - 0.5):
            poly.material_index = 1
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl[li].uv = (co.x / S, (co.z - G.SLIDE_TEX_Z0) / Sv)

    # ---- recoil-spring lug under the muzzle (sits in the dust cover notch)
    lug = [(-5.0, -19.8), (5.0, -19.8)] + G.arc_pts(0.0, -25.2, 5.0, 0, -180, 12)
    lug_ob = obj_from_bm("SlideLug", prism(lug, "X", 0.0, 12.0))
    bevel_mod(lug_ob, 0.35, 2, 40.0)
    apply_modifiers(lug_ob)
    boolean(lug_ob, prism(circle(0.0, -25.2, 2.8, 20), "X", -1.0, 6.0))
    set_material(lug_ob, M["slide"])

    parts = [slide, lug_ob]
    parts += build_sights(M)
    parts.append(build_extractor(M))
    parts.append(build_cover_plate(M))
    for p in parts[1:]:
        ensure_uv(p)
    for p in parts:
        finish_shading(p, 32.0)
    return join(parts, "Slide")


def build_sights(M):
    fs = G.FRONT_SIGHT
    front = curve_solid("FrontSight", [G.rounded_poly([
        (fs["x0"] - 0.1, -0.5, 0.0), (fs["x0"] + 1.6, fs["top"], 0.7),
        (fs["x1"], fs["top"], 0.45), (fs["x1"], -0.5, 0.0)], 4)],
        fs["hw"], 0.3, 1)
    set_material(front, M["polymer"])
    dot = obj_from_bm("FrontDot", prism(circle(0.0, 1.55, 0.72, 16), "X",
                                        fs["x1"] - 0.2, fs["x1"] + 0.06))
    set_material(dot, M["white"])

    rs = G.REAR_SIGHT
    nh, nd, top = rs["notch_hw"], rs["notch_depth"], rs["top"]
    prof = G.rounded_poly([
        (-rs["hw_base"], -0.5, 0.0), (rs["hw_base"], -0.5, 0.0),
        (rs["hw_base"], 0.0, 0.0), (rs["hw_top"], top, 0.5),
        (nh, top, 0.25), (nh, top - nd, 0.7), (-nh, top - nd, 0.7),
        (-nh, top, 0.25), (-rs["hw_top"], top, 0.5), (-rs["hw_base"], 0.0, 0.0)],
        4)
    bm = prism(prof, "X", rs["x0"], rs["x1"])
    for v in bm.verts:
        z = max(v.co.z, 0.0)
        if abs(v.co.x - rs["x0"]) < 1e-4:
            v.co.x = rs["x0"] + 2.6 * z / top
        else:
            v.co.x = rs["x1"] - 2.7 * z / top
    rear = obj_from_bm("RearSight", bm)
    bevel_mod(rear, 0.22, 2, 40.0)
    apply_modifiers(rear)
    set_material(rear, M["polymer"])

    # white "U" outline on the rear face (sheared onto the sloped face),
    # built from five quads: two corners, bottom bar and two side bars
    uo, ui, zb, zi, zt = 3.7, 2.9, 0.75, 1.55, top - 0.05
    bm = bmesh.new()
    V = {k: bm.verts.new((0.0, y, z)) for k, (y, z) in {
        "A": (-uo, zb), "B": (-ui, zb), "C": (ui, zb), "D": (uo, zb),
        "K": (-uo, zi), "H": (-ui, zi), "G": (ui, zi), "L": (uo, zi),
        "J": (-uo, zt), "I": (-ui, zt), "F": (ui, zt), "E": (uo, zt)}.items()}
    for quad in ("ABHK", "KHIJ", "BCGH", "CDLG", "GLEF"):
        bm.faces.new([V[c] for c in quad])
    slope = 2.7 / top
    nrm = Vector((1.0, 0.0, slope)).normalized()
    for v in bm.verts:
        v.co.x = rs["x1"] - slope * v.co.z
        v.co += nrm * 0.03
    bm.normal_update()
    for f in bm.faces:
        if f.normal.dot(nrm) < 0:
            f.normal_flip()
    uline = obj_from_bm("RearSightU", bm)
    set_material(uline, M["white"])
    return [front, dot, rear, uline]


def build_extractor(M):
    ob = curve_solid("Extractor", [G.rounded_poly([
        (G.PORT_X1 + 0.2, -6.6, 0.4), (140.8, -6.6, 1.4),
        (140.8, -11.4, 1.4), (118.2, -11.4, 0.8),
        (G.PORT_X1 + 0.2, -10.2, 0.4)], 4)],
        0.35, 0.18, 1, y_center=G.SLIDE_HW - 0.13)
    set_material(ob, M["steel"])
    return ob


def build_cover_plate(M):
    bm = prism(rrect(-7.2, 7.2, -17.0, -3.9, 1.6), "X",
               G.SLIDE_LEN - 0.3, G.SLIDE_LEN + 0.3)
    ob = obj_from_bm("SlideCoverPlate", bm)
    bevel_mod(ob, 0.15, 1, 40.0)
    apply_modifiers(ob)
    set_material(ob, M["polymer"])
    return ob


# ==========================================================================
# Barrel and recoil spring guide
# ==========================================================================
def build_barrel(M):
    seg = 36
    cz, R = G.BORE_Z, G.BARREL_R

    def ring(x, r, hexa=False):
        pts = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            rr = r
            if hexa:
                phi = ((math.degrees(a) + 30.0) % 60.0) - 30.0
                rr = min(r / math.cos(math.radians(phi)), r * 1.07)
            pts.append((x, rr * math.cos(a), cz + rr * math.sin(a)))
        return pts

    defs = [ring(84.0, R), ring(1.0, R), ring(0.45, R - 0.5),
            ring(0.45, 5.35), ring(0.85, 4.6, True), ring(16.0, 4.45, True)]
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in r] for r in defs]
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    tube = obj_from_bm("BarrelTube", bm)
    set_material(tube, M["barrel"])
    tube.data.materials.append(M["bore"])
    for p in tube.data.polygons:
        if p.center.x > 0.8 and abs(math.hypot(p.center.y, p.center.z - cz)) < 5.0:
            p.material_index = 1

    hood = curve_solid("BarrelHood", [G.rounded_poly([
        (82.4, -0.3, 0.6), (G.CHAMBER_X, -0.3, 0.5), (G.CHAMBER_X, -17.0, 0.0),
        (80.6, -17.0, 0.0), (80.6, -7.0, 2.0)], 4)], 8.3, 0.55, 2)
    # chamber, seen when the slide is open
    boolean(hood, prism(circle(0.0, cz, G.CHAMBER_R, 24), "X",
                        G.CHAMBER_X - 21.0, G.CHAMBER_X + 1.0))
    set_material(hood, M["barrel"])
    hood.data.materials.append(M["bore"])
    for p in hood.data.polygons:
        if p.center.x < G.CHAMBER_X - 0.05 and \
                math.hypot(p.center.y, p.center.z - cz) < G.CHAMBER_R + 0.1:
            p.material_index = 1
    for p in (tube, hood):
        ensure_uv(p)
        finish_shading(p, 32.0)
    return join([tube, hood], "Barrel")


def build_recoil_guide(M):
    bm = bmesh.new()
    cz, seg = -25.2, 20
    # the rod shows in the dust cover notch when the slide is open
    defs = [(24.0, 2.35), (1.15, 2.35), (0.9, 2.1), (0.9, 1.0), (1.05, 0.0)]
    rings = []
    for x, r in defs:
        if r == 0.0:
            rings.append([bm.verts.new((x, 0.0, cz))])
            continue
        rings.append([bm.verts.new((x, r * math.cos(2 * math.pi * k / seg),
                                    cz + r * math.sin(2 * math.pi * k / seg)))
                      for k in range(seg)])
    for a, b in zip(rings[:-2], rings[1:-1]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    last, tip = rings[-2], rings[-1][0]
    for k in range(seg):
        bm.faces.new((last[k], last[(k + 1) % seg], tip))
    bm.faces.new(rings[0])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm("RecoilSpringGuide", bm)
    set_material(ob, M["steel"])
    ensure_uv(ob)
    finish_shading(ob, 40.0)
    return ob


# ==========================================================================
# Frame
# ==========================================================================
def build_grip(M):
    levels = G.grip_levels()
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    S = G.GRIP_TEX_SIZE * G.GRIP_TEX_MM_PER_PX
    rings, arcs, zs = [], [], []
    for z, inset in levels:
        pts, arcl, _ = G.grip_ring(z, inset)
        rings.append([bm.verts.new((x, y, z)) for x, y in pts])
        arcs.append(arcl)
        zs.append(z)
    n = len(rings[0])
    for i in range(len(rings) - 1):
        up, lo = rings[i], rings[i + 1]
        for j in range(n):
            j1 = (j + 1) % n
            f = bm.faces.new((lo[j], lo[j1], up[j1], up[j]))
            uvs = [(arcs[i + 1][j], zs[i + 1]), (arcs[i + 1][j + 1], zs[i + 1]),
                   (arcs[i][j + 1], zs[i]), (arcs[i][j], zs[i])]
            for loop, (u, z) in zip(f.loops, uvs):
                loop[uv].uv = (u / S, (z - G.GRIP_TEX_Z0) / S)
    top = bm.faces.new(rings[0])
    bot = bm.faces.new(rings[-1][::-1])
    for f in (top, bot):
        for loop in f.loops:
            loop[uv].uv = (0.93 + loop.vert.co.x * 1e-4,
                           0.93 + loop.vert.co.y * 1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj_from_bm("Grip", bm)
    ob["flat_axis"] = "Z"
    ob["flat_width"] = False
    set_material(ob, M["grip"])
    return ob


def build_frame(M):
    parts = []
    # ---- dust cover with rail
    dc = curve_solid("DustCover", [G.rounded_poly(G.DUSTCOVER, 6)],
                     G.DUSTCOVER_HW, 1.0, 3)
    cut = bmesh.new()
    hw = G.DUSTCOVER_HW
    for s in (-1, 1):
        prism(rrect(3.4, 56.5, -29.75, -28.35, 0.65), "Y",
              s * (hw - 1.0), s * (hw + 2.0), cut)
    prism(rrect(23.4, 27.8, -41.0, -34.9, 0.3), "Y", -hw - 2, hw + 2, cut)
    notch = [(-5.35, -18.0), (5.35, -18.0)] + G.arc_pts(0.0, -25.2, 5.35, 0,
                                                        -180, 14)
    prism(notch, "X", -2.0, 13.0, cut)
    boolean(dc, cut)
    parts.append(dc)

    # ---- frame body with the slide-lock pockets
    body = curve_solid("FrameBody", [G.rounded_poly(G.FRAME_BODY, 6)],
                       G.FRAME_BODY_HW, 1.0, 3)
    cut = bmesh.new()
    x0, x1, z0, z1 = G.SLIDE_LOCK_POCKET
    pocket = G.rounded_poly([(x0, z1, 0.0), (x1, z1, 0.0), (x1, z0, 3.2),
                             (x0, z0, 3.2)], 4)
    hwb = G.FRAME_BODY_HW
    for s in (-1, 1):
        prism(pocket, "Y", s * (hwb - 1.3), s * (hwb + 2.0), cut)
    boolean(body, cut)
    boolean(body, magwell_cutter(*G.MAG_WELL_TOP))
    parts.append(body)

    # ---- trigger guard (with the Gen4 front serrations)
    tg = curve_solid("TriggerGuard", [G.TG_OUTER, G.TG_HOLE], G.TG_HW, 2.3, 3)
    cut = bmesh.new()
    for k in range(8):
        zc = -46.4 - k * 1.45
        prism(rrect(69.0, 71.45, zc - 0.36, zc + 0.36, 0.0), "Y", -5.2, 5.2, cut)
    boolean(tg, cut)
    boolean(tg, magwell_cutter(*G.MAG_WELL_TOP))
    parts.append(tg)

    # grip with the magazine well mouth (bottom) and the top of the well
    grip = build_grip(M)
    plain = (0.93, 0.93)                    # flat spot of the grip texture
    z0, z1 = G.MAG_WELL_BOTTOM
    boolean(grip, magwell_cutter(z0, z1, G.MAG_WELL_FLARE, G.GRIP_Z_BOTTOM,
                                 uv=plain))
    boolean(grip, magwell_cutter(*G.MAG_WELL_TOP, uv=plain))
    for p in parts:
        set_material(p, M["polymer"])
        ensure_uv(p)
        for li in p.data.uv_layers[0].data:
            li.uv = (0.95, 0.95)
    parts.append(grip)

    # ---- slide-stop guard (raised ledge around the slide-stop tab)
    path = []
    for x, z in G.SLIDE_STOP_GUARD:
        ys = max(G.FRAME_BODY_HW, G.grip_surface_y(x, z))
        path.append((x, -(ys - 0.35), z))
    guard = tube_along("SlideStopGuard", path, 1.0, 2)
    set_material(guard, M["polymer"])
    ensure_uv(guard)
    parts.append(guard)

    for p in parts:
        finish_shading(p, 38.0)
    frame = join(parts, "Frame")

    # ---- small metal parts that live in the frame
    metal = []
    for (x, z, r, on_grip) in G.PINS:
        ys = G.grip_surface_y(x, z) if on_grip else G.FRAME_BODY_HW
        for s in (-1, 1):
            bm = bmesh.new()
            seg = 16
            defs = [(ys - 1.5, r), (ys + 0.02, r), (ys + 0.12, r - 0.18)]
            rings = [[bm.verts.new((x + rr * math.cos(2 * math.pi * k / seg),
                                    s * yy,
                                    z + rr * math.sin(2 * math.pi * k / seg)))
                      for k in range(seg)] for yy, rr in defs]
            for a, b in zip(rings[:-1], rings[1:]):
                for k in range(seg):
                    bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
            bm.faces.new(rings[0])
            bm.faces.new(rings[-1])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            metal.append(obj_from_bm("Pin", bm))

    # slide lock (takedown lever) - both sides, serrated
    lx0, lx1, lz0, lz1 = G.SLIDE_LOCK_LEVER
    for s in (-1, 1):
        lever = curve_solid("SlideLock", [rrect(lx0, lx1, lz0, lz1, 1.3)],
                            0.65, 0.3, 1, y_center=s * (hwb - 0.7))
        metal.append(lever)
        for k in range(3):
            xc = lx0 + 1.6 + k * 1.8
            rib = curve_solid("SlideLockRib", [rrect(xc - 0.35, xc + 0.35,
                                                     lz0 + 1.0, lz1 - 1.0, 0.3)],
                              0.325, 0.12, 1, y_center=s * (hwb - 0.025))
            metal.append(rib)

    # serial number plate under the dust cover
    plate = obj_from_bm("SerialPlate", prism(rrect(47.0, 59.0, -3.2, 3.2, 0.6),
                                             "Z", -37.3, -36.8))
    for o in metal:
        set_material(o, M["steel"])
        ensure_uv(o)
        finish_shading(o, 40.0)
    set_material(plate, M["plate"])
    ensure_uv(plate)
    finish_shading(plate, 40.0)
    return join([frame] + metal + [plate], "Frame")


# ==========================================================================
# Trigger, controls, magazine
# ==========================================================================
def build_trigger(M):
    trig = curve_solid("TriggerShoe", [G.smooth_closed(G.TRIGGER, 1)],
                       G.TRIGGER_HW, 1.1, 2)
    # trigger safety blade protruding from the trigger face
    fr = G.TRIGGER[3:12]
    inner, outer = [], []
    for i, (x, z) in enumerate(fr):
        xa, za = fr[max(i - 1, 0)]
        xb, zb = fr[min(i + 1, len(fr) - 1)]
        tx, tz = xb - xa, zb - za
        L = math.hypot(tx, tz)
        nx, nz = tz / L, -tx / L
        off = 1.15 * min(1.0, i / 2.5) * (0.75 if i == len(fr) - 1 else 1.0)
        inner.append((x - nx * 0.8, z - nz * 0.8))
        outer.append((x + nx * off, z + nz * off))
    blade = curve_solid("TriggerSafety", [G.smooth_closed(inner + outer[::-1], 1)],
                        1.25, 0.4, 1)
    for p in (trig, blade):
        set_material(p, M["polymer"])
        ensure_uv(p)
        finish_shading(p, 40.0)
    trig.name = trig.data.name = "Trigger"
    return trig, blade


def build_slide_stop(M):
    x0, x1, z0, z1 = G.SLIDE_STOP_TAB
    ys = max(G.FRAME_BODY_HW, G.grip_surface_y(0.5 * (x0 + x1), 0.5 * (z0 + z1)))
    parts = [curve_solid("SlideStopTab", [rrect(x0, x1, z0, z1, 1.4)],
                         1.5, 0.45, 2, y_center=-(ys + 0.4))]
    for k in range(4):
        zc = z1 - 1.25 - k * 1.2
        parts.append(curve_solid("SlideStopRib", [rrect(x0 + 0.9, x1 - 0.9,
                                                        zc - 0.28, zc + 0.28,
                                                        0.25)],
                                 0.3, 0.12, 1, y_center=-(ys + 1.85)))
    for p in parts:
        set_material(p, M["steel"])
        ensure_uv(p)
        finish_shading(p, 40.0)
    return join(parts, "SlideStop")


def build_mag_catch(M):
    mc = G.MAG_CATCH
    a = math.radians(mc["angle"])
    dx, dz = math.sin(a), -math.cos(a)        # along the grip axis (down)
    px, pz = math.cos(a), math.sin(a)          # across (towards the back)

    def box(u0, u1, v0, v1, r):
        loc = G.rounded_poly([(u0, v0, r), (u1, v0, r), (u1, v1, r), (u0, v1, r)],
                             4)
        return [(mc["cx"] + u * dx + v * px, mc["cz"] + u * dz + v * pz)
                for u, v in loc]

    ys = G.grip_surface_y(mc["cx"], mc["cz"])
    hu, hv = mc["along"] / 2, mc["across"] / 2
    parts = [curve_solid("MagCatch", [box(-hu, hu, -hv, hv, 1.6)], 1.7, 0.5, 2,
                         y_center=-(ys + 0.5))]
    for k in range(6):
        v = -hv + 1.3 + k * (2 * hv - 2.6) / 5
        parts.append(curve_solid("MagCatchRib", [box(-hu + 1.0, hu - 1.0,
                                                     v - 0.3, v + 0.3, 0.28)],
                                 0.3, 0.12, 1, y_center=-(ys + 2.2)))
    for p in parts:
        set_material(p, M["polymer"])
        ensure_uv(p)
        finish_shading(p, 40.0)
    return join(parts, "MagazineCatch")


def build_magazine(M):
    plate = curve_solid("MagPlate", [G.rounded_poly(G.MAG_PLATE, 5)],
                        G.MAG_PLATE_HW, 1.1, 2)
    body = obj_from_bm("MagBody", mag_loft([(G.MAG_ZB, 0.0), (G.MAG_ZT, 0.0)]))
    body["flat_axis"] = "Z"
    bevel_mod(body, 0.8, 2, 40.0)
    apply_modifiers(body)
    for p in (plate, body):
        set_material(p, M["polymer"])
        ensure_uv(p)
        finish_shading(p, 38.0)
    return join([plate, body], "Magazine")


def cartridge_to_build(ob, head_x, axis_z):
    """Place a part modelled along +X (head at 0) with its head at head_x on
    a horizontal axis at axis_z, pointing at the muzzle (-X)."""
    ob.data.transform(Matrix.Translation((head_x, 0.0, axis_z))
                      @ Matrix.Rotation(math.pi, 4, "Z"))


def build_casing(M):
    """Empty 9x19 case, in the chamber (it is ejected by the fire clip)."""
    ob = obj_from_bm("Casing", lathe(G.CASE_PROFILE, 16))
    ob["flat_axis"] = "X"
    set_material(ob, M["brass"])
    ensure_uv(ob)
    finish_shading(ob, 35.0)
    cartridge_to_build(ob, G.CHAMBER_X, G.BORE_Z)
    return ob


def build_cartridge(M, name="MagazineRound"):
    """Loaded 9x19 round (FMJ), on top of the magazine."""
    ob = obj_from_bm(name, lathe(G.CARTRIDGE_PROFILE, 16))
    ob["flat_axis"] = "X"
    set_material(ob, M["brass"])
    ob.data.materials.append(M["copper"])
    for p in ob.data.polygons:
        if p.center.x > G.CASE_LEN + 0.01:
            p.material_index = 1
    ensure_uv(ob)
    finish_shading(ob, 35.0)
    cartridge_to_build(ob, G.MAG_ROUND_HEAD_X, G.MAG_ROUND_Z)
    return ob


def build_muzzle_flash(M):
    """Three crossed flame cards and a star of petals.  Modelled collapsed
    inside the bore (FLASH_REST_SCALE); the fire clip scales it up."""
    bm = bmesh.new()
    card = [(0.0, 0.0), (7.0, 4.6), (14.0, 3.0), (24.0, 6.6), (36.0, 2.6),
            (50.0, 0.0), (36.0, -2.6), (24.0, -6.6), (14.0, -3.0), (7.0, -4.6)]
    for k in range(3):
        a = math.pi * k / 3
        bm.faces.new([bm.verts.new((x, r * math.cos(a), r * math.sin(a)))
                      for x, r in card])
    star = []
    for k in range(12):
        a = 2 * math.pi * k / 12 + math.pi / 12
        r = 14.0 if k % 2 == 0 else 3.6
        star.append(bm.verts.new((3.0, r * math.cos(a), r * math.sin(a))))
    bm.faces.new(star)
    s = G.FLASH_REST_SCALE
    ob = obj_from_bm("MuzzleFlash", bm)
    set_material(ob, M["flash"])
    ensure_uv(ob)
    x0 = G.BONE_POINT_MM["Gun_Flash"][0]
    ob.data.transform(Matrix.Translation((x0, 0.0, G.BORE_Z))
                      @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(s, 4))
    return ob


# ==========================================================================
# Scene: assembly, lights, cameras, render, export
# ==========================================================================
def poly_stats(objs):
    faces = tris = 0
    for o in objs:
        for p in o.data.polygons:
            faces += 1
            tris += len(p.vertices) - 2
    return faces, tris


# build mm -> scene metres in the GTA V weapon orientation (X = muzzle,
# Z = up, origin of the standard pistol skeleton, see glock_data)
XF = (Matrix.Scale(0.001, 4) @ Matrix.Rotation(math.pi, 4, "Z")
      @ Matrix.Translation(-Vector(G.GTA_ORIGIN_MM)))
XF_ROT = Matrix.Rotation(math.pi, 3, "Z")


def bone_rest_matrices():
    """Scene-space rest matrices of the skeleton bones (G.GTA_BONES)."""
    W = {}
    for name, parent, kind, (t, q) in G.GTA_BONES:
        rot = Quaternion((q[3], q[0], q[1], q[2])).normalized().to_matrix()
        if kind == "local":
            base = W[parent] if parent else Matrix.Identity(4)
            W[name] = base @ Matrix.Translation(t) @ rot.to_4x4()
        else:
            W[name] = Matrix.Translation(XF @ Vector(t)) @ rot.to_4x4()
    return W


def build_rig(objs):
    """Armature with the GTA V pistol skeleton; every part is skinned
    rigidly to one bone (G.PART_BONES)."""
    arm = bpy.data.armatures.new("Glock17_Gen4")
    arm.display_type = "STICK"
    rig = link(bpy.data.objects.new("Glock17_Gen4", arm))
    rig.show_in_front = True
    W = bone_rest_matrices()
    vl = bpy.context.view_layer
    vl.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    ebs = {}
    for name, parent, _, _ in G.GTA_BONES:
        eb = arm.edit_bones.new(name)
        eb.head, eb.tail = (0.0, 0.0, 0.0), (0.0, 0.012, 0.0)
        eb.matrix = W[name]
        if parent:
            eb.parent = ebs[parent]
        ebs[name] = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    for ob in objs:
        vg = ob.vertex_groups.new(name=G.PART_BONES[ob.name])
        vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
        m = ob.modifiers.new("Armature", "ARMATURE")
        m.object = rig
        ob.parent = rig
    return rig


def build_model():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = make_materials()
    trigger, safety = build_trigger(M)
    objs = [
        build_slide(M),
        build_barrel(M),
        build_recoil_guide(M),
        build_frame(M),
        trigger,
        safety,
        build_slide_stop(M),
        build_mag_catch(M),
        build_magazine(M),
        build_cartridge(M),
        build_casing(M),
        build_muzzle_flash(M),
    ]
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for v in o.data.vertices:
            for i in range(3):
                mins[i] = min(mins[i], v.co[i])
                maxs[i] = max(maxs[i], v.co[i])
    for o in objs:
        o.data.transform(XF)
    rig = build_rig(objs)
    print("bbox mm:", tuple(round(v, 2) for v in (maxs - mins)))
    return rig, objs, (maxs - mins)


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def add_area(name, loc, size, power, target=(0, 0, 0), size_y=None,
             color=(1, 1, 1), parent=None, spread=180.0):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size = size
    ld.size_y = size_y or size
    ld.energy = power
    ld.color = color
    ld.spread = math.radians(spread)
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    look_at(ob, target)
    ob.parent = parent
    return ob


LIGHT_RIG = None


def setup_scene():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.3
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "MILLIMETERS"

    world = bpy.data.worlds.new("Studio")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    # vertical gradient: bright "ceiling", darker floor (reflections on metal)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.035, 0.035, 0.037, 1)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (0.30, 0.30, 0.31, 1)
    mapr = nt.nodes.new("ShaderNodeMapRange")
    mapr.inputs["From Min"].default_value = -1.0
    mapr.inputs["From Max"].default_value = 1.0
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], mapr.inputs["Value"])
    nt.links.new(mapr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0

    global LIGHT_RIG
    LIGHT_RIG = link(bpy.data.objects.new("LightRig", None))
    # rig defined for a camera on the pistol's left side (build -Y); it is
    # turned with every view (aim_light_rig)
    add_area("Key", (-0.10, -0.30, 0.70), 1.1, 22.0, size_y=0.55,
             parent=LIGHT_RIG)
    add_area("FrontCard", (0.0, -1.9, -0.05), 2.6, 11.0, size_y=1.4,
             parent=LIGHT_RIG)
    add_area("Rim", (0.25, 0.55, 0.40), 1.0, 7.0, size_y=0.25,
             parent=LIGHT_RIG)
    add_area("Kicker", (-0.55, -0.35, -0.10), 0.6, 2.0, size_y=0.3,
             parent=LIGHT_RIG)

    # composite over a white background
    sc.use_nodes = True
    ct = sc.node_tree
    for n in list(ct.nodes):
        ct.nodes.remove(n)
    rl = ct.nodes.new("CompositorNodeRLayers")
    ao = ct.nodes.new("CompositorNodeAlphaOver")
    ao.inputs[1].default_value = (40.0, 40.0, 40.0, 1)   # white after AgX
    out = ct.nodes.new("CompositorNodeComposite")
    ct.links.new(rl.outputs["Image"], ao.inputs[2])
    ct.links.new(ao.outputs["Image"], out.inputs["Image"])


def add_camera(name, loc, target=(0, 0, 0), lens=100.0, ortho=None):
    cd = bpy.data.cameras.new(name)
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    else:
        cd.lens = lens
    cd.sensor_width = 36.0
    cd.clip_start = 0.01
    cd.clip_end = 20.0
    ob = link(bpy.data.objects.new(name, cd))
    ob.location = loc
    look_at(ob, target)
    return ob


def sph(dist, yaw, elev):
    """Scene offset for a camera: yaw 0 = looking at the pistol's LEFT side,
    +yaw swings towards the muzzle, elev = degrees above the horizon."""
    y, e = math.radians(yaw), math.radians(elev)
    return XF_ROT @ Vector((-dist * math.cos(e) * math.sin(y),
                            -dist * math.cos(e) * math.cos(y),
                            dist * math.sin(e)))


def mm(x, y, z):
    """Build-space millimetres -> scene metres."""
    return XF @ Vector((x, y, z))


def aim_light_rig(target, yaw):
    """The light rig is defined for yaw 0; turn it with the camera."""
    LIGHT_RIG.rotation_euler = (0.0, 0.0, math.radians(-yaw) + math.pi)
    LIGHT_RIG.location = target


# name: (target in build mm, distance m, yaw, elevation, lens mm, ortho scale)
VIEWS = {
    "hero":        ((103.0, 0.0, -66.0), 0.88, 16.0, 9.0, 100, None),
    "left":        ((100.7, 0.0, -64.8), 1.50, 0.0, 0.0, 100, 0.232),
    "right":       ((100.7, 0.0, -64.8), 1.50, 180.0, 0.0, 100, 0.232),
    "right_rear":  ((100.7, 0.0, -62.0), 0.92, 218.0, 16.0, 100, None),
    "front":       ((84.0, 0.0, -60.0), 0.80, 62.0, 6.0, 100, None),
    "top":         ((100.0, 0.0, -45.0), 0.95, 150.0, 50.0, 100, None),
    "cu_grip":     ((160.0, 0.0, -85.0), 0.42, 8.0, 6.0, 100, None),
    "cu_trigger":  ((95.0, 0.0, -45.0), 0.36, 18.0, 4.0, 100, None),
    "cu_rear":     ((160.0, 0.0, -12.0), 0.36, 215.0, 22.0, 100, None),
    "cu_muzzle":   ((10.0, 0.0, -22.0), 0.30, 55.0, 10.0, 100, None),
    "cu_sight":    ((174.0, 0.0, 1.0), 0.16, -75.0, 8.0, 100, None),
    "bottom":      ((100.7, 0.0, -64.8), 1.05, 150.0, -55.0, 100, None),
    "cu_trigger_low": ((96.0, 0.0, -50.0), 0.30, 28.0, -22.0, 100, None),
    "cu_port":     ((105.0, 8.0, -8.0), 0.30, 160.0, 28.0, 100, None),
}
MAIN_VIEWS = ["hero", "left", "right", "right_rear", "front", "top"]


def render_views(names, res=(1920, 1200), samples=192, suffix=""):
    sc = bpy.context.scene
    os.makedirs(RENDER_DIR, exist_ok=True)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    out = []
    for name in names:
        tgt_mm, dist, yaw, elev, lens, ortho = VIEWS[name]
        tgt = mm(*tgt_mm)
        cam = add_camera("Cam_" + name, tgt + sph(dist, yaw, elev), tgt, lens,
                         ortho)
        aim_light_rig(tgt, yaw)
        sc.camera = cam
        path = os.path.join(RENDER_DIR, f"{name}{suffix}.png")
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out.append(path)
    return out


def export_model(rig, objs):
    """Save the .blend and export glTF binary + FBX: skinned parts, the
    skeleton and the animation clips."""
    bpy.ops.file.pack_all()
    blend = os.path.join(ROOT, "glock17_gen4.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    vl = bpy.context.view_layer
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in [rig] + list(objs):
        o.select_set(True)
    vl.objects.active = rig
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(ROOT, "glock17_gen4.glb"),
        export_format="GLB", use_selection=True, export_apply=True,
        export_yup=True, export_image_format="AUTO", export_skins=True,
        export_animations=True, export_animation_mode="ACTIONS",
        export_def_bones=False, export_frame_range=False)
    # FBX: triangulate on export so tangents can be written for normal maps
    for o in objs:
        m = o.modifiers.new("export_tri", "TRIANGULATE")
        m.keep_custom_normals = True
        m.quad_method = "BEAUTY"
        o.modifiers.move(len(o.modifiers) - 1, 0)
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(ROOT, "glock17_gen4.fbx"),
        use_selection=True, object_types={"ARMATURE", "MESH"},
        use_mesh_modifiers=True, apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
        mesh_smooth_type="OFF", use_tspace=True, path_mode="COPY",
        embed_textures=True, add_leaf_bones=False, bake_anim=True,
        bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0)
    for o in objs:
        o.modifiers.remove(o.modifiers["export_tri"])
        o.select_set(False)
    rig.select_set(False)
    return blend


def render_wireframe(objs, view="hero", res=(1920, 1200), samples=64):
    """Clay render with the polygon edges drawn on top (wireframe modifier)."""
    clay = principled("Clay", (0.42, 0.42, 0.44), 0.0, 0.55)
    wire = principled("Wire", (0.015, 0.02, 0.035), 0.0, 0.6)
    for o in objs:
        for slot in o.material_slots:
            slot.link = "OBJECT"
            slot.material = clay
        dup = o.copy()
        link(dup)
        for slot in dup.material_slots:
            slot.link = "OBJECT"
            slot.material = wire
        m = dup.modifiers.new("wire", "WIREFRAME")
        m.thickness = 0.00011
        m.use_even_offset = True
        m.use_relative_offset = False
        m.use_replace = True
        m.offset = 1.0
    return render_views([view], res=res, samples=samples, suffix="_wireframe")


if __name__ == "__main__":
    import glock_anim
    rig, objs, size = build_model()
    glock_anim.create_actions(rig)
    f, t = poly_stats(objs)
    print(f"faces={f} tris={t}")
    os.makedirs(RENDER_DIR, exist_ok=True)
    with open(os.path.join(RENDER_DIR, "stats.json"), "w") as fh:
        json.dump({"faces": f, "tris": t, "size_mm": [round(v, 2) for v in size],
                   "objects": {o.name: {"faces": len(o.data.polygons),
                                        "tris": sum(len(p.vertices) - 2
                                                    for p in o.data.polygons)}
                               for o in objs}}, fh, indent=2)
    for o in objs:
        print(f"  {o.name:16s} faces={len(o.data.polygons):6d} "
              f"tris={sum(len(p.vertices) - 2 for p in o.data.polygons):6d}")
    setup_scene()
    bpy.context.scene.render.use_persistent_data = True
    if QUICK:
        views = ONLY_VIEWS.split(",") if ONLY_VIEWS else MAIN_VIEWS
        render_views(views, res=(960, 600), samples=40, suffix="_q")
    else:
        # the hero camera becomes the scene camera of the saved .blend
        tgt_mm, dist, yaw, elev, lens, ortho = VIEWS["hero"]
        tgt = mm(*tgt_mm)
        bpy.context.scene.camera = add_camera("Camera", tgt + sph(dist, yaw, elev),
                                              tgt, lens)
        aim_light_rig(tgt, yaw)
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1200
        bpy.context.scene.cycles.samples = 256
        print("saved", export_model(rig, objs))
        if not NO_RENDER:
            views = ONLY_VIEWS.split(",") if ONLY_VIEWS else (
                MAIN_VIEWS + ["cu_grip", "cu_trigger", "cu_rear", "cu_muzzle",
                              "cu_port"])
            for v in views:
                big = v == "hero"
                render_views([v], res=(1920, 1200) if big else (1600, 1000),
                             samples=160 if big else 96)
            render_wireframe(objs)
