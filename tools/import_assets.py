#!/usr/bin/env python3
"""Genera los recursos gráficos del sitio a partir del logotipo oficial y las fotos de obra.

Uso: python3 tools/import_assets.py [carpeta_fotos]
  carpeta_fotos: carpeta public/img del paquete DISPRON (por defecto ~/dispron-src/public/img)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
from content import HERO_PHOTOS, SERVICES  # noqa: E402
from gallery import all_photos, gallery_url  # noqa: E402

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path.home() / "dispron-src/public/img"
LOGO = ROOT / "assets-src/logo-oficial.jpg"
LOGO_V = ROOT / "assets-src/logo-vertical.jpg"
IMG = ROOT / "static/img"
NAVY = (15, 26, 43)


def knockout_white(im):
    """Convierte el fondo blanco del logotipo en transparencia conservando los bordes suaves."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    alpha = np.clip((242 - a.min(axis=2)) * 5.0, 0, 255) / 255.0
    safe = np.where(alpha > 0, alpha, 1)[..., None]
    rgb = np.clip((a - 255 * (1 - alpha[..., None])) / safe, 0, 255)
    out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, "RGBA")
    return img.crop(img.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox())


def logos():
    full = knockout_white(Image.open(LOGO))
    w, h = full.size
    cols = np.asarray(full.split()[3]).max(axis=0)
    gap = next(x for x in range(int(w * 0.2), w) if cols[x] < 10)
    mark = full.crop((0, 0, gap, h))
    mark = mark.crop(mark.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox())
    full.save(IMG / "logo-dispron-horizontal.png", optimize=True)
    knockout_white(Image.open(LOGO_V)).save(IMG / "logo-dispron-vertical.png", optimize=True)
    m = mark.copy()
    m.thumbnail((256, 256), Image.LANCZOS)
    m.save(IMG / "logo-dispron-mark.png", optimize=True)
    ml = lighten_navy(mark.copy())
    ml.thumbnail((256, 256), Image.LANCZOS)
    ml.save(IMG / "logo-dispron-mark-light.png", optimize=True)
    for size, name in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")]:
        bg = Image.new("RGBA", (size, size), NAVY + (255,))
        mm = mark.copy()
        mm.thumbnail((int(size * 0.74), int(size * 0.74)), Image.LANCZOS)
        mm = lighten_navy(mm)
        bg.alpha_composite(mm, ((size - mm.width) // 2, (size - mm.height) // 2))
        bg.convert("RGB").save(IMG / name, optimize=True)
    fav = Image.new("RGBA", (64, 64), NAVY + (255,))
    mm = lighten_navy(mark.copy())
    mm.thumbnail((54, 54), Image.LANCZOS)
    fav.alpha_composite(mm, ((64 - mm.width) // 2, (64 - mm.height) // 2))
    fav.save(ROOT / "static/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    return mark


def lighten_navy(mark):
    """Aclara la parte azul oscuro del isotipo para que contraste sobre fondo navy."""
    a = np.asarray(mark).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3:]
    dark = (rgb[..., 2] >= rgb[..., 0]) & (rgb.mean(axis=2) < 120)
    rgb[dark] = rgb[dark] * 0.55 + np.array([185, 196, 212]) * 0.45
    return Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), "RGBA")


def save_photo(src, dest, width):
    im = Image.open(src).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=74, method=6)
    return im.size


def photos():
    sizes = {}
    for i, (src, _cap) in enumerate(HERO_PHOTOS, 1):
        sizes[f"/img/hero/hero-{i}.webp"] = save_photo(SRC / src, IMG / f"hero/hero-{i}.webp", 1600)
        save_photo(SRC / src, IMG / f"hero/hero-{i}-sm.webp", 800)
    for s in SERVICES:
        for i, (src, _cap) in enumerate(s["photos"], 1):
            base = f"obras/{s['slug']}-{i}"
            sizes[f"/img/{base}.webp"] = save_photo(SRC / src, IMG / f"{base}.webp", 1200)
            save_photo(SRC / src, IMG / f"{base}-sm.webp", 640)
    return sizes


def gallery():
    n = 0
    for src, _cap, _cat in all_photos():
        big, small = ROOT / "static" / gallery_url(src).lstrip("/"), ROOT / "static" / gallery_url(src, True).lstrip("/")
        if not big.exists():
            save_photo(SRC / src, big, 1200)
            save_photo(SRC / src, small, 560)
        n += 1
    return n


def og_image(mark):
    W, H = 1200, 630
    bg = Image.open(IMG / "hero/hero-1.webp").convert("RGB")
    scale = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * scale), round(bg.height * scale)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(1.5))
    shade = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(shade)
    for x in range(W):
        d.line([(x, 0), (x, H)], fill=NAVY + (int(245 - 120 * x / W),))
    img = bg.convert("RGBA")
    img.alpha_composite(shade)
    mm = lighten_navy(mark.copy())
    mm.thumbnail((210, 210), Image.LANCZOS)
    img.alpha_composite(mm, (70, 70))
    d = ImageDraw.Draw(img)
    font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
    font_m = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    d.text((310, 105), "DISPRON", font=font_b, fill="white")
    d.text((310, 180), "GROUP", font=font_b, fill=(214, 178, 106))
    d.text((70, 330), "Ingeniería, construcción y", font=font_m, fill="white")
    d.text((70, 372), "mantenimiento industrial en Panamá", font=font_m, fill="white")
    d.rectangle([70, 440, 190, 444], fill=(214, 178, 106))
    d.text((70, 470), "Obra civil · Electricidad · HVAC · Metalmecánica · Contra incendios", font=font_s, fill=(220, 226, 235))
    d.text((70, 540), "dicprom.com", font=font_s, fill=(214, 178, 106))
    img.convert("RGB").save(IMG / "og-dispron.jpg", quality=86, optimize=True)


if __name__ == "__main__":
    if "--gallery" in sys.argv:
        print(f"Galería: {gallery()} fotos")
        sys.exit(0)
    mark = logos()
    sizes = photos() if "--logos" not in sys.argv else {}
    if "--gallery" in sys.argv or "--logos" not in sys.argv:
        print(f"Galería: {gallery()} fotos")
    og_image(mark)
    print(f"OK: logotipos, iconos, {len(sizes)} fotos y og-dispron.jpg generados")
