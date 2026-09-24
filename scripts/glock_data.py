"""
Glock 17 Gen4 - shared dimension data and pure-python geometry helpers.

All values are in millimetres. Build coordinate system:
  X - along the bore, 0 = slide front face, +X towards the rear (grip)
  Y - lateral; the pistol's LEFT side (slide stop, magazine catch) is -Y
  Z - vertical, 0 = top of the slide, +Z up

Profiles were measured from the official GLOCK dimension sheet side view
(0.3537 mm/px; slide 186 mm, overall length 202 mm, height 139 mm,
slide width 25.5 mm) and cross-checked against the product photo.
This module has no Blender dependency so the texture generator can use it.
"""
import math

# --------------------------------------------------------------------------
# Main dimensions
# --------------------------------------------------------------------------
SLIDE_LEN = 185.5          # slide front face -> rear face
SLIDE_H = 20.34            # height of the slide side walls
SLIDE_HW = 12.75           # half of the 25.5 mm slide width
SLIDE_TOP_HW = 10.0        # half width of the flat top (top edges are chamfered)
SLIDE_CHAMFER_Z = -3.3     # where the top chamfer meets the side
BORE_Z = -10.8             # bore axis height
BARREL_R = 6.7             # barrel outer radius at the muzzle
FRAME_TOP = -20.45         # frame top (small gap under the slide)

# Slide serrations: 7 grooves on each side of the rear of the slide
SERR_X0 = 143.2
SERR_PITCH = 5.01
SERR_W = 2.97
SERR_COUNT = 7
SERR_DEPTH = 0.9

# Ejection port (right side / top)
PORT_X0, PORT_X1 = 81.6, 115.3
PORT_Z_BOTTOM = -12.6

# Sights (polymer, factory)
FRONT_SIGHT = dict(x0=7.4, x1=12.8, top=2.85, hw=1.65)
REAR_SIGHT = dict(x0=170.3, x1=177.2, top=4.24, hw_base=9.0, hw_top=7.25,
                  notch_hw=1.7, notch_depth=2.4)

# Markings on the left side of the slide (X range, Z range) - used by the
# texture generator.  Positions measured from the dimension sheet.
MARKINGS = {
    "logo": (14.1, 24.8, -15.5, -7.5),
    "17": (31.4, 35.8, -13.7, -8.4),
    "Gen4": (37.1, 45.6, -13.7, -10.6),
    "AUSTRIA": (51.1, 65.6, -13.1, -10.2),
    "9x19": (82.7, 91.1, -13.3, -9.7),
}

# Slide-side texture: planar projection of the left side of the slide
SLIDE_TEX_W, SLIDE_TEX_H = 4096, 512
SLIDE_TEX_MM_PER_PX = 0.05                 # 204.8 x 25.6 mm
SLIDE_TEX_Z0 = -23.0                       # Z at the bottom edge of the texture

# Grip texture: U = arc length around the grip section, V = Z
GRIP_TEX_SIZE = 2048
GRIP_TEX_MM_PER_PX = 0.1                   # 204.8 x 204.8 mm
GRIP_TEX_Z0 = -130.0                       # Z at the bottom edge of the texture


# --------------------------------------------------------------------------
# Small math helpers
# --------------------------------------------------------------------------
def pchip(xs, ys):
    """Monotone cubic (PCHIP) interpolator through (xs, ys); xs ascending."""
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1 = 2 * h[i] + h[i - 1]
            w2 = h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        lo, hi = 0, n - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        i = lo
        t = (x - xs[i]) / h[i]
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1
        h10 = t ** 3 - 2 * t ** 2 + t
        h01 = -2 * t ** 3 + 3 * t ** 2
        h11 = t ** 3 - t ** 2
        return (h00 * ys[i] + h10 * h[i] * m[i] +
                h01 * ys[i + 1] + h11 * h[i] * m[i + 1])
    return f


def arc_pts(cx, cy, r, a0_deg, a1_deg, n):
    """Points on a circular arc from a0 to a1 (degrees), n segments."""
    out = []
    for k in range(n + 1):
        a = math.radians(a0_deg + (a1_deg - a0_deg) * k / n)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def rounded_poly(pts, seg90=6):
    """Closed polygon with filleted corners.

    pts: list of (x, y) or (x, y, r); r is the fillet radius of that corner.
    Returns a list of (x, y)."""
    out = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i - 1][:2]
        x1, y1 = pts[i][:2]
        r = pts[i][2] if len(pts[i]) > 2 else 0.0
        x2, y2 = pts[(i + 1) % n][:2]
        if r <= 0:
            out.append((x1, y1))
            continue
        ax, ay = x0 - x1, y0 - y1
        la = math.hypot(ax, ay)
        bx, by = x2 - x1, y2 - y1
        lb = math.hypot(bx, by)
        ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
        ang = math.acos(max(-1.0, min(1.0, ax * bx + ay * by)))
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append((x1, y1))
            continue
        t = r / math.tan(ang / 2)
        tmax = 0.5 * min(la, lb)
        if t > tmax:
            t = tmax
            r = t * math.tan(ang / 2)
        p1 = (x1 + ax * t, y1 + ay * t)
        p2 = (x1 + bx * t, y1 + by * t)
        bisx, bisy = ax + bx, ay + by
        lbis = math.hypot(bisx, bisy)
        dc = r / math.sin(ang / 2)
        cx, cy = x1 + bisx / lbis * dc, y1 + bisy / lbis * dc
        a1 = math.atan2(p1[1] - cy, p1[0] - cx)
        a2 = math.atan2(p2[1] - cy, p2[0] - cx)
        da = a2 - a1
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        nseg = max(1, int(math.ceil(abs(da) / (math.pi / 2) * seg90)))
        for k in range(nseg + 1):
            a = a1 + da * k / nseg
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def smooth_closed(pts, iterations=1):
    """Light Laplacian smoothing of a closed polyline."""
    for _ in range(iterations):
        n = len(pts)
        pts = [((pts[i - 1][0] + 2 * pts[i][0] + pts[(i + 1) % n][0]) / 4,
                (pts[i - 1][1] + 2 * pts[i][1] + pts[(i + 1) % n][1]) / 4)
               for i in range(n)]
    return pts


# --------------------------------------------------------------------------
# Frame side profiles (X, Z[, fillet r])
# --------------------------------------------------------------------------
# Dust cover with the accessory rail (23.5 mm wide)
DUSTCOVER = [
    (1.2, FRAME_TOP, 0.8),
    (64.0, FRAME_TOP, 0.0),
    (64.0, -38.3, 0.0),
    (56.0, -37.35, 12.0),
    (1.2, -37.1, 5.8),
]
DUSTCOVER_HW = 11.75

# Frame body above the trigger guard (26.5 mm wide); rear part hides in grip
FRAME_BODY = [
    (60.5, -20.55, 0.6),
    (160.0, -20.55, 0.0),
    (160.0, -45.0, 0.0),
    (117.6, -45.0, 0.0),
    (117.6, -39.8, 1.0),
    (84.0, -39.45, 0.0),
    (70.0, -38.9, 0.0),
    (60.5, -38.4, 0.6),
]
FRAME_BODY_HW = 13.25

# Trigger guard outer outline (13.8 mm wide).  The top part is hidden in the
# dust cover / frame body; the concave fillet under the dust cover is explicit.
# Keep the hidden band above the opening thicker than 2 x the edge bevel,
# otherwise the curve fill self-intersects and fills part of the opening.
TG_OUTER = (
    [(58.0, -30.0), (61.5, -30.0), (63.3, -37.4)]
    + arc_pts(64.1, -44.9, 7.0, 90, 0, 7)
    + rounded_poly([
        (70.0, -44.9),          # dummy neighbour (removed below)
        (71.1, -45.2, 0.0),
        (71.1, -54.0, 10.0),
        (68.5, -66.9, 3.2),
        (110.5, -66.9, 7.5),
        (119.8, -63.1, 0.0),
        (124.0, -62.0, 0.0),
    ], seg90=6)[1:]
    + [(124.0, -30.0)]
)

# Trigger guard opening (hole), explicit smooth outline
TG_HOLE = [
    (118.5, -37.2), (92.0, -37.2), (81.5, -37.2),
    (80.6, -39.2), (79.6, -40.4), (78.6, -41.5), (77.8, -42.6), (77.2, -43.8),
    (76.85, -45.0), (76.8, -54.3),
    (77.1, -55.5), (77.7, -56.6), (78.6, -57.6), (79.8, -58.6), (81.3, -59.5),
    (83.1, -60.3), (85.3, -60.9), (88.0, -61.2),
    (104.5, -61.2),
    (107.2, -61.0), (109.6, -60.5), (111.6, -59.7), (113.2, -58.7),
    (114.4, -57.5), (115.3, -56.2), (115.9, -54.9), (116.4, -53.4),
    (117.0, -51.5), (118.0, -49.0), (118.5, -46.5),
]
TG_HW = 6.9

# Trigger (7 mm wide); top part hidden inside the frame
TRIGGER = [
    (101.8, -38.0), (101.6, -39.6), (101.3, -44.0), (101.0, -47.5),
    (100.4, -50.3), (99.3, -51.9), (97.8, -53.5), (96.4, -55.2), (95.3, -56.8),
    (94.8, -58.2), (94.9, -59.4), (95.6, -60.3), (96.8, -60.75), (98.2, -60.6),
    (99.6, -59.9), (101.3, -58.9), (103.0, -57.9), (104.4, -56.7),
    (105.7, -55.3), (106.9, -53.8), (108.2, -52.4), (109.6, -50.9),
    (111.4, -49.8), (113.3, -48.9), (114.8, -47.9), (115.5, -46.5),
    (115.4, -44.5), (114.8, -41.5), (114.4, -38.0),
]
TRIGGER_HW = 3.5
# front edge of the trigger (subset) used to build the trigger safety blade
TRIGGER_FRONT = TRIGGER[2:13]

# Magazine floor plate (28.5 mm wide)
MAG_PLATE = [
    (150.7, -126.2, 0.6), (188.0, -126.2, 0.0), (189.8, -127.0, 0.0),
    (191.0, -128.4, 1.0), (191.5, -130.3, 0.0), (191.4, -132.5, 1.0),
    (190.4, -133.8, 0.8), (160.5, -133.8, 3.0), (153.2, -133.0, 1.5),
    (150.7, -131.2, 0.8),
]
MAG_PLATE_HW = 14.25

# --------------------------------------------------------------------------
# Grip (lofted from horizontal sections)
# --------------------------------------------------------------------------
_GRIP_FRONT = [  # (Z, X) front strap incl. Gen4 finger grooves
    (-20.45, 120.0), (-38.0, 118.4), (-45.0, 117.6), (-50.0, 117.4),
    (-53.5, 117.3), (-57.0, 117.5), (-60.0, 118.0), (-62.0, 118.8),
    (-63.3, 120.0), (-64.2, 122.0), (-65.2, 123.4), (-66.4, 124.6),
    (-68.0, 125.8), (-70.5, 126.9), (-73.5, 128.1), (-76.5, 129.1),
    (-78.8, 129.3), (-80.6, 128.7), (-82.0, 128.5), (-83.4, 129.7),
    (-85.2, 131.9), (-87.5, 133.7), (-90.5, 135.0), (-93.5, 135.8),
    (-95.5, 136.0), (-97.3, 135.4), (-98.8, 135.2), (-100.2, 136.4),
    (-102.2, 138.7), (-105.0, 140.6), (-108.5, 142.0), (-112.0, 143.2),
    (-115.0, 144.1), (-118.0, 144.4), (-121.0, 144.6), (-123.0, 145.2),
    (-124.5, 146.3), (-125.3, 147.2),
]
_GRIP_BACK = [  # (Z, X) backstrap incl. beavertail
    (-20.45, 185.6), (-21.6, 186.2), (-22.8, 186.8), (-24.3, 187.4),
    (-25.8, 187.8), (-27.0, 187.8), (-28.1, 187.4), (-29.1, 186.6),
    (-29.9, 185.3), (-30.5, 183.0), (-31.0, 180.0), (-31.6, 178.2),
    (-32.5, 176.6), (-33.6, 175.2), (-35.0, 173.9), (-36.6, 172.8),
    (-38.5, 172.1), (-41.0, 171.8), (-46.0, 171.8), (-49.5, 172.0),
    (-52.0, 172.7), (-55.0, 173.8), (-58.5, 175.1), (-62.0, 176.5),
    (-66.0, 178.2), (-70.0, 180.1), (-74.0, 182.0), (-78.0, 184.1),
    (-82.0, 186.4), (-86.0, 188.8), (-90.0, 191.2), (-94.0, 193.6),
    (-98.0, 195.7), (-102.0, 197.4), (-106.0, 198.9), (-110.0, 200.2),
    (-113.5, 201.0), (-116.5, 201.4), (-118.8, 201.3), (-120.6, 200.5),
    (-122.0, 199.3), (-123.3, 197.5), (-124.4, 195.4), (-125.3, 193.0),
]
_GRIP_WIDTH = [  # (Z, full width)
    (-20.45, 27.6), (-22.0, 28.4), (-24.0, 29.2), (-27.0, 29.4),
    (-30.0, 29.0), (-33.0, 28.5), (-42.0, 28.4), (-47.0, 29.3),
    (-55.0, 29.4), (-125.3, 29.6),
]


def _mk(table):
    tab = sorted(table)
    return pchip([t[0] for t in tab], [t[1] for t in tab])


grip_front_x = _mk(_GRIP_FRONT)
grip_back_x = _mk(_GRIP_BACK)
grip_width = _mk(_GRIP_WIDTH)

GRIP_Z_TOP = FRAME_TOP
GRIP_Z_BOTTOM = -125.3
GRIP_RF = 10.5      # front corner radius of the section
GRIP_RB = 6.2       # back corner radius
GRIP_TAPER = 2.0    # section is 2 mm narrower at the front strap


def grip_levels():
    """Z levels of the grip sections, top to bottom, with edge insets."""
    zs = [(-20.45, 0.45), (-20.95, 0.0)]
    for z in [-21.8, -22.8, -24.0, -25.3, -26.6, -27.8, -28.8, -29.6, -30.2,
              -30.7, -31.2, -31.8, -32.6, -33.6, -34.8, -36.2, -37.8, -39.6,
              -41.6, -44.0, -46.5, -49.0, -51.5, -54.0, -56.5, -59.0, -61.0,
              -62.6, -63.6, -64.6, -65.6, -66.8, -68.2]:
        zs.append((z, 0.0))
    z = -69.7
    while z > -123.0:
        zs.append((round(z, 3), 0.0))
        z -= 1.45
    zs += [(-123.4, 0.0), (-124.35, 0.0), (-124.95, 0.3), (-125.3, 0.95)]
    return zs


def _tangent_normal(a, b):
    ax, ay, ra = a
    bx, by, rb = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    vx, vy = uy, -ux
    c = (ra - rb) / L
    s = math.sqrt(max(0.0, 1 - c * c))
    return (ux * c + vx * s, uy * c + vy * s)


GRIP_SIDE_BULGE = 0.55  # the Gen4 grip sides are slightly convex


def grip_ring(z, inset=0.0, n_front=7, n_back=5, n_bflat=2, n_side=3):
    """Horizontal grip section at height z.

    Returns (points, arclengths, marks) - points are (x, y) CCW seen from
    above, starting at the centre of the front strap and going round the LEFT
    (-Y) side first.  arclengths has len(points)+1 entries (last = perimeter);
    marks holds the indices of the front-arc end (left), the back centre and
    the front-arc start (right)."""
    xf = grip_front_x(z) + inset
    xb = grip_back_x(z) - inset
    w = grip_width(z) - 2 * inset - 2 * 0.85 * GRIP_SIDE_BULGE
    wf = w - GRIP_TAPER
    rf = min(GRIP_RF - inset, wf / 2 - 0.3)
    rb = min(GRIP_RB - inset, w / 2 - 0.3)
    FL = (xf + rf, -(wf / 2 - rf), rf)
    BL = (xb - rb, -(w / 2 - rb), rb)
    BR = (xb - rb, (w / 2 - rb), rb)
    FR = (xf + rf, (wf / 2 - rf), rf)
    n1 = _tangent_normal(FL, BL)
    n2 = _tangent_normal(BR, FR)
    a1 = math.atan2(n1[1], n1[0]) % (2 * math.pi)
    a2 = math.atan2(n2[1], n2[0]) % (2 * math.pi)

    def arc(c, t0, t1, n):
        return [(c[0] + c[2] * math.cos(t0 + (t1 - t0) * k / n),
                 c[1] + c[2] * math.sin(t0 + (t1 - t0) * k / n))
                for k in range(n + 1)]

    def side(p0, p1, nrm):
        bulge = GRIP_SIDE_BULGE * max(0.0, 1.0 - inset / 0.6)
        out = []
        for k in range(1, n_side):
            t = k / n_side
            b = bulge * math.sin(math.pi * t)
            out.append((p0[0] + (p1[0] - p0[0]) * t + nrm[0] * b,
                        p0[1] + (p1[1] - p0[1]) * t + nrm[1] * b))
        return out

    pts = [(xf, 0.0)]
    pts += arc(FL, math.pi, a1, n_front)
    fl_end = len(pts) - 1
    bl = arc(BL, a1, 2 * math.pi, n_back)
    pts += side(pts[-1], bl[0], n1)
    pts += bl
    back = len(pts)
    for k in range(1, n_bflat):
        pts.append((xb, -(w / 2 - rb) + (w - 2 * rb) * k / n_bflat))
    pts += arc(BR, 0.0, a2, n_back)
    fr = arc(FR, a2, math.pi, n_front)
    pts += side(pts[-1], fr[0], n2)
    fr_start = len(pts)
    pts += fr
    arcl = [0.0]
    for i in range(1, len(pts) + 1):
        p0, p1 = pts[i - 1], pts[i % len(pts)]
        arcl.append(arcl[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
    return pts, arcl, {"fl_end": fl_end, "back": back, "fr_start": fr_start}


def grip_surface_y(x, z):
    """|Y| of the grip surface at (x, z) (0 if outside the section)."""
    pts, _, _ = grip_ring(z)
    best = 0.0
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if y0 < 0 and y1 < 0 and (x0 - x) * (x1 - x) <= 0 and x0 != x1:
            t = (x - x0) / (x1 - x0)
            best = max(best, -(y0 + (y1 - y0) * t))
    return best


def grip_uv_of_point(x, z, side=-1):
    """Arc-length coordinate (mm) of the point on the grip surface with the
    given X at height z, on the left (side=-1) or right (side=+1) half."""
    pts, arcl, _ = grip_ring(z)
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 * side >= 0) and (y1 * side >= 0) and x0 != x1 \
                and (x0 - x) * (x1 - x) <= 0:
            t = (x - x0) / (x1 - x0)
            return arcl[i] + t * (arcl[i + 1] - arcl[i])
    return None


# --------------------------------------------------------------------------
# Small parts (positions measured on the dimension-sheet overlay)
# --------------------------------------------------------------------------
PINS = [  # (X, Z, radius, on_grip)
    (106.0, -24.0, 1.5, False),    # trigger pin
    (104.3, -30.5, 1.75, False),   # locking block pin
    (167.4, -47.7, 1.2, True),     # trigger housing pin
]
SLIDE_LOCK_POCKET = (79.5, 95.0, -33.4, -18.0)   # X0, X1, Z0, Z1 (open at top)
SLIDE_LOCK_LEVER = (84.8, 91.6, -31.9, -21.9)
SLIDE_STOP_TAB = (127.0, 136.4, -26.8, -21.6)
SLIDE_STOP_GUARD = [(122.6, -27.6), (123.4, -29.3), (125.2, -30.2),
                    (128.0, -30.4), (134.5, -30.4), (137.4, -30.2),
                    (139.2, -29.3), (140.0, -27.6)]
MAG_CATCH = dict(cx=131.0, cz=-53.5, along=10.5, across=9.0, angle=21.0)
GRIP_LOGO = dict(x=173.3, z=-98.4, w=10.6, h=8.6)

# --------------------------------------------------------------------------
# Magazine and magazine well.  The magazine body is a slanted prism: at
# height z its front/back X are MAG_X0/MAG_X1 at MAG_ZB shifted forward by
# (z - MAG_ZB) * tan(MAG_ANGLE).
# --------------------------------------------------------------------------
MAG_ANGLE = 21.0
MAG_TAN = math.tan(math.radians(MAG_ANGLE))
MAG_X0, MAG_X1 = 152.0, 185.8
MAG_ZB, MAG_ZT = -126.4, -22.3             # body bottom / top (feed lips)
MAG_HW = 11.2
MAG_RF, MAG_RB = 6.0, 2.0                  # section corner radii (front, back)
MAG_WELL_CLEAR = 0.3
# direction in which the magazine leaves the grip (build mm, unit vector)
MAG_DROP_DIR = (math.sin(math.radians(MAG_ANGLE)), 0.0,
                -math.cos(math.radians(MAG_ANGLE)))


def mag_x_range(z):
    s = (z - MAG_ZB) * MAG_TAN
    return MAG_X0 - s, MAG_X1 - s


def mag_section(z, grow=0.0, seg90=4):
    """Horizontal section (x, y) of the magazine body at height z, grown by
    `grow` mm (clearance of the magazine well)."""
    xa, xb = mag_x_range(z)
    hw = MAG_HW + grow
    rf, rb = MAG_RF + grow, MAG_RB + grow
    return rounded_poly([(xa - grow, -hw, rf), (xb + grow, -hw, rb),
                         (xb + grow, hw, rb), (xa - grow, hw, rf)], seg90)


# Hollow parts of the frame (openings only; the solid in between is hidden):
# the magazine well mouth under the grip and the pocket under the slide
MAG_WELL_BOTTOM = (-140.0, -95.0)          # z range of the lower pocket
MAG_WELL_FLARE = 0.6                       # flare of the mouth (mm)
MAG_WELL_TOP = (-35.0, -10.0)              # z range of the upper pocket

# Cavity inside the slide under the ejection port (seen when the slide is
# back) and the chamber (the casing head is flush with the barrel hood)
SLIDE_CAVITY = (PORT_X0, PORT_X1, 8.7, -21.5, -3.0)   # x0, x1, half y, z0, z1
CHAMBER_X = 114.9
CHAMBER_R = 5.05
SLIDE_TRAVEL = 34.0         # full recoil stroke
SLIDE_LOCK_TRAVEL = 31.0    # slide held open by the slide stop
BARREL_TRAVEL = 3.0         # barrel moves back with the slide, then drops
BARREL_TILT = 1.1           # degrees (rear end down) when unlocked

# --------------------------------------------------------------------------
# 9x19 mm Parabellum cartridge (C.I.P. dimensions).  Lathe profiles (x, r):
# x along the cartridge axis, 0 = case head, +x towards the bullet.
# --------------------------------------------------------------------------
CASE_LEN = 19.15
CARTRIDGE_LEN = 29.69
_CASE_HEAD = [
    (0.10, 0.0), (0.10, 2.05), (0.0, 2.25),        # primer
    (0.0, 4.72), (0.12, 4.98), (1.05, 4.98),       # head face, rim
    (1.27, 4.72), (1.35, 4.02), (1.95, 4.02),      # extractor groove
    (2.55, 4.965),                                  # base of the body
]
CASE_PROFILE = _CASE_HEAD + [
    (CASE_LEN, 4.825), (CASE_LEN, 4.52),           # tapered body, mouth
    (6.2, 4.40), (5.6, 3.6), (5.4, 0.0),           # inside of the case
]


def _bullet_nose(x0, x1, r, n=7):
    """Round-nose FMJ ogive (quarter ellipse) from x0 to the tip at x1."""
    pts = []
    for k in range(1, n + 1):
        a = math.radians(84.0 * k / n)
        pts.append((x0 + (x1 - x0) * math.sin(a), r * math.cos(a)))
    return pts + [(x1, 0.0)]


CARTRIDGE_PROFILE = _CASE_HEAD + [
    (CASE_LEN, 4.825), (CASE_LEN, 4.505), (22.0, 4.505),
] + _bullet_nose(22.0, CARTRIDGE_LEN, 4.505)

# top round in the magazine: head X and axis Z (horizontal, points forward)
MAG_ROUND_HEAD_X = 144.6
MAG_ROUND_Z = -24.3

# --------------------------------------------------------------------------
# GTA V orientation.  Build mm -> GTA metres: X forward (muzzle), Y left,
# Z up, origin where the standard GTA pistol skeleton has it, so the grip
# lines up with the ped's hand:  X = (89.5 - x) / 1000, Y = -y / 1000,
# Z = (z + 51.76) / 1000
# --------------------------------------------------------------------------
GTA_ORIGIN_MM = (89.5, 0.0, -51.76)

# Weapon skeleton.  ("local", (t, q)) is a transform relative to the parent
# bone (metres, quaternion x, y, z, w as in CodeWalker XML) copied from the
# standard pistol skeleton: those bones are animated by the game's pistol
# clips (slide recoil, trigger), so their rest pose must match.  ("mm", (p, q))
# places a bone at point p of this model (build mm) with rotation q in GTA
# space.  Custom bones (after WAPSupp) are only used by this model's clips.
GTA_BONES = [
    ("Gun_Root", None, "local", ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_GripR", "Gun_Root", "local",
     ((-0.118278, -0.015998, -0.047679),
      (0.6552189, -0.0031388, 0.0380732, 0.7544724))),
    ("Gun_Main_Bone", "Gun_GripR", "local",
     ((0.121391, 0.042062, -0.00374),
      (-0.6552188, 0.0031391, -0.0380733, 0.7544725))),
    ("Gun_Trigger_Pr", "Gun_Main_Bone", "local",
     ((-0.012811, -3.6e-05, 0.009202), (0.8646954, 0.0, -0.5022964, 0.0))),
    ("Gun_Cock1", "Gun_Main_Bone", "local",
     ((-0.018411, -3.6e-05, 0.033822), (0.9999999, 0.0, -0.000175, 0.0))),
    ("Gun_Hammer", "Gun_Main_Bone", "local",
     ((-0.081533, -3.6e-05, 0.02503), (0.6214617, 0.0, 0.7834446, 0.0))),
    ("Gun_Safety", "Gun_Main_Bone", "local",
     ((-0.077974, -3.6e-05, 0.020796), (0.9998599, 0.0, 0.0167412, 0.0))),
    ("Gun_VFX_Eject", "Gun_Main_Bone", "mm",
     ((100.0, 8.0, -4.2), (0.0, 0.0, -0.7071068, 0.7071068))),
    ("Gun_Muzzle", "Gun_Main_Bone", "mm",
     ((0.0, 0.0, BORE_Z), (0.9999999, 0.0, 0.0001814, 0.0))),
    ("WAPClip", "Gun_Main_Bone", "local",
     ((-0.054254, -1.7e-05, 0.022823), (0.0, 0.0, 0.0, 1.0))),
    ("WAPFlshLasr", "Gun_Main_Bone", "mm",
     ((21.7, 0.0, -40.2), (0.0, 0.0, 0.0, 1.0))),
    ("WAPSupp", "Gun_Main_Bone", "mm",
     ((0.0, 0.0, BORE_Z), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_Barrel", "Gun_Main_Bone", "mm",
     ((1.0, 0.0, BORE_Z), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_TriggerSafety", "Gun_Trigger_Pr", "mm",
     ((101.2, 0.0, -46.0), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_SlideStop", "Gun_Main_Bone", "mm",
     ((106.0, 0.0, -24.0), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_MagRelease", "Gun_Main_Bone", "mm",
     ((MAG_CATCH["cx"], 0.0, MAG_CATCH["cz"]), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_MagRound", "WAPClip", "mm",
     ((MAG_ROUND_HEAD_X - CARTRIDGE_LEN / 2, 0.0, MAG_ROUND_Z),
      (0.0, 0.0, 0.0, 1.0))),
    ("Gun_Shell", "Gun_Main_Bone", "mm",
     ((CHAMBER_X - CASE_LEN / 2, 0.0, BORE_Z), (0.0, 0.0, 0.0, 1.0))),
    ("Gun_Flash", "Gun_Main_Bone", "mm",
     ((2.0, 0.0, BORE_Z), (0.0, 0.0, 0.0, 1.0))),
]
# build-mm points of the bones placed on this model
BONE_POINT_MM = {b[0]: b[3][0] for b in GTA_BONES if b[2] == "mm"}
GTA_PISTOL_BONES = 12        # the first 12 bones form the standard skeleton

# which bone each part of the model follows
PART_BONES = {
    "Slide": "Gun_Cock1",
    "Barrel": "Gun_Barrel",
    "RecoilSpringGuide": "Gun_Main_Bone",
    "Frame": "Gun_Main_Bone",
    "Trigger": "Gun_Trigger_Pr",
    "TriggerSafety": "Gun_TriggerSafety",
    "SlideStop": "Gun_SlideStop",
    "MagazineCatch": "Gun_MagRelease",
    "Magazine": "WAPClip",
    "MagazineRound": "Gun_MagRound",
    "Casing": "Gun_Shell",
    "MuzzleFlash": "Gun_Flash",
}
FLASH_REST_SCALE = 0.01      # the flash is modelled collapsed in the bore
