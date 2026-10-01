"""Auditoría SEO técnica del build: JSON-LD válido, enlaces internos, títulos/descripciones, H1 y datos pendientes."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ld, self.h1, self.title, self._in, self._buf = [], [], 0, "", None, ""
        self.desc = self.canonical = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("link", "script", "img") and (a.get("href") or a.get("src")):
            self.links.append(a.get("href") or a.get("src"))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a["href"]
        if tag == "meta" and a.get("name") == "description":
            self.desc = a["content"]
        if tag == "h1":
            self.h1 += 1
        if tag == "title" or (tag == "script" and a.get("type") == "application/ld+json"):
            self._in, self._buf = tag, ""

    def handle_data(self, data):
        if self._in:
            self._buf += data

    def handle_endtag(self, tag):
        if tag == self._in:
            if tag == "title":
                self.title = self._buf
            else:
                self.ld.append(self._buf)
            self._in = None


def main():
    errors, warns, titles, descs = [], [], {}, {}
    pages = sorted(DIST.rglob("*.html"))
    for f in pages:
        rel = "/" + str(f.relative_to(DIST)).replace("index.html", "")
        p = P()
        p.feed(f.read_text(encoding="utf-8"))
        for raw in p.ld:
            try:
                data = json.loads(raw)
                ids = {n.get("@id") for n in data["@graph"]}
                for ref in re.findall(r'"@id":"([^"]+)"', raw):
                    if ref not in ids and "#service" not in ref and "#logo" not in ref:
                        errors.append(f"{rel}: @id sin nodo {ref}")
            except (json.JSONDecodeError, KeyError) as exc:
                errors.append(f"{rel}: JSON-LD inválido {exc}")
        if rel.endswith("404.html"):
            continue
        if p.h1 != 1:
            errors.append(f"{rel}: {p.h1} etiquetas H1")
        if not 30 <= len(p.title) <= 75:
            warns.append(f"{rel}: título {len(p.title)} caracteres")
        if not 110 <= len(p.desc) <= 165:
            warns.append(f"{rel}: descripción {len(p.desc)} caracteres")
        titles.setdefault(p.title, []).append(rel)
        descs.setdefault(p.desc, []).append(rel)
        if not p.canonical.endswith(rel):
            errors.append(f"{rel}: canonical {p.canonical}")
        for href in p.links:
            if href.startswith("/") and not href.startswith("//"):
                path = href.split("?")[0].split("#")[0]
                target = DIST / path.lstrip("/")
                if path.endswith("/"):
                    target = target / "index.html"
                if not target.exists():
                    errors.append(f"{rel}: enlace roto {href}")
    errors += [f"título duplicado: {v}" for v in titles.values() if len(v) > 1]
    errors += [f"descripción duplicada: {v}" for v in descs.values() if len(v) > 1]
    site = json.loads((DIST.parent / "data" / "site.json").read_text(encoding="utf-8"))
    for k, v in site.items():
        if k.startswith("_"):
            continue
        if "REEMPLAZAR" in json.dumps(v, ensure_ascii=False) or (k == "phone" and "6000-0000" in v):
            warns.append(f"site.json: completar '{k}' con datos reales")
    sm = (DIST / "sitemap.xml").read_text()
    print(f"Páginas HTML: {len(pages)} · URLs en sitemap: {sm.count('<loc>')}")
    for w in warns:
        print("AVISO:", w)
    for er in errors:
        print("ERROR:", er)
    print("Resultado:", "FALLÓ" if errors else "OK")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
