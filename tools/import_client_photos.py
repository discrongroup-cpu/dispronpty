"""Importa las carpetas de fotos del cliente (assets-src/fotos-cliente/<carpeta>/) a la galería.

Genera static/img/galeria/cliente-<cat>-<slug>[-sm].webp y data/client_photos.json.
Descarta duplicados (dHash) frente a la galería existente y entre sí.
"""
import json
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets-src" / "fotos-cliente"
OUT = ROOT / "static" / "img" / "galeria"
MANIFEST = ROOT / "data" / "client_photos.json"

FOLDERS = {
    "Anti incendios": "fire",
    "Epoxi": "epoxi",
    "Eventos corporativos": "eventos",
    "Maquinaria": "maquinaria",
    "Plomeria": "plomeria",
    "Refrigeracion y aire acondicionado": "hvac",
    "Restauracion y pintura": "fachadas",
    "Soldadura": "soldadura",
    "ingenieria electrica": "electrica",
    "obra civil": "obra-civil",
}
SKIP = {"Camiones ejemplo.png"}
TYPOS = {
    "maaquinaria": "maquinaria", "boomberos": "bomberos", "tanqe": "tanque", "razo": "raso", "roceadores": "rociadores",
    "estacionaineto": "estacionamiento", "suleo": "suelo", "preaparacion": "preparación", "superifice": "superficie",
    "pisot": "piso", "grane": "grande", "evneto": "evento", "organizaion": "organización", "preperado": "preparado",
    "pnael": "panel", "swichera": "switchgear", "boma": "bomba", "coina": "cocina", "liimpieza": "limpieza",
    "edifcios": "edificios", "edifico": "edificio", "profesionl": "profesional", "on": "con", "list": "lista",
    "discron": "DISPRON", "dry": "drywall", "wall": "", "absorcion": "extracción", "aterramiento": "puesta a tierra",
    "aterrado": "puesta a tierra", "instalacion": "instalación", "preparacion": "preparación", "aplicacion": "aplicación",
    "reparacion": "reparación", "restauracion": "restauración", "remodelacion": "remodelación", "revision": "revisión",
    "construccion": "construcción", "conexion": "conexión", "comprobacion": "comprobación", "electrica": "eléctrica",
    "electrico": "eléctrico", "electricos": "eléctricos", "electricidad": "electricidad", "subestacion": "subestación",
    "tension": "tensión", "presion": "presión", "tuberia": "tubería", "tuberias": "tuberías", "epoxico": "epóxico",
    "osmosis": "ósmosis", "inspeccion": "inspección", "ventilacion": "ventilación", "refrigeracion": "refrigeración",
    "recepcion": "recepción", "decoracion": "decoración", "organizacion": "organización", "panoramica": "panorámica",
    "logistica": "logística", "precision": "precisión", "automatica": "automática", "metalica": "metálica",
    "metalico": "metálico", "daños": "daños", "sotano": "sótano", "camion": "camión", "grua": "grúa", "gruas": "grúas",
    "termofusion": "termofusión", "filtracion": "filtración", "hidrofóbica": "hidrofóbica", "rediseño": "rediseño",
    "configuracion": "configuración", "coctel": "cóctel", "informativa": "informativa", "ejecutivas": "ejecutivas", "tratado": "tratamiento",
}
GENERIC = {  # nombres de terceros en el archivo: no se publican como clientes sin confirmación
    "banco general de panama evento": "Montaje de evento corporativo",
    "cable and wireless panama stand": "Stand corporativo en centro de convenciones",
    "copa airlines evento": "Montaje de evento corporativo de gran formato",
    "evento grupo mall": "Evento corporativo en centro comercial",
    "fcc construcciones stand": "Stand corporativo para empresa constructora",
    "stand banco nacional de panama": "Stand corporativo para entidad bancaria",
    "digicell panama": "Stand corporativo de telecomunicaciones",
    "evento pcc": "Montaje de evento corporativo",
    "evento cerveceria nacional": "Evento corporativo de marca",
    "evento copasa": "Evento corporativo con escenario",
    "evento fcc construccion": "Evento corporativo para empresa constructora",
    "evento fcc construction": "Evento corporativo para empresa constructora",
    "ejemplo de filtro viejo": "Filtro saturado antes del reemplazo",
    "grua publicidad": "Grúa en obra",
    "camiones ejemplo": "Camiones de obra",
}


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def base_name(fn):
    s = Path(fn).stem.replace("_", " ")
    s = re.sub(r"\(\d+\)", "", s)
    s = re.sub(r"\s+\d+$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def caption(fn):
    b = base_name(fn).lower()
    if b in GENERIC:
        return GENERIC[b]
    words = [TYPOS.get(w, w) for w in b.split()]
    s = " ".join(w for w in words if w).replace("anti incendios", "contra incendios").replace("anti incendio", "contra incendio")
    s = s.replace("drywall pintura", "drywall y pintura")
    return s[:1].upper() + s[1:]


def dhash(im, size=8):
    g = ImageOps.exif_transpose(im).convert("L").resize((size + 1, size), Image.LANCZOS)
    px = g.tobytes()
    return sum(1 << i for i in range(size * size) if px[(i // size) * (size + 1) + i % size] > px[(i // size) * (size + 1) + i % size + 1])


def save(im, dest, width):
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dest, "WEBP", quality=72, method=6)


def main():
    seen = []
    for f in sorted(OUT.glob("*-sm.webp")):
        if not f.name.startswith("cliente-"):
            with Image.open(f) as im:
                seen.append(dhash(im))
    items, dup, used = [], 0, set()
    for folder, cat in FOLDERS.items():
        for f in sorted((SRC / folder).iterdir()):
            if f.name in SKIP or f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            with Image.open(f) as raw:
                im = ImageOps.exif_transpose(raw).convert("RGB")
            h = dhash(im)
            if any(bin(h ^ x).count("1") <= 5 for x in seen):
                dup += 1
                continue
            seen.append(h)
            slug = slugify(base_name(f.name))[:48] or "foto"
            n, key = 1, slug
            while f"{cat}-{key}" in used:
                n += 1
                key = f"{slug}-{n}"
            used.add(f"{cat}-{key}")
            src = f"cliente/{cat}-{key}.webp"
            big = OUT / f"cliente-{cat}-{key}.webp"
            if not big.exists():
                save(im, big, 1200)
                save(im, OUT / f"cliente-{cat}-{key}-sm.webp", 560)
            items.append([src, caption(f.name), cat])
    MANIFEST.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {len(items)} fotos nuevas · {dup} duplicadas descartadas")


if __name__ == "__main__":
    main()
