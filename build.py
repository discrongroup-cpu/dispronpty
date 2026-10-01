#!/usr/bin/env python3
"""Generador estático del sitio de DISPRON GROUP (dicprom.com). Uso: python3 build.py  ->  dist/"""
import datetime
import html
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "data"))
from content import (CATEGORIES, GENERAL_FAQS, HERO_PHOTOS, INDUSTRIES,  # noqa: E402
                     PROCESS, PROVINCES, SERVICES, VALUES)
from gallery import GALLERY_CATS, all_photos, gallery_url  # noqa: E402

S = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
PLATFORM = json.loads((ROOT / "data" / "platform.json").read_text(encoding="utf-8"))
DIST = ROOT / "dist"
D = S["domain"].rstrip("/")
TODAY = datetime.date.today().isoformat()
BUILD_ID = datetime.datetime.now().strftime("%Y%m%d%H%M")
SVC = {s["slug"]: s for s in SERVICES}
ORG_ID = f"{D}/#organization"
SITE_ID = f"{D}/#website"
LOGO_ID = f"{D}/#logo"
OG_IMAGE = f"{D}/img/og-dispron.jpg"


def e(text):
    return html.escape(str(text), quote=True)


def real(value):
    return bool(value) and "REEMPLAZAR" not in str(value)


def svc_url(slug):
    return f"/servicios/{slug}/"


# ------------------------------------------------------------------ iconos SVG
ICON_PATHS = {
    "design": '<path d="M3 21l3-1 11-11-2-2L4 18l-1 3z"/><path d="M14 6l2-2 4 4-2 2"/><path d="M3 3h6v6H3z"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1.1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.5-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z"/>',
    "robot": '<rect x="4" y="8" width="16" height="11" rx="2"/><path d="M12 4v4M8 13h.01M16 13h.01M9 17h6M2 12v3M22 12v3"/>',
    "plant": '<path d="M2 21h20M4 21V10l5 3V8l5 3V4h4v17"/><path d="M18 8h2v13"/>',
    "crane": '<path d="M4 21V3h2v18M6 5h14l-3 4M6 3l14 2M17 9v5"/><rect x="15" y="14" width="4" height="3"/><path d="M2 21h8"/>',
    "brush": '<path d="M18 2l4 4-9 9-4-4 9-9z"/><path d="M9 11l-4 4c-1.5 1.5-1 4-3 6 3 0 6-.5 7.5-2l4-4"/>',
    "layers": '<path d="M12 2l10 5-10 5L2 7l10-5z"/><path d="M2 12l10 5 10-5M2 17l10 5 10-5"/>',
    "building": '<rect x="4" y="2" width="16" height="20" rx="1"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>',
    "cube": '<path d="M21 16V8l-9-5-9 5v8l9 5 9-5z"/><path d="M3.3 7L12 12l8.7-5M12 22V12"/>',
    "stand": '<rect x="3" y="3" width="18" height="12" rx="1"/><path d="M7 21h10M12 15v6M7 7h6M7 10h10"/>',
    "key": '<circle cx="7.5" cy="15.5" r="4.5"/><path d="M10.7 12.3L21 2M16 7l3 3M18 5l2 2"/>',
    "bolt": '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>',
    "snow": '<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1L19.1 4.9M9 3l3 3 3-3M9 21l3-3 3 3M3 9l3 3-3 3M21 9l-3 3 3 3"/>',
    "weld": '<path d="M2 22l6-6M8 16l3 3 9-9-3-3-9 9z"/><path d="M14 4l1-2M18 6l2-1M17 3l1-1"/>',
    "drop": '<path d="M12 2.7l5.7 5.6a8 8 0 11-11.4 0L12 2.7z"/>',
    "box": '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3.3 7.6L12 12.5l8.7-4.9M12 22V12.5M7.5 5.3l9 5"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.4 1.8.7 2.7a2 2 0 01-.5 2.1L8 9.8a16 16 0 006 6l1.3-1.3a2 2 0 012.1-.4c.9.3 1.8.6 2.7.7a2 2 0 011.7 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON_PATHS[name]}</svg>')


WA_SVG = ('<svg class="ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1112 21.8zm8.4-18.2A11.8 11.8 0 002 17.7L.3 24l6.4-1.7A11.8 11.8 0 0024 12c0-3.2-1.2-6.2-3.6-8.4z"/></svg>')


# ------------------------------------------------------------------ JSON-LD
def postal_address():
    a = S["address"]
    node = {"@type": "PostalAddress", "addressLocality": a["locality"], "addressRegion": a["region"],
            "postalCode": a["postalCode"], "addressCountry": a["country"]}
    if real(a["street"]):
        node["streetAddress"] = a["street"]
    return node


def area_served():
    country = {"@type": "Country", "name": "Panamá", "sameAs": "https://www.wikidata.org/wiki/Q804"}
    return [country] + [{"@type": "AdministrativeArea", "name": p, "containedInPlace": {"@type": "Country", "name": "Panamá"}}
                        for p, _ in PROVINCES[:-1]]


def organization_node():
    node = {
        "@type": ["GeneralContractor", "ProfessionalService"],
        "@id": ORG_ID,
        "name": S["brand"],
        "legalName": S["legalName"],
        "alternateName": S["alternateNames"],
        "url": f"{D}/",
        "logo": {"@type": "ImageObject", "@id": LOGO_ID, "url": f"{D}/img/logo-dispron-vertical.png", "contentUrl": f"{D}/img/logo-dispron-vertical.png",
                 "width": 765, "height": 526, "caption": f"Logotipo {S['brand']}"},
        "image": [OG_IMAGE, f"{D}/img/logo-dispron-horizontal.png"] + [f"{D}/img/hero/hero-{i + 1}.webp" for i in range(len(HERO_PHOTOS))],
        "description": ("DISPRON GROUP es una empresa panameña de diseño industrial, ingeniería de producto, mantenimiento industrial "
                        "predictivo, construcción y obra civil, remodelación y fit-out, ingeniería eléctrica, HVAC, metalmecánica, "
                        "soldadura, fontanería y sistemas contra incendios, con cobertura en toda la República de Panamá."),
        "slogan": S["slogan"],
        "telephone": S["phone"],
        "email": S["email"],
        "address": postal_address(),
        "geo": {"@type": "GeoCoordinates", "latitude": S["geo"]["lat"], "longitude": S["geo"]["lng"]},
        "hasMap": S["googleMapsUrl"],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]} for h in S["hours"]],
        "areaServed": area_served(),
        "priceRange": "$$",
        "currenciesAccepted": "USD",
        "paymentAccepted": "Transferencia bancaria, ACH, cheque, tarjeta de crédito",
        "knowsLanguage": ["es", "en"],
        "knowsAbout": [s["serviceType"] for s in SERVICES] + [
            "Termografía infrarroja", "Análisis de vibraciones", "Análisis por elementos finitos (FEA)", "Ergonomía industrial",
            "Proyectos EPC llave en mano", "Subestaciones eléctricas", "Chillers y sistemas VRF", "Soldadura SMAW GMAW GTAW",
            "Pintura epóxica", "Fit-out de oficinas", "Render 3D", "Stands para ferias", "NFPA 13", "ASME B31.3", "AWS D1.1"],
        "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "telephone": S["phone"], "email": S["email"],
                          "areaServed": "PA", "availableLanguage": ["Spanish", "English"]},
                         {"@type": "ContactPoint", "contactType": "emergency", "telephone": S["phone"], "areaServed": "PA",
                          "availableLanguage": ["Spanish"], "hoursAvailable": {"@type": "OpeningHoursSpecification",
                          "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}}],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Servicios de ingeniería, construcción y mantenimiento DISPRON GROUP",
            "itemListElement": [{"@type": "OfferCatalog", "name": cname, "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@id": f"{D}{svc_url(s['slug'])}#service"}} for s in SERVICES if s["cat"] == ckey]}
                for ckey, cname in CATEGORIES]},
        "sameAs": [u for u in S["sameAs"] if u],
    }
    if real(S["foundingYear"]):
        node["foundingDate"] = S["foundingYear"]
    if real(S["taxID"]):
        node["taxID"] = S["taxID"]
    node["foundingLocation"] = {"@type": "Place", "name": "Ciudad de Panamá, Panamá"}
    return node


def website_node():
    return {"@type": "WebSite", "@id": SITE_ID, "url": f"{D}/", "name": S["brand"], "alternateName": S["alternateNames"],
            "description": S["tagline"], "publisher": {"@id": ORG_ID}, "inLanguage": "es-PA"}


def service_node(s):
    url = f"{D}{svc_url(s['slug'])}"
    return {
        "@type": "Service", "@id": f"{url}#service", "name": s["name"], "serviceType": s["serviceType"],
        "description": s["desc"], "url": url, "provider": {"@id": ORG_ID}, "brand": {"@id": ORG_ID},
        "areaServed": {"@type": "Country", "name": "Panamá", "sameAs": "https://www.wikidata.org/wiki/Q804"},
        "audience": {"@type": "BusinessAudience", "audienceType": ", ".join(s["applications"])},
        "category": dict(CATEGORIES)[s["cat"]],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["name"], "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": h, "description": p}} for h, p in s["items"]]},
        "termsOfService": f"{D}/politica-de-privacidad/",
        "image": [{"@type": "ImageObject", "contentUrl": f"{D}/img/obras/{s['slug']}-{i + 1}.webp", "caption": cap}
                  for i, (_src, cap) in enumerate(s["photos"])],
    }


def faq_node(url, faqs):
    return {"@type": "FAQPage", "@id": f"{url}#faq", "url": url, "isPartOf": {"@id": f"{url}#webpage"}, "inLanguage": "es-PA",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def breadcrumb_node(url, crumbs):
    return {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{D}{p}"} for i, (n, p) in enumerate(crumbs)]}


def webpage_node(url, title, desc, ptype="WebPage", extra=None):
    node = {"@type": ptype, "@id": f"{url}#webpage", "url": url, "name": title, "description": desc,
            "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
            "primaryImageOfPage": {"@type": "ImageObject", "url": OG_IMAGE}, "inLanguage": "es-PA",
            "datePublished": "2026-10-01", "dateModified": TODAY, "breadcrumb": {"@id": f"{url}#breadcrumb"}}
    node.update(extra or {})
    return node


# ------------------------------------------------------------------ imágenes
PHOTO_DIMS = {}
LOAD_EAGER = 'fetchpriority="high"'
LOAD_LAZY = 'loading="lazy"'


def photo_url(slug, i, small=False):
    return f"/img/obras/{slug}-{i}{'-sm' if small else ''}.webp"


def dims(url):
    if url not in PHOTO_DIMS:
        with Image.open(ROOT / "static" / url.lstrip("/")) as im:
            PHOTO_DIMS[url] = im.size
    return PHOTO_DIMS[url]


def picture(url, alt, cls="", eager=False, sizes="(max-width: 700px) 100vw, 400px"):
    small = url.replace(".webp", "-sm.webp")
    w, h = dims(url)
    sw = dims(small)[0]
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{url}" srcset="{small} {sw}w, {url} {w}w" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{e(alt)}" {load}>')


def svc_photos(s):
    return [(photo_url(s["slug"], i + 1), cap) for i, (_src, cap) in enumerate(s["photos"])]


def svc_cover(s):
    return svc_photos(s)[0][0]


# ------------------------------------------------------------------ layout
NAV = [("/servicios/", "Servicios"), ("/sectores/", "Sectores"), ("/proyectos/", "Proyectos"), ("/blog/", "Blog"),
       ("/recursos/", "Recursos"), ("/nosotros/", "Nosotros"), ("/contacto/", "Contacto")]


def nav_html(active):
    groups = ""
    for ckey, cname in CATEGORIES:
        links = "".join(f'<li><a href="{svc_url(s["slug"])}">{icon(s["icon"])}<span>{e(s["name"])}</span></a></li>'
                        for s in SERVICES if s["cat"] == ckey)
        groups += f'<div class="mega-col"><p class="mega-title">{e(cname)}</p><ul>{links}</ul></div>'
    items = ""
    for path, label in NAV:
        cur = ' aria-current="page"' if active == path else ""
        if path == "/servicios/":
            items += (f'<li class="has-mega"><a href="{path}"{cur}>{label}<svg class="chev" viewBox="0 0 24 24" aria-hidden="true">'
                      f'<path d="M6 9l6 6 6-6"/></svg></a><div class="mega"><div class="mega-inner">{groups}</div></div></li>')
        else:
            items += f'<li><a href="{path}"{cur}>{label}</a></li>'
    return f'''<header class="site-header" id="top">
  <div class="topbar"><div class="container topbar-inner">
    <span>{icon("pin")} Cobertura en toda la República de Panamá</span>
    <span class="topbar-r"><a href="tel:{e(S["phone"])}">{icon("phone")} {e(S["phoneDisplay"])}</a><a href="mailto:{e(S["email"])}">{icon("mail")} {e(S["email"])}</a><span class="badge-24">{icon("clock")} Emergencias 24/7</span></span>
  </div></div>
  <div class="container header-inner">
    <a class="brand" href="/" aria-label="{e(S["brand"])} – inicio"><img src="/img/logo-dispron-horizontal.png" alt="Logotipo {e(S["brand"])}" width="1114" height="416"></a>
    <nav id="nav" class="nav" aria-label="Principal"><ul class="nav-list">{items}</ul>
      <a class="btn btn-gold nav-cta" href="/cotizar/">Cotizar proyecto {icon("arrow")}</a></nav>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Abrir menú"><span></span><span></span><span></span></button>
  </div>
</header>'''


def footer_html():
    cols = ""
    for ckey, cname in CATEGORIES:
        links = "".join(f'<li><a href="{svc_url(s["slug"])}">{e(s["name"])}</a></li>' for s in SERVICES if s["cat"] == ckey)
        cols += f'<div><p class="f-title">{e(cname)}</p><ul>{links}</ul></div>'
    a = S["address"]
    street = f'{e(a["street"])}, ' if real(a["street"]) else ""
    social = "".join(f'<li><a href="{e(u)}" rel="noopener me" target="_blank">{e(u.split("/")[2].replace("www.", "").split(".")[0].capitalize())}</a></li>' for u in S["sameAs"] if u)
    return f'''<footer class="site-footer">
  <div class="footer-cta container">
    <div><p class="eyebrow">Hablemos de su proyecto</p><p class="footer-cta-t">Un solo responsable técnico, de la ingeniería al mantenimiento.</p></div>
    <a class="btn btn-gold" href="/cotizar/">Solicitar cotización {icon("arrow")}</a>
  </div>
  <div class="container footer-grid">
    <div class="f-brand">
      <a class="f-logo" href="/" aria-label="{e(S["brand"])}"><img src="/img/logo-dispron-mark-light.png" alt="" width="243" height="256" loading="lazy"><span>DISPRON <b>GROUP</b></span></a>
      <p>{e(S["tagline"])}. Diseño industrial, mantenimiento, obra civil, electricidad, HVAC, metalmecánica e hidráulica en toda la República de Panamá.</p>
      <address>
        <p>{icon("pin")} {street}{e(a["locality"])}, Panamá</p>
        <p>{icon("phone")} <a href="tel:{e(S["phone"])}">{e(S["phoneDisplay"])}</a></p>
        <p>{icon("mail")} <a href="mailto:{e(S["email"])}">{e(S["email"])}</a></p>
        <p>{icon("clock")} {e(S["hoursDisplay"])}</p>
      </address>
      <ul class="social">{social}</ul>
    </div>
    {cols}
  </div>
  <div class="container footer-bottom">
    <p>© {datetime.date.today().year} {e(S["legalName"])} · Todos los derechos reservados.</p>
    <p><a href="/sectores/">Sectores</a> · <a href="/blog/">Blog técnico</a> · <a href="/recursos/">Recursos</a> · <a href="/cobertura/">Cobertura</a> · <a href="/preguntas-frecuentes/">Preguntas</a> · <a href="/politica-de-privacidad/">Privacidad</a> · <a href="/sitemap.xml">Mapa del sitio</a> · <a href="/acceso/" rel="nofollow">Acceso del equipo</a></p>
  </div>
</footer>
<a class="wa-float" href="https://wa.me/{e(S["whatsapp"])}?text={e("Hola DISPRON GROUP, quiero solicitar una cotización.")}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp">{WA_SVG}</a>
<a class="to-top" href="#top" aria-label="Volver arriba">{icon("arrow")}</a>'''


def breadcrumbs_html(crumbs):
    if len(crumbs) < 2:
        return ""
    parts = []
    for i, (n, p) in enumerate(crumbs):
        parts.append(f'<li><span aria-current="page">{e(n)}</span></li>' if i == len(crumbs) - 1 else f'<li><a href="{p}">{e(n)}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Migas de pan"><ol>{"".join(parts)}</ol></nav>'


def page(path, title, desc, body, graph, crumbs, active=None, og_type="website", robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1", images=None,
         listed=True, chrome=True, sofia=True, css=(), scripts=(), body_class=""):
    url = f"{D}{path}"
    ld = {"@context": "https://schema.org", "@graph": [organization_node(), website_node()] + graph + ([breadcrumb_node(url, crumbs)] if crumbs else [])}
    verif = ""
    if S.get("googleSiteVerification"):
        verif += f'<meta name="google-site-verification" content="{e(S["googleSiteVerification"])}">\n'
    if S.get("bingSiteVerification"):
        verif += f'<meta name="msvalidate.01" content="{e(S["bingSiteVerification"])}">\n'
    ga = ""
    if S.get("gaMeasurementId"):
        gid = e(S["gaMeasurementId"])
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{gid}");</script>')
    doc = f'''<!doctype html>
<html lang="es-PA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="es-PA" href="{url}">
<link rel="alternate" hreflang="es" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="author" content="{e(S["brand"])}">
<meta name="geo.region" content="PA-8">
<meta name="geo.placename" content="Ciudad de Panamá">
<meta name="geo.position" content="{S["geo"]["lat"]};{S["geo"]["lng"]}">
<meta name="ICBM" content="{S["geo"]["lat"]}, {S["geo"]["lng"]}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="es_PA">
<meta property="og:site_name" content="{e(S["brand"])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(S["brand"])} – {e(S["tagline"])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<meta name="theme-color" content="#0f1a2b">
{verif}<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/img/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/fonts/montserrat-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/styles.css?v={BUILD_ID}">
{"".join(f'<link rel="stylesheet" href="{c}?v={BUILD_ID}">' for c in css)}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
{ga}</head>
<body{f' class="{body_class}"' if body_class else ""}>
<a class="skip" href="#main">Saltar al contenido</a>
{nav_html(active or path) if chrome else mini_header()}
<main id="main">
{body}
</main>
{footer_html() if chrome else ""}
{sofia_html() if chrome and sofia else ""}
<script src="/js/main.js?v={BUILD_ID}" defer></script>
{"".join(f'<script src="{j}?v={BUILD_ID}" defer></script>' for j in scripts)}
</body>
</html>
'''
    doc = doc.replace("<!--CRUMBS-->", breadcrumbs_html(crumbs))
    out = DIST / path.strip("/") / "index.html" if path.endswith("/") else DIST / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    if listed:
        PAGES.append(path)
        PAGE_IMAGES[path] = images or []


PAGES = []
PAGE_IMAGES = {}


# ------------------------------------------------------------------ bloques reutilizables
def page_hero(h1, lead, bg=None, eyebrow="", extra="", aside=""):
    style = f' style="--hero-bg:url(\'{bg}\')"' if bg else ""
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    return f'''<section class="page-hero{' has-bg' if bg else ''}"{style}>
  <div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div>
  <div class="container page-hero-inner{' with-aside' if aside else ''}">
    <div class="reveal"><!--CRUMBS-->{eb}<h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div>
    {aside}
  </div>
</section>'''


def chevrons_svg():
    return ('<svg viewBox="0 0 600 600" preserveAspectRatio="xMaxYMid slice"><g fill="none" stroke-width="2">'
            '<path class="l1" d="M80 60 L80 420 L300 560 L520 420 L520 140"/>'
            '<path class="l2" d="M160 120 L160 380 L300 470 L440 380 L440 220 L360 220"/>'
            '<path class="l3" d="M520 60 L300 200 L300 300"/></g></svg>')


def cta_block(title="¿Tiene un proyecto en Panamá?", text="Cuéntenos su necesidad y reciba una propuesta técnica y económica sin compromiso."):
    return f'''<section class="cta"><div class="container cta-inner reveal">
  <div class="cta-mark" aria-hidden="true"><img src="/img/logo-dispron-mark-light.png" alt="" width="243" height="256" loading="lazy"></div>
  <div class="cta-text"><h2>{e(title)}</h2><p>{e(text)}</p></div>
  <div class="cta-actions"><a class="btn btn-gold" href="/cotizar/">Solicitar cotización {icon("arrow")}</a>
  <a class="btn btn-ghost" href="https://wa.me/{e(S["whatsapp"])}" target="_blank" rel="noopener">{WA_SVG} WhatsApp</a></div>
</div></section>'''


def faq_html(faqs, title="Preguntas frecuentes", eyebrow="Respuestas claras"):
    items = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3><span class="faq-i" aria-hidden="true"></span></summary><div class="faq-a"><p>{e(a)}</p></div></details>' for q, a in faqs)
    return f'<section class="section" id="faq"><div class="container narrow"><div class="sec-head center reveal"><p class="eyebrow dk">{e(eyebrow)}</p><h2>{e(title)}</h2></div>{items}</div></section>'


def service_card(s, n=None):
    num = f'<span class="num">{n:02d}</span>' if n else ""
    return (f'<a class="svc-card reveal" href="{svc_url(s["slug"])}"><div class="svc-ph">'
            f'{picture(svc_cover(s), s["photos"][0][1] + " – " + s["name"] + " en Panamá", sizes="(max-width: 700px) 100vw, (max-width: 1080px) 50vw, 380px")}{num}</div>'
            f'<div class="svc-body"><span class="svc-ico">{icon(s["icon"])}</span><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p>'
            f'<span class="more">Ver servicio {icon("arrow")}</span></div></a>')


def process_html():
    steps = "".join(f'<li class="reveal"><span class="step-n">{i + 1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(PROCESS))
    return f'''<section class="section dark process"><div class="container">
  <div class="sec-head reveal"><p class="eyebrow">Metodología</p><h2>Cómo trabajamos</h2><p class="sec-lead">Un proceso claro, documentado y con un solo responsable técnico desde la primera visita hasta el mantenimiento.</p></div>
  <ol class="steps">{steps}</ol></div></section>'''


def gallery_html(photos, label):
    items = "".join(f'<figure class="g-item reveal"><a href="{u}" data-lightbox data-caption="{e(c)}">{picture(u, c + " – " + label, sizes="(max-width: 700px) 100vw, 400px")}</a><figcaption>{e(c)}</figcaption></figure>' for u, c in photos)
    return f'<div class="gallery">{items}</div>'


# ------------------------------------------------------------------ páginas
def build_home():
    path = "/"
    title = "DISPRON GROUP | Ingeniería, Construcción y Mantenimiento en Panamá"
    desc = ("Empresa panameña de ingeniería, construcción y mantenimiento industrial: obra civil, fit-out, electricidad, "
            "HVAC, soldadura y contra incendios en todo Panamá.")
    slides = "".join(
        f'<img class="slide" src="/img/hero/hero-{i + 1}.webp" srcset="/img/hero/hero-{i + 1}-sm.webp 800w, /img/hero/hero-{i + 1}.webp 1600w" '
        f'sizes="100vw" alt="" {LOAD_EAGER if i == 0 else LOAD_LAZY} decoding="async" style="--i:{i}">' for i in range(len(HERO_PHOTOS)))
    ticker = "".join(f'<li>{icon(s["icon"])}{e(s["serviceType"])}</li>' for s in SERVICES)
    bento = ""
    for idx, (ckey, cname) in enumerate(CATEGORIES):
        svcs = [s for s in SERVICES if s["cat"] == ckey]
        links = "".join(f'<li><a href="{svc_url(s["slug"])}">{e(s["name"])}</a></li>' for s in svcs)
        bento += (f'<article class="bento-tile t{idx + 1} reveal">{picture(svc_cover(svcs[0]), cname, sizes="(max-width: 700px) 100vw, 600px")}'
                  f'<div class="bento-body"><span class="bento-n">{idx + 1:02d} · {len(svcs)} servicios</span><h3>{e(cname)}</h3><ul>{links}</ul></div></article>')
    cards = "".join(service_card(s, i + 1) for i, s in enumerate(SERVICES))
    values = "".join(f'<div class="value reveal">{icon("shield")}<h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in VALUES)
    inds = "".join(f"<li>{icon('check')}{e(i)}</li>" for i in INDUSTRIES)
    provs = "".join(f"<li>{e(p)}</li>" for p, _ in PROVINCES)
    strip_photos = [p for s in SERVICES for p in svc_photos(s)[1:2]]
    strip = "".join(f'<figure>{picture(u, c, sizes="320px")}</figure>' for u, c in strip_photos)
    body = f'''<section class="hero">
  <div class="hero-slides" aria-hidden="true">{slides}</div>
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div>
  <div class="container hero-inner">
    <div class="hero-copy">
      <p class="eyebrow pill"><span class="dot"></span>Ingeniería · Construcción · Mantenimiento · Panamá</p>
      <h1>Ingeniería, construcción y mantenimiento industrial <span class="gold-text">en Panamá</span></h1>
      <p class="lead"><strong>DISPRON GROUP</strong> es una empresa panameña multidisciplinaria que diseña, construye, instala y mantiene infraestructura industrial, comercial y residencial —obra civil, remodelaciones, electricidad, HVAC, metalmecánica, hidráulica y sistemas contra incendios— con proyectos llave en mano en toda la República de Panamá.</p>
      <div class="hero-actions"><a class="btn btn-gold" href="/cotizar/">Solicitar cotización {icon("arrow")}</a><a class="btn btn-ghost" href="/servicios/">Explorar servicios</a></div>
    </div>
    <aside class="hero-panel" aria-label="DISPRON GROUP en cifras">
      <img class="hero-panel-logo" src="/img/logo-dispron-mark-light.png" alt="" width="243" height="256">
      <ul class="stats">
        <li><strong data-count="{len(SERVICES)}">{len(SERVICES)}</strong><span>líneas de servicio</span></li>
        <li><strong data-count="10">10</strong><span>provincias + comarcas</span></li>
        <li><strong>24/7</strong><span>atención de emergencias</span></li>
        <li><strong>EPC</strong><span>proyectos llave en mano</span></li>
      </ul>
    </aside>
  </div>
  <div class="ticker" aria-hidden="true"><ul>{ticker}{ticker}</ul></div>
</section>
<section class="section intro"><div class="container split">
  <div class="reveal"><p class="eyebrow dk">Un solo aliado técnico</p><h2>Diseñamos, construimos y mantenemos la infraestructura que mueve a Panamá</h2>
  <p>Integramos ingeniería, obra civil, instalaciones electromecánicas, metalmecánica y suministro bajo una misma gerencia. Menos interfaces entre contratistas, plazos más cortos y un responsable único por resultados, seguridad y calidad.</p>
  <ul class="checklist">{"".join(f"<li>{icon('check')}{e(t)}</li>" for t, _ in VALUES[:4])}</ul>
  <a class="link" href="/nosotros/">Conozca DISPRON GROUP {icon("arrow")}</a></div>
  <div class="split-media reveal">{picture(svc_photos(SVC["construccion-obra-civil"])[0][0], "Obra civil ejecutada por DISPRON GROUP en Panamá", sizes="(max-width: 960px) 100vw, 560px")}
    <div class="float-card">{icon("shield")}<div><strong>Seguridad y calidad</strong><span>Normas REP, NFPA, ASHRAE, AWS y API</span></div></div></div>
</div></section>
<section class="section alt" id="areas"><div class="container">
  <div class="sec-head reveal"><p class="eyebrow dk">Áreas de negocio</p><h2>Cuatro divisiones, una sola operación</h2></div>
  <div class="bento">{bento}</div>
</div></section>
<section class="section" id="servicios"><div class="container">
  <div class="sec-head row reveal"><div><p class="eyebrow dk">Servicios</p><h2>Servicios de ingeniería y construcción en Panamá</h2></div><a class="link" href="/servicios/">Ver todos {icon("arrow")}</a></div>
  <div class="svc-grid four">{cards}</div>
</div></section>
{process_html()}
<section class="section"><div class="container">
  <div class="sec-head center reveal"><p class="eyebrow dk">Por qué elegirnos</p><h2>¿Por qué elegir DISPRON GROUP?</h2></div>
  <div class="values">{values}</div>
</div></section>
<section class="section alt works"><div class="container sec-head row reveal"><div><p class="eyebrow dk">Proyectos</p><h2>Trabajo real en campo</h2></div><a class="link" href="/proyectos/">Ver galería de proyectos {icon("arrow")}</a></div>
  <div class="marquee" aria-label="Fotografías de proyectos"><div class="marquee-track">{strip}{strip.replace('alt="', 'aria-hidden="true" alt="" data-alt="')}</div></div>
</section>
<section class="section"><div class="container two-col">
  <div class="reveal"><p class="eyebrow dk">Sectores</p><h2>Industrias que atendemos</h2><ul class="checklist cols-2">{inds}</ul></div>
  <div class="reveal coverage-card"><p class="eyebrow">Cobertura nacional</p><h2>Presentes en toda Panamá</h2><p>Movilizamos cuadrillas, equipos e ingenieros desde la Ciudad de Panamá hacia todas las provincias y comarcas.</p><ul class="pill-list">{provs}</ul><a class="link light" href="/cobertura/">Ver cobertura detallada {icon("arrow")}</a></div>
</div></section>
{home_platform_sections()}
<section class="section alt"><div class="container narrow summary reveal">
  <p class="eyebrow dk">Ficha de empresa</p>
  <h2>DISPRON GROUP en resumen</h2>
  <dl class="facts">
    <dt>Qué es</dt><dd>Empresa panameña de diseño industrial, ingeniería, construcción, mantenimiento industrial y suministro de equipos.</dd>
    <dt>Sede</dt><dd>{e(S["address"]["locality"])}, República de Panamá.</dd>
    <dt>Cobertura</dt><dd>Todas las provincias de Panamá y comarcas, incluidos puertos, zonas francas y proyectos mineros.</dd>
    <dt>Especialidades</dt><dd>Diseño industrial y FEA, mantenimiento predictivo (termografía y vibraciones), montaje de maquinaria, obra civil, fit-out, pintura epóxica, mantenimiento de PH, arquitectura y render 3D, stands corporativos, EPC, electricidad de potencia, HVAC, soldadura, fontanería y contra incendios.</dd>
    <dt>Modalidades</dt><dd>Llave en mano (EPC), administración de obra, contratos de mantenimiento, consultoría e inspección técnica.</dd>
    <dt>Contacto</dt><dd><a href="tel:{e(S["phone"])}">{e(S["phoneDisplay"])}</a> · <a href="mailto:{e(S["email"])}">{e(S["email"])}</a></dd>
  </dl>
</div></section>
{faq_html(GENERAL_FAQS[:6])}
{cta_block()}'''
    url = f"{D}/"
    graph = [webpage_node(url, title, desc, extra={"mainEntity": {"@id": ORG_ID}}), faq_node(url, GENERAL_FAQS[:6]),
             {"@type": "ItemList", "@id": f"{url}#servicios", "name": "Servicios DISPRON GROUP", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": f"{D}{svc_url(s['slug'])}", "name": s["name"]} for i, s in enumerate(SERVICES)]}]
    page(path, title, desc, body, graph, [("Inicio", "/")], images=[(f"/img/hero/hero-{i + 1}.webp", c) for i, (_s, c) in enumerate(HERO_PHOTOS)])


def build_services_hub():
    path = "/servicios/"
    title = "Servicios de Ingeniería y Construcción en Panamá | DISPRON GROUP"
    desc = "Servicios DISPRON GROUP en Panamá: diseño industrial, mantenimiento, montaje, obra civil, fit-out, eléctrico, HVAC, metalmecánica, hidráulica y suministro."
    sections = ""
    n = 0
    for ckey, cname in CATEGORIES:
        cards = ""
        for s in SERVICES:
            if s["cat"] == ckey:
                n += 1
                cards += service_card(s, n)
        sections += f'<section class="section"><div class="container"><div class="sec-head reveal"><p class="eyebrow dk">División</p><h2>{e(cname)}</h2></div><div class="svc-grid">{cards}</div></div></section>'
    body = f'''{page_hero("Servicios de ingeniería, construcción y mantenimiento en Panamá",
                      f"DISPRON GROUP integra {len(SERVICES)} líneas de servicio para que su empresa tenga un único aliado técnico durante todo el ciclo de vida de sus instalaciones.",
                      bg="/img/hero/hero-4.webp", eyebrow="Catálogo de servicios")}
{sections}{process_html()}{cta_block()}'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, "CollectionPage", {"mainEntity": {"@id": f"{url}#lista"}}),
             {"@type": "ItemList", "@id": f"{url}#lista", "name": "Servicios DISPRON GROUP", "numberOfItems": len(SERVICES), "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": f"{D}{svc_url(s['slug'])}", "name": s["name"]} for i, s in enumerate(SERVICES)]}]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Servicios", path)], active="/servicios/",
         images=[(svc_cover(s), s["photos"][0][1]) for s in SERVICES])


def build_service(s):
    path = svc_url(s["slug"])
    url = f"{D}{path}"
    photos = svc_photos(s)
    intro = "".join(f"<p>{e(p)}</p>" for p in s["intro"])
    items = "".join(f'<article class="item reveal"><span class="item-n">{i + 1:02d}</span><h3>{e(h)}</h3><p>{e(p)}</p></article>' for i, (h, p) in enumerate(s["items"]))
    apps = "".join(f"<li>{icon('check')}{e(a)}</li>" for a in s["applications"])
    stds = "".join(f"<li>{icon('shield')}{e(a)}</li>" for a in s["standards"])
    rel = "".join(service_card(SVC[r]) for r in s["related"])
    actions = (f'<div class="hero-actions"><a class="btn btn-gold" href="/cotizar/?servicio={e(s["slug"])}">Cotizar este servicio {icon("arrow")}</a>'
               f'<a class="btn btn-ghost" href="https://wa.me/{e(S["whatsapp"])}?text={e("Hola DISPRON GROUP, necesito información sobre " + s["name"])}" target="_blank" rel="noopener">{WA_SVG} WhatsApp</a></div>')
    aside = f'''<aside class="facts-card reveal" aria-label="Datos clave">
    <p class="facts-title">{icon(s["icon"])} Datos clave</p>
    <dl class="facts">
      <dt>Servicio</dt><dd>{e(s["serviceType"])}</dd>
      <dt>Proveedor</dt><dd>{e(S["brand"])}</dd>
      <dt>Cobertura</dt><dd>Toda la República de Panamá</dd>
      <dt>Sectores</dt><dd>{e(", ".join(s["applications"][:3]))}</dd>
      <dt>Normas</dt><dd>{e(", ".join(x.split(" (")[0] for x in s["standards"][:3]))}</dd>
    </dl>
  </aside>'''
    body = f'''{page_hero(e(s["name"]) + ' <span class="gold-text">en Panamá</span>', e(s["lead"]), bg=photos[0][0], eyebrow=dict(CATEGORIES)[s["cat"]], extra=actions, aside=aside)}
<section class="section"><div class="container split">
  <div class="prose reveal"><p class="eyebrow dk">Descripción del servicio</p><h2>¿Qué ofrece DISPRON GROUP en {e(s["serviceType"].lower())}?</h2>{intro}</div>
  <div class="split-media reveal">{picture(photos[1][0], photos[1][1] + " – " + s["name"], sizes="(max-width: 960px) 100vw, 560px")}</div>
</div></section>
<section class="section alt"><div class="container">
  <div class="sec-head reveal"><p class="eyebrow dk">Alcance</p><h2>Servicios incluidos</h2></div>
  <div class="items">{items}</div>
</div></section>
<section class="section"><div class="container two-col">
  <div class="reveal"><p class="eyebrow dk">Aplicaciones</p><h2>Sectores y aplicaciones</h2><ul class="checklist">{apps}</ul></div>
  <div class="reveal"><p class="eyebrow dk">Calidad</p><h2>Normas y buenas prácticas</h2><ul class="checklist">{stds}</ul><p class="note">Trabajamos conforme a la normativa panameña aplicable y a los estándares internacionales indicados según el alcance de cada proyecto.</p></div>
</div></section>
<section class="section alt"><div class="container">
  <div class="sec-head row reveal"><div><p class="eyebrow dk">Proyectos</p><h2>{e(s["name"])}: trabajo en campo</h2></div><a class="link" href="/proyectos/">Ver todos los proyectos {icon("arrow")}</a></div>
  {gallery_html(photos, s["name"] + " en Panamá – DISPRON GROUP")}
</div></section>
{related_posts_html([p for p in POSTS if s["slug"] in post_services(p)], "Guías y artículos sobre " + s["serviceType"].lower())}
{process_html()}
{faq_html(s["faqs"], "Preguntas frecuentes sobre " + s["serviceType"].lower())}
<section class="section alt"><div class="container"><div class="sec-head reveal"><p class="eyebrow dk">Complementos</p><h2>Servicios relacionados</h2></div><div class="svc-grid">{rel}</div></div></section>
{cta_block("Cotice " + s["serviceType"].lower() + " en Panamá")}'''
    graph = [webpage_node(url, s["title"], s["desc"], extra={"mainEntity": {"@id": f"{url}#service"},
                                                             "primaryImageOfPage": {"@type": "ImageObject", "url": f"{D}{photos[0][0]}", "caption": photos[0][1]}}),
             service_node(s), faq_node(url, s["faqs"])]
    page(path, s["title"], s["desc"], body, graph, [("Inicio", "/"), ("Servicios", "/servicios/"), (s["name"], path)], active="/servicios/", og_type="article",
         images=photos)


def build_coverage():
    path = "/cobertura/"
    title = "Cobertura en Toda Panamá: Provincias y Ciudades | DISPRON GROUP"
    desc = "DISPRON GROUP ejecuta ingeniería, construcción y mantenimiento en todas las provincias de Panamá: Panamá, Colón, Chiriquí, Coclé, Veraguas, Azuero, Bocas y Darién."
    rows = "".join(f'<article class="card prov">{icon("pin")}<h2>{e(p)}</h2><p>{e(c)}.</p></article>' for p, c in PROVINCES)
    body = f'''<section class="page-hero"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div><div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><h1>Ingeniería, construcción y mantenimiento en toda Panamá</h1>
<p class="lead">Desde nuestra sede en la Ciudad de Panamá movilizamos cuadrillas, equipos e ingenieros a cualquier provincia, zona franca, puerto o proyecto minero del país.</p></div></div></section>
<section class="section"><div class="container"><div class="grid grid-3">{rows}</div></div></section>
<section class="section alt"><div class="container narrow prose">
<h2>Áreas industriales y logísticas</h2>
<p>Atendemos clientes en la Zona Libre de Colón, Panamá Pacífico, los puertos de Balboa, Manzanillo, Cristóbal y Rodman, el corredor logístico de Tocumen y Juan Díaz, parques industriales de Panamá Oeste y Chiriquí, y proyectos mineros y energéticos en el interior del país.</p>
<p>Todos nuestros servicios —desde el <a href="{svc_url("mantenimiento-industrial")}">mantenimiento industrial</a> y la <a href="{svc_url("ingenieria-electrica")}">ingeniería eléctrica</a> hasta la <a href="{svc_url("construccion-obra-civil")}">construcción de obra civil</a>— están disponibles a nivel nacional.</p>
</div></section>{cta_block()}'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, extra={"mainEntity": {"@id": ORG_ID}, "spatialCoverage": area_served()})]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Cobertura", path)])


def build_about():
    path = "/nosotros/"
    title = "Nosotros: Empresa de Ingeniería y Construcción en Panamá | DISPRON GROUP"
    desc = "Conozca a DISPRON GROUP, empresa panameña de diseño industrial, ingeniería, construcción, mantenimiento y suministro industrial. Misión, visión y valores."
    values = "".join(f'<div class="value">{icon("shield")}<h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in VALUES)
    body = f'''<section class="page-hero"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div><div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><h1>Sobre DISPRON GROUP</h1>
<p class="lead">{e(S["slogan"])}</p></div></div></section>
<section class="section"><div class="container narrow prose">
<h2>Quiénes somos</h2>
<p><strong>{e(S["legalName"])}</strong> (DISPRON) es una empresa panameña de ingeniería, construcción y servicios industriales con sede en la Ciudad de Panamá. Integramos diseño industrial e ingeniería de producto, mantenimiento industrial avanzado, construcción y obra civil, remodelación, ingeniería eléctrica y de potencia, HVAC, metalmecánica y soldadura, fontanería e hidráulica, y el suministro de materiales y equipos relacionados.</p>
<p>Nuestro modelo multidisciplinario permite a industrias, empresas logísticas, mineras, bancos, instituciones y propietarios contratar con un solo responsable técnico, reduciendo interfaces, tiempos y sobrecostos.</p>
<h2>Misión</h2>
<p>Diseñar, construir y mantener infraestructura segura, eficiente y duradera para nuestros clientes en Panamá, aplicando ingeniería basada en datos y los más altos estándares de calidad y seguridad.</p>
<h2>Visión</h2>
<p>Ser la empresa de referencia en Panamá y la región en soluciones integrales de ingeniería, construcción y mantenimiento industrial.</p>
<h2>Equipo</h2>
<p>Contamos con ingenieros civiles, mecánicos, electricistas, industriales, arquitectos, diseñadores, técnicos de mantenimiento, soldadores calificados y personal de seguridad ocupacional, con idoneidad profesional en Panamá.</p>
</div></section>
<section class="section alt"><div class="container"><h2 class="section-title">Nuestros valores</h2><div class="grid grid-3 values">{values}</div></div></section>
{cta_block()}'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, "AboutPage", {"mainEntity": {"@id": ORG_ID}})]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Nosotros", path)])


def build_faq():
    path = "/preguntas-frecuentes/"
    title = "Preguntas Frecuentes: Ingeniería y Construcción en Panamá | DISPRON GROUP"
    desc = "Respuestas sobre DISPRON GROUP en Panamá: cobertura, cotizaciones, proyectos llave en mano, mantenimiento, normas, emergencias y suministro de equipos."
    all_faqs = list(GENERAL_FAQS)
    blocks = faq_html(GENERAL_FAQS, "Sobre DISPRON GROUP")
    for s in SERVICES:
        all_faqs += s["faqs"]
        items = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{e(a)} <a href="{svc_url(s["slug"])}">Más sobre {e(s["serviceType"].lower())}</a>.</p></details>' for q, a in s["faqs"])
        blocks += f'<section class="section tight"><div class="container narrow"><h2 class="section-title sm">{e(s["name"])}</h2>{items}</div></section>'
    body = f'''<section class="page-hero"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div><div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><h1>Preguntas frecuentes</h1>
<p class="lead">Todo lo que necesita saber antes de contratar ingeniería, construcción o mantenimiento con DISPRON GROUP en Panamá.</p></div></div></section>
{blocks}{cta_block("¿No encontró su respuesta?", "Escríbanos y un ingeniero le responderá en menos de 24 horas hábiles.")}'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, extra={"mainEntity": {"@id": f"{url}#faq"}}), faq_node(url, all_faqs)]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Preguntas frecuentes", path)])


def build_contact():
    path = "/contacto/"
    title = "Contacto y Cotizaciones | DISPRON GROUP Panamá"
    desc = f"Solicite una cotización de ingeniería, construcción o mantenimiento en Panamá. Llame al {S['phoneDisplay']}, escriba por WhatsApp o a {S['email']}."
    opts = "".join(f'<option value="{e(s["slug"])}">{e(s["name"])}</option>' for s in SERVICES)
    provs = "".join(f"<option>{e(p)}</option>" for p, _ in PROVINCES)
    a = S["address"]
    street = f'{e(a["street"])}, ' if real(a["street"]) else ""
    body = f'''<section class="page-hero"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div><div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><h1>Contacto y cotizaciones</h1>
<p class="lead">Cuéntenos sobre su proyecto. Un ingeniero de DISPRON GROUP le responderá en menos de 24 horas hábiles.</p></div></div></section>
<section class="section"><div class="container two-col contact">
  <form class="form card" id="quote-form" data-lead action="{e(S.get("formEndpoint") or "/api/leads")}" method="post" data-wa="{e(S["whatsapp"])}" data-email="{e(S["email"])}">
    <h2>Solicitar cotización</h2>
    <div class="row"><label>Nombre completo*<input name="nombre" required autocomplete="name"></label>
    <label>Empresa<input name="empresa" autocomplete="organization"></label></div>
    <div class="row"><label>Teléfono*<input name="telefono" type="tel" required autocomplete="tel" placeholder="+507"></label>
    <label>Correo electrónico*<input name="email" type="email" required autocomplete="email"></label></div>
    <div class="row"><label>Servicio de interés<select name="servicio" id="servicio"><option value="">Seleccione…</option>{opts}</select></label>
    <label>Provincia<select name="provincia"><option value="">Seleccione…</option>{provs}</select></label></div>
    <label>Describa su proyecto*<textarea name="mensaje" rows="5" required></textarea></label>
    <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="consent"><input type="checkbox" required> Acepto la <a href="/politica-de-privacidad/">política de privacidad</a>.</label>
    <button class="btn btn-accent" type="submit">Enviar solicitud {icon("arrow")}</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
  <div class="contact-info">
    <h2>Datos de contacto</h2>
    <ul class="contact-list">
      <li>{icon("phone")}<div><strong>Teléfono</strong><a href="tel:{e(S["phone"])}">{e(S["phoneDisplay"])}</a></div></li>
      <li>{WA_SVG}<div><strong>WhatsApp</strong><a href="https://wa.me/{e(S["whatsapp"])}" target="_blank" rel="noopener">{e(S["phoneDisplay"])}</a></div></li>
      <li>{icon("mail")}<div><strong>Correo</strong><a href="mailto:{e(S["email"])}">{e(S["email"])}</a></div></li>
      <li>{icon("pin")}<div><strong>Oficina</strong>{street}{e(a["locality"])}, República de Panamá · <a href="{e(S["googleMapsUrl"])}" target="_blank" rel="noopener">Ver en Google Maps</a></div></li>
      <li>{icon("clock")}<div><strong>Horario</strong>{e(S["hoursDisplay"])}</div></li>
    </ul>
  </div>
</div></section>'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, "ContactPage", {"mainEntity": {"@id": ORG_ID}})]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Contacto", path)], scripts=("/js/quote.js",))


def build_privacy():
    path = "/politica-de-privacidad/"
    title = "Política de Privacidad | DISPRON GROUP"
    desc = "Política de privacidad y tratamiento de datos personales de DISPRON GROUP conforme a la Ley 81 de 2019 de Protección de Datos Personales de Panamá."
    body = f'''<section class="page-hero"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div><div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><h1>Política de privacidad</h1></div></div></section>
<section class="section"><div class="container narrow prose">
<p>En {e(S["legalName"])} respetamos su privacidad y tratamos sus datos personales conforme a la Ley 81 de 2019 sobre Protección de Datos Personales de la República de Panamá y su reglamentación.</p>
<h2>Datos que recopilamos</h2><p>Nombre, empresa, teléfono, correo electrónico, provincia y la información que usted nos proporciona voluntariamente al solicitar una cotización o contactarnos.</p>
<h2>Finalidad</h2><p>Responder a sus solicitudes, elaborar cotizaciones, prestar nuestros servicios y, con su consentimiento, enviarle información comercial.</p>
<h2>Conservación y seguridad</h2><p>Conservamos sus datos solo durante el tiempo necesario para la finalidad indicada y aplicamos medidas técnicas y organizativas para protegerlos.</p>
<h2>Sus derechos</h2><p>Puede ejercer sus derechos de acceso, rectificación, cancelación, oposición y portabilidad escribiendo a <a href="mailto:{e(S["email"])}">{e(S["email"])}</a>.</p>
<h2>Cookies y analítica</h2><p>Este sitio puede utilizar herramientas de analítica web para medir el uso del sitio de forma agregada.</p>
<p>Última actualización: {TODAY}.</p>
</div></section>'''
    url = f"{D}{path}"
    page(path, title, desc, body, [webpage_node(url, title, desc)], [("Inicio", "/"), ("Política de privacidad", path)])


def build_404():
    title = "Página no encontrada | DISPRON GROUP"
    desc = "La página solicitada no existe."
    cards = "".join(service_card(s) for s in SERVICES[:6])
    body = f'''<section class="page-hero"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div><div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><h1>Página no encontrada</h1><p class="lead">La página que busca no existe o fue movida. Estos son algunos de nuestros servicios:</p>
<p><a class="btn btn-accent" href="/">Ir al inicio</a></p></div></div></section>
<section class="section"><div class="container"><div class="grid grid-3">{cards}</div></div></section>'''
    page("/404.html", title, desc, body, [], [], robots="noindex, follow", listed=False)


# ------------------------------------------------------------------ archivos técnicos
def build_sitemap():
    prio = {"/": "1.0", "/servicios/": "0.9", "/cotizar/": "0.9", "/contacto/": "0.8", "/blog/": "0.8", "/sectores/": "0.8"}
    urls = "".join(
        f"<url><loc>{D}{p}</loc><lastmod>{TODAY}</lastmod><changefreq>{'weekly' if p in prio else 'monthly'}</changefreq>"
        f"<priority>{prio.get(p, '0.8' if p.startswith(('/servicios/', '/sectores/')) else '0.7' if p.startswith('/blog/') else '0.6')}</priority>"
        + "".join(f"<image:image><image:loc>{D}{u}</image:loc></image:image>" for u, c in (PAGE_IMAGES.get(p) or [(OG_IMAGE.replace(D, ""), S["brand"])]))
        + "</url>\n" for p in PAGES)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + urls + "</urlset>\n", encoding="utf-8")


def build_robots():
    ai_bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User", "ClaudeBot", "Claude-User",
               "Claude-SearchBot", "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot", "CCBot", "DuckAssistBot",
               "meta-externalagent", "Amazonbot", "cohere-ai", "MistralAI-User"]
    txt = "# robots.txt – dicprom.com\n# Rastreo permitido para buscadores y asistentes de IA (GEO).\n\nUser-agent: *\nAllow: /\nDisallow: /404.html\nDisallow: /crm/\nDisallow: /acceso/\nDisallow: /api/\n\n"
    txt += "".join(f"User-agent: {b}\nAllow: /\nDisallow: /crm/\nDisallow: /acceso/\nDisallow: /api/\n\n" for b in ai_bots)
    txt += f"Sitemap: {D}/sitemap.xml\n"
    (DIST / "robots.txt").write_text(txt, encoding="utf-8")


def build_llms():
    lines = [f"# {S['brand']}", "",
             f"> {S['brand']} ({S['legalName']}) es una empresa panameña de diseño industrial, ingeniería de producto, mantenimiento "
             "industrial avanzado, construcción y obra civil, remodelación y fit-out, ingeniería eléctrica, HVAC, metalmecánica y soldadura, "
             "fontanería, hidráulica y sistemas contra incendios, y suministro de materiales y equipos. Sede en la Ciudad de Panamá; "
             "cobertura en todas las provincias de la República de Panamá.", "",
             "## Datos de la empresa", "",
             f"- Nombre: {S['brand']} ({S['legalName']})", f"- Sitio web: {D}/", f"- Teléfono / WhatsApp: {S['phoneDisplay']}",
             f"- Correo: {S['email']}", f"- Ubicación: {S['address']['locality']}, Panamá", f"- Horario: {S['hoursDisplay']}",
             "- Cobertura: " + ", ".join(p for p, _ in PROVINCES), "- Modalidades: llave en mano (EPC/Turnkey), administración de obra, contratos de mantenimiento, consultoría e inspección técnica", "",
             "## Servicios", ""]
    for s in SERVICES:
        lines.append(f"- [{s['name']}]({D}{svc_url(s['slug'])}): {s['short']}")
    lines += ["", "## Páginas principales", "",
              f"- [Inicio]({D}/): visión general de la empresa", f"- [Servicios]({D}/servicios/): catálogo completo", f"- [Proyectos]({D}/proyectos/): galería de obras y trabajos en campo",
              f"- [Cobertura]({D}/cobertura/): provincias y zonas atendidas", f"- [Nosotros]({D}/nosotros/): misión, visión y valores",
              f"- [Preguntas frecuentes]({D}/preguntas-frecuentes/): respuestas detalladas", f"- [Contacto]({D}/contacto/): datos de contacto",
              f"- [Cotizador]({D}/cotizar/): solicitud de visita técnica en 3 pasos", f"- [Sectores]({D}/sectores/): banca, hotelería, PH, eventos e industria",
              f"- [Recursos]({D}/recursos/): guías y checklists técnicos", f"- [Blog técnico]({D}/blog/): artículos con respuesta directa", f"- [Ficha estructurada]({D}/knowledge.json): datos de entidad en JSON", "",
              "## Blog técnico", ""] + [f"- [{p['title']}]({D}/blog/{p['slug']}/): {p['meta']}" for p in PLATFORM["posts"]] + ["",
              "## Optional", "", f"- [Contenido completo]({D}/llms-full.txt): texto completo de todos los servicios y preguntas frecuentes", ""]
    (DIST / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    full = [f"# {S['brand']} – contenido completo", "", lines[2], ""]
    full += ["## Preguntas frecuentes generales", ""] + [f"### {q}\n\n{a}\n" for q, a in GENERAL_FAQS]
    for s in SERVICES:
        full += [f"## {s['name']}", "", f"URL: {D}{svc_url(s['slug'])}", "", s["lead"], ""] + [p + "\n" for p in s["intro"]]
        full += ["### Servicios incluidos", ""] + [f"- {h}: {p}" for h, p in s["items"]]
        full += ["", "### Sectores", ""] + [f"- {a}" for a in s["applications"]]
        full += ["", "### Normas de referencia", ""] + [f"- {a}" for a in s["standards"]]
        full += ["", "### Preguntas frecuentes", ""] + [f"**{q}**\n{a}\n" for q, a in s["faqs"]] + [""]
    for p in PLATFORM["posts"]:
        full += [f"## {p['title']}", "", f"URL: {D}/blog/{p['slug']}/", "", p["answer"], ""] + [f"### {h}\n\n{t}\n" for h, t in p["sections"]]
        full += [f"**{p['faq'][0]}**\n{p['faq'][1]}\n", ""]
    (DIST / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")


def build_misc():
    (DIST / "manifest.webmanifest").write_text(json.dumps({
        "name": f"{S['brand']} – {S['tagline']}", "short_name": S["brand"], "start_url": "/", "display": "standalone", "lang": "es-PA",
        "background_color": "#0f1a2b", "theme_color": "#0f1a2b",
        "icons": [{"src": "/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (DIST / "humans.txt").write_text(f"/* TEAM */\nEmpresa: {S['legalName']}\nSitio: {D}\nContacto: {S['email']}\nUbicación: Ciudad de Panamá, Panamá\n\n/* SITE */\nÚltima actualización: {TODAY}\nIdioma: Español (Panamá)\nEstándares: HTML5, CSS3, Schema.org JSON-LD\n", encoding="utf-8")
    if S.get("indexNowKey"):
        (DIST / f"{S['indexNowKey']}.txt").write_text(S["indexNowKey"], encoding="utf-8")
    wk = DIST / ".well-known"
    wk.mkdir(exist_ok=True)
    (wk / "security.txt").write_text(f"Contact: mailto:{S['email']}\nPreferred-Languages: es, en\nCanonical: {D}/.well-known/security.txt\nExpires: {datetime.date.today().year + 1}-12-31T23:59:59Z\n", encoding="utf-8")


# ------------------------------------------------------------------ plataforma: blog, sectores, recursos, cotizador, CRM
POSTS = PLATFORM["posts"]
CHECK_ICO = icon("check")
SECTORS = PLATFORM["sectores"]
GUIDES = PLATFORM["guias"]
GALLERY = all_photos()
GCAT = {k: n for k, n, _ in GALLERY_CATS}
AUTHOR = "Equipo técnico DISPRON GROUP"
PSVC = {
    "remodelacion-diseno-interiores": ["remodelacion-fit-out", "arquitectura-planos-render-3d"],
    "plomeria-sistemas-hidrosanitarios": ["fontaneria-hidraulica-contra-incendios"],
    "ebanisteria-carpinteria-arquitectonica": ["remodelacion-fit-out"],
    "mantenimiento-integral-bancos-hoteles-ph": ["mantenimiento-ph-edificios"],
    "eventos-corporativos-stands": ["stands-corporativos"],
    "restauracion-pintura-fachadas": ["mantenimiento-ph-edificios", "remodelacion-fit-out"],
    "electricidad-ingenieria-electrica": ["ingenieria-electrica"],
    "recubrimientos-pisos-epoxicos": ["pisos-pintura-epoxica"],
    "soporte-industrial": ["mantenimiento-industrial", "metalmecanica-soldadura", "construccion-obra-civil",
                           "fontaneria-hidraulica-contra-incendios", "hvac-aire-acondicionado"],
}
POST_CAT_SVC = {"fire": ["fontaneria-hidraulica-contra-incendios"], "obra-civil": ["construccion-obra-civil"],
                "soldadura": ["metalmecanica-soldadura"], "industrial": ["hvac-aire-acondicionado", "mantenimiento-industrial"]}
SECTOR_EXTRA = {
    "bancario": ["hvac-aire-acondicionado", "ingenieria-electrica"],
    "hotelero": ["hvac-aire-acondicionado", "fontaneria-hidraulica-contra-incendios"],
    "ph": ["mantenimiento-ph-edificios", "fontaneria-hidraulica-contra-incendios"],
    "eventos": ["stands-corporativos", "arquitectura-planos-render-3d"],
    "industrial": ["mantenimiento-industrial", "montaje-maquinaria-automatizacion", "metalmecanica-soldadura", "pisos-pintura-epoxica"],
}
SECTOR_META = {
    "bancario": ("building", "remodelacion", "Bancos y sucursales"),
    "hotelero": ("key", "plomeria", "Hoteles y hospitalidad"),
    "ph": ("building", "fachadas", "Propiedad horizontal (PH)"),
    "eventos": ("stand", "eventos", "Eventos corporativos y stands"),
    "industrial": ("plant", "soldadura", "Plantas e instalaciones industriales"),
}
SECTOR_FAQ = {
    "bancario": [("¿Se puede trabajar en una sucursal bancaria sin cerrarla al público?",
                  "Sí. La obra se divide en fases y se programa en horario nocturno o de fin de semana, coordinando cada corte de energía, datos o agua con la administración de la agencia."),
                 ("¿Qué incluye el mantenimiento para bancos?",
                  "Mantenimiento eléctrico, aire acondicionado de precisión, UPS, plomería, pintura y acabados, además de remodelaciones por fases y adecuaciones de imagen corporativa.")],
    "hotelero": [("¿Cómo se evita afectar a los huéspedes durante los trabajos?",
                  "Se planifica por pisos o áreas, se controlan ruido y polvo, y los trabajos críticos se programan en horarios de baja ocupación coordinados con operaciones del hotel."),
                 ("¿Qué sistemas de un hotel requieren mantenimiento preventivo?",
                  "Cuartos de bombas, agua caliente, aire acondicionado, tableros eléctricos, plantas de emergencia, sistemas contra incendios, fachadas y áreas comunes.")],
    "ph": [("¿Qué incluye el mantenimiento de un PH?",
            "Áreas comunes, cuartos de bombas, sistemas eléctricos, impermeabilización, pintura de fachadas, sistemas contra incendios y atención de fugas, con reportes para la administración."),
           ("¿Pueden preparar una propuesta para la junta directiva o la asamblea?",
            "Sí. Se entrega una propuesta técnica con alcance, fases, cronograma y presupuesto desglosado para que la administración la presente a la junta o a la asamblea de propietarios.")],
    "eventos": [("¿Montan stands en el Centro de Convenciones de Panamá?",
                 "Sí. Diseñamos, fabricamos y montamos stands corporativos coordinando los horarios de montaje y desmontaje y los requisitos técnicos del recinto."),
                ("¿Con cuánta anticipación conviene solicitar un stand?",
                 "Lo recomendable es iniciar el diseño varias semanas antes del evento para aprobar renders, fabricar y coordinar la logística del recinto.")],
    "industrial": [("¿Atienden plantas industriales fuera de la Ciudad de Panamá?",
                    "Sí. Atendemos plantas, galeras, puertos y proyectos en todas las provincias, con planificación de paradas programadas."),
                   ("¿Ofrecen mantenimiento predictivo?",
                    "Sí. Termografía, análisis de vibraciones y pruebas eléctricas para anticipar fallas, combinados con mantenimiento preventivo y correctivo.")],
}
SECTOR_BY_ID = {x["id"]: x for x in SECTORS}
URGENCIES = [("Planificada", "Programar en las próximas semanas"), ("Prioritaria", "Necesito atención en menos de 15 días"),
             ("Crítica", "Emergencia o falla que detiene la operación")]
SLOTS = ["Mañana (8:00–12:00)", "Tarde (12:00–17:00)", "Nocturno", "Fin de semana"]


def uniq(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def gpic(src, alt, sizes="(max-width: 700px) 100vw, 400px", eager=False, cls=""):
    return picture(gallery_url(src), alt, cls=cls, eager=eager, sizes=sizes)


def cat_photos(cat):
    return [(src, cap) for src, cap, k in GALLERY if k == cat]


def post_gcat(p):
    return {"ebanisteria": "remodelacion", "restauracion": "fachadas"}.get(p["cat"], p["cat"])


def post_photos(i, p):
    ph = cat_photos(post_gcat(p))
    start = (i * 3) % len(ph)
    return [ph[(start + k) % len(ph)] for k in range(min(5, len(ph)))]


def post_url(p):
    return f"/blog/{p['slug']}/"


def post_date(i):
    return f"2026-09-{10 + i % 20:02d}"


def post_services(p):
    return POST_CAT_SVC.get(p["cat"]) or PSVC.get(p["service"], [])


def read_mins(p):
    words = len(p["answer"].split()) + sum(len(t.split()) for _h, t in p["sections"])
    return max(3, round(words / 180))


def date_es(iso):
    m = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    y, mo, d = iso.split("-")
    return f"{int(d)} de {m[int(mo) - 1]} de {y}"


def sector_url(sid):
    return f"/sectores/{sid}/"


def sector_services(sec):
    return uniq([x for ps in sec["services"] for x in PSVC.get(ps, [])] + SECTOR_EXTRA.get(sec["id"], []))


def sector_cover(sec):
    return cat_photos(SECTOR_META[sec["id"]][1])[0]


def post_card(p):
    i = POSTS.index(p)
    src, cap = post_photos(i, p)[0]
    svc = post_services(p)
    tag = SVC[svc[0]]["name"] if svc else ""
    sec = SECTOR_BY_ID.get(p["sector"], {}).get("name", "")
    return (f'<a class="post-card reveal" href="{post_url(p)}" data-cat="{e(p["sector"])}"><div class="post-ph">'
            f'{gpic(src, cap, sizes="(max-width: 700px) 100vw, (max-width: 1080px) 50vw, 380px")}<span class="post-tag">{e(sec)}</span></div>'
            f'<div class="post-body"><span class="post-svc">{e(tag)}</span><h3>{e(p["title"])}</h3><p>{e(p["meta"])}</p>'
            f'<small>{date_es(post_date(i))} · {read_mins(p)} min de lectura</small></div></a>')


def related_posts_html(posts, title, eyebrow="Blog técnico"):
    if not posts:
        return ""
    cards = "".join(post_card(p) for p in posts[:3])
    return (f'<section class="section"><div class="container"><div class="sec-head row reveal"><div><p class="eyebrow dk">{e(eyebrow)}</p>'
            f'<h2>{e(title)}</h2></div><a class="link" href="/blog/">Ver el blog {icon("arrow")}</a></div><div class="post-grid">{cards}</div></div></section>')


def sector_card(sec):
    ico, _c, _n = SECTOR_META[sec["id"]]
    src, cap = sector_cover(sec)
    needs = "".join(f"<li>{icon('check')}{e(n)}</li>" for n in sec["needs"][:2])
    return (f'<a class="sector-card reveal" href="{sector_url(sec["id"])}">{gpic(src, cap + " – sector " + sec["name"].lower(), sizes="(max-width: 700px) 100vw, 420px")}'
            f'<div class="sector-body"><span class="sector-ico">{icon(ico)}</span><h3>{e(SECTOR_META[sec["id"]][2])}</h3><p>{e(sec["lead"])}</p>'
            f'<ul class="checklist sm">{needs}</ul><span class="more">Ver soluciones {icon("arrow")}</span></div></a>')


def home_platform_sections():
    sectors = "".join(sector_card(x) for x in SECTORS)
    latest = "".join(post_card(p) for p in POSTS[:3])
    return f'''<section class="section alt" id="sectores"><div class="container">
  <div class="sec-head row reveal"><div><p class="eyebrow dk">Sectores</p><h2>Soluciones por sector</h2><p class="sec-lead">Cada sector opera con restricciones distintas. Planificamos según horarios, riesgos y criticidad de su instalación.</p></div><a class="link" href="/sectores/">Ver sectores {icon("arrow")}</a></div>
  <div class="sector-grid">{sectors}</div>
</div></section>
<section class="section quote-band"><div class="container quote-band-inner reveal">
  <div><p class="eyebrow">Cotizador inteligente</p><h2>Solicite una visita técnica en 3 pasos</h2>
  <p>Indique servicio, sitio y urgencia. Recibirá un número de referencia y un especialista coordinará el diagnóstico. ¿Prefiere conversar? Sofía, nuestra asistente, le guía por chat.</p></div>
  <ol class="mini-steps"><li><b>1</b>Necesidad</li><li><b>2</b>Sitio y fecha</li><li><b>3</b>Contacto</li></ol>
  <div class="cta-actions"><a class="btn btn-gold" href="/cotizar/">Abrir cotizador {icon("arrow")}</a><button class="btn btn-ghost" type="button" data-sofia>Hablar con Sofía</button></div>
</div></section>
<section class="section"><div class="container">
  <div class="sec-head row reveal"><div><p class="eyebrow dk">Blog técnico</p><h2>Guías para decidir mejor</h2></div><a class="link" href="/blog/">Ver los {len(POSTS)} artículos {icon("arrow")}</a></div>
  <div class="post-grid">{latest}</div>
</div></section>'''


def build_projects():
    path = "/proyectos/"
    title = "Proyectos y Galería de Obras en Panamá | DISPRON GROUP"
    desc = "Galería de proyectos de DISPRON GROUP en Panamá: obra civil, estructuras metálicas, electricidad, contra incendios, epóxicos, fit-out y stands."
    counts = {k: sum(1 for _s, _c, c in GALLERY if c == k) for k, _n, _sv in GALLERY_CATS}
    filters = f'<button class="chip active" data-filter="all" aria-pressed="true">Todos <span>{len(GALLERY)}</span></button>' + "".join(
        f'<button class="chip" data-filter="{k}" aria-pressed="false">{e(n)} <span>{counts[k]}</span></button>' for k, n, _sv in GALLERY_CATS if counts[k])
    items = ""
    for src, cap, cat in GALLERY:
        sv = SVC[dict((k, sv) for k, _n, sv in GALLERY_CATS)[cat]]
        u = gallery_url(src)
        items += (f'<figure class="g-item reveal" data-cat="{cat}"><a href="{u}" data-lightbox data-caption="{e(cap)} · {e(GCAT[cat])}">'
                  f'{gpic(src, cap + " – " + GCAT[cat] + " en Panamá")}</a>'
                  f'<figcaption><strong>{e(cap)}</strong><a href="{svc_url(sv["slug"])}">{e(sv["name"])}</a></figcaption></figure>')
    stats = "".join(f'<li><strong>{counts[k]}</strong><span>{e(n)}</span></li>' for k, n, _sv in GALLERY_CATS[:4])
    body = f'''{page_hero("Proyectos y obras en Panamá", f"{len(GALLERY)} fotografías de trabajos en campo: construcción, montaje, instalaciones electromecánicas, sistemas contra incendios, mantenimiento y acabados.", bg="/img/hero/hero-3.webp", eyebrow="Galería de proyectos", aside=f'<aside class="facts-card reveal"><p class="facts-title">{icon("layers")} Archivo fotográfico</p><ul class="stats sm">{stats}</ul></aside>')}
<section class="section"><div class="container">
  <div class="filters" role="group" aria-label="Filtrar proyectos por categoría">{filters}</div>
  <div class="gallery masonry" id="project-grid">{items}</div>
</div></section>{cta_block("¿Quiere un resultado así en su instalación?")}'''
    url = f"{D}{path}"
    gallery_node = {"@type": "ImageGallery", "@id": f"{url}#galeria", "name": "Proyectos DISPRON GROUP en Panamá", "url": url,
                    "about": {"@id": ORG_ID}, "inLanguage": "es-PA", "numberOfItems": len(GALLERY),
                    "image": [{"@type": "ImageObject", "contentUrl": f"{D}{gallery_url(src)}", "caption": f"{cap} – {GCAT[cat]}",
                               "creator": {"@id": ORG_ID}, "copyrightHolder": {"@id": ORG_ID},
                               "contentLocation": {"@type": "Country", "name": "Panamá"}} for src, cap, cat in GALLERY]}
    graph = [webpage_node(url, title, desc, "CollectionPage", {"mainEntity": {"@id": f"{url}#galeria"}}), gallery_node]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Proyectos", path)],
         images=[(gallery_url(src), cap) for src, cap, _c in GALLERY])


def build_sectors_hub():
    path = "/sectores/"
    title = "Sectores: Banca, Hoteles, PH, Eventos e Industria en Panamá | DISPRON"
    desc = "Soluciones de ingeniería, construcción y mantenimiento por sector en Panamá: bancos, hoteles, propiedad horizontal, eventos corporativos e industria."
    cards = "".join(sector_card(x) for x in SECTORS)
    inds = "".join(f"<li>{icon('check')}{e(i)}</li>" for i in INDUSTRIES)
    body = f'''{page_hero("Soluciones por sector en Panamá", "Cada operación tiene horarios, riesgos y normas distintas. Estas son las necesidades que más atendemos y cómo las resolvemos.", bg=gallery_url(sector_cover(SECTORS[0])[0]), eyebrow="Sectores")}
<section class="section"><div class="container"><div class="sector-grid">{cards}</div></div></section>
<section class="section alt"><div class="container two-col">
  <div class="reveal"><p class="eyebrow dk">Industrias</p><h2>También atendemos</h2><ul class="checklist cols-2">{inds}</ul></div>
  <div class="reveal prose"><p class="eyebrow dk">Método</p><h2>Planificación según su operación</h2><p>Antes de cotizar realizamos una visita técnica para entender restricciones de horario, accesos, permisos y riesgos. Con esa información definimos fases, cuadrillas y un único responsable técnico.</p><a class="link" href="/cotizar/">Solicitar visita técnica {icon("arrow")}</a></div>
</div></section>{cta_block()}'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, "CollectionPage", {"mainEntity": {"@id": f"{url}#lista"}}),
             {"@type": "ItemList", "@id": f"{url}#lista", "name": "Sectores atendidos por DISPRON GROUP", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": f"{D}{sector_url(x['id'])}", "name": SECTOR_META[x["id"]][2]} for i, x in enumerate(SECTORS)]}]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Sectores", path)], active="/sectores/",
         images=[(gallery_url(sector_cover(x)[0]), sector_cover(x)[1]) for x in SECTORS])


def build_sector(sec):
    sid = sec["id"]
    path = sector_url(sid)
    url = f"{D}{path}"
    name = SECTOR_META[sid][2]
    title = f"{name} en Panamá: Ingeniería y Mantenimiento | DISPRON GROUP"
    if len(title) > 70:
        title = f"{name} en Panamá | DISPRON GROUP"
    desc = f"{sec['lead']} Servicios de DISPRON GROUP para el sector {sec['name'].lower()} en toda la República de Panamá."[:165]
    svcs = [SVC[x] for x in sector_services(sec)]
    needs = "".join(f'<li class="reveal"><span class="need-n">{i + 1:02d}</span>{e(n)}</li>' for i, n in enumerate(sec["needs"]))
    cards = "".join(service_card(s) for s in svcs)
    photos = uniq([ph for s in svcs for ph in svc_photos(s)[:2]])[:6]
    posts = [p for p in POSTS if p["sector"] == sid]
    faqs = SECTOR_FAQ[sid]
    src, cap = sector_cover(sec)
    body = f'''{page_hero(e(name) + ' <span class="gold-text">en Panamá</span>', e(sec["lead"]), bg=gallery_url(src), eyebrow="Sector " + sec["name"],
                      extra=f'<div class="hero-actions"><a class="btn btn-gold" href="/cotizar/?sector={sid}">Solicitar visita técnica {icon("arrow")}</a><button class="btn btn-ghost" type="button" data-sofia>Hablar con Sofía</button></div>')}
<section class="section"><div class="container split">
  <div class="reveal"><p class="eyebrow dk">Necesidades del sector</p><h2>Lo que exige una operación {e(sec["name"].lower())}</h2><ol class="needs">{needs}</ol></div>
  <div class="split-media reveal">{gpic(src, cap, sizes="(max-width: 960px) 100vw, 560px")}</div>
</div></section>
<section class="section alt"><div class="container"><div class="sec-head reveal"><p class="eyebrow dk">Servicios recomendados</p><h2>Servicios para el sector {e(sec["name"].lower())}</h2></div><div class="svc-grid">{cards}</div></div></section>
<section class="section"><div class="container"><div class="sec-head row reveal"><div><p class="eyebrow dk">Trabajo en campo</p><h2>Fotografías de referencia</h2></div><a class="link" href="/proyectos/">Ver galería completa {icon("arrow")}</a></div>{gallery_html(photos, name + " – DISPRON GROUP")}</div></section>
{related_posts_html(posts, "Artículos para el sector " + sec["name"].lower())}
{faq_html(faqs, "Preguntas frecuentes del sector " + sec["name"].lower())}
{cta_block()}'''
    graph = [webpage_node(url, title, desc, extra={"about": {"@type": "Thing", "name": name}, "mainEntity": {"@id": f"{url}#servicios"}}),
             {"@type": "ItemList", "@id": f"{url}#servicios", "name": f"Servicios para {name}", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "item": {"@id": f"{D}{svc_url(s['slug'])}#service"}, "name": s["name"], "url": f"{D}{svc_url(s['slug'])}"}
                 for i, s in enumerate(svcs)]},
             faq_node(url, faqs)]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Sectores", "/sectores/"), (name, path)], active="/sectores/", images=photos)


def build_blog_index():
    path = "/blog/"
    title = "Blog Técnico de Ingeniería y Mantenimiento en Panamá | DISPRON GROUP"
    desc = "Guías prácticas sobre remodelación, mantenimiento de PH, electricidad, plomería, pisos epóxicos, fachadas, stands y obra civil en Panamá."
    used = uniq([p["sector"] for p in POSTS])
    filters = f'<button class="chip active" data-filter="all" aria-pressed="true">Todos <span>{len(POSTS)}</span></button>' + "".join(
        f'<button class="chip" data-filter="{s}" aria-pressed="false">{e(SECTOR_BY_ID[s]["name"])} <span>{sum(1 for p in POSTS if p["sector"] == s)}</span></button>' for s in used)
    cards = "".join(post_card(p) for p in POSTS)
    body = f'''{page_hero("Blog técnico DISPRON GROUP", "Respuestas directas y criterios técnicos para administradores, gerentes de planta, facilities y compras en Panamá.", bg="/img/hero/hero-2.webp", eyebrow=f"{len(POSTS)} artículos")}
<section class="section"><div class="container">
  <div class="filters" role="group" aria-label="Filtrar artículos por sector">{filters}</div>
  <div class="post-grid" id="post-grid">{cards}</div>
</div></section>{cta_block("¿Necesita una evaluación en sitio?", "Agende una visita técnica y reciba un diagnóstico con alcance y presupuesto.")}'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, "CollectionPage", {"mainEntity": {"@id": f"{url}#blog"}}),
             {"@type": "Blog", "@id": f"{url}#blog", "name": "Blog técnico DISPRON GROUP", "url": url, "inLanguage": "es-PA", "publisher": {"@id": ORG_ID},
              "blogPost": [{"@type": "BlogPosting", "headline": p["title"][:110], "url": f"{D}{post_url(p)}"} for p in POSTS]}]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Blog", path)], active="/blog/",
         images=[(gallery_url(post_photos(i, p)[0][0]), post_photos(i, p)[0][1]) for i, p in enumerate(POSTS)])


SEO_TITLES = {
    "checklist-mantenimiento-preventivo-anual-edificios-panama": "Checklist de mantenimiento preventivo anual para edificios en Panamá",
    "cuanto-tiempo-antes-contratar-montaje-de-stand-para-un-evento": "¿Con cuánto tiempo contratar el montaje de un stand en Panamá?",
    "mobiliario-a-medida-counters-recepcion-oficinas-panama": "Mobiliario a medida y counters de recepción para oficinas en Panamá",
}


def build_blog_post(i, p):
    path = post_url(p)
    url = f"{D}{path}"
    title = SEO_TITLES.get(p["slug"], p["title"])
    if len(title) > 70:
        cut = min((title.index(c) + (1 if c == "?" else 0) for c in ":?" if c in title), default=len(title))
        title = title[:cut].strip()
    full_title = f"{title} | DISPRON" if len(title) <= 60 else title
    desc = p["meta"]
    photos = post_photos(i, p)
    svcs = [SVC[x] for x in post_services(p)]
    sec = SECTOR_BY_ID.get(p["sector"])
    pub = post_date(i)
    sections = ""
    for k, (h, t) in enumerate(p["sections"]):
        sections += f"<h2>{e(h)}</h2><p>{e(t)}</p>"
        if k == 0 and len(photos) > 1:
            src, cap = photos[1]
            sections += f'<figure class="art-fig">{gpic(src, cap, sizes="(max-width: 960px) 100vw, 760px")}<figcaption>{e(cap)}</figcaption></figure>'
    q, a = p["faq"]
    svc_links = "".join(f'<li><a href="{svc_url(s["slug"])}">{icon(s["icon"])}{e(s["name"])}</a></li>' for s in svcs)
    sec_link = f'<li><a href="{sector_url(sec["id"])}">{icon(SECTOR_META[sec["id"]][0])}{e(SECTOR_META[sec["id"]][2])}</a></li>' if sec else ""
    related = [x for x in POSTS if x is not p and (x["sector"] == p["sector"] or set(post_services(x)) & set(post_services(p)))][:3]
    gal = gallery_html([(gallery_url(s), c) for s, c in photos[2:5]], p["title"])
    body = f'''<section class="page-hero art-hero has-bg" style="--hero-bg:url('{gallery_url(photos[0][0])}')"><div class="hero-lines" aria-hidden="true">{chevrons_svg()}</div>
<div class="container page-hero-inner"><div class="reveal"><!--CRUMBS--><p class="eyebrow">{e(svcs[0]["name"] if svcs else "Blog técnico")}</p><h1>{e(p["title"])}</h1>
<p class="lead art-meta">Por {AUTHOR} · <time datetime="{pub}">{date_es(pub)}</time> · {read_mins(p)} min de lectura</p></div></div></section>
<section class="section"><div class="container art-layout">
  <article class="prose art-body">
    <div class="answer reveal"><p class="answer-t">{icon("check")} Respuesta directa</p><p>{e(p["answer"])}</p></div>
    {sections}
    <h2>Pregunta frecuente</h2>
    <details class="faq" open><summary><h3>{e(q)}</h3><span class="faq-i" aria-hidden="true"></span></summary><div class="faq-a"><p>{e(a)}</p></div></details>
    {gal}
    <p class="note">Este artículo es orientativo. Cada instalación requiere una evaluación técnica en sitio antes de definir alcance y presupuesto.</p>
  </article>
  <aside class="art-aside">
    <div class="aside-card dark"><p class="eyebrow">Visita técnica</p><h2 class="h3">¿Aplica a su instalación?</h2><p>Registre su requerimiento y reciba una referencia de seguimiento.</p>
      <a class="btn btn-gold block" href="/cotizar/?servicio={svcs[0]["slug"] if svcs else ""}{"&amp;sector=" + sec["id"] if sec else ""}">Cotizar {icon("arrow")}</a>
      <button class="btn btn-ghost block" type="button" data-sofia>Consultar a Sofía</button></div>
    <div class="aside-card"><p class="aside-t">Servicios relacionados</p><ul class="aside-links">{svc_links}{sec_link}</ul></div>
  </aside>
</div></section>
{related_posts_html(related, "Artículos relacionados")}
{cta_block()}'''
    images = [f"{D}{gallery_url(s)}" for s, _c in photos]
    article = {"@type": "BlogPosting", "@id": f"{url}#article", "headline": p["title"][:110], "description": desc, "url": url,
               "mainEntityOfPage": {"@id": f"{url}#webpage"}, "datePublished": pub, "dateModified": TODAY, "inLanguage": "es-PA",
               "author": {"@type": "Organization", "name": AUTHOR, "url": f"{D}/nosotros/"}, "publisher": {"@id": ORG_ID},
               "image": images, "articleSection": sec["name"] if sec else "Blog", "wordCount": len(p["answer"].split()) + sum(len(t.split()) for _h, t in p["sections"]),
               "keywords": ", ".join(uniq([p["title"].split(":")[0]] + [s["serviceType"] for s in svcs] + ["Panamá"])),
               "about": [{"@id": f"{D}{svc_url(s['slug'])}#service"} for s in svcs], "isPartOf": {"@id": f"{D}/blog/#blog"},
               "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".answer", "h1"]}}
    graph = [webpage_node(url, full_title, desc, extra={"mainEntity": {"@id": f"{url}#article"},
                                                       "primaryImageOfPage": {"@type": "ImageObject", "url": images[0]}}),
             article, faq_node(url, [p["faq"]]),
             {"@type": "Blog", "@id": f"{D}/blog/#blog", "name": "Blog técnico DISPRON GROUP", "url": f"{D}/blog/"}]
    page(path, full_title, desc, body, graph, [("Inicio", "/"), ("Blog", "/blog/"), (p["title"], path)], active="/blog/", og_type="article",
         images=[(gallery_url(s), c) for s, c in photos])


def build_resources():
    path = "/recursos/"
    title = "Recursos Técnicos: Guías y Checklists | DISPRON GROUP Panamá"
    desc = "Checklists para preparar visitas técnicas, inspecciones eléctricas, mantenimiento de PH, remodelaciones y stands en Panamá, más el proceso de trabajo."
    guides = "".join(
        f'<article class="guide reveal" id="guia-{i + 1}"><span class="guide-n">{i + 1:02d}</span><h2 class="h3">{e(g["t"])}</h2>'
        f'<ul class="checklist sm">{"".join(f"<li>{CHECK_ICO}{e(x)}</li>" for x in g["items"])}</ul></article>'
        for i, g in enumerate(GUIDES))
    steps = "".join(f'<li class="reveal"><span class="step-n">{i + 1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(PLATFORM["proceso"]))
    cats = uniq([p["sector"] for p in POSTS])
    by_sector = "".join(
        f'<div class="res-col reveal"><p class="aside-t">{e(SECTOR_BY_ID[s]["name"])}</p><ul class="aside-links">'
        + "".join(f'<li><a href="{post_url(p)}">{e(p["title"])}</a></li>' for p in POSTS if p["sector"] == s) + "</ul></div>" for s in cats)
    machine = "".join(f'<li><a href="{u}">{icon("box")}<span><b>{e(n)}</b>{e(d)}</span></a></li>' for u, n, d in [
        ("/knowledge.json", "knowledge.json", "Ficha estructurada de la entidad"), ("/llms.txt", "llms.txt", "Índice para asistentes de IA"),
        ("/llms-full.txt", "llms-full.txt", "Contenido completo en texto"), ("/sitemap.xml", "sitemap.xml", "Mapa del sitio con imágenes")])
    body = f'''{page_hero("Recursos técnicos", "Checklists para preparar su solicitud y acelerar el diagnóstico, el proceso de trabajo y la biblioteca de artículos del blog.", bg="/img/hero/hero-5.webp", eyebrow="Guías y checklists")}
<section class="section"><div class="container"><div class="sec-head reveal"><p class="eyebrow dk">Antes de la visita</p><h2>Qué preparar según su necesidad</h2></div><div class="guides">{guides}</div></div></section>
<section class="section dark process"><div class="container"><div class="sec-head reveal"><p class="eyebrow">Proceso</p><h2>De la solicitud al seguimiento</h2></div><ol class="steps">{steps}</ol></div></section>
<section class="section"><div class="container"><div class="sec-head reveal"><p class="eyebrow dk">Biblioteca</p><h2>Artículos por sector</h2></div><div class="res-cols">{by_sector}</div></div></section>
<section class="section alt"><div class="container narrow"><div class="sec-head reveal"><p class="eyebrow dk">Datos abiertos</p><h2>Información para buscadores y asistentes de IA</h2></div><ul class="machine">{machine}</ul></div></section>
{cta_block()}'''
    url = f"{D}{path}"
    howtos = [{"@type": "HowTo", "@id": f"{url}#guia-{i + 1}", "name": g["t"], "inLanguage": "es-PA",
               "step": [{"@type": "HowToStep", "position": k + 1, "text": x} for k, x in enumerate(g["items"])]} for i, g in enumerate(GUIDES)]
    graph = [webpage_node(url, title, desc, "CollectionPage")] + howtos
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Recursos", path)], active="/recursos/")


def build_quote():
    path = "/cotizar/"
    title = "Cotizar Proyecto o Visita Técnica en Panamá | DISPRON GROUP"
    desc = "Solicite una cotización o visita técnica en 3 pasos: servicio, sitio y contacto. Ingeniería, construcción y mantenimiento en toda Panamá."
    sectors = "".join(f'<option value="{e(x["name"])}" data-id="{x["id"]}">{e(SECTOR_META[x["id"]][2])}</option>' for x in SECTORS)
    groups = "".join(f'<optgroup label="{e(cn)}">' + "".join(f'<option value="{e(s["name"])}" data-slug="{s["slug"]}">{e(s["name"])}</option>'
                                                         for s in SERVICES if s["cat"] == ck) + "</optgroup>" for ck, cn in CATEGORIES)
    urg = "".join(f'<label class="opt"><input type="radio" name="urgency" value="{u}"{" checked" if k == 0 else ""}><span><b>{u}</b><small>{e(d)}</small></span></label>'
                  for k, (u, d) in enumerate(URGENCIES))
    provs = "".join(f"<option>{e(x)}</option>" for x in PLATFORM["provincias"])
    slots = "".join(f"<option>{e(x)}</option>" for x in SLOTS)
    steps_aside = "".join(f'<li><span>{i + 1:02d}</span><div><b>{e(t)}</b><small>{e(d)}</small></div></li>' for i, (t, d) in enumerate(PLATFORM["proceso"][:4]))
    body = f'''{page_hero("Cotice su proyecto en 3 pasos", "Cuéntenos qué necesita, dónde y con qué urgencia. Recibirá un número de referencia y un especialista coordinará la visita técnica.", eyebrow="Cotizador")}
<section class="section"><div class="container quote-layout">
  <form class="form card wizard" id="qform" data-lead action="{e(S.get("formEndpoint") or "/api/leads")}" method="post" novalidate data-wa="{e(S["whatsapp"])}">
    <ol class="wz-progress" aria-hidden="true"><li class="on"><b>1</b>Necesidad</li><li><b>2</b>Sitio y fecha</li><li><b>3</b>Contacto</li></ol>
    <fieldset class="wz-step" data-step="1"><legend>1. ¿Qué necesita?</legend>
      <div class="row"><label>Sector<select name="sector" id="q-sector"><option value="">Seleccione…</option>{sectors}<option value="Otro">Otro sector</option></select></label>
      <label>Servicio*<select name="service" id="servicio" required><option value="">Seleccione…</option>{groups}</select></label></div>
      <p class="lbl">Urgencia</p><div class="opts">{urg}</div>
      <label>Describa el requerimiento*<textarea name="description" rows="4" required minlength="10" placeholder="Área, equipo, problema o alcance esperado"></textarea></label>
    </fieldset>
    <fieldset class="wz-step" data-step="2" hidden><legend>2. ¿Dónde y cuándo?</legend>
      <div class="row"><label>Provincia*<select name="province" required><option value="">Seleccione…</option>{provs}</select></label>
      <label>Sitio o dirección<input name="site" autocomplete="street-address" placeholder="Edificio, planta, sucursal…"></label></div>
      <div class="row"><label>Fecha preferida para la visita<input name="date" type="date"></label>
      <label>Franja horaria<select name="slot"><option value="">Indiferente</option>{slots}</select></label></div>
    </fieldset>
    <fieldset class="wz-step" data-step="3" hidden><legend>3. Datos de contacto</legend>
      <div class="row"><label>Nombre*<input name="name" required autocomplete="name"></label>
      <label>Empresa<input name="company" autocomplete="organization"></label></div>
      <div class="row"><label>Teléfono<input name="phone" type="tel" autocomplete="tel" placeholder="+507"></label>
      <label>Correo<input name="email" type="email" autocomplete="email"></label></div>
      <p class="hint">Indique al menos un teléfono o un correo.</p>
      <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <label class="consent"><input type="checkbox" name="consent" required> Acepto la <a href="/politica-de-privacidad/">política de privacidad</a> y el tratamiento de mis datos para atender esta solicitud.</label>
    </fieldset>
    <p class="form-status" role="status" aria-live="polite"></p>
    <div class="wz-nav"><button class="btn btn-line" type="button" data-prev hidden>Atrás</button><button class="btn btn-accent" type="button" data-next>Continuar {icon("arrow")}</button><button class="btn btn-gold" type="submit" hidden>Enviar solicitud {icon("arrow")}</button></div>
    <div class="wz-done" hidden><span class="done-ico">{icon("check")}</span><h2>Solicitud registrada</h2><p>Su referencia es <strong class="wz-ref"></strong>. Un especialista de DISPRON GROUP le contactará para coordinar la visita técnica.</p><p><a class="btn btn-line" href="/servicios/">Ver servicios</a></p></div>
  </form>
  <aside class="quote-aside">
    <div class="aside-card dark"><p class="eyebrow">Qué sigue</p><ol class="next-steps">{steps_aside}</ol></div>
    <div class="aside-card"><p class="aside-t">¿Prefiere conversar?</p><p>Sofía le guía por chat o escríbanos directamente.</p>
      <button class="btn btn-line block" type="button" data-sofia>Hablar con Sofía</button>
      <a class="btn btn-wa block" href="https://wa.me/{e(S["whatsapp"])}?text={e("Hola DISPRON GROUP, quiero solicitar una cotización.")}" target="_blank" rel="noopener">{WA_SVG} WhatsApp</a></div>
    <div class="aside-card"><p class="aside-t">Recomendado</p><p>Revise las <a href="/recursos/">guías de preparación</a> para acelerar el diagnóstico.</p></div>
  </aside>
</div></section>'''
    url = f"{D}{path}"
    graph = [webpage_node(url, title, desc, extra={"potentialAction": {"@type": "QuoteAction", "target": url, "object": {"@id": ORG_ID}}})]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Cotizar", path)], active="/cotizar/", scripts=("/js/quote.js",))


def mini_header():
    return f'''<header class="mini-header"><div class="container mini-inner">
  <a class="brand" href="/" aria-label="{e(S["brand"])} – inicio"><img src="/img/logo-dispron-horizontal.png" alt="Logotipo {e(S["brand"])}" width="1114" height="416"></a>
  <a class="link" href="/">Volver al sitio {icon("arrow")}</a></div></header>'''


def build_access():
    path = "/acceso/"
    title = "Acceso del equipo | DISPRON GROUP"
    desc = "Acceso privado al CRM comercial de DISPRON GROUP para el equipo autorizado."
    body = f'''<section class="auth-wrap"><div class="auth-card">
  <img src="/img/logo-dispron-mark.png" alt="" width="64" height="67">
  <p class="eyebrow dk">CRM comercial</p><h1>Acceso del equipo</h1>
  <div class="tabs" role="tablist"><button type="button" role="tab" aria-selected="true" data-t="login">Ingresar</button><button type="button" role="tab" aria-selected="false" data-t="reg">Registrarse</button></div>
  <div id="aalert" class="alert" role="alert" hidden></div>
  <form id="login" class="form"><label>Correo<input id="le" type="email" autocomplete="email" required></label>
    <label>Contraseña<input id="lp" type="password" autocomplete="current-password" required></label>
    <button class="btn btn-accent block">Ingresar {icon("arrow")}</button></form>
  <form id="reg" class="form" hidden><label>Nombre<input id="rn" autocomplete="name" required></label>
    <label>Correo<input id="re" type="email" autocomplete="email" required></label>
    <label>Contraseña (mínimo 10 caracteres)<input id="rp" type="password" autocomplete="new-password" minlength="10" required></label>
    <p class="hint">La primera cuenta registrada es administradora. Las siguientes quedan pendientes de aprobación.</p>
    <button class="btn btn-accent block">Crear cuenta</button></form>
  <p class="hint">Requiere el servidor de la plataforma (<code>npm start</code>).</p>
</div></section>'''
    page(path, title, desc, body, [], [], robots="noindex, nofollow", listed=False, chrome=False, scripts=("/js/auth.js",), body_class="app-page")


def build_crm():
    path = "/crm/"
    title = "CRM | DISPRON GROUP"
    desc = "CRM comercial privado de DISPRON GROUP."
    body = '<h1 class="sr">CRM comercial DISPRON GROUP</h1><div id="crm-app"><p class="loading">Cargando CRM…</p></div>'
    page(path, title, desc, body, [], [], robots="noindex, nofollow", listed=False, chrome=False,
         css=("/css/crm.css", "/css/alfred.css"), scripts=("/js/alfred.js", "/js/crm.js"), body_class="app-page crm")


def sofia_html():
    data = {"services": [{"slug": s["slug"], "name": s["name"]} for s in SERVICES],
            "sectores": [{"id": x["id"], "name": x["name"]} for x in SECTORS] + [{"id": "otro", "name": "Otro"}],
            "provincias": PLATFORM["provincias"], "wa": S["whatsapp"]}
    return f'''<button id="sofia-open" class="sofia-fab" type="button" aria-expanded="false" aria-controls="sofia"><img src="/img/logo-dispron-mark-light.png" alt="" width="26" height="27"><span>¿Le ayudo? <b>Sofía</b></span></button>
<section id="sofia" class="sofia" role="dialog" aria-label="Sofía, asistente técnica" hidden>
  <header class="sofia-h"><span class="sofia-av"><img src="/img/logo-dispron-mark-light.png" alt="" width="22" height="23"></span><div><strong>Sofía</strong><small>Asistente técnica · DISPRON GROUP</small></div><button id="sofia-close" type="button" aria-label="Cerrar chat">×</button></header>
  <div id="sofia-log" class="sofia-log" aria-live="polite"></div>
  <div id="sofia-quick" class="sofia-quick"></div>
  <form id="sofia-form" class="sofia-form"><input id="sofia-in" autocomplete="off" placeholder="Escriba su mensaje…" aria-label="Mensaje para Sofía"><button type="submit" aria-label="Enviar">{icon("arrow")}</button></form>
  <p class="sofia-legal">Al compartir sus datos acepta la <a href="/politica-de-privacidad/">política de privacidad</a>.</p>
</section>
<script type="application/json" id="sofia-data">{json.dumps(data, ensure_ascii=False)}</script>
<script src="/js/sofia.js?v={BUILD_ID}" defer></script>'''


def build_knowledge():
    a = S["address"]
    contact = {"phone": S["phoneDisplay"] if real(S["phone"]) and "6000-0000" not in S["phone"] else None,
               "email": S["email"], "whatsapp": S["whatsapp"] if "60000000" not in S["whatsapp"] else None,
               "address": f'{a["street"]}, {a["locality"]}' if real(a["street"]) else None, "hours": S["hoursDisplay"]}
    k = {"@context": "https://schema.org", "name": S["brand"], "legalName": S["legalName"], "alternateName": S["alternateNames"], "url": f"{D}/",
         "description": f"{S['brand']} es una empresa panameña de ingeniería, construcción, mantenimiento industrial, remodelación e instalaciones electromecánicas, con suministro de materiales y equipos.",
         "slogan": S["slogan"], "areaServed": PLATFORM["provincias"], "inLanguage": "es-PA", "dateModified": TODAY,
         "contact": contact, "pendingVerification": [k for k, v in contact.items() if v is None],
         "services": [{"name": s["name"], "serviceType": s["serviceType"], "url": f"{D}{svc_url(s['slug'])}", "summary": s["short"],
                       "category": dict(CATEGORIES)[s["cat"]], "faq": [{"q": q, "a": a_} for q, a_ in s["faqs"]]} for s in SERVICES],
         "sectors": [{"id": x["id"], "name": SECTOR_META[x["id"]][2], "url": f"{D}{sector_url(x['id'])}", "needs": x["needs"],
                      "services": [f"{D}{svc_url(v)}" for v in sector_services(x)]} for x in SECTORS],
         "articles": [{"title": p["title"], "url": f"{D}{post_url(p)}", "answer": p["answer"]} for p in POSTS],
         "faq": [{"q": q, "a": a_} for q, a_ in GENERAL_FAQS],
         "process": [{"step": t, "detail": d} for t, d in PLATFORM["proceso"]],
         "links": {"llms": f"{D}/llms.txt", "llmsFull": f"{D}/llms-full.txt", "sitemap": f"{D}/sitemap.xml", "quote": f"{D}/cotizar/"}}
    (DIST / "knowledge.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    wk = DIST / ".well-known"
    wk.mkdir(exist_ok=True)
    (wk / "ai-plugin-info.json").write_text(json.dumps({"name": S["brand"], "url": f"{D}/", "llms": f"{D}/llms.txt", "knowledge": f"{D}/knowledge.json"},
                                                       ensure_ascii=False, indent=1), encoding="utf-8")
    cat_svc = {kk: sv for kk, _n, sv in GALLERY_CATS}
    alfred = {
        "SERVICES": [{"slug": s["slug"], "name": s["name"], "short": s["short"],
                      "sectors": [x["id"] for x in SECTORS if s["slug"] in sector_services(x)] or ["industrial"],
                      "photos": [u for u, _c in svc_photos(s)] + [gallery_url(src) for src, _c, c in GALLERY if cat_svc[c] == s["slug"]],
                      "scope": [t for t, _d in s["items"]],
                      "faq": [list(f) for f in s["faqs"]]} for s in SERVICES],
        "SECTORES": [dict(x, services=sector_services(x)) for x in SECTORS],
        "GUIAS": GUIDES, "PROCESO": PLATFORM["proceso"], "PROVINCIAS": PLATFORM["provincias"], "CONTACT": contact,
        "GALLERY": [{"url": gallery_url(src), "cat": c, "caption": cap} for src, cap, c in GALLERY],
        "PATHS": list(PAGES),
        "KEYWORDS": {s["slug"]: uniq([f"{s['serviceType']} Panamá", f"{s['name']} Panamá", f"empresa de {s['serviceType'].lower()} en Panamá"]) for s in SERVICES},
    }
    out = ROOT / "server" / "site-data.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(alfred, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    build_home()
    build_services_hub()
    for s in SERVICES:
        build_service(s)
    build_projects()
    build_sectors_hub()
    for sec in SECTORS:
        build_sector(sec)
    build_blog_index()
    for i, post in enumerate(POSTS):
        build_blog_post(i, post)
    build_resources()
    build_quote()
    build_access()
    build_crm()
    build_coverage()
    build_about()
    build_faq()
    build_contact()
    build_privacy()
    build_404()
    build_sitemap()
    build_robots()
    build_llms()
    build_misc()
    build_knowledge()
    print(f"OK: {len(PAGES)} páginas indexables generadas en {DIST}")


if __name__ == "__main__":
    main()
