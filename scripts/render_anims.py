"""
Render the animation previews (requires the bpy module or Blender 4.2+).

  python scripts/render_anims.py [--quick] [--clips=fire,reload,...]
                                 [--frames=a,b,...]   (single test frames)

For every preview in PREVIEWS: renders/anim_<name>.gif (for the README) and
renders/anim_<name>.mp4 (H.264).  The firing clips are rendered in slow
motion (every quarter frame), so the slide cycle and the ejected case can
be followed.
"""
import math
import os
import shutil
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_glock17 as B  # noqa: E402
import glock_anim as A  # noqa: E402

ARGS = B.ARGS
QUICK = "--quick" in ARGS
ONLY = [c for c in B._arg("--clips", "").split(",") if c]
TEST_FRAMES = [float(f) for f in B._arg("--frames", "").split(",") if f]
OUT = B.RENDER_DIR
TMP = os.path.join(OUT, "_frames")

# name: (clip, (target mm, distance m, yaw, elevation, lens), slow-motion,
#        frame of the still used on the contact sheet)
PREVIEWS = {
    "fire": ("fire", ((95.0, 60.0, -15.0), 1.05, 240.0, 26.0, 100), 4, 5.5),
    "fire_empty": ("fire_empty", ((75.0, 0.0, -45.0), 0.90, 150.0, 14.0, 100),
                   2, 3.5),
    "reload": ("reload", ((140.0, 0.0, -92.0), 1.05, 22.0, -6.0, 100), 1, 30.0),
    "reload_empty": ("reload_empty", ((118.0, 0.0, -78.0), 1.05, 150.0, 8.0,
                                      100), 1, 50.0),
}


def dress_flash():
    """Blender-only look of the muzzle flash: hot core fading to orange and
    transparent tips (the exported material is a plain emissive one)."""
    mat = bpy.data.materials["Muzzle_Flash"]
    nt = mat.node_tree
    out = nt.nodes["Material Output"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, (1.0, 0.92, 0.65, 1.0)
    els[1].position, els[1].color = 1.0, (0.95, 0.22, 0.03, 1.0)
    mid = els.new(0.35)
    mid.color = (1.0, 0.55, 0.12, 1.0)
    nt.links.new(sep.outputs["X"], ramp.inputs["Fac"])
    strength = nt.nodes.new("ShaderNodeMapRange")
    strength.inputs["To Min"].default_value = 7.0
    strength.inputs["To Max"].default_value = 2.0
    nt.links.new(sep.outputs["X"], strength.inputs["Value"])
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
    nt.links.new(strength.outputs["Result"], emit.inputs["Strength"])
    alpha = nt.nodes.new("ShaderNodeMapRange")
    alpha.inputs["From Min"].default_value = 0.45
    alpha.inputs["From Max"].default_value = 1.0
    alpha.inputs["To Min"].default_value = 1.0
    alpha.inputs["To Max"].default_value = 0.0
    nt.links.new(sep.outputs["X"], alpha.inputs["Value"])
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(alpha.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(transp.outputs["BSDF"], mix.inputs[1])
    nt.links.new(emit.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


def flash_light(rig):
    """Point light at the muzzle, keyed on the firing clips' flash."""
    ld = bpy.data.lights.new("FlashLight", "POINT")
    ld.color = (1.0, 0.55, 0.2)
    ld.shadow_soft_size = 0.004
    ob = B.link(bpy.data.objects.new("FlashLight", ld))
    ob.location = rig.data.bones["Gun_Muzzle"].head_local + Vector((0.02, 0.0, 0.0))
    return ld


def key_flash_light(ld, clip):
    ld.animation_data_clear()
    ld.energy = 0.0
    if not clip.startswith("fire"):
        return
    t0 = A.T_SHOT
    for t, e in ((t0 - 0.25, 0.0), (t0, 0.5), (t0 + 0.5, 0.4), (t0 + 1.0, 0.15),
                 (t0 + 1.25, 0.0)):
        ld.energy = e
        ld.keyframe_insert("energy", frame=t)


def set_camera(view):
    tgt_mm, dist, yaw, elev, lens = view
    tgt = B.mm(*tgt_mm)
    cam = B.add_camera("AnimCam", tgt + B.sph(dist, yaw, elev), tgt, lens)
    B.aim_light_rig(tgt, yaw)
    bpy.context.scene.camera = cam
    return cam


def render_frames(rig, name, clip, view, slow, res, samples, frames=None):
    sc = bpy.context.scene
    A.reset_pose(rig)
    A.play(rig, clip)
    key_flash_light(bpy.data.lights["FlashLight"], clip)
    cam = set_camera(view)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    act = bpy.data.actions[clip]
    end = act.frame_range[1]
    times = frames or [k / slow for k in range(int(round(end * slow)) + 1)]
    folder = os.path.join(TMP, name)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    paths = []
    for i, t in enumerate(times):
        sc.frame_set(int(math.floor(t)), subframe=t - math.floor(t))
        sc.render.filepath = os.path.join(folder, f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
        paths.append(sc.render.filepath)
    bpy.data.objects.remove(cam)
    return paths


def write_gif(paths, out, fps=30, hold_last=0.6):
    from PIL import Image
    frames = [Image.open(p).convert("RGB") for p in paths]
    pal = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT,
                      dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    dur = [int(round(1000 / fps))] * len(pal)
    dur[-1] += int(hold_last * 1000)
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=dur,
                loop=0, optimize=True, disposal=1)
    return out


def write_mp4(paths, out, fps=30):
    """Encode the PNG frames with Blender's FFmpeg (H.264)."""
    src = bpy.context.scene
    sc = bpy.data.scenes.new("encode")
    sc.render.resolution_x = src.render.resolution_x
    sc.render.resolution_y = src.render.resolution_y
    sc.render.resolution_percentage = 100
    sc.render.fps, sc.render.fps_base = fps, 1.0
    sc.view_settings.view_transform = "Standard"
    se = sc.sequence_editor_create()
    strips = getattr(se, "strips", None) or se.sequences
    st = strips.new_image("frames", paths[0], channel=1, frame_start=1)
    for p in paths[1:]:
        st.elements.append(os.path.basename(p))
    sc.frame_start, sc.frame_end = 1, len(paths)
    im = sc.render.image_settings
    im.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.ffmpeg_preset = "GOOD"
    sc.render.filepath = out
    sc.render.use_file_extension = False
    bpy.ops.render.render(animation=True, scene=sc.name)
    bpy.data.scenes.remove(sc)
    return out


def main():
    rig, objs, _ = B.build_model()
    A.create_actions(rig)
    B.setup_scene()
    dress_flash()
    flash_light(rig)
    sc = bpy.context.scene
    sc.render.use_persistent_data = True
    res, samples = ((640, 400), 12) if QUICK else ((960, 600), 40)
    names = ONLY or list(PREVIEWS)
    for name in names:
        clip, view, slow, still = PREVIEWS[name]
        if B._arg("--view", ""):            # try another camera (tests)
            v = [float(x) for x in B._arg("--view", "").split(",")]
            view = ((v[0], v[1], v[2]), v[3], v[4], v[5], 100)
        if TEST_FRAMES:
            paths = render_frames(rig, name, clip, view, slow, res, samples,
                                  TEST_FRAMES)
            tag = B._arg("--tag", "")
            for p, t in zip(paths, TEST_FRAMES):
                shutil.copyfile(p, os.path.join(TMP, f"{name}{tag}_{t:g}.png"))
            continue
        paths = render_frames(rig, name, clip, view, slow, res, samples)
        print("gif:", write_gif(paths, os.path.join(OUT, f"anim_{name}.gif")))
        print("mp4:", write_mp4(paths, os.path.join(OUT, f"anim_{name}.mp4")))
        # the most telling moment, for the contact sheet
        shutil.copyfile(paths[min(int(round(still * slow)), len(paths) - 1)],
                        os.path.join(OUT, f"anim_{name}_still.png"))
    if not TEST_FRAMES:
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
