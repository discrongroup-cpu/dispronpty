# DISPRON GROUP · dicprom.com

Plataforma web de DISPRON GROUP (ingeniería, construcción y mantenimiento industrial – Panamá): sitio corporativo optimizado para SEO local y GEO (motores de IA) más cotizador, asistente Sofía, CRM comercial y Alfred (centro de mando con 12 agentes y 30 herramientas).

## Estructura

- `data/site.json` – datos de la empresa (NAP, dominio, verificaciones). **Completar antes de publicar.**
- `data/content.py` – 16 servicios, FAQ, cobertura y fotos por servicio.
- `data/platform.json` – blog (25 artículos), sectores, guías, proceso y provincias (exportado con `tools/export_platform.js`).
- `data/gallery.py` – clasificación de las 171 fotografías reales de obra.
- `build.py` – generador → `dist/` (58 URL indexables + páginas de aplicación, JSON-LD, sitemap de imágenes, robots, `llms.txt`, `llms-full.txt`, `knowledge.json`) y `server/site-data.json` para Alfred.
- `server/` – servidor Node/Express: sirve `dist/` y la API (leads, autenticación, usuarios, CRM, CSV, Sofía, Alfred).
- `static/` – CSS, JS (`main`, `quote`, `sofia`, `auth`, `crm`, `alfred`), fuentes e imágenes.
- `tools/check.py` – auditoría SEO técnica · `tools/api-test.js` – pruebas de API · `tools/smoke.py` – prueba en navegador (Playwright, escritorio y móvil).

## Uso

```bash
python3 build.py && python3 tools/check.py   # genera y audita dist/
npm install
npm test                                      # 60 pruebas de API, seguridad y Alfred
PORT=8000 DATA_DIR=/var/lib/dispron FORCE_HTTPS=1 npm start
python3 tools/smoke.py http://127.0.0.1:8000  # opcional
```

Requiere Python 3.10+ con Pillow (NumPy para `tools/import_assets.py`) y Node 20+.

- El primer usuario registrado en `/acceso/` queda como administrador; los siguientes quedan pendientes de aprobación.
- `DATA_DIR` guarda `db.json` y las propuestas; debe estar fuera del repositorio y con respaldo.
- Sin Node, `dist/` puede publicarse como sitio estático: los formularios y Sofía pasan a WhatsApp.

Ver `PLAN-COMPLETO.md` para el diseño, la estrategia SEO/GEO, la hoja de ruta y el checklist de publicación.
