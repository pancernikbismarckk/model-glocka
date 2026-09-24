"""
Export the Glock 17 Gen4 as a standalone FiveM add-on weapon (GTA V).

Needs Blender 4.2+ (or the bpy module) with the Sollumz add-on (2.8.x) and
cwxml2bin (tools/cwxml2bin: .NET 8 + CodeWalker.Core), which turns the
CodeWalker XML written by Sollumz into binary GTA V resources.

  python scripts/export_fivem.py [--sollumz=DIR] [--cwxml2bin=EXE] [--keep-xml]

  --sollumz=DIR     folder that contains the "sollumz" add-on package
                    (default: the add-on installed in Blender)
  --cwxml2bin=EXE   converter (default: tools/cwxml2bin/bin/Release/net8.0/)
  --keep-xml        keep the intermediate XML/DDS files (fivem/_xml)

Output: fivem/glock17/ - a resource folder ready for the server's resources:
  fxmanifest.lua, client.lua, meta/*.meta, stream/*.ydr, *.ytd, *.ycd
"""
import importlib
import io
import os
import shutil
import struct
import subprocess
import sys

import bpy
import numpy as np
from mathutils import Matrix
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_glock17 as B  # noqa: E402
import glock_anim as A  # noqa: E402
import glock_data as G  # noqa: E402

ROOT = B.ROOT
OUT = os.path.join(ROOT, "fivem", "glock17")
XML = os.path.join(ROOT, "fivem", "_xml")

WEAPON = "WEAPON_GLOCK17"
MODEL = "w_pi_glock17"
MAG_MODEL = "w_pi_glock17_mag1"
CLIP_COMPONENT = "COMPONENT_GLOCK17_CLIP_01"
ANIM_DICT = "anim@w_pi_glock17"
DISPLAY_NAME = "Glock 17 Gen4"
CLIP_SIZE = 17
UNBRANDED = os.path.join("optional", "bez_oznaczen")

# bones of the in-game skeleton: the standard pistol bones (the game's
# pistol clips animate them) plus parts only the anim@w_pi_glock17 clips move
WEAPON_BONES = [b[0] for b in G.GTA_BONES[:G.GTA_PISTOL_BONES]] + [
    "Gun_Barrel", "Gun_SlideStop", "Gun_MagRelease"]
# parts of the weapon drawable -> skin bone (the magazine is a component,
# the casing and the flash are particle effects in the game)
WEAPON_PARTS = {
    "Slide": "Gun_Cock1", "Barrel": "Gun_Barrel",
    "RecoilSpringGuide": "Gun_Main_Bone", "Frame": "Gun_Main_Bone",
    "Trigger": "Gun_Trigger_Pr", "TriggerSafety": "Gun_Trigger_Pr",
    "SlideStop": "Gun_SlideStop", "MagazineCatch": "Gun_MagRelease",
}
MAG_PARTS = ["Magazine", "MagazineRound"]

# GTA V shader look (normal_spec): palette swatch per Blender material:
# (diffuse sRGB, specular intensity 0-255, glossiness 0-255)
PALETTE = {
    "Polymer_Frame": ((30, 30, 32), 60, 110),
    "Slide_Nitride": ((46, 47, 50), 150, 215),
    "Barrel_Nitride": ((62, 62, 64), 170, 225),
    "Steel_Black": ((36, 36, 38), 140, 200),
    "Sight_White": ((225, 225, 220), 40, 90),
    "Serial_Plate": ((150, 150, 150), 180, 220),
    "Bore_Dark": ((10, 10, 10), 30, 60),
    "Brass_Case": ((180, 140, 72), 200, 220),
    "Copper_Jacket": ((175, 104, 64), 190, 210),
}
PAL_CELL, PAL_GRID = 16, 4                 # 64 x 64 palette, 16 px swatches
SHADER_PARAMS = {"bumpiness": 1.0, "specularIntensityMult": 0.9647,
                 "specularFalloffMult": 26.58, "specularFresnel": 0.75,
                 "specMapIntMask": (1.0, 0.0, 0.0), "HardAlphaBlend": 1.0,
                 "useTessellation": 0.0, "wetnessMultiplier": 1.0}


def _arg(name, default=None):
    return B._arg(name, default)


# ==========================================================================
# DDS textures (DXT5 with a full mip chain)
# ==========================================================================
def dds_write(img, path):
    """Save an RGBA image as DXT5 DDS with mipmaps down to 4 x 4."""
    img = img.convert("RGBA")
    levels, im = [], img
    while True:
        buf = io.BytesIO()
        im.save(buf, "DDS", pixel_format="DXT5")
        data = buf.getvalue()
        levels.append(data[128:])
        if min(im.size) <= 4:
            break
        im = im.resize((max(1, im.width // 2), max(1, im.height // 2)),
                       Image.Resampling.BOX)
    w, h = img.size
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000
    header = struct.pack("<4sIIIIIII44x", b"DDS ", 124, flags, h, w,
                         len(levels[0]), 0, len(levels))
    header += struct.pack("<II4s20x", 32, 0x4, b"DXT5")
    header += struct.pack("<IIII4x", 0x1000 | 0x400000 | 0x8, 0, 0, 0)
    assert len(header) == 128
    with open(path, "wb") as f:
        f.write(header)
        for lv in levels:
            f.write(lv)
    return {"name": os.path.splitext(os.path.basename(path))[0],
            "width": w, "height": h, "mips": len(levels)}


def flip_green(img):
    """Blender (OpenGL) normal map -> GTA V (DirectX, green down)."""
    a = np.asarray(img.convert("RGBA")).copy()
    a[..., 1] = 255 - a[..., 1]
    return Image.fromarray(a, "RGBA")


def solid(rgb, alpha=255, size=32):
    return Image.new("RGBA", (size, size), (*rgb, alpha))


def palette_uv(index):
    """Blender UV of the centre of palette swatch `index`."""
    gx, gy = index % PAL_GRID, index // PAL_GRID
    n = PAL_CELL * PAL_GRID
    return ((gx + 0.5) * PAL_CELL / n, 1.0 - (gy + 0.5) * PAL_CELL / n)


def make_textures(folder, unbranded=False):
    """Write the DDS files; returns {texture name: info}.  unbranded: plain
    slide (no engravings) and the grip texture without the GLOCK logos."""
    os.makedirs(folder, exist_ok=True)
    tex = {}

    def put(name, img):
        tex[name] = dds_write(img, os.path.join(folder, name + ".dds"))

    n = PAL_CELL * PAL_GRID
    dif = np.full((n, n, 4), (*PALETTE["Polymer_Frame"][0], 255), np.uint8)
    spc = np.full((n, n, 4), (60, 60, 60, 110), np.uint8)   # unused swatches
    for i, (rgb, s, gl) in enumerate(PALETTE.values()):
        gx, gy = i % PAL_GRID, i // PAL_GRID
        sl = np.s_[gy * PAL_CELL:(gy + 1) * PAL_CELL,
                   gx * PAL_CELL:(gx + 1) * PAL_CELL]
        dif[sl] = (*rgb, 255)
        spc[sl] = (s, s, s, gl)
    put("glock17_pal_d", Image.fromarray(dif, "RGBA"))
    put("glock17_pal_s", Image.fromarray(spc, "RGBA"))
    put("glock17_flat_n", solid((128, 128, 255)))

    td = B.TEX_DIR
    grip = "grip_normal_plain.png" if unbranded else "grip_normal.png"
    put("glock17_grip_n", flip_green(Image.open(os.path.join(td, grip))
                                     .convert("RGBA")
                                     .resize((1024, 1024),
                                             Image.Resampling.LANCZOS)))
    put("glock17_grip_d", solid(PALETTE["Polymer_Frame"][0]))
    put("glock17_grip_s", solid((50, 50, 50), 95))
    if unbranded:
        rgb, sp, gl = PALETTE["Slide_Nitride"]
        put("glock17_slide_d", Image.new("RGBA", (64, 8), (*rgb, 255)))
        put("glock17_slide_n", Image.new("RGBA", (64, 8), (128, 128, 255, 255)))
        put("glock17_slide_s", Image.new("RGBA", (64, 8), (sp, sp, sp, gl)))
        return tex
    # slide markings: the Blender texture is linear 0.16 (base) .. 0.26
    col = np.asarray(Image.open(os.path.join(td, "slide_markings_color.png"))
                     .convert("RGB"), np.float32) / 255.0
    lin = np.where(col <= 0.04045, col / 12.92, ((col + 0.055) / 1.055) ** 2.4)
    base = np.array(PALETTE["Slide_Nitride"][0], np.float32)
    rgb = np.clip(base * lin / 0.16, 0, 255).astype(np.uint8)
    sd = Image.fromarray(rgb, "RGB").resize((2048, 256), Image.Resampling.LANCZOS)
    put("glock17_slide_d", sd)
    rough = np.asarray(Image.open(os.path.join(td, "slide_markings_rough.png"))
                       .convert("L").resize((2048, 256), Image.Resampling.LANCZOS),
                       np.float32) / 255.0
    k = np.clip((rough - 0.4) / 0.25, 0, 1)
    s = (150 - 70 * k).astype(np.uint8)
    gl = (215 - 95 * k).astype(np.uint8)
    put("glock17_slide_s", Image.fromarray(np.dstack([s, s, s, gl]), "RGBA"))
    nrm = Image.open(os.path.join(td, "slide_markings_normal.png")).convert("RGBA")
    put("glock17_slide_n", flip_green(nrm.resize((2048, 256),
                                                  Image.Resampling.LANCZOS)))
    return tex


def write_ytd_xml(path, textures):
    items = []
    for t in textures:
        items.append(f"""  <Item>
   <Name>{t['name']}</Name>
   <Unk32 value="128" />
   <Usage>DEFAULT</Usage>
   <UsageFlags>0</UsageFlags>
   <ExtraFlags value="0" />
   <Width value="{t['width']}" />
   <Height value="{t['height']}" />
   <MipLevels value="{t['mips']}" />
   <Format>D3DFMT_DXT5</Format>
   <FileName>{t['name']}.dds</FileName>
  </Item>""")
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<TextureDictionary>\n'
                + "\n".join(items) + "\n</TextureDictionary>\n")


# ==========================================================================
# Sollumz objects
# ==========================================================================
def enable_sollumz():
    import addon_utils
    path = _arg("--sollumz")
    if path:
        path = os.path.abspath(path)
        sys.path.insert(0, path)
        pf = bpy.context.preferences.filepaths
        parent = os.path.dirname(path)
        if not any(d.directory == parent for d in pf.script_directories):
            d = pf.script_directories.new()
            d.directory, d.name = parent, "sollumz_export"
        bpy.utils.refresh_script_paths()
        addon_utils.modules_refresh()
    for name in ("sollumz", "bl_ext.user_default.sollumz"):
        try:
            if addon_utils.enable(name, default_set=True) is None:
                continue
        except Exception:                      # noqa: BLE001 - try the next
            continue
        return Sollumz(name)
    raise SystemExit("Sollumz is not available: install it in Blender or "
                     "pass --sollumz=<folder containing the sollumz package>")


class Sollumz:
    """The few Sollumz modules used here."""

    def __init__(self, package):
        def mod(sub):
            return importlib.import_module(f"{package}.{sub}")
        self.create_shader = mod("ydr.shader_materials").create_shader
        self.convert_obj_to_model = mod("tools.drawablehelper").convert_obj_to_model
        self.SollumType = mod("sollumz_properties").SollumType


def gta_material(SZ, name, textures):
    """normal_spec shader with the given {sampler: texture file} images."""
    mat = SZ.create_shader("normal_spec.sps")
    mat.name = name
    nodes = mat.node_tree.nodes
    for sampler, path in textures.items():
        img = bpy.data.images.load(path, check_existing=True)
        img.colorspace_settings.name = "sRGB" if sampler == "DiffuseSampler" \
            else "Non-Color"
        nodes[sampler].image = img
    for pname, val in SHADER_PARAMS.items():
        node = nodes.get(pname)
        if node is None:
            continue
        vals = val if isinstance(val, tuple) else (val,)
        for i, v in enumerate(vals):
            node.set(i, v)
    return mat


def gta_armature(SZ, name, bones, rest):
    """Drawable armature; bones = [(name, parent)], rest = {name: matrix}."""
    arm = bpy.data.armatures.new(name)
    ob = B.link(bpy.data.objects.new(name, arm))
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    ebs = {}
    for bname, parent in bones:
        eb = arm.edit_bones.new(bname)
        eb.head, eb.tail = (0.0, 0.0, 0.0), (0.0, 0.012, 0.0)
        eb.matrix = rest[bname]
        if parent:
            eb.parent = ebs[parent]
        ebs[bname] = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in arm.bones:
        for fl in ("RotX", "RotY", "RotZ", "TransX", "TransY", "TransZ"):
            b.bone_properties.flags.add().name = fl
    for pb in ob.pose.bones:
        pb.rotation_mode = "QUATERNION"
    ob.sollum_type = SZ.SollumType.DRAWABLE
    return ob


def joined_copy(parts, name, groups, xform=None):
    """Join copies of the parts into one mesh object; groups maps part name
    -> vertex group (skin bone)."""
    copies = []
    for src in parts:
        ob = src.copy()
        ob.data = src.data.copy()
        ob.modifiers.clear()
        ob.vertex_groups.clear()
        ob.parent = None
        B.link(ob)
        vg = ob.vertex_groups.new(name=groups[src.name])
        vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
        copies.append(ob)
    joined = B.join(copies, name)
    if xform is not None:
        joined.data.transform(xform)
    return joined


def assign_gta_materials(ob, mats):
    """Swap the Blender materials for the GTA shaders, set palette UVs,
    rename the UV map for Sollumz and add the vertex colour layer."""
    me = ob.data
    uv = me.uv_layers[0]
    uv.name = "UVMap 0"
    old = [s.material.name for s in ob.material_slots]
    targets = []
    for mname in old:
        if mname == "Slide_Nitride_Markings":
            targets.append(mats["slide"])
        elif mname == "Polymer_Grip_RTF":
            targets.append(mats["grip"])
        else:
            targets.append(mats["main"])
    uniq = list(dict.fromkeys(targets))
    remap = [uniq.index(t) for t in targets]
    pal_index = {m: i for i, m in enumerate(PALETTE)}
    new_index = []
    for poly in me.polygons:
        mname = old[poly.material_index]
        if mname in pal_index:
            u, v = palette_uv(pal_index[mname])
            for li in poly.loop_indices:
                uv.data[li].uv = (u, v)
        new_index.append(remap[poly.material_index])
    me.materials.clear()                     # (this resets material_index)
    for m in uniq:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", new_index)
    me.update()
    col = me.color_attributes.new("Color 1", "BYTE_COLOR", "CORNER")
    col.data.foreach_set("color", [1.0] * (4 * len(me.loops)))


def make_model(SZ, ob, drawable):
    ob.parent = drawable
    m = ob.modifiers.new("Armature", "ARMATURE")
    m.object = drawable
    SZ.convert_obj_to_model(ob)
    ob.name = drawable.name + ".model"


# ==========================================================================
# Animation clip dictionary
# ==========================================================================
def bake_clip(rig, arm_ob, clip, bones):
    """Copy clip `clip` from the model rig onto the export armature, one key
    per frame (the rest poses of these bones are identical)."""
    sc = bpy.context.scene
    src = bpy.data.actions[clip]
    act = bpy.data.actions.new("gta_" + clip)
    ad = arm_ob.animation_data or arm_ob.animation_data_create()
    ad.action = act
    rig.animation_data.action = src
    A.reset_pose(rig)
    end = int(src.frame_range[1])
    for f in range(0, end + 1):
        sc.frame_set(f)
        for b in bones:
            s, d = rig.pose.bones[b], arm_ob.pose.bones[b]
            d.location, d.rotation_quaternion = s.location, s.rotation_quaternion
            d.keyframe_insert("location", frame=f, group=b)
            d.keyframe_insert("rotation_quaternion", frame=f, group=b)
    act.use_frame_range = True
    act.frame_start, act.frame_end = 0.0, float(end)
    ad.action = None
    rig.animation_data.action = None
    return act


def clip_dictionary(SZ, arm_ob, actions):
    ST = SZ.SollumType
    root = B.link(bpy.data.objects.new(ANIM_DICT, None))
    root.sollum_type = ST.CLIP_DICTIONARY
    anims = B.link(bpy.data.objects.new("Animations", None))
    anims.sollum_type = ST.ANIMATIONS
    anims.parent = root
    clips = B.link(bpy.data.objects.new("Clips", None))
    clips.sollum_type = ST.CLIPS
    clips.parent = root
    for name, act in actions.items():
        a = B.link(bpy.data.objects.new("anim_" + name, None))
        a.sollum_type = ST.ANIMATION
        a.parent = anims
        ap = a.animation_properties
        ap.hash = name + "_anim"
        ap.target_id_type = "ARMATURE"
        ap.target_id = arm_ob.data
        ap.action = act
        c = B.link(bpy.data.objects.new(name, None))
        c.sollum_type = ST.CLIP
        c.parent = clips
        cp = c.clip_properties
        cp.hash, cp.name = name, name
        cp.duration = act.frame_range[1] / A.FPS
        ca = cp.animations.add()
        ca.animation = a
        ca.start_frame, ca.end_frame = act.frame_range
    return root


# ==========================================================================
# metadata files
# ==========================================================================
META_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_resource_files(folder):
    import fivem_meta as FM
    for fname, text in FM.metas(WEAPON, MODEL, MAG_MODEL, CLIP_COMPONENT,
                                CLIP_SIZE).items():
        write(os.path.join(folder, "meta", fname), META_HEADER + text)
    write(os.path.join(folder, "fxmanifest.lua"), FM.fxmanifest(
        WEAPON, f"{DISPLAY_NAME} - add-on weapon {WEAPON}"))
    write(os.path.join(folder, "config.lua"), FM.config_lua(DISPLAY_NAME))
    write(os.path.join(folder, "client.lua"), FM.client_lua(
        WEAPON, CLIP_COMPONENT, ANIM_DICT, CLIP_SIZE))


def render_icon(path, res=(512, 320)):
    """Side view on a transparent background (inventory icon)."""
    B.setup_scene()
    sc = bpy.context.scene
    sc.use_nodes = False                     # keep the alpha channel
    tgt_mm, dist, yaw, elev, lens, ortho = B.VIEWS["left"]
    tgt = B.mm(*tgt_mm)
    sc.camera = B.add_camera("IconCam", tgt + B.sph(dist, yaw, elev), tgt,
                             lens, ortho * 1.06)
    B.aim_light_rig(tgt, yaw)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.cycles.samples = 96
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)


# ==========================================================================
def run_cwxml2bin(files, out):
    exe = _arg("--cwxml2bin") or os.path.join(
        ROOT, "tools", "cwxml2bin", "bin", "Release", "net8.0", "cwxml2bin")
    for f in files:
        r = subprocess.run([exe, f, out], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        if r.returncode != 0:
            raise SystemExit(f"cwxml2bin failed for {f}:\n{r.stderr}")


def main():
    rig, objs, _ = B.build_model()      # resets Blender (factory settings)
    A.create_actions(rig)
    render_icon(os.path.join(OUT, "images", WEAPON.lower() + ".png"))
    SZ = enable_sollumz()
    by_name = {o.name: o for o in objs}

    shutil.rmtree(XML, ignore_errors=True)
    os.makedirs(XML)
    tex_dir = os.path.join(XML, MODEL)             # cwxml2bin texture folder
    tex = make_textures(tex_dir)
    tpath = {n: os.path.join(tex_dir, n + ".dds") for n in tex}
    mats = {
        "main": gta_material(SZ, "glock17_main", {
            "DiffuseSampler": tpath["glock17_pal_d"],
            "BumpSampler": tpath["glock17_flat_n"],
            "SpecSampler": tpath["glock17_pal_s"]}),
        "slide": gta_material(SZ, "glock17_slide", {
            "DiffuseSampler": tpath["glock17_slide_d"],
            "BumpSampler": tpath["glock17_slide_n"],
            "SpecSampler": tpath["glock17_slide_s"]}),
        "grip": gta_material(SZ, "glock17_grip", {
            "DiffuseSampler": tpath["glock17_grip_d"],
            "BumpSampler": tpath["glock17_grip_n"],
            "SpecSampler": tpath["glock17_grip_s"]}),
    }

    # ---- weapon drawable (skinned to the pistol skeleton)
    rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}
    parents = {b[0]: b[1] for b in G.GTA_BONES}
    wbones = [(n, parents[n]) for n in WEAPON_BONES]
    weapon = gta_armature(SZ, MODEL, wbones, rest)
    wmesh = joined_copy([by_name[n] for n in WEAPON_PARTS], MODEL + "_mesh",
                        WEAPON_PARTS)
    assign_gta_materials(wmesh, mats)
    make_model(SZ, wmesh, weapon)

    # ---- magazine drawable: root bone AAPClip = the weapon's WAPClip
    clip_at = rest["WAPClip"].translation.copy()
    mag = gta_armature(SZ, MAG_MODEL, [("AAPClip", None)],
                       {"AAPClip": Matrix.Identity(4)})
    mmesh = joined_copy([by_name[n] for n in MAG_PARTS], MAG_MODEL + "_mesh",
                        {n: "AAPClip" for n in MAG_PARTS},
                        Matrix.Translation(-clip_at))
    assign_gta_materials(mmesh, mats)
    make_model(SZ, mmesh, mag)

    # ---- clips for the in-game bones
    moving = [b for b in WEAPON_BONES
              if b in ("Gun_Cock1", "Gun_Trigger_Pr", "Gun_Barrel",
                       "Gun_SlideStop", "Gun_MagRelease", "WAPClip")]
    gta_actions = {c: bake_clip(rig, weapon, c, moving) for c in A.CLIPS}
    cd = clip_dictionary(SZ, weapon, gta_actions)

    # ---- export XML with Sollumz, then the texture dictionaries
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in (weapon, mag, cd):
        o.select_set(True)
    res = bpy.ops.sollumz.export_assets(
        directory=XML, direct_export=True, use_custom_settings=True,
        target_formats={"CWXML"}, target_versions={"GEN8"},
        limit_to_selected=True, apply_transforms=False)
    print("sollumz export:", res)
    xml_files = []
    for dirpath, _, files in os.walk(XML):
        for f in files:
            if f.endswith(".xml"):
                xml_files.append(os.path.join(dirpath, f))
    print("xml:", xml_files)

    all_tex = list(tex.values())
    write_ytd_xml(os.path.join(XML, MODEL + ".ytd.xml"), all_tex)
    mag_tex = [tex[n] for n in ("glock17_pal_d", "glock17_pal_s", "glock17_flat_n")]
    os.makedirs(os.path.join(XML, MAG_MODEL), exist_ok=True)
    for t in mag_tex:
        shutil.copyfile(tpath[t["name"]], os.path.join(XML, MAG_MODEL,
                                                       t["name"] + ".dds"))
    write_ytd_xml(os.path.join(XML, MAG_MODEL + ".ytd.xml"), mag_tex)

    stream = os.path.join(OUT, "stream")
    shutil.rmtree(stream, ignore_errors=True)
    os.makedirs(stream)
    ydr = [f for f in xml_files if f.endswith(".ydr.xml")]
    ycd = [f for f in xml_files if f.endswith(".ycd.xml")]
    run_cwxml2bin(ydr + ycd + [os.path.join(XML, MODEL + ".ytd.xml"),
                               os.path.join(XML, MAG_MODEL + ".ytd.xml")], stream)
    # first-person / close-up versions use the same model and textures
    shutil.copyfile(os.path.join(stream, MODEL + ".ydr"),
                    os.path.join(stream, MODEL + "_hi.ydr"))
    shutil.copyfile(os.path.join(stream, MODEL + ".ytd"),
                    os.path.join(stream, MODEL + "+hi.ytd"))

    # textures without the GLOCK markings (copy over stream/ to use them)
    ub_xml = os.path.join(XML, "unbranded")
    ub_tex = make_textures(os.path.join(ub_xml, MODEL), unbranded=True)
    write_ytd_xml(os.path.join(ub_xml, MODEL + ".ytd.xml"), list(ub_tex.values()))
    ub_out = os.path.join(OUT, UNBRANDED)
    shutil.rmtree(ub_out, ignore_errors=True)
    run_cwxml2bin([os.path.join(ub_xml, MODEL + ".ytd.xml")], ub_out)
    shutil.copyfile(os.path.join(ub_out, MODEL + ".ytd"),
                    os.path.join(ub_out, MODEL + "+hi.ytd"))

    write_resource_files(OUT)
    if "--keep-xml" not in B.ARGS:
        shutil.rmtree(XML, ignore_errors=True)
    print("done:", OUT)


if __name__ == "__main__":
    code = 0
    try:
        main()
    except SystemExit as e:
        print(e)
        code = e.code if isinstance(e.code, int) else 1
    except Exception:                                  # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(code)      # Sollumz keeps a thread alive: do not hang on exit
