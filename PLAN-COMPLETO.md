# DISPRON GROUP · Plan completo del sitio web y de posicionamiento (Google + IA) · Panamá

> **Dominio:** https://dicprom.com · **Marca:** DISPRON GROUP (logotipo oficial) · **Idioma:** español de Panamá (`es-PA`)
>
> **Objetivo:** que DISPRON GROUP aparezca entre los primeros resultados de Google Panamá y sea la empresa que ChatGPT, Gemini, Perplexity, Copilot y Claude citan en ingeniería, construcción y mantenimiento industrial en Panamá.
>
> **Nota:** nadie puede garantizar el puesto #1 en Google ni en ChatGPT. Este sitio deja lista toda la parte técnica. El resultado final depende de la autoridad de la marca (reseñas, menciones, enlaces), de la antigüedad del dominio y de publicar contenido con constancia. Las fases 2 a 4 de la hoja de ruta (§12) cubren esa parte.

---

## 0. Decisiones de marca y dominio (confirmar)

| Punto | Valor actual en el sitio | Acción |
|---|---|---|
| Marca comercial | **DISPRON GROUP** (alternativos: DISPRON, Dispron Group Panamá) | Confirmar |
| Razón social (`legalName`) | DISPRON GROUP, S.A. | **Confirmar nombre exacto** en el Registro Público |
| Dominio | `dicprom.com` | Confirmar. Si se registra `dispron.com` / `disprongroup.com`, cambiar `domain` en `data/site.json`, regenerar y redirigir 301 el dominio antiguo |
| Logotipo | Archivo oficial del cliente (`assets-src/logo-oficial.jpg`) → PNG transparentes, favicon, iconos PWA e imagen OG | Listo |

Lo ideal es que la marca y el dominio coincidan. Si el dominio dice *dicprom* y la marca *DISPRON*, Google y los LLM ven dos entidades distintas. Mientras no se cambie, el JSON-LD declara `alternateName` y la misma URL para mantenerlas unidas.

---

## 1. Objetivos y KPI

| Horizonte | KPI | Meta orientativa |
|---|---|---|
| 30 días | Páginas indexadas (Search Console + Bing) | 24/24 |
| 90 días | Impresiones orgánicas/mes en Google Panamá | 5 000+ |
| 90 días | Reseñas reales en Google Business Profile | 20+ (promedio ≥ 4,7) |
| 6 meses | Palabras clave en top 10 Google Panamá | 40+ (marca + servicio + Panamá) |
| 6 meses | Solicitudes de cotización/mes (formulario + WhatsApp) | 30+ |
| 12 meses | Menciones de DISPRON GROUP en respuestas de ChatGPT/Perplexity/Gemini para las 20 preguntas objetivo (§11) | ≥ 50 % |

---

## 2. Identidad visual y diseño

**Concepto:** *ingeniería de precisión*. Los colores salen del logotipo oficial: azul acero/navy y oro cepillado. Las líneas geométricas del isotipo se repiten como trazos dorados animados en los héroes.

- **Paleta:** navy `#0F1A2B` / `#16243A` / `#1F3150`, acero `#3A4A62`, oro `#C9A45C` y degradado oro cepillado `#A8823F → #F0DCA8`, fondo cálido `#F5F3EE`.
- **Tipografía:** Montserrat (títulos, la misma familia geométrica del logotipo) + Inter (texto). Las fuentes están alojadas en el propio sitio (`/fonts/*.woff2`): no se usa Google Fonts, no hay cookies de terceros y la carga es más rápida.
- **Componentes innovadores**
  - Hero a pantalla completa con 5 fotografías de obra en fundido con efecto *Ken Burns*, panel de cristal (*glassmorphism*) con cifras animadas y una cinta continua con todos los servicios.
  - Retícula *bento* con las 4 divisiones de negocio.
  - Tarjetas de servicio con foto, número de orden e icono flotante.
  - Metodología en 4 pasos sobre fondo oscuro.
  - Carrusel continuo de fotos de obra que se detiene al pasar el cursor.
  - Galería `/proyectos/` con filtros por división y visor ampliado (*lightbox*) accesible.
  - Páginas de servicio con foto de fondo, ficha “Datos clave”, galería propia, FAQ desplegable y servicios relacionados.
  - Animaciones de entrada al hacer scroll, cabecera con efecto cristal, mega menú, botón de WhatsApp y botón “volver arriba”.
- **Accesibilidad (WCAG 2.1 AA):** contraste AA, foco visible dorado, enlace “saltar al contenido”, navegación completa por teclado, `aria-*` en menú, filtros y visor, y `prefers-reduced-motion`, que desactiva todas las animaciones.
- **Rendimiento:** HTML estático. Las 78 fotografías están en WebP (146 archivos, `srcset` 640/1200 px) y `width`/`height` fijos (CLS ≈ 0). Lazy-loading en todo salvo la primera imagen del hero, que se carga con `fetchpriority="high"`. El sitio entero lleva unos 5 KB de JavaScript.

---

## 3. Arquitectura del sitio (24 URL indexables)

| URL | Tipo Schema | Palabra clave principal |
|---|---|---|
| `/` | WebPage + Organization/GeneralContractor | ingeniería, construcción y mantenimiento industrial Panamá |
| `/servicios/` | CollectionPage + ItemList | servicios de ingeniería y construcción Panamá |
| `/servicios/diseno-industrial-ingenieria-de-producto/` | Service | diseño industrial Panamá, análisis de fallas FEA |
| `/servicios/mantenimiento-industrial/` | Service | mantenimiento industrial Panamá, termografía, vibraciones |
| `/servicios/montaje-maquinaria-automatizacion/` | Service | montaje de maquinaria industrial Panamá |
| `/servicios/ingenieria-proyectos-industriales-petroleros-mineria/` | Service | ingeniería de proyectos industriales / petroleros / minería Panamá |
| `/servicios/construccion-obra-civil/` | Service | empresa de construcción Panamá, obra civil, asfalto |
| `/servicios/remodelacion-fit-out/` | Service | remodelación de oficinas Panamá, fit-out |
| `/servicios/pisos-pintura-epoxica/` | Service | pintura epóxica Panamá, pisos epóxicos |
| `/servicios/mantenimiento-ph-edificios/` | Service | mantenimiento de PH Panamá, bancos, instituciones |
| `/servicios/arquitectura-planos-render-3d/` | Service | planos arquitectónicos, render 3D, diseño de interiores Panamá |
| `/servicios/stands-corporativos/` | Service | stands para ferias Panamá, centro de convenciones |
| `/servicios/gerencia-proyectos-epc-llave-en-mano/` | Service | proyectos llave en mano Panamá, EPC |
| `/servicios/ingenieria-electrica/` | Service | ingeniería eléctrica Panamá, subestaciones, generadores |
| `/servicios/hvac-aire-acondicionado/` | Service | aire acondicionado industrial Panamá, chillers, VRF |
| `/servicios/metalmecanica-soldadura/` | Service | estructuras metálicas Panamá, soldadura industrial |
| `/servicios/fontaneria-hidraulica-contra-incendios/` | Service | sistemas contra incendios Panamá, plomería industrial |
| `/servicios/suministro-equipos-materiales/` | Service | venta de materiales y equipos industriales Panamá |
| `/proyectos/` | CollectionPage + ImageGallery | proyectos de construcción Panamá, galería de obras |
| `/cobertura/` | WebPage + spatialCoverage | provincias de Panamá |
| `/nosotros/` | AboutPage | empresa de ingeniería Panamá |
| `/preguntas-frecuentes/` | FAQPage | consultas long-tail y conversacionales |
| `/contacto/` | ContactPage | cotización |
| `/politica-de-privacidad/` | WebPage | Ley 81 de 2019 |

Reglas que se cumplen:
- Una URL por intención de búsqueda, sin canibalización entre páginas.
- Un solo H1 por página.
- Títulos de 70 caracteres o menos y descripciones de 160 o menos.
- Migas de pan en todas las páginas internas.
- Cada servicio enlaza a 3 servicios relacionados.
- El mega menú y el pie de página enlazan los 16 servicios.

**Futuras secciones (fase 3):**
- `/blog/<slug>/` con `Article`.
- `/proyectos/<slug>/`: casos de éxito con `CreativeWork` o `Article`.
- `/sectores/<slug>/`: bancos, hoteles, PH, industria, minería y eventos, aprovechando la estructura de sectores de la plataforma DISPRON.
- `/provincias/<slug>/`: solo si hay obras reales en esa provincia, para evitar contenido delgado.

---

## 4. Datos estructurados JSON-LD

Cada página tiene un único bloque `@graph`. Sus nodos se enlazan entre sí por `@id`.

- **`GeneralContractor` + `ProfessionalService`** (`https://dicprom.com/#organization`). Contiene:
  - Identificación: `name`, `legalName`, `alternateName` y logotipo oficial como `ImageObject`.
  - Imágenes de obra.
  - Datos de contacto (NAP), `geo` y horario.
  - `areaServed`: Panamá (Wikidata Q804) más 10 provincias y comarcas.
  - `knowsAbout`.
  - `hasOfferCatalog`: 4 divisiones con los 16 servicios.
  - `contactPoint` de ventas y de emergencias 24/7, y `sameAs`.
- **`WebSite`** (`/#website`) con `inLanguage: es-PA`.
- **Página web por URL:** `WebPage`, `CollectionPage`, `AboutPage` o `ContactPage`, con `breadcrumb`, `primaryImageOfPage` (la foto real del servicio) y `dateModified`.
- **`Service`** por cada servicio: `provider`, `serviceType`, `areaServed`, `audience`, `hasOfferCatalog` con los subservicios e `image` con las fotos de obra y su descripción.
- **`ImageGallery`** en `/proyectos/`: 68 fotos, cada una como `ImageObject` con `caption`, `creator`, `copyrightHolder` y `contentLocation`.
- **`FAQPage`** en inicio, en cada servicio y en preguntas frecuentes.
- **`BreadcrumbList`** e **`ItemList`**.

Validar tras publicar en https://search.google.com/test/rich-results y https://validator.schema.org/.

**Lo que no se marca a propósito:** `AggregateRating`, reseñas, premios y certificaciones, porque todavía no hay datos verificables. Google penaliza el marcado de reseñas propias. Las reseñas reales se muestran en Google Business Profile.

---

## 5. SEO técnico incluido

- **HTML estático y lenguaje:** el HTML es estático, así que los rastreadores de IA, que no ejecutan JavaScript, ven todo el contenido. Incluye `lang="es-PA"`, `hreflang` es-PA / es / x-default y `canonical` absoluto con barra final.
- **Metadatos para redes y geolocalización:** Open Graph y Twitter Card con la imagen `og-dispron.jpg` (1200×630, logotipo + foto de obra), y metas `geo.region=PA-8`, `geo.position` e `ICBM`.
- **Archivos para buscadores e IA:**
  - `robots.txt` abierto a Googlebot, Bingbot, GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended, Applebot y otros.
  - `sitemap.xml` con `lastmod` y **las fotos de cada página** (sitemap de imágenes).
  - `llms.txt` y `llms-full.txt`: la empresa explicada en texto plano para los LLM.
- **Archivos de soporte:** `manifest.webmanifest` (PWA), favicon con el isotipo, `apple-touch-icon`, `humans.txt` y `.well-known/security.txt`. Clave IndexNow para avisar los cambios a Bing, Copilot y Yandex.
- **Configuración del servidor:**
  - `.htaccess` para Apache/cPanel y `_headers` / `_redirects` para Netlify/Cloudflare.
  - Fuerzan HTTPS, dominio sin `www`, HSTS, compresión y caché de 1 año.
  - El CSS y el JS llevan un parámetro de versión `?v=` para que el navegador descargue la versión nueva tras cada cambio.
- **Formulario de cotización:**
  - Envía a WhatsApp por defecto.
  - Si se configura `formEndpoint`, envía por POST a ese servicio: Formspree, Getform o el CRM de la plataforma DISPRON (§14).
  - Tiene un campo oculto anti-spam (honeypot).
  - Si el enlace lleva `?servicio=<slug>`, el servicio queda preseleccionado.
- **Analítica:** GA4 opcional (`gaMeasurementId`).

---

## 6. GEO: optimización para ChatGPT y motores generativos

1. **Entidad consistente:** todas las páginas definen “DISPRON GROUP es una empresa panameña de…”, con `alternateName` para las variantes del nombre.
2. **Hechos citables:** “Datos clave” en cada servicio y “DISPRON GROUP en resumen” en inicio, en formato `<dl>`.
3. **FAQ conversacionales:** redactadas como se las preguntaría un usuario a ChatGPT.
4. **Terminología y normas:** NFPA, ASHRAE, AWS D1.1, ASME B31.3, API 650, ISO 55000, REP, JTIA y Bomberos de Panamá. Son señales de experiencia (E-E-A-T).
5. **Bing Webmaster Tools es obligatorio:** ChatGPT Search y Copilot usan el índice de Bing.
6. **Acceso para IA:** `llms.txt` y `robots.txt` abiertos a los bots de IA.
7. **Coherencia externa:** el mismo nombre, descripción y NAP en LinkedIn, directorios y prensa. Los LLM dan peso a lo que dicen otras fuentes sobre la marca.

---

## 7. Mapa de palabras clave (clusters)

| División | Palabras clave principales (Google Panamá) | Long-tail / conversacionales (IA) |
|---|---|---|
| Diseño industrial y mantenimiento | mantenimiento industrial Panamá · termografía Panamá · análisis de vibraciones · montaje de maquinaria · diseño industrial Panamá | ¿qué empresa hace mantenimiento predictivo en Panamá? · costo de termografía industrial |
| Construcción y remodelación | empresa de construcción Panamá · constructora Panamá · obra civil · asfalto y pavimentación · remodelación de oficinas · fit-out Panamá · pintura epóxica · pisos epóxicos · mantenimiento de PH · render 3D Panamá · stands para ferias | ¿cuánto cuesta un piso epóxico por m² en Panamá? · empresa para mantenimiento de PH en Costa del Este |
| Electromecánica | ingeniería eléctrica Panamá · subestaciones · plantas eléctricas · aire acondicionado industrial · chillers · VRF · estructuras metálicas · soldadura industrial · sistemas contra incendios · plomería industrial | requisitos de Bomberos para rociadores · mantenimiento de chiller cada cuánto |
| Suministro | venta de materiales industriales Panamá · alquiler de equipos · repuestos industriales | dónde comprar tubería de acero en Panamá |
| Geográficas | + Ciudad de Panamá, Colón, Zona Libre, Chiriquí/David, Coclé, Panamá Oeste, Veraguas | “cerca de mí” (lo resuelve Google Business Profile) |

---

## 8. Plan de contenidos (12 meses)

**Casos de éxito.** Uno por mes en `/proyectos/<slug>/`, con esta estructura: cliente o sector, reto, solución, normas aplicadas, resultado medible, fotos y testimonio con autorización.

**Blog técnico.** Dos artículos al mes de 1 200 a 2 000 palabras, cada uno con FAQ, enlace al servicio y autor con nombre y credenciales (E-E-A-T).

| Mes | Artículos sugeridos |
|---|---|
| 1 | Cada cuánto dar mantenimiento a un chiller en Panamá · Guía de pisos epóxicos: tipos, espesores y costo por m² |
| 2 | Requisitos de Bomberos de Panamá para sistemas contra incendios · Mantenimiento predictivo con termografía: beneficios y ROI |
| 3 | Checklist de mantenimiento para PH en Panamá · Cómo planificar un fit-out de oficinas sin detener la operación |
| 4 | Subestaciones eléctricas: mantenimiento preventivo y pruebas · Qué es un proyecto EPC / llave en mano |
| 5 | Soldadura SMAW, MIG y TIG: cuándo usar cada una · Estructuras metálicas para galeras en Panamá |
| 6 | Cómo elegir un sistema VRF vs. chiller · Stands para ferias en el Panama Convention Center: tiempos y permisos |
| 7–12 | Temas guiados por Search Console (consultas con impresiones y sin clic), por preguntas reales de clientes y por la temporada de lluvias (impermeabilización y pluviales) |

**Redes sociales.** Publicar en LinkedIn (prioridad B2B), Instagram y Facebook el mismo contenido adaptado, siempre con enlace a la URL del sitio.

---

## 9. SEO local

- **Google Business Profile**
  - Categoría principal: “Contratista general”.
  - Categorías secundarias: “Servicio de mantenimiento industrial”, “Contratista eléctrico”, “Contratista de aire acondicionado”, “Taller de soldadura”, “Empresa de construcción” y “Servicio de protección contra incendios”.
  - Cargar los 16 servicios, fotos reales semanales, horario, área de servicio (todas las provincias) y publicaciones quincenales.
- **Bing Places y Apple Business Connect:** con el mismo NAP.
- **Citas NAP idénticas en:**
  - Páginas Amarillas Panamá.
  - Gremios: CCIAP, SIP, CAPAC y APEDE.
  - PanamaCompra (proveedor del Estado).
  - Directorios de la Zona Libre de Colón.
  - LinkedIn Company Page, Facebook, Instagram, YouTube y Crunchbase.
- **Reseñas:** pedirlas por WhatsApp con el enlace directo al terminar cada servicio y responderlas todas en menos de 48 h.

---

## 10. Autoridad y enlaces

- Alianzas con fabricantes y distribuidores (marcas de HVAC, eléctricas y de recubrimientos) para aparecer en su sección de instaladores o partners.
- Notas de prensa y artículos de experto en medios panameños: La Prensa, Capital Financiero, Martes Financiero y revistas de construcción e industria.
- Patrocinio o participación en ferias (Expocomer, Expo Construcción), con stand propio como caso de éxito.
- Entrada en Wikidata cuando exista cobertura de prensa verificable. Refuerza el Knowledge Graph y la comprensión de los LLM.
- No comprar enlaces ni usar redes de blogs (PBN): Google penaliza esas prácticas.

---

## 11. Medición

- **Google Search Console:** impresiones, clics, CTR y posición por página y consulta. Informe mensual.
- **Bing Webmaster Tools:** indexación y consultas. Es la base de ChatGPT Search y Copilot.
- **GA4:**
  - Eventos `generate_lead` (envío del formulario), `click_whatsapp`, `click_tel` y `click_email`.
  - Marcarlos como conversiones.
- **Seguimiento en IA (mensual).** Hacer 20 preguntas fijas en ChatGPT, Perplexity, Gemini y Copilot y registrar si citan a DISPRON GROUP y con qué fuente. Ejemplos:
  - “mejor empresa de mantenimiento industrial en Panamá”
  - “quién instala sistemas contra incendios en Panamá”
  - “empresa de pisos epóxicos en Panamá”

---

## 12. Hoja de ruta

| Fase | Plazo | Tareas |
|---|---|---|
| **0 · Pre-publicación** | Antes de publicar | Confirmar marca, razón social y dominio (§0). Completar `data/site.json` (§13). Revisar fotos (§13). Regenerar (`python3 build.py`) y ejecutar `python3 tools/check.py` sin avisos |
| **1 · Lanzamiento** | Semana 1 | Publicar con HTTPS. Alta en Search Console y Bing Webmaster, enviar `sitemap.xml` y activar IndexNow. Crear Google Business Profile, Bing Places y Apple Business Connect. Configurar GA4 y el formulario |
| **2 · Autoridad local** | Días 8–30 | Citas NAP (§9). Primeras 10 reseñas. Perfiles sociales con `sameAs` actualizado. Validar rich results |
| **3 · Contenido** | Meses 2–6 | 2 artículos y 1 caso de éxito al mes. Páginas `/sectores/`. Optimizar títulos según el CTR de Search Console |
| **4 · Escala** | Meses 6–12 | Prensa y alianzas. Wikidata. Páginas por provincia con obras reales. Versión en inglés (`/en/`) si se buscan clientes internacionales (minería, Zona Libre) |

---

## 13. Datos que deben completarse antes de publicar

Editar `data/site.json` y ejecutar `python3 build.py`:

| Campo | Estado |
|---|---|
| `phone`, `phoneDisplay`, `whatsapp` | **Reemplazar** (hoy aparece el número de ejemplo +507 6000-0000) |
| `email` | Confirmar buzón real (`info@dicprom.com`) |
| `address.street`, `postalCode`, `geo` (latitud y longitud exactas) | **Reemplazar** |
| `foundingYear`, `taxID` (RUC) | **Reemplazar** (no salen en el JSON-LD mientras digan REEMPLAZAR) |
| `legalName` | Confirmar razón social exacta |
| `sameAs` | Agregar las URL reales de LinkedIn, Facebook, Instagram y YouTube |
| `googleSiteVerification`, `bingSiteVerification`, `gaMeasurementId` | Agregar tras crear las cuentas |
| `formEndpoint` | Opcional (§14) |

**Fotografías.** Se usan las fotos del paquete de la plataforma DISPRON, cuyo README las describe como fotos reales. El sitio las publica como obras propias: el JSON-LD declara a DISPRON GROUP como `creator`/`copyrightHolder`. Antes de publicar hay que confirmar que **todas** corresponden a trabajos propios con derecho de uso. Si alguna no lo es, o muestra marcas de terceros (por ejemplo, el stand con logotipos de aerolínea), se cambia la ruta en `PHOTOS` dentro de `data/content.py` y se ejecuta `python3 tools/import_assets.py`.

---

## 14. Relación con la plataforma DISPRON (Node/Express: CRM, cotizador, Sofía)

- **Sitio público** (`dicprom.com`): este sitio estático. Es la mejor opción para SEO y para la IA: rápido, sin JavaScript obligatorio y fácil de alojar.
- **Plataforma interna:** `app.dicprom.com` o `crm.dicprom.com`, con CRM, panel y asistente. Debe llevar `noindex` para no competir con el sitio público.
- **Integración:** apuntar `formEndpoint` a un endpoint del CRM que acepte POST con los campos `nombre`, `empresa`, `telefono`, `email`, `servicio`, `provincia` y `mensaje`. Así las cotizaciones entran directo al CRM y WhatsApp queda como respaldo.

---

## 15. Compilar y publicar

```bash
python3 tools/import_assets.py   # (solo si cambian el logotipo o las fotos) genera logos, iconos, OG y WebP
python3 build.py                 # genera dist/
python3 tools/check.py           # auditoría SEO: JSON-LD, enlaces, H1, títulos, datos pendientes
cd dist && python3 -m http.server 8080   # vista previa local
```

Subir **el contenido de `dist/`** a la raíz del hosting.

- **Cloudflare Pages / Netlify:** directorio de publicación `dist`. Comando: `python3 build.py`, con Pillow disponible.
- **cPanel / Apache:** subir `dist/*` a `public_html`, incluido `.htaccess`.
- **Nginx:**
  - Usar `try_files $uri $uri/ =404; error_page 404 /404.html;`.
  - Redirigir con 301 `www` y `http` a `https://dicprom.com`.

Después de cada publicación, reenviar el sitemap en Search Console y en Bing, y notificar a IndexNow:

```bash
curl "https://api.indexnow.org/indexnow?url=https://dicprom.com/&key=<indexNowKey>"
```
