"""Genera los íconos de las apps "FIG Directivos" (una por área), a partir de
logos/fig-oro.png sobre el color de esa área en vez del navy general, con un
anillo del color de acento del área para distinguirlas del ícono público.

Salida en directivos/<area>/iconos/: mismos 4 archivos que generar_iconos_app.py
(icono-192, icono-512, icono-mascara-512, apple-touch-icon).

Agregar un área nueva = sumar una entrada a AREAS.

Uso: python generar_iconos_directivos.py [area]   (todas si se omite)
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent
LOGOS = {}


def logo(nombre):
    if nombre not in LOGOS:
        img = Image.open(RAIZ / "logos" / nombre).convert("RGBA")
        LOGOS[nombre] = img.crop(img.getbbox())
    return LOGOS[nombre]


# Los colores viven en directivos/areas.json (los mismos que usa la app
# abierta, vía generar_apps_directivos.py). Elegidos por Francisco probándolos
# en vivo en el artefacto "Íconos de FIG Directivos": toro blanco en todas.
def _rgba(hexa):
    h = hexa.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


AREAS = {
    carpeta: {"fondo": _rgba(a["fondo"]), "acento": _rgba(a["acento"]), "logo": a.get("logo", "fig-blanco.png")}
    for carpeta, a in json.loads((RAIZ / "directivos" / "areas.json").read_text(encoding="utf-8"))["areas"].items()
}


def icono(area, fondo, acento, logo_img, lado, fraccion, nombre):
    lienzo = Image.new("RGBA", (lado, lado), fondo)
    d = round(lado * fraccion)
    l = logo_img.resize((d, d), Image.LANCZOS)
    lienzo.alpha_composite(l, ((lado - d) // 2, (lado - d) // 2))
    ancho_anillo = max(2, round(lado * 0.035))
    margen = ancho_anillo
    ImageDraw.Draw(lienzo).ellipse(
        [margen, margen, lado - margen, lado - margen], outline=acento, width=ancho_anillo
    )
    salida = RAIZ / "directivos" / area / "iconos"
    salida.mkdir(parents=True, exist_ok=True)
    lienzo.convert("RGB").save(salida / nombre, optimize=True)
    print(f"  directivos/{area}/iconos/{nombre}  {lado}px")


def generar(area):
    cfg = AREAS[area]
    l = logo(cfg["logo"])
    icono(area, cfg["fondo"], cfg["acento"], l, 192, 0.80, "icono-192.png")
    icono(area, cfg["fondo"], cfg["acento"], l, 512, 0.80, "icono-512.png")
    icono(area, cfg["fondo"], cfg["acento"], l, 512, 0.62, "icono-mascara-512.png")
    icono(area, cfg["fondo"], cfg["acento"], l, 180, 0.76, "apple-touch-icon.png")


if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(AREAS)
    for a in pedidas:
        if a not in AREAS:
            print(f"área desconocida: {a} (opciones: {', '.join(AREAS)})")
            sys.exit(1)
        generar(a)
