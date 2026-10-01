# DICPROM – Documento técnico de SEO y GEO (Google + ChatGPT/IA) · Panamá

> Objetivo: posicionar **dicprom.com** en los primeros resultados de Google Panamá y como empresa de referencia citada por ChatGPT, Gemini, Perplexity, Copilot y Claude para ingeniería, construcción y mantenimiento industrial en Panamá.
>
> Nota honesta: ningún proveedor puede garantizar el puesto #1 en Google ni en ChatGPT. El sitio está construido con todas las bases técnicas; el ranking final depende además de la **autoridad** (reseñas, menciones y enlaces), la **antigüedad** del dominio y la **constancia** en contenido. La sección 6 detalla las acciones fuera del sitio que marcan la diferencia.

---

## 1. Arquitectura del sitio

| URL | Tipo de página | Palabra clave principal |
|---|---|---|
| `/` | Inicio (Organization + LocalBusiness) | ingeniería, construcción y mantenimiento industrial Panamá |
| `/servicios/` | CollectionPage | servicios de ingeniería y construcción Panamá |
| `/servicios/diseno-industrial-ingenieria-de-producto/` | Service | diseño industrial Panamá, análisis de fallas FEA |
| `/servicios/mantenimiento-industrial/` | Service | mantenimiento industrial Panamá, termografía, análisis de vibraciones |
| `/servicios/montaje-maquinaria-automatizacion/` | Service | montaje de maquinaria industrial Panamá |
| `/servicios/ingenieria-proyectos-industriales-petroleros-mineria/` | Service | ingeniería de proyectos industriales / petroleros Panamá |
| `/servicios/construccion-obra-civil/` | Service | empresa de construcción Panamá, obra civil |
| `/servicios/remodelacion-fit-out/` | Service | remodelación de oficinas Panamá, fit-out |
| `/servicios/pisos-pintura-epoxica/` | Service | pintura epóxica Panamá, pisos epóxicos |
| `/servicios/mantenimiento-ph-edificios/` | Service | mantenimiento de PH Panamá |
| `/servicios/arquitectura-planos-render-3d/` | Service | planos arquitectónicos, render 3D, diseño de interiores Panamá |
| `/servicios/stands-corporativos/` | Service | stands para ferias Panamá, Panama Convention Center |
| `/servicios/gerencia-proyectos-epc-llave-en-mano/` | Service | proyectos llave en mano Panamá, EPC |
| `/servicios/ingenieria-electrica/` | Service | ingeniería eléctrica Panamá, subestaciones |
| `/servicios/hvac-aire-acondicionado/` | Service | aire acondicionado industrial Panamá, chillers, VRF |
| `/servicios/metalmecanica-soldadura/` | Service | estructuras metálicas Panamá, soldadura industrial |
| `/servicios/fontaneria-hidraulica-contra-incendios/` | Service | sistemas contra incendios Panamá, plomería |
| `/servicios/suministro-equipos-materiales/` | Service | venta de materiales y equipos industriales Panamá |
| `/cobertura/` | WebPage + spatialCoverage | provincias de Panamá |
| `/nosotros/` | AboutPage | empresa de ingeniería Panamá |
| `/preguntas-frecuentes/` | FAQPage (47 preguntas) | consultas long-tail y conversacionales |
| `/contacto/` | ContactPage | cotización |

Cada servicio tiene **una sola URL** (sin canibalización), un H1 único, título ≤ 60–70 caracteres, meta descripción 110–160 caracteres, enlazado interno a 3 servicios relacionados y migas de pan.

## 2. Datos estructurados JSON-LD (Schema.org)

Cada página incluye un único bloque `@graph` interconectado por `@id`:

- `GeneralContractor` + `ProfessionalService` (`https://dicprom.com/#organization`): nombre, razón social, nombres alternativos, logo, NAP, `geo`, horario, `areaServed` (Panamá – Wikidata Q804 – y 10 provincias), `knowsAbout`, `hasOfferCatalog` con los 15 servicios, `contactPoint` ventas y emergencias 24/7, `sameAs`.
- `WebSite` (`/#website`) con `inLanguage: es-PA`.
- `WebPage` / `CollectionPage` / `AboutPage` / `ContactPage` por URL, con `breadcrumb`, `primaryImageOfPage`, `dateModified`.
- `Service` por servicio con `provider`, `serviceType`, `areaServed`, `audience` y `OfferCatalog` de sub‑servicios.
- `FAQPage` en inicio, cada servicio y la página de preguntas frecuentes.
- `BreadcrumbList` e `ItemList`.

Validar tras publicar: https://search.google.com/test/rich-results y https://validator.schema.org/

> No se incluyen `AggregateRating` ni reseñas inventadas: Google penaliza el marcado de reseñas propias. Cuando existan reseñas reales en Google Business Profile, se mostrarán allí.

## 3. SEO técnico incluido

- HTML estático puro (sin frameworks): carga < 1 s, ideal para Core Web Vitals (LCP, INP, CLS) y para rastreadores de IA que **no ejecutan JavaScript**.
- `lang="es-PA"`, `hreflang` es-PA / es / x-default, `canonical` absoluto con barra final.
- Open Graph + Twitter Card con imagen 1200×630, metas `geo.region=PA-8`, `geo.position`, `ICBM`.
- `robots.txt` permitiendo explícitamente a Googlebot, Bingbot, GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended, Applebot, etc.
- `sitemap.xml` con `lastmod` e imágenes.
- `llms.txt` y `llms-full.txt` (estándar emergente para que los LLM entiendan la empresa en texto plano).
- `manifest.webmanifest`, favicon, apple-touch-icon, `humans.txt`, `.well-known/security.txt`.
- Clave IndexNow (`/<clave>.txt`) para notificar cambios a Bing/Copilot/Yandex al instante.
- `.htaccess` (Apache/cPanel) y `_headers` / `_redirects` (Netlify/Cloudflare): HTTPS forzado, dominio canónico sin `www`, HSTS, caché de 1 año para estáticos, compresión.
- Accesibilidad: enlace “saltar al contenido”, `aria-*`, contraste AA, navegación por teclado, `prefers-reduced-motion`.
- Formulario de cotización: envía a WhatsApp por defecto; si se configura `formEndpoint` (Formspree, Getform, etc.) envía por POST. Incluye honeypot anti‑spam.
- Analítica GA4 opcional (`gaMeasurementId`).

## 4. GEO – Optimización para ChatGPT y motores generativos

1. **Definición de entidad consistente**: todas las páginas repiten la frase “DICPROM es una empresa panameña de …” → los LLM aprenden a asociar la marca con la categoría y el país.
2. **Bloques “Datos clave” y “DICPROM en resumen”** (`<dl>`): hechos citables en formato pregunta‑respuesta.
3. **FAQ conversacionales** (47 preguntas) redactadas como las preguntaría un usuario a ChatGPT.
4. **Normas y terminología técnica** (NFPA, ASHRAE, AWS D1.1, ASME B31.3, API 650, ISO 55000, REP, JTIA, BCBRP) → señales de experiencia (E‑E‑A‑T).
5. **ChatGPT Search usa el índice de Bing** → registrar el sitio en **Bing Webmaster Tools** es obligatorio (sección 6).
6. `llms.txt` / `llms-full.txt` + robots abiertos a bots de IA.
7. Menciones externas consistentes (directorios, prensa, LinkedIn) – los LLM ponderan lo que dicen otras fuentes sobre la marca.

## 5. Datos que debe completar antes de publicar

Edite `data/site.json` y ejecute `python3 build.py`:

| Campo | Estado |
|---|---|
| `phone`, `phoneDisplay`, `whatsapp` | **Reemplazar** (hoy +507 6000‑0000 de ejemplo) |
| `address.street`, `postalCode`, `geo` (lat/lng exactos de la oficina) | **Reemplazar** |
| `foundingYear`, `taxID` (RUC) | **Reemplazar** (se omiten del JSON‑LD mientras digan REEMPLAZAR) |
| `sameAs` (LinkedIn, Facebook, Instagram reales) | Verificar URLs |
| `googleSiteVerification`, `bingSiteVerification`, `gaMeasurementId` | Agregar tras crear cuentas |
| `formEndpoint` | Opcional |
| `legalName` | Confirmar razón social exacta (DICPROM, S.A.) |

`python3 tools/check.py` avisa si quedan datos pendientes y valida JSON‑LD, enlaces, H1, títulos y descripciones.

## 6. Plan de posicionamiento fuera del sitio (decisivo para el #1)

**Semana 1 – Indexación**
- [ ] Publicar en hosting con HTTPS (Cloudflare Pages, Netlify, Vercel o cPanel).
- [ ] Google Search Console: verificar dominio, enviar `sitemap.xml`, solicitar indexación de inicio y servicios.
- [ ] Bing Webmaster Tools: importar desde Search Console, enviar sitemap, activar IndexNow → **base de ChatGPT Search y Copilot**.
- [ ] Google Business Profile: categoría principal “Contratista general”, secundarias “Servicio de mantenimiento industrial”, “Contratista eléctrico”, “Contratista de aire acondicionado”, “Taller de soldadura”, “Empresa de construcción”; mismo NAP exacto; agregar los 15 servicios, fotos reales y horario.
- [ ] Bing Places y Apple Business Connect con el mismo NAP.

**Mes 1 – Autoridad local**
- [ ] Citas NAP idénticas: Páginas Amarillas Panamá, Cámara de Comercio, Industrias y Agricultura de Panamá (CCIAP), Sindicato de Industriales de Panamá (SIP), CAPAC, Panamá Compra (proveedor del Estado), LinkedIn Company Page, Facebook, Instagram, Crunchbase.
- [ ] Pedir reseñas reales en Google a cada cliente (meta: 20+ reseñas en 90 días) y responderlas todas.
- [ ] Fotos y casos reales: reemplazar ilustraciones por fotografías WebP propias con `alt` descriptivo.

**Meses 2–6 – Contenido y enlaces**
- [ ] Página de **proyectos/casos de éxito** (un caso por servicio: problema, solución, resultado medible, fotos) con `Article`/`CreativeWork`.
- [ ] Blog técnico mensual (ej.: “Cada cuánto dar mantenimiento a un chiller en Panamá”, “Requisitos de Bomberos para sistemas contra incendios”, “Costo de un piso epóxico por m² en Panamá”).
- [ ] Notas de prensa y menciones en medios panameños (La Prensa, Capital Financiero, revistas de construcción) y en sitios de proveedores/marcas aliadas.
- [ ] Perfil en Wikidata para la empresa cuando exista cobertura de prensa verificable (refuerza la entidad en Google Knowledge Graph y LLM).
- [ ] Monitorear en Search Console (consultas, CTR) y en ChatGPT/Perplexity preguntando “mejor empresa de mantenimiento industrial en Panamá”.

## 7. Compilar y publicar

```bash
python3 tools/make_images.py   # (opcional) regenerar logo, iconos e imagen OG
python3 build.py               # genera dist/
python3 tools/check.py         # auditoría SEO
cd dist && python3 -m http.server 8080   # vista previa local
```

Subir **el contenido de `dist/`** a la raíz del hosting.

- **Cloudflare Pages / Netlify**: directorio de publicación `dist`, comando `python3 build.py`.
- **cPanel / Apache**: subir `dist/*` (incluido `.htaccess`) a `public_html`.
- **Nginx**: `try_files $uri $uri/ =404; error_page 404 /404.html;` + redirección 301 de `www` y `http` a `https://dicprom.com`.

Después de cada publicación: reenviar sitemap en Search Console / Bing y notificar IndexNow:

```bash
curl "https://api.indexnow.org/indexnow?url=https://dicprom.com/&key=<indexNowKey>"
```
