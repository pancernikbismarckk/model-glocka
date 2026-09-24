"""
Glock 17 Gen4 - animation clips for the rigged model (Blender actions).

Clips (30 fps):
  fire          one shot: trigger safety and trigger, muzzle flash, slide
                cycle, barrel unlock/lock, extraction and ejection of the
                empty case, feeding the next round, trigger reset
  fire_empty    last shot: as fire, but the slide stop rises and holds the
                slide open (the magazine is empty)
  reload        magazine change with a round in the chamber
  reload_empty  magazine change from slide lock, then slide release

Every clip only moves bones of the armature (see glock_data.GTA_BONES), so
the clips export unchanged to glTF, FBX and GTA V (.ycd).  Motions are
written as functions of time and sampled (quarter frames for the fast firing
cycle, so slow-motion renders stay smooth).
"""
import math

import bpy
from mathutils import Matrix, Vector

import glock_data as G

FPS = 30
CLIPS = ["fire", "fire_empty", "reload", "reload_empty"]

# scene axes (GTA V orientation: X = muzzle, Y = left, Z = up)
FORWARD = Vector((1.0, 0.0, 0.0))
BACK = -FORWARD
RIGHT = Vector((0.0, -1.0, 0.0))
UP = Vector((0.0, 0.0, 1.0))
AXIS_Y = Vector((0.0, 1.0, 0.0))

T_SHOT = 3.0            # frame of the shot (trigger breaks)
FLASH_ON = 1.0 / G.FLASH_REST_SCALE


def xf_point(p):
    """Build mm -> scene metres (same mapping as build_glock17.XF)."""
    o = G.GTA_ORIGIN_MM
    return Vector(((o[0] - p[0]) / 1000.0, (o[1] - p[1]) / 1000.0,
                   (p[2] - o[2]) / 1000.0))


MAG_DROP = Vector((-G.MAG_DROP_DIR[0], -G.MAG_DROP_DIR[1], G.MAG_DROP_DIR[2]))
TRIGGER_PIN = xf_point((106.0, 0.0, -24.0))


# --------------------------------------------------------------------------
# easing and the shared motions
# --------------------------------------------------------------------------
def clamp01(u):
    return max(0.0, min(1.0, u))


def ramp(t, t0, t1):
    return clamp01((t - t0) / (t1 - t0))


def smooth(u):
    u = clamp01(u)
    return u * u * (3.0 - 2.0 * u)


def ease_out(u):
    u = clamp01(u)
    return 1.0 - (1.0 - u) ** 2


def ease_in(u):
    u = clamp01(u)
    return u * u


def slide_stroke(t, t0=T_SHOT, back=2.0, fwd=3.0, stop=0.0):
    """Slide travel (mm) for a recoil cycle starting at t0: rearward in
    `back` frames (the spring decelerates it), forward in `fwd` frames
    (accelerating) until it reaches `stop` (0 = in battery)."""
    S = G.SLIDE_TRAVEL
    if t <= t0:
        return 0.0
    if t <= t0 + back:
        return S * ease_out((t - t0) / back)
    u = (t - t0 - back) / fwd
    return max(stop, S - (S - 0.0) * ease_in(u)) if u < 1.0 else stop


def slide_return(t, t0, dur, s0):
    """Slide running forward from s0 (mm) at t0 into battery."""
    if t <= t0:
        return s0
    return s0 * (1.0 - ease_in((t - t0) / dur))


def barrel_motion(s, closing):
    """Barrel travel (mm) and tilt (degrees) for slide travel s.  The barrel
    stays locked for the first 3 mm, then drops at the rear and stops."""
    b = min(s, G.BARREL_TRAVEL)
    tilt = G.BARREL_TILT * smooth((s - G.BARREL_TRAVEL) / 2.5)
    return b, tilt


def feed_fraction(s):
    """How far the next round has been pushed from the magazine into the
    chamber when the returning slide is at travel s (mm)."""
    head_rest = G.MAG_ROUND_HEAD_X
    breech = G.PORT_X1 + s                       # breech face (build X)
    span = head_rest - G.PORT_X1
    return clamp01((head_rest - breech) / span)


def round_motion(phi):
    """Top round moving up the feed ramp into the chamber (0..1)."""
    dx = (G.MAG_ROUND_HEAD_X - G.PORT_X1) * phi
    dz = (G.BORE_Z - G.MAG_ROUND_Z) * smooth(phi)
    tilt = -9.0 * math.sin(math.pi * phi)        # nose up while feeding
    return FORWARD * dx / 1000.0 + UP * dz / 1000.0, tilt


# ejection of the empty case: ballistic flight after the ejector strikes
EJECT_AT = 24.0                          # slide travel (mm) at ejection
EJECT_V = Vector((-0.5, -1.7, 1.4))      # m/s: back, to the right, up
EJECT_W = Vector((0.0, -11.0, -38.0))    # rad/s: tumbling, mouth swings right
GRAVITY = Vector((0.0, 0.0, -9.81))


def eject_time(t_shot, back=2.0):
    """Frame at which the slide passes EJECT_AT on its way back."""
    u = 1.0 - math.sqrt(1.0 - EJECT_AT / G.SLIDE_TRAVEL)
    return t_shot + back * u


def casing_pose(t, t_shot, s_of_t):
    """(location, (axis, degrees)) of the case at frame t."""
    te = eject_time(t_shot)
    if t <= t_shot:
        return Vector(), None
    if t <= te:
        return BACK * s_of_t(t) / 1000.0, None
    dt = (t - te) / FPS
    p0 = BACK * EJECT_AT / 1000.0
    loc = p0 + EJECT_V * dt + 0.5 * GRAVITY * dt * dt
    w = EJECT_W.length
    return loc, (EJECT_W.normalized(), math.degrees(w * dt))


# --------------------------------------------------------------------------
# keying
# --------------------------------------------------------------------------
class Clip:
    """Samples bone motions into a new action on the rig.

    A motion is a function t -> dict with optional keys
      loc   : Vector, scene-space translation (metres)
      rot   : (axis, degrees[, pivot]) scene-space rotation about pivot
              (default: the bone head)
      scale : uniform scale about the bone head
    expressed relative to the rest pose (children: relative to the parent)."""

    def __init__(self, rig, name, end):
        self.rig = rig
        self.name = name
        self.end = end
        self.motions = {}
        self.rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}

    def add(self, bone, fn, step=1.0, extra=()):
        """Sample fn every `step` frames, plus at the `extra` frames (used
        right before a jump, so the jump happens between two samples)."""
        self.motions[bone] = (fn, step, tuple(extra))

    def pose_basis(self, bone, m):
        R = self.rest[bone]
        head = R.translation
        D = Matrix.Translation(m.get("loc", Vector()))
        rot = m.get("rot")
        if rot and abs(rot[1]) > 1e-9:
            axis, deg = rot[0], rot[1]
            pv = Vector(rot[2]) if len(rot) > 2 else head
            D = D @ (Matrix.Translation(pv)
                     @ Matrix.Rotation(math.radians(deg), 4, Vector(axis))
                     @ Matrix.Translation(-pv))
        s = m.get("scale", 1.0)
        if s != 1.0:
            D = D @ (Matrix.Translation(head) @ Matrix.Scale(s, 4)
                     @ Matrix.Translation(-head))
        return R.inverted() @ D @ R

    def hold_rest(self, bones):
        """Key the rest pose on `bones` this clip does not move, so every
        clip sets all moving parts (no leftovers when switching clips)."""
        for b in bones:
            if b not in self.motions:
                self.add(b, lambda t: {}, self.end)

    def build(self):
        act = bpy.data.actions.new(self.name)
        act.use_fake_user = True
        ad = self.rig.animation_data or self.rig.animation_data_create()
        ad.action = act
        for bone, (fn, step, extra) in self.motions.items():
            pb = self.rig.pose.bones[bone]
            last_q = None
            n = int(round(self.end / step))
            times = sorted({min(i * step, self.end) for i in range(n + 1)}
                           | set(extra))
            for t in times:
                basis = self.pose_basis(bone, fn(t))
                loc, q, sc = basis.decompose()
                if last_q is not None and q.dot(last_q) < 0.0:
                    q.negate()
                last_q = q
                pb.location, pb.rotation_quaternion, pb.scale = loc, q, sc
                for path in ("location", "rotation_quaternion", "scale"):
                    pb.keyframe_insert(path, frame=t, group=bone)
        for fc in fcurves(act):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
        act.use_frame_range = True
        act.frame_start, act.frame_end = 0.0, float(self.end)
        ad.action = None
        reset_pose(self.rig)
        return act


def fcurves(action):
    if hasattr(action, "layers") and bpy.app.version >= (5, 0, 0):
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
    else:
        yield from action.fcurves


def reset_pose(rig):
    for pb in rig.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)


# --------------------------------------------------------------------------
# clips
# --------------------------------------------------------------------------
def add_trigger_pull(c, t_press, t_release):
    """Trigger safety pressed flush, trigger pulled to the break at T_SHOT,
    held and released (the trigger resets forward)."""
    def safety(t):
        a = 6.0 * (smooth(ramp(t, t_press, t_press + 1.0))
                   - smooth(ramp(t, t_release + 2.0, t_release + 3.0)))
        return {"rot": (AXIS_Y, a)}

    def trigger(t):
        a = 17.0 * (smooth(ramp(t, t_press + 0.5, T_SHOT))
                    - smooth(ramp(t, t_release, t_release + 3.0)))
        return {"rot": (AXIS_Y, a, TRIGGER_PIN)}
    c.add("Gun_TriggerSafety", safety, 0.25)
    c.add("Gun_Trigger_Pr", trigger, 0.25)


def add_flash(c):
    keys = [(T_SHOT - 0.25, 1.0), (T_SHOT, FLASH_ON), (T_SHOT + 0.5, FLASH_ON * 1.15),
            (T_SHOT + 1.0, FLASH_ON * 0.55), (T_SHOT + 1.25, 1.0)]

    def flash(t):
        if t <= keys[0][0] or t >= keys[-1][0]:
            return {}
        for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
            if t0 <= t <= t1:
                return {"scale": v0 + (v1 - v0) * (t - t0) / (t1 - t0),
                        "rot": (FORWARD, 25.0)}
        return {}
    c.add("Gun_Flash", flash, 0.25)


def add_barrel(c, s_of_t, t_close):
    def barrel(t):
        b, tilt = barrel_motion(s_of_t(t), t >= t_close)
        return {"loc": BACK * b / 1000.0, "rot": (AXIS_Y, -tilt)}
    c.add("Gun_Barrel", barrel, 0.25)


def fire_clip(rig, empty=False):
    end = 21.0
    c = Clip(rig, "fire_empty" if empty else "fire", end)
    back, fwd = 2.0, 3.0
    t_back = T_SHOT + back
    if empty:
        def s_of_t(t):
            if t <= t_back:
                return slide_stroke(t, T_SHOT, back, fwd)
            u = smooth(ramp(t, t_back, t_back + 1.5))
            return G.SLIDE_TRAVEL - (G.SLIDE_TRAVEL - G.SLIDE_LOCK_TRAVEL) * u
    else:
        def s_of_t(t):
            return slide_stroke(t, T_SHOT, back, fwd)

    c.add("Gun_Cock1", lambda t: {"loc": BACK * s_of_t(t) / 1000.0}, 0.25)
    add_barrel(c, s_of_t, t_back)
    add_trigger_pull(c, 0.0, 9.0)
    add_flash(c)

    def casing(t):
        loc, rot = casing_pose(t, T_SHOT, s_of_t)
        return {"loc": loc, "rot": rot} if rot else {"loc": loc}
    c.add("Gun_Shell", casing, 0.25)

    if empty:
        # the follower lifts the slide stop as the slide passes over it
        def stop(t):
            return {"rot": (AXIS_Y, 6.0 * smooth(ramp(t, T_SHOT + 1.2,
                                                      T_SHOT + 2.0)))}
        c.add("Gun_SlideStop", stop, 0.25)
        c.add("Gun_MagRound", lambda t: {"scale": 0.001}, end)
    else:
        def rnd(t):
            if t >= t_back + fwd + 0.25:            # the next round in place
                return {}
            loc, tilt = round_motion(feed_fraction(s_of_t(t))
                                     if t > t_back else 0.0)
            return {"loc": loc, "rot": (AXIS_Y, tilt)}
        c.add("Gun_MagRound", rnd, 0.25)
    return c


def mag_drop(t, t0):
    """Magazine falling free out of the grip (metres along the grip axis),
    tipping forward once clear."""
    if t <= t0:
        return {}
    dt = (t - t0) / FPS
    d = 0.5 * 9.81 * dt * dt + 0.25 * dt
    tip = 25.0 * smooth((d - 0.10) / 0.25)
    return {"loc": MAG_DROP * d, "rot": (AXIS_Y, tip)}


def mag_insert(t, t_in, t_seat):
    """New magazine brought up to the grip and pushed home."""
    far, near = 0.095, 0.022
    t_mid = t_seat - 4.0
    if t < t_in:
        return {"loc": MAG_DROP * 0.9}
    if t < t_mid:
        u = smooth(ramp(t, t_in, t_mid))
        d = far + (near - far) * u
        return {"loc": MAG_DROP * d, "rot": (AXIS_Y, 7.0 * (1.0 - u))}
    u = ease_in(ramp(t, t_mid, t_seat))
    d = near * (1.0 - u)
    bounce = 0.0012 * math.sin(math.pi * ramp(t, t_seat, t_seat + 2.0))
    return {"loc": MAG_DROP * (d + bounce)}


def reload_clip(rig, empty=False):
    end = 64.0 if empty else 52.0
    c = Clip(rig, "reload_empty" if empty else "reload", end)
    t_drop, t_in, t_seat = 3.0, 20.0, 40.0

    def catch(t):
        press = (smooth(ramp(t, 0.0, 3.0)) - smooth(ramp(t, 15.0, 18.0))) * 2.0
        click = 1.1 * math.sin(math.pi * ramp(t, t_seat - 1.0, t_seat + 1.5))
        return {"loc": RIGHT * (press + click) / 1000.0}
    c.add("Gun_MagRelease", catch, 1.0)

    def mag(t):
        if t < t_in - 0.02:
            m = mag_drop(t, t_drop)
            if m.get("loc") is not None and m["loc"].length > 0.9:
                m["loc"] = MAG_DROP * 0.9
            return m
        return mag_insert(t, t_in, t_seat)
    c.add("WAPClip", mag, 1.0, extra=[t_in - 0.05])

    if empty:
        t_rel, t_home = 46.0, 49.0            # slide stop pressed, released

        def s_of_t(t):
            return slide_return(t, t_home, 3.0, G.SLIDE_LOCK_TRAVEL)
        c.add("Gun_Cock1", lambda t: {"loc": BACK * s_of_t(t) / 1000.0}, 0.25)

        def stop(t):
            return {"rot": (AXIS_Y, 6.0 * (1.0 - smooth(ramp(t, t_rel, t_home))))}
        c.add("Gun_SlideStop", stop, 0.25)

        def barrel(t):
            s = s_of_t(t)
            b, tilt = barrel_motion(s, True)
            return {"loc": BACK * b / 1000.0, "rot": (AXIS_Y, -tilt)}
        c.add("Gun_Barrel", barrel, 0.25)

        def rnd(t):
            if t < t_in - 0.02:
                return {"scale": 0.001}          # the empty magazine
            if t >= t_home + 3.25:
                return {}
            s = s_of_t(t)
            loc, tilt = round_motion(feed_fraction(s) if t > t_home else 0.0)
            return {"loc": loc, "rot": (AXIS_Y, tilt)}
        c.add("Gun_MagRound", rnd, 0.25, extra=[t_in - 0.05])
    return c


def create_actions(rig):
    """Create all clips; returns {name: action}.  The rig is left in the rest
    pose with no active action."""
    sc = bpy.context.scene
    sc.render.fps, sc.render.fps_base = FPS, 1.0
    clips = [fire_clip(rig), fire_clip(rig, empty=True), reload_clip(rig),
             reload_clip(rig, empty=True)]
    moving = sorted({b for c in clips for b in c.motions})
    acts = {}
    for c in clips:
        c.hold_rest(moving)
        acts[c.name] = c.build()
    # an NLA track per clip keeps the actions attached to the rig (exporters
    # and the Blender UI list them); the tracks are muted
    ad = rig.animation_data
    for name in CLIPS:
        tr = ad.nla_tracks.new()
        tr.name = name
        st = tr.strips.new(name, 0, acts[name])
        st.action_frame_end = acts[name].frame_range[1]
        tr.mute = True
    return acts


def play(rig, name):
    """Make clip `name` the active action and set the scene frame range."""
    act = bpy.data.actions[name]
    rig.animation_data.action = act
    sc = bpy.context.scene
    sc.frame_start = int(act.frame_range[0])
    sc.frame_end = int(act.frame_range[1])
    sc.render.fps = FPS
    return act
