# DISPRON GROUP · dicprom.com

Sitio web estático de DISPRON GROUP (ingeniería, construcción y mantenimiento industrial – Panamá), optimizado para SEO local y GEO (motores de IA).

- `data/site.json` – datos de la empresa (NAP, dominio, verificaciones). **Completar antes de publicar.**
- `data/content.py` – textos de servicios, FAQ, cobertura y fotografías asignadas a cada servicio.
- `build.py` – generador → `dist/` (HTML + JSON-LD + sitemap de imágenes + robots + llms.txt).
- `tools/check.py` – auditoría SEO técnica.
- `tools/import_assets.py` – genera logotipos transparentes, favicon, iconos, imagen OG y fotos WebP a partir de `assets-src/` y de la carpeta de fotos DISPRON.
- `static/` – CSS, JS, fuentes, imágenes, `.htaccess`, `_headers`, `_redirects`.

```bash
python3 build.py && python3 tools/check.py
cd dist && python3 -m http.server 8080
```

Requiere Python 3.10+ y Pillow (y NumPy para `tools/import_assets.py`).

Ver `PLAN-COMPLETO.md` para el diseño, la estrategia SEO/GEO, la hoja de ruta y el checklist de publicación.
