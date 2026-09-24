"""
Assemble the preview images (requires Pillow).

  python scripts/make_sheet.py

Reads renders/*.png and renders/stats.json written by build_glock17.py and
writes preview.png (main preview) and renders/preview_sheet.png (all views).
"""
import json
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "renders")

FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf"]
FONTS_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "/Library/Fonts/Arial Bold.ttf"]


def font(size, bold=False):
    for p in (FONTS_BOLD if bold else FONTS):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def load(name, w, h):
    p = os.path.join(R, name + ".png")
    im = Image.open(p).convert("RGB")
    return im.resize((w, h), Image.LANCZOS)


def fmt(n):
    return f"{n:,}".replace(",", " ")


def plural(n, one, few, many):
    """Polish plural form for n (1 trójkąt, 2 trójkąty, 5 trójkątów)."""
    if n == 1:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many


def main():
    with open(os.path.join(R, "stats.json")) as f:
        st = json.load(f)
    W, pad = 2400, 24
    title_h = 130
    rows = [
        # (list of (view, label), height)
        ([("hero", "Widok 3/4 z przodu (lewa strona)")], 1200 * (W - 2 * pad) // 1920),
        ([("left", "Lewa strona (rzut prostokątny)"),
          ("right", "Prawa strona (rzut prostokątny)")], None),
        ([("right_rear", "3/4 z tyłu (prawa strona)"), ("front", "3/4 z przodu – wylot lufy"),
          ("top", "Z góry – okno wyrzutnika")], None),
        ([("cu_grip", "Tekstura RTF Gen4 i logo"), ("cu_trigger", "Spust, zatrzask, kołki"),
          ("cu_rear", "Szczerbinka i nacięcia zamka"), ("cu_muzzle", "Muszka i wylot lufy")], None),
        ([("hero_wireframe", f"Siatka – {fmt(st['tris'])} "
                             f"{plural(st['tris'], 'trójkąt', 'trójkąty', 'trójkątów')}"),
          ("cu_port", "Okno wyrzutnika i wyciąg")], None),
    ]
    anims = [("anim_fire_still", "Strzał – wyrzut łuski"),
             ("anim_fire_empty_still", "Ostatni strzał – zamek w tyle"),
             ("anim_reload_still", "Przeładowanie"),
             ("anim_reload_empty_still", "Zwolnienie zamka")]
    if all(os.path.exists(os.path.join(R, v + ".png")) for v, _ in anims):
        rows.append((anims, None))
    label_h = 44
    layout = []
    y = title_h
    for items, h in rows:
        n = len(items)
        w = (W - pad * (n + 1)) // n
        h = h or int(w * 1000 / 1600)
        x = pad
        for view, label in items:
            layout.append((view, label, x, y, w, h))
            x += w + pad
        y += h + label_h + pad
    H = y
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 22), "GLOCK 17 Gen4 – model 3D (Blender)", font=font(52, True),
           fill=(20, 20, 22))
    tri_word = plural(st["tris"], "trójkąt", "trójkąty", "trójkątów")
    face_word = plural(st["faces"], "poligon", "poligony", "poligonów")
    info = (f"{fmt(st['tris'])} {tri_word}  ·  {fmt(st['faces'])} {face_word} (quady/n-gony)"
            "  ·  " + " × ".join(f"{v:.1f}".replace(".", ",") for v in st["size_mm"])
            + " mm  ·  Cycles")
    d.text((pad, 86), info, font=font(28), fill=(90, 90, 96))
    for view, label, x, y, w, h in layout:
        sheet.paste(load(view, w, h), (x, y))
        d.rectangle((x, y, x + w - 1, y + h - 1), outline=(225, 225, 228))
        d.text((x + 4, y + h + 8), label, font=font(26), fill=(60, 60, 66))
    sheet.save(os.path.join(R, "preview_sheet.png"), optimize=True)
    shutil.copyfile(os.path.join(R, "hero.png"), os.path.join(ROOT, "preview.png"))
    print("written preview.png and renders/preview_sheet.png", sheet.size)


if __name__ == "__main__":
    main()
