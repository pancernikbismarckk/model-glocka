"""
Texture generator for the Glock 17 Gen4 model (requires numpy + Pillow).

  python scripts/make_textures.py

Writes into textures/:
  slide_markings_normal.png  slide_markings_color.png  slide_markings_rough.png
      left side of the slide (planar projection, 0.05 mm/px): engraved
      GLOCK logo, "17 Gen4", "AUSTRIA", "9x19"
  grip_normal.png
      Gen4 RTF grip texture (0.1 mm/px): square bumps on the grip panels,
      ridges on the finger grooves of the front strap, moulded GLOCK logos.
      U = arc length around the grip section, V = height (see glock_data).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glock_data as G  # noqa: E402

TEX_DIR = os.path.join(os.path.dirname(HERE), "textures")

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
             "/usr/share/fonts/TTF", "C:/Windows/Fonts", "/Library/Fonts",
             "/System/Library/Fonts/Supplemental"]


def font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


SANS = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf"]
SANS_BOLD = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf",
             "arialbd.ttf"]
SANS_COND_BOLD = ["DejaVuSansCondensed-Bold.ttf", "LiberationSansNarrow-Bold.ttf",
                  "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"]


def draw_text_box(draw, text, box, fnames, fill=255):
    """Draw text scaled to fit box=(x0, y0, x1, y1) in pixels."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    size = int(h * 1.4)
    f = font(fnames, size)
    for _ in range(40):
        bb = draw.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if tw <= w * 1.001 and th <= h * 1.001:
            break
        size = int(size * min(w / max(tw, 1), h / max(th, 1), 0.97))
        f = font(fnames, max(size, 4))
    bb = draw.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    ox = x0 + (w - tw) / 2 - bb[0]
    oy = y0 + (h - th) / 2 - bb[1]
    draw.text((ox, oy), text, font=f, fill=fill)


def draw_glock_logo(draw, box, fill=255):
    """Stylised GLOCK logo: rounded-square 'G' enclosing 'LOCK'."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    s = max(2, int(round(min(w, h) * 0.075)))       # stroke
    r = int(min(w, h) * 0.24)
    draw.rounded_rectangle(box, radius=r, outline=fill, width=s)
    # opening of the G on the upper right, crossbar at mid height
    gap_top, gap_bot = y0 + h * 0.16, y0 + h * 0.60
    draw.rectangle((x1 - s - 1, gap_top, x1 + 1, gap_bot), fill=0)
    draw.rectangle((x1 - w * 0.34, gap_bot - s, x1, gap_bot), fill=fill)
    draw.rectangle((x1 - w * 0.34, gap_bot - s, x1 - w * 0.34 + s,
                    gap_bot + h * 0.12), fill=fill)
    draw_text_box(draw, "LOCK", (x0 + w * 0.2, y0 + h * 0.24, x1 - w * 0.2,
                                 y0 + h * 0.5), SANS_COND_BOLD, fill)


def height_to_normal(h, px_mm, strength=1.0):
    """Height map (mm, row 0 = top) -> OpenGL tangent-space normal map."""
    gy, gx = np.gradient(h, px_mm)
    nx = -gx * strength
    ny = gy * strength          # image rows grow downwards, V grows upwards
    nz = np.ones_like(h)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    rgb = np.stack([nx / n, ny / n, nz / n], -1) * 0.5 + 0.5
    return Image.fromarray(np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8))


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --------------------------------------------------------------------------
# Slide markings
# --------------------------------------------------------------------------
def slide_textures():
    W, H, mm = G.SLIDE_TEX_W, G.SLIDE_TEX_H, G.SLIDE_TEX_MM_PER_PX
    z_top = G.SLIDE_TEX_Z0 + H * mm

    def px(x, z):
        return x / mm, (z_top - z) / mm

    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    for key, (x0, x1, z0, z1) in G.MARKINGS.items():
        a, b = px(x0, z1)
        c, e = px(x1, z0)
        if key == "logo":
            draw_glock_logo(d, (a, b, c, e))
        elif key in ("AUSTRIA", "9x19"):
            draw_text_box(d, key, (a, b, c, e), SANS_BOLD)
        else:
            draw_text_box(d, key, (a, b, c, e), SANS)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    depth = 0.06                                   # engraving depth (mm)
    normal = height_to_normal(-m * depth, mm, strength=1.0)
    normal.save(os.path.join(TEX_DIR, "slide_markings_normal.png"))

    base = np.array([0.16, 0.16, 0.168])           # linear, as the material
    engr = np.array([0.26, 0.26, 0.265])
    col = base[None, None, :] * (1 - m[..., None]) + engr[None, None, :] * m[..., None]
    srgb = np.where(col <= 0.0031308, col * 12.92,
                    1.055 * np.power(col, 1 / 2.4) - 0.055)
    Image.fromarray((srgb * 255 + 0.5).astype(np.uint8)).save(
        os.path.join(TEX_DIR, "slide_markings_color.png"))
    rough = 0.4 * (1 - m) + 0.65 * m
    Image.fromarray((rough * 255 + 0.5).astype(np.uint8)).save(
        os.path.join(TEX_DIR, "slide_markings_rough.png"))


# --------------------------------------------------------------------------
# Grip (Gen4 Rough Textured Frame)
# --------------------------------------------------------------------------
def grip_texture():
    """Gen4 RTF texture in the grip UV space (U = arc length, V = height).

    The bump lattice is laid out in a shear-free surface chart (c, a):
      c - arc length of the section projected perpendicular to the grip axis,
          measured from the centre of the backstrap (continuous round the back)
      a - distance along the grip axis (tilted BETA from vertical)
    so the bumps stay square and aligned with the grip on both sides."""
    N, mm = G.GRIP_TEX_SIZE, G.GRIP_TEX_MM_PER_PX
    beta = math.radians(23.0)
    sb, cb = math.sin(beta), math.cos(beta)
    rows = np.arange(N)
    zrow = G.GRIP_TEX_Z0 + (N - rows - 0.5) * mm           # height of each row
    u = (np.arange(N) + 0.5) * mm                           # arc length (cols)

    C = np.zeros((N, N), np.float32)       # chart coordinate c
    A = np.zeros((N, N), np.float32)       # chart coordinate a
    lm = np.zeros((N, 4))                  # s_fl, s_back, s_fr, perimeter
    cback = np.zeros(N)
    for j in range(N):
        zz = min(max(zrow[j], G.GRIP_Z_BOTTOM + 0.3), G.GRIP_Z_TOP - 0.3)
        pts, arcl, mk = G.grip_ring(zz)
        n = len(pts)
        P = np.array(pts + [pts[0]])
        d = np.diff(P, axis=0)
        dproj = np.sqrt((d[:, 0] * cb) ** 2 + d[:, 1] ** 2)
        cc = np.concatenate([[0.0], np.cumsum(dproj)])
        cc -= cc[mk["back"]]
        arc = np.array(arcl)
        C[j] = np.interp(u, arc, cc)
        X = np.interp(u, arc, P[:, 0])
        A[j] = X * sb - zrow[j] * cb
        lm[j] = (arcl[mk["fl_end"]], arcl[mk["back"]], arcl[mk["fr_start"]],
                 arcl[n])
        cback[j] = -cc[0]                  # |c| at the front-strap seam
    s_fl, s_back, s_fr, perim = (lm[:, k][:, None] for k in range(4))
    U, Z = np.meshgrid(u, zrow)

    # ---- panel mask in (U, Z)
    t = np.where(U <= s_back, (U - s_fl) / (s_back - s_fl),
                 (s_fr - U) / (s_fr - s_back))
    z_top = -54.0 + 4.0 * np.clip(t, 0, 1)
    panel = (U > s_fl + 0.8) & (U < s_fr - 0.8) & (Z > -118.3) & (Z < z_top)

    # ---- logo positions in the chart
    logos = []
    for side in (-1, +1):
        lu = G.grip_uv_of_point(G.GRIP_LOGO["x"], G.GRIP_LOGO["z"], side)
        jj = int(round(N - (G.GRIP_LOGO["z"] - G.GRIP_TEX_Z0) / mm - 0.5))
        ii = int(round(lu / mm - 0.5))
        logos.append((float(C[jj, ii]), float(A[jj, ii])))
    lw, lh = G.GRIP_LOGO["w"], G.GRIP_LOGO["h"]
    for c0, a0 in logos:
        panel &= ~((np.abs(C - c0) < lw / 2 + 1.0) & (np.abs(A - a0) < lh / 2 + 1.0))

    # ---- square bumps, whole bumps only (mask sampled at the bump centre)
    pitch, half = 1.55, 0.46
    cc_ = (np.floor(C / pitch) + 0.5) * pitch
    ac_ = (np.floor(A / pitch) + 0.5) * pitch
    dC, dA = cc_ - C, ac_ - A
    gCz, gCu = np.gradient(C, -mm, mm)      # d/dZ (rows go down), d/dU
    gAz, gAu = np.gradient(A, -mm, mm)
    det = gCu * gAz - gCz * gAu
    det = np.where(np.abs(det) < 1e-6, 1e-6, det)
    du = (gAz * dC - gCz * dA) / det
    dz = (-gAu * dC + gCu * dA) / det
    ii = np.clip(np.round((U + du) / mm - 0.5), 0, N - 1).astype(int)
    jj = np.clip(np.round(N - (Z + dz - G.GRIP_TEX_Z0) / mm - 0.5), 0, N - 1).astype(int)
    inside = panel[jj, ii] & panel
    dist = np.maximum(np.abs(dC), np.abs(dA))
    bump = smoothstep(half + 0.1, half - 0.18, dist)
    height = np.where(inside, bump * 0.28, 0.0).astype(np.float32)

    # ---- ridges in the finger grooves of the front strap (mirror-symmetric
    #      about the U seam at the centre of the front strap)
    front = (U < s_fl - 0.6) | (U > s_fr + 0.6)
    inband = np.zeros_like(front)
    for z0, z1 in [(-75.5, -66.3), (-92.0, -84.3), (-112.0, -103.3)]:
        inband |= (Z > z0) & (Z < z1)
    cf = cback[:, None] - np.abs(C)                       # 0 on the seam
    rp, rs = 1.5, 2.3
    ra = (np.floor(A / rp) + 0.5) * rp
    rc = (np.floor(cf / rs + 0.5)) * rs
    dash = (smoothstep(0.42, 0.22, np.abs(A - ra)) *
            smoothstep(0.95, 0.7, np.abs(cf - rc)))
    height += np.where(front & inband, dash * 0.25, 0.0)

    # ---- moulded GLOCK logos, drawn upright in the chart (c right, -a up)
    lmm = 0.025
    Wl, Hl = int(lw / lmm), int(lh / lmm)
    img = Image.new("L", (Wl, Hl), 0)
    draw_glock_logo(ImageDraw.Draw(img), (2, 2, Wl - 3, Hl - 3))
    logo = np.asarray(img.filter(ImageFilter.GaussianBlur(1.6)), np.float32) / 255
    for c0, a0 in logos:
        xi = np.round((C - c0 + lw / 2) / lmm).astype(int)
        yi = np.round((A - a0 + lh / 2) / lmm).astype(int)
        ok = (xi >= 0) & (xi < Wl) & (yi >= 0) & (yi < Hl)
        height += np.where(ok, logo[np.clip(yi, 0, Hl - 1),
                                    np.clip(xi, 0, Wl - 1)], 0.0) * 0.22

    normal = height_to_normal(height, mm, strength=1.0)
    normal.save(os.path.join(TEX_DIR, "grip_normal.png"))
    return height


if __name__ == "__main__":
    os.makedirs(TEX_DIR, exist_ok=True)
    slide_textures()
    grip_texture()
    print("textures written to", TEX_DIR)
