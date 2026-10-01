# dicprom.com

Sitio web estático de DICPROM (ingeniería, construcción y mantenimiento industrial – Panamá), optimizado para SEO local y GEO (motores de IA).

- `data/site.json` – datos de la empresa (NAP). **Completar antes de publicar.**
- `data/content.py` – textos de servicios, FAQ, cobertura.
- `build.py` – generador → `dist/` (HTML + JSON-LD + sitemap + robots + llms.txt).
- `tools/check.py` – auditoría SEO técnica. `tools/make_images.py` – logo, iconos e imagen OG.
- `static/` – CSS, JS, imágenes, `.htaccess`, `_headers`, `_redirects`.

```bash
python3 build.py && python3 tools/check.py
cd dist && python3 -m http.server 8080
```

Ver `SEO-TECNICO.md` para la estrategia completa y el checklist de publicación.
