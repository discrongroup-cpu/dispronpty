"""Prueba de humo en navegador (Playwright): python3 tools/smoke.py [base_url]"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
SHOTS = Path(__file__).resolve().parent.parent / "shots"
SHOTS.mkdir(exist_ok=True)
PAGES = ["/", "/servicios/", "/servicios/pisos-pintura-epoxica/", "/proyectos/", "/sectores/", "/blog/",
         "/blog/checklist-mantenimiento-preventivo-anual-edificios-panama/", "/recursos/", "/cotizar/", "/acceso/",
         "/contacto/", "/nosotros/", "/cobertura/", "/preguntas-frecuentes/"]
fails = []


def check(ok, msg):
    print(("  ✓ " if ok else "  ✗ ") + msg)
    if not ok:
        fails.append(msg)


def audit(page, path, tag):
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errs.append(str(e)))
    r = page.goto(BASE + path, wait_until="networkidle")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(400)
    over = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    broken = page.evaluate("[...document.images].filter(i => i.getAttribute('src') && i.complete && i.naturalWidth === 0 && i.loading !== 'lazy').map(i => i.src)")
    check(r.status == 200 and over <= 1 and not broken and not errs,
          f"{tag} {path} status={r.status} overflow={over} broken={len(broken)} errors={errs[:2]}")


with sync_playwright() as p:
    exe = os.environ.get("CHROME_PATH")
    b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    for tag, vp in (("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})):
        ctx = b.new_context(viewport=vp)
        for path in PAGES:
            pg = ctx.new_page()
            audit(pg, path, tag)
            if path in ("/", "/proyectos/", "/cotizar/"):
                pg.evaluate("window.scrollTo(0,0)")
                pg.screenshot(path=str(SHOTS / f"{tag}-{path.strip('/') or 'home'}.png"))
            pg.close()
        ctx.close()

    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    pg.goto(BASE + "/proyectos/", wait_until="networkidle")
    total = pg.locator("#project-grid .g-item:visible").count()
    pg.locator("[data-filter]").nth(1).click()
    pg.wait_for_timeout(300)
    check(0 < pg.locator("#project-grid .g-item:visible").count() < total, f"Filtro de galería ({total} fotos)")

    pg.goto(BASE + "/cotizar/", wait_until="networkidle")
    form = pg.locator("#qform")
    form.locator("[name=service]").select_option(index=1)
    form.locator("[name=description]").fill("Piso epóxico de 400 m2 en almacén")
    form.locator("[data-next]").click()
    form.locator("[name=province]").select_option(index=1)
    form.locator("[data-next]").click()
    form.locator("[name=name]").fill("Prueba Smoke")
    form.locator("[name=phone]").fill("61234567")
    form.locator("[name=email]").fill("smoke@example.com")
    form.locator("[name=consent]").check()
    with pg.expect_response("**/api/leads") as resp:
        form.locator("[type=submit]").click()
    check(resp.value.status in (200, 201), f"Cotizador envía lead (HTTP {resp.value.status})")
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(SHOTS / "cotizador-ok.png"))

    pg.goto(BASE + "/", wait_until="networkidle")
    pg.locator("#sofia-open").click()
    pg.wait_for_timeout(500)
    check(pg.locator("#sofia").is_visible(), "Sofía abre")
    pg.screenshot(path=str(SHOTS / "sofia.png"))

    pg.goto(BASE + "/acceso/", wait_until="networkidle")
    pg.locator(".tabs button[data-t=reg]").click()
    pg.locator("#rn").fill("Admin Smoke")
    pg.locator("#re").fill("admin@example.com")
    pg.locator("#rp").fill("clave-segura-123")
    pg.locator("#rp").press("Enter")
    pg.wait_for_url("**/crm/**", timeout=5000)
    pg.wait_for_timeout(1500)
    check(pg.locator(".lead-c").count() >= 1, "CRM muestra leads tras registro")
    pg.screenshot(path=str(SHOTS / "crm.png"))
    hud = pg.locator("#alf-open")
    if hud.count():
        hud.first.click()
        pg.wait_for_timeout(800)
        pg.screenshot(path=str(SHOTS / "alfred.png"))
    check(hud.count() > 0, "Alfred HUD disponible en CRM")
    b.close()

print(f"\n{'Resultado: OK' if not fails else f'FALLOS: {len(fails)}'}")
sys.exit(1 if fails else 0)
