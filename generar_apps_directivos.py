"""Escribe la carcasa de cada app "FIG Directivos" a partir de
directivos/areas.json: directivos/<carpeta>/index.html + manifest.webmanifest.

Todo el comportamiento vive en directivos/app.js y app.css (compartidos);
la carcasa solo trae el color del área, su ícono y su manifest, para que cada
área se instale como una app aparte con su propio logo en el teléfono.

Agregar un área o cambiar un color = editar directivos/areas.json y correr:
    python generar_iconos_directivos.py
    python generar_apps_directivos.py
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIR = RAIZ / "directivos"

PLANTILLA = """<!doctype html>
<html lang="es-CL">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<!-- GENERADO por generar_apps_directivos.py desde directivos/areas.json — no editar a mano. -->
<title>FIG Directivos · {nombre}</title>
<meta name="theme-color" content="{fondo}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="iconos/icono-192.png">
<link rel="apple-touch-icon" href="iconos/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="FIG {codigo}">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="stylesheet" href="../app.css">
<style>:root{{--area:{fondo};--acento:{acento}}}</style>
</head>
<body>
<div id="app"><p style="text-align:center;padding:40px;color:#5D6270">Cargando…</p></div>
<noscript><p style="padding:24px">Esta app necesita JavaScript.</p></noscript>
<script>
window.FIG_AREA = {area_js};
window.FIG_AREAS = {areas_js};
</script>
<script src="../app.js"></script>
</body>
</html>
"""


def main():
    cfg = json.loads((DIR / "areas.json").read_text(encoding="utf-8"))["areas"]
    por_codigo = {a["codigo"]: {"nombre": a["nombre"], "carpeta": c} for c, a in cfg.items()}
    for carpeta, a in cfg.items():
        destino = DIR / carpeta
        destino.mkdir(exist_ok=True)
        area_js = json.dumps({"codigo": a["codigo"], "nombre": a["nombre"], "carpeta": carpeta}, ensure_ascii=False)
        (destino / "index.html").write_text(PLANTILLA.format(
            nombre=a["nombre"], codigo=a["codigo"], fondo=a["fondo"], acento=a["acento"],
            area_js=area_js, areas_js=json.dumps(por_codigo, ensure_ascii=False)), encoding="utf-8")
        manifest = {
            "id": "./", "name": f"FIG Directivos · {a['nombre']}", "short_name": f"FIG {a['codigo']}",
            "description": f"App interna de directivos de {a['nombre']}: publicar eventos, fotos y comunicados de FIG.",
            "lang": "es-CL", "dir": "ltr", "start_url": "./", "scope": "./", "display": "standalone",
            "orientation": "portrait", "background_color": "#F4F3EF", "theme_color": a["fondo"],
            "categories": ["business", "productivity"],
            "icons": [
                {"src": "iconos/icono-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                {"src": "iconos/icono-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                {"src": "iconos/icono-mascara-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
            ],
        }
        (destino / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        falta = not (destino / "iconos" / "icono-192.png").exists()
        print(f"  directivos/{carpeta}/  {a['codigo']}  {a['fondo']}+{a['acento']}" + ("  ⚠ faltan íconos" if falta else ""))


if __name__ == "__main__":
    main()
