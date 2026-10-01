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

S = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
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
NAV = [("/", "Inicio"), ("/servicios/", "Servicios"), ("/proyectos/", "Proyectos"), ("/cobertura/", "Cobertura"),
       ("/nosotros/", "Nosotros"), ("/preguntas-frecuentes/", "Preguntas"), ("/contacto/", "Contacto")]


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
      <a class="btn btn-gold nav-cta" href="/contacto/">Cotizar proyecto {icon("arrow")}</a></nav>
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
    <a class="btn btn-gold" href="/contacto/">Solicitar cotización {icon("arrow")}</a>
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
    <p><a href="/politica-de-privacidad/">Política de privacidad</a> · <a href="/sitemap.xml">Mapa del sitio</a> · <a href="/llms.txt">llms.txt</a></p>
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


def page(path, title, desc, body, graph, crumbs, active=None, og_type="website", robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1", images=None):
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
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
{ga}</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
{nav_html(active or path)}
<main id="main">
{body}
</main>
{footer_html()}
<script src="/js/main.js?v={BUILD_ID}" defer></script>
</body>
</html>
'''
    doc = doc.replace("<!--CRUMBS-->", breadcrumbs_html(crumbs))
    out = DIST / path.strip("/") / "index.html" if path.endswith("/") else DIST / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
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
  <div class="cta-actions"><a class="btn btn-gold" href="/contacto/">Solicitar cotización {icon("arrow")}</a>
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
      <div class="hero-actions"><a class="btn btn-gold" href="/contacto/">Solicitar cotización {icon("arrow")}</a><a class="btn btn-ghost" href="/servicios/">Explorar servicios</a></div>
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
    actions = (f'<div class="hero-actions"><a class="btn btn-gold" href="/contacto/?servicio={e(s["slug"])}">Cotizar este servicio {icon("arrow")}</a>'
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
{process_html()}
{faq_html(s["faqs"], "Preguntas frecuentes sobre " + s["serviceType"].lower())}
<section class="section alt"><div class="container"><div class="sec-head reveal"><p class="eyebrow dk">Complementos</p><h2>Servicios relacionados</h2></div><div class="svc-grid">{rel}</div></div></section>
{cta_block("Cotice " + s["serviceType"].lower() + " en Panamá")}'''
    graph = [webpage_node(url, s["title"], s["desc"], extra={"mainEntity": {"@id": f"{url}#service"},
                                                             "primaryImageOfPage": {"@type": "ImageObject", "url": f"{D}{photos[0][0]}", "caption": photos[0][1]}}),
             service_node(s), faq_node(url, s["faqs"])]
    page(path, s["title"], s["desc"], body, graph, [("Inicio", "/"), ("Servicios", "/servicios/"), (s["name"], path)], active="/servicios/", og_type="article",
         images=photos)


def build_projects():
    path = "/proyectos/"
    title = "Proyectos y Galería de Obras en Panamá | DISPRON GROUP"
    desc = "Galería de proyectos de DISPRON GROUP en Panamá: obra civil, estructuras metálicas, electricidad, HVAC, contra incendios, epóxicos, fit-out y stands."
    filters = '<button class="chip active" data-filter="all" aria-pressed="true">Todos</button>' + "".join(
        f'<button class="chip" data-filter="{ckey}" aria-pressed="false">{e(cname)}</button>' for ckey, cname in CATEGORIES)
    items, all_photos, seen = "", [], set()
    for s in SERVICES:
        for u, c in svc_photos(s):
            if c in seen:
                continue
            seen.add(c)
            all_photos.append((u, c, s))
            items += (f'<figure class="g-item reveal" data-cat="{s["cat"]}"><a href="{u}" data-lightbox data-caption="{e(c)} · {e(s["name"])}">'
                      f'{picture(u, c + " – " + s["name"] + " en Panamá", sizes="(max-width: 700px) 100vw, 400px")}</a>'
                      f'<figcaption><strong>{e(c)}</strong><a href="{svc_url(s["slug"])}">{e(s["name"])}</a></figcaption></figure>')
    body = f'''{page_hero("Proyectos y obras en Panamá", "Fotografías de trabajos en campo de DISPRON GROUP: construcción, montaje, instalaciones electromecánicas, mantenimiento y acabados.", bg="/img/hero/hero-3.webp", eyebrow="Galería de proyectos")}
<section class="section"><div class="container">
  <div class="filters" role="group" aria-label="Filtrar proyectos por división">{filters}</div>
  <div class="gallery masonry" id="project-grid">{items}</div>
</div></section>{cta_block("¿Quiere un resultado así en su instalación?")}'''
    url = f"{D}{path}"
    gallery_node = {"@type": "ImageGallery", "@id": f"{url}#galeria", "name": "Proyectos DISPRON GROUP en Panamá", "url": url,
                    "about": {"@id": ORG_ID}, "inLanguage": "es-PA",
                    "image": [{"@type": "ImageObject", "contentUrl": f"{D}{u}", "caption": f"{c} – {s['name']}", "creator": {"@id": ORG_ID},
                               "copyrightHolder": {"@id": ORG_ID}, "contentLocation": {"@type": "Country", "name": "Panamá"}} for u, c, s in all_photos]}
    graph = [webpage_node(url, title, desc, "CollectionPage", {"mainEntity": {"@id": f"{url}#galeria"}}), gallery_node]
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Proyectos", path)], images=[(u, c) for u, c, _s in all_photos])


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
  <form class="form card" id="quote-form" action="{e(S.get("formEndpoint") or "#")}" method="post" data-wa="{e(S["whatsapp"])}" data-email="{e(S["email"])}">
    <h2>Solicitar cotización</h2>
    <div class="row"><label>Nombre completo*<input name="nombre" required autocomplete="name"></label>
    <label>Empresa<input name="empresa" autocomplete="organization"></label></div>
    <div class="row"><label>Teléfono*<input name="telefono" type="tel" required autocomplete="tel" placeholder="+507"></label>
    <label>Correo electrónico*<input name="email" type="email" required autocomplete="email"></label></div>
    <div class="row"><label>Servicio de interés<select name="servicio" id="servicio"><option value="">Seleccione…</option>{opts}</select></label>
    <label>Provincia<select name="provincia"><option value="">Seleccione…</option>{provs}</select></label></div>
    <label>Describa su proyecto*<textarea name="mensaje" rows="5" required></textarea></label>
    <input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
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
    page(path, title, desc, body, graph, [("Inicio", "/"), ("Contacto", path)])


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
    page("/404.html", title, desc, body, [], [], robots="noindex, follow")
    PAGES.remove("/404.html")


# ------------------------------------------------------------------ archivos técnicos
def build_sitemap():
    prio = {"/": "1.0", "/servicios/": "0.9", "/contacto/": "0.8"}
    urls = "".join(
        f"<url><loc>{D}{p}</loc><lastmod>{TODAY}</lastmod><changefreq>{'weekly' if p in prio else 'monthly'}</changefreq>"
        f"<priority>{prio.get(p, '0.8' if p.startswith('/servicios/') else '0.6')}</priority>"
        + "".join(f"<image:image><image:loc>{D}{u}</image:loc></image:image>" for u, c in (PAGE_IMAGES.get(p) or [(OG_IMAGE.replace(D, ""), S["brand"])]))
        + "</url>\n" for p in PAGES)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + urls + "</urlset>\n", encoding="utf-8")


def build_robots():
    ai_bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User", "ClaudeBot", "Claude-User",
               "Claude-SearchBot", "Google-Extended", "Applebot", "Applebot-Extended", "Bingbot", "CCBot", "DuckAssistBot",
               "meta-externalagent", "Amazonbot", "cohere-ai", "MistralAI-User"]
    txt = "# robots.txt – dicprom.com\n# Rastreo permitido para buscadores y asistentes de IA (GEO).\n\nUser-agent: *\nAllow: /\nDisallow: /404.html\n\n"
    txt += "".join(f"User-agent: {b}\nAllow: /\n\n" for b in ai_bots)
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
              f"- [Preguntas frecuentes]({D}/preguntas-frecuentes/): respuestas detalladas", f"- [Contacto]({D}/contacto/): cotizaciones", "",
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


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    build_home()
    build_services_hub()
    for s in SERVICES:
        build_service(s)
    build_projects()
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
    print(f"OK: {len(PAGES)} páginas indexables generadas en {DIST}")


if __name__ == "__main__":
    main()
