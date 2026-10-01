"""Genera logo PNG, iconos, favicon.ico e imagen Open Graph en static/img."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMG = Path(__file__).resolve().parent.parent / "static" / "img"
NAVY, NAVY2, AMBER, ORANGE = (11, 31, 58), (19, 41, 75), (245, 158, 11), (234, 88, 12)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def logo(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .22), fill=NAVY)
    u = s / 64
    w = int(6 * u)
    d.line([(16 * u, 14 * u), (32 * u, 14 * u)], fill=AMBER, width=w)
    d.line([(16 * u, 50 * u), (32 * u, 50 * u)], fill=ORANGE, width=w)
    d.line([(16 * u, 11 * u), (16 * u, 53 * u)], fill=AMBER, width=w)
    d.arc([14 * u, 14 * u, 50 * u, 50 * u], start=-90, end=90, fill=ORANGE, width=w)
    d.rectangle([26 * u, 24 * u, 32 * u, 40 * u], fill=AMBER)
    d.pieslice([24 * u, 24 * u, 40 * u, 40 * u], start=-90, end=90, fill=ORANGE)
    return im.resize((size, size), Image.LANCZOS)


def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * t) for i in range(3)))
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(25, 50, 85))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(25, 50, 85))
    im.paste(logo(160), (80, 80), logo(160))
    d.text((270, 110), "DICPROM", font=ImageFont.truetype(FONT_B, 92), fill=(255, 255, 255))
    d.rectangle([80, 290, 200, 298], fill=AMBER)
    d.text((80, 320), "Ingeniería, construcción y", font=ImageFont.truetype(FONT_B, 48), fill=(255, 255, 255))
    d.text((80, 380), "mantenimiento industrial en Panamá", font=ImageFont.truetype(FONT_B, 48), fill=(255, 255, 255))
    d.text((80, 485), "Diseño industrial · Obra civil · Eléctrica · HVAC · Metalmecánica · Contra incendios",
           font=ImageFont.truetype(FONT_R, 26), fill=(203, 213, 225))
    d.text((80, 545), "dicprom.com", font=ImageFont.truetype(FONT_B, 32), fill=AMBER)
    im.save(IMG / "og-dicprom.png", optimize=True)


if __name__ == "__main__":
    logo(512).save(IMG / "logo-dicprom.png", optimize=True)
    logo(512).save(IMG / "icon-512.png", optimize=True)
    logo(192).save(IMG / "icon-192.png", optimize=True)
    logo(180).convert("RGB").save(IMG / "apple-touch-icon.png", optimize=True)
    logo(64).save(IMG.parent / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    og()
    print("imágenes generadas")
