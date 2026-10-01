"""Galería completa de fotografías del paquete DISPRON (public/img). Cada foto: (ruta origen, pie de foto).

Los pies de foto describen lo que se ve; antes de publicar, el cliente debe confirmar qué fotos
corresponden a trabajos propios y cuáles son de referencia (ver PLAN-COMPLETO.md, sección de pendientes).
"""
import json
from pathlib import Path

from content import HERO_PHOTOS, PHOTOS

CLIENT_PHOTOS = Path(__file__).resolve().parent / "client_photos.json"

GALLERY_CATS = [
    ("industrial", "Industrial y montaje", "mantenimiento-industrial"),
    ("maquinaria", "Maquinaria y equipos", "montaje-maquinaria-automatizacion"),
    ("obra-civil", "Obra civil", "construccion-obra-civil"),
    ("electrica", "Electricidad", "ingenieria-electrica"),
    ("hvac", "HVAC y refrigeración", "hvac-aire-acondicionado"),
    ("fire", "Contra incendios", "fontaneria-hidraulica-contra-incendios"),
    ("plomeria", "Plomería e hidráulica", "fontaneria-hidraulica-contra-incendios"),
    ("soldadura", "Metalmecánica y soldadura", "metalmecanica-soldadura"),
    ("remodelacion", "Remodelación e interiores", "remodelacion-fit-out"),
    ("epoxi", "Pisos epóxicos", "pisos-pintura-epoxica"),
    ("fachadas", "Fachadas y PH", "mantenimiento-ph-edificios"),
    ("eventos", "Stands y eventos", "stands-corporativos"),
    ("mantenimiento", "Mantenimiento", "mantenimiento-ph-edificios"),
]

EXTRA_CAPTIONS = {
    "fire/fire-01.webp": "Red de rociadores sobre racks en centro de datos",
    "fire/fire-02.webp": "Tubería contra incendios en sala de servidores",
    "fire/fire-03.webp": "Válvula de alarma y tren de control de rociadores",
    "fire/fire-04.webp": "Toma siamesa para bomberos en fachada",
    "fire/fire-06.webp": "Rociadores en nave con tragaluces",
    "fire/fire-07.webp": "Toma de bomberos en escalera de emergencia",
    "fire/fire-08.webp": "Instalación de rociadores desde plataforma elevadora",
    "fire/fire-09.webp": "Rociador oculto en vestíbulo corporativo",
    "fire/fire-10.webp": "Manifold de control con manómetros",
    "fire/fire-11.webp": "Distribución de rociadores sobre tableros",
    "fire/fire-13.webp": "Revisión de panel de detección y alarma",
    "fire/fire-15.webp": "Bomba contra incendio y tablero de control",
    "fire/fire-17.webp": "Cocina industrial con campana y supresión",
    "fire/fire-18.webp": "Ajuste de rociadores en galera logística",
    "fire/fire-19.webp": "Columna seca con toma de bomberos",
    "fire/fire-20.webp": "Montante contra incendios en escalera",
    "fire/fire-21.webp": "Montaje de red en bodega con estanterías",
    "fire/fire-22.webp": "Gabinete de manguera en lobby",
    "fire/fire-23.webp": "Válvula de diluvio y accesorios de control",
    "fire/fire-24.webp": "Tablero de bomba y panel de alarma",
    "fire/fire-25.webp": "Red de rociadores en cuarto eléctrico",
    "fire/fire-27.webp": "Rociador decorativo en cielo de madera",
    "fire/fire-28.webp": "Cuarto eléctrico con tubería roja de protección",
    "fire/fire-29.webp": "Mantenimiento de sistema de supresión en cocina",
    "fire/fire-30.webp": "Manómetros y válvulas en cuarto de bombas",
    "fire/fire-31.webp": "Rociador montante en tubería de acero",
    "fire/fire-32.webp": "Cabezal de succión de bombas contra incendio",
    "fire/fire-34.webp": "Válvula de compuerta en línea de succión",
    "fire/fire-35.webp": "Toma siamesa de bronce en fachada de granito",
    "obra-civil/obra-civil-01.webp": "Concreto lanzado para estabilizar talud",
    "obra-civil/obra-civil-03.webp": "Allanado de losa de concreto en sitio",
    "obra-civil/obra-civil-06.webp": "Terracería y vialidad de parque logístico",
    "obra-civil/obra-civil-07.webp": "Armado de columnas en excavación tablestacada",
    "obra-civil/obra-civil-11.webp": "Estribos y vigas de puente en construcción",
    "obra-civil/obra-civil-12.webp": "Muro de contención curvo en obra",
    "obra-civil/obra-civil-13.webp": "Vista de obra desde oficina de campo",
    "obra-civil/obra-civil-14.webp": "Cuadrilla armando acero de refuerzo",
    "obra-civil/obra-civil-15.webp": "Excavadora y mixer en cimentación",
    "obra-civil/obra-civil-18.webp": "Impermeabilización de azotea",
    "obra-civil/obra-civil-19.webp": "Instalación de cámara de inspección pluvial",
    "obra-civil/obra-civil-21.webp": "Trabajo nocturno de demolición controlada",
    "obra-civil/obra-civil-22.webp": "Oficina adecuada en edificio industrial",
    "obra-civil/obra-civil-25.webp": "Trazo topográfico y planos en losa",
    "obra-civil/obra-civil-27.webp": "Vaciado de losa de cimentación",
    "obra-civil/obra-civil-29.webp": "Trabajos en planta de alimentos en operación",
    "obra-civil/obra-civil-30.webp": "Zanja para canalizaciones subterráneas",
    "plomeria/plomeria-01.webp": "Tanques hidroneumáticos y cabezal de distribución",
    "plomeria/plomeria-02.webp": "Sistema de bombeo de presión constante",
    "plomeria/plomeria-04.webp": "Válvula reductora de presión en ducto",
    "plomeria/plomeria-05.webp": "Instalación de tubería de cobre",
    "plomeria/plomeria-06.webp": "Ajuste de unión en tubería de agua",
    "plomeria/plomeria-07.webp": "Conexión de termofusión a cobre",
    "plomeria/plomeria-09.webp": "Unión de tubería de cobre con llave",
    "plomeria/plomeria-10.webp": "Cuarto de máquinas con tanques y tuberías",
    "plomeria/plomeria-11.webp": "Medición con detector en tubería",
    "plomeria/plomeria-12.webp": "Inspección de trampa de grasa",
    "plomeria/plomeria-13.webp": "Línea de gas en azotea",
    "plomeria/plomeria-14.webp": "Planta de tratamiento de agua",
    "plomeria/plomeria-15.webp": "Instalación de trampa de grasa",
    "plomeria/plomeria-16.webp": "Trampa de grasa en cocina comercial",
    "plomeria/plomeria-17.webp": "Interceptor de grasa bajo fregadero",
    "plomeria/plomeria-19.webp": "Prensado de accesorio de cobre",
    "plomeria/plomeria-20.webp": "Tubería sanitaria colgada en sótano",
    "plomeria/plomeria-21.webp": "Red pluvial en estacionamiento",
    "plomeria/plomeria-22.webp": "Bajantes y colectores en estacionamiento",
    "soldadura/soldadura-01.webp": "Esmerilado de estructura metálica",
    "soldadura/soldadura-02.webp": "Fabricación de escalera metálica",
    "soldadura/soldadura-04.webp": "Soldadura de mezzanine metálico",
    "soldadura/soldadura-05.webp": "Inspección de soldadura en tubería",
    "soldadura/soldadura-08.webp": "Nave de fabricación metalmecánica",
    "soldadura/soldadura-11.webp": "Soldadura de virola de tanque",
    "soldadura/soldadura-12.webp": "Fabricación de tanque de almacenamiento",
    "soldadura/soldadura-13.webp": "Corte y soldadura de lámina curva",
    "soldadura/soldadura-15.webp": "Soldadura TIG de tubería",
    "soldadura/soldadura-18.webp": "Soldadura de unión estructural",
    "soldadura/soldadura-19.webp": "Soldadura de viga en taller",
    "soldadura/soldadura-20.webp": "Soldadura de estructura en altura con arnés",
    "soldadura/soldadura-21.webp": "Corte de acero con chispas",
    "soldadura/soldadura-23.webp": "Soldadura de nodo de estructura",
    "soldadura/soldadura-24.webp": "Cordón de soldadura en tubo",
    "soldadura/soldadura-25.webp": "Reparación de estructura en muelle",
    "soldadura/soldadura-27.webp": "Soldadura de columna metálica",
    "svc/dispron-ebanisteria-1.webp": "Pintura de muros en remodelación",
    "svc/dispron-ebanisteria-3.webp": "Pintura de acento en apartamento",
    "svc/dispron-epoxi-3.webp": "Piso epóxico con canaleta de drenaje",
    "svc/dispron-epoxi-6.webp": "Piso de bodega para montacargas",
    "svc/dispron-eventos-4.webp": "Montaje de stand con estructura de truss",
    "svc/dispron-industrial-1.webp": "Sellado de panel en cuarto frío",
    "svc/dispron-industrial-2.webp": "Centro de datos con racks y climatización",
    "svc/dispron-industrial-5.webp": "Cimentación de nave industrial",
    "svc/dispron-industrial-6.webp": "Armado de pedestales en excavación",
    "svc/dispron-mantenimiento-2.webp": "Mantenimiento de cielo raso en vestíbulo",
    "svc/dispron-mantenimiento-6.webp": "Diagnóstico de cuarto de máquinas",
    "svc/dispron-plomeria-1.webp": "Instalación de tubería de cobre en muro",
    "svc/dispron-plomeria-3.webp": "Cuarto de bombeo y distribución",
    "svc/dispron-plomeria-5.webp": "Ajuste de conexión de cobre",
    "svc/dispron-plomeria-6.webp": "Trampa de grasa en cocina",
    "svc/dispron-remodelacion-1.webp": "Remodelación dentro de planta en operación",
    "svc/dispron-remodelacion-2.webp": "Oficina terminada en edificio histórico",
    "svc/dispron-remodelacion-6.webp": "Acabado de drywall en remodelación",
    "svc/dispron-restauracion-1.webp": "Reparación de grieta en fachada",
    "svc/dispron-restauracion-2.webp": "Tratamiento de acero expuesto en balcón",
    "svc/dispron-restauracion-4.webp": "Sellado de junta en fachada",
}

SVC_CAT = {
    "ebanisteria": "remodelacion", "remodelacion": "remodelacion", "electrica": "electrica", "epoxi": "epoxi",
    "eventos": "eventos", "hero": "obra-civil", "industrial": "industrial", "mantenimiento": "mantenimiento",
    "plomeria": "plomeria", "restauracion": "fachadas",
}


def client_photos():
    if not CLIENT_PHOTOS.exists():
        return []
    return [tuple(x) for x in json.loads(CLIENT_PHOTOS.read_text(encoding="utf-8"))]


def category(src):
    folder, name = src.split("/")
    if folder == "svc":
        return SVC_CAT[name.split("-")[1]]
    return folder


def all_photos():
    caps = dict(EXTRA_CAPTIONS)
    for src, cap in HERO_PHOTOS:
        caps.setdefault(src, cap)
    for items in PHOTOS.values():
        for src, cap in items:
            caps.setdefault(src, cap)
    order = [c for c, _, _ in GALLERY_CATS]
    items = client_photos() + [(src, cap, category(src)) for src, cap in caps.items()]
    items.sort(key=lambda x: (order.index(x[2]), not x[0].startswith("cliente/"), x[0]))
    return items


def gallery_url(src, small=False):
    return "/img/galeria/" + src.replace("/", "-").replace(".webp", "-sm.webp" if small else ".webp")
