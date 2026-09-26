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


# Mismo dibujo que el artefacto donde Francisco eligió los colores: cuadrado de
# esquinas redondeadas (radio 22,6 %, el de iOS), marco del acento PEGADO AL
# BORDE siguiendo esas esquinas (7 % de grosor) y el toro al 66 %. Hasta el
# 25-sep el marco era un círculo alrededor del toro, que no era lo elegido.
RADIO, GROSOR, TORO = 0.226, 0.071, 0.66
X = 4   # se dibuja 4x más grande y se reduce: bordes del marco sin serrucho


def icono(area, cfg, logo_img, lado, nombre, modo):
    """modo "any": fuera del cuadrado redondeado queda transparente (así se ve en
    Chrome/escritorio igual que en el artefacto). "apple": opaco, iOS recorta
    solo con esas mismas esquinas. "mascara": Android recorta con la forma de
    cada teléfono (círculo, gota…), así que el ícono entero se achica al 76 %
    para que el marco completo quepa incluso en un recorte circular."""
    G = lado * X
    escala = 0.76 if modo == "mascara" else 1.0
    t = round(G * escala)
    o = (G - t) // 2
    capa = Image.new("RGBA", (G, G), (0, 0, 0, 0) if modo == "any" else cfg["fondo"])
    dib = ImageDraw.Draw(capa)
    r, g = round(t * RADIO), round(t * GROSOR)
    dib.rounded_rectangle([o, o, o + t - 1, o + t - 1], radius=r, fill=cfg["acento"])
    dib.rounded_rectangle([o + g, o + g, o + t - 1 - g, o + t - 1 - g], radius=max(1, r - g), fill=cfg["fondo"])
    d = round(t * TORO)
    capa.alpha_composite(logo_img.resize((d, d), Image.LANCZOS), ((G - d) // 2, (G - d) // 2))
    final = capa.resize((lado, lado), Image.LANCZOS)
    salida = RAIZ / "directivos" / area / "iconos"
    salida.mkdir(parents=True, exist_ok=True)
    (final if modo == "any" else final.convert("RGB")).save(salida / nombre, optimize=True)
    print(f"  directivos/{area}/iconos/{nombre}  {lado}px")


def generar(area):
    cfg = AREAS[area]
    l = logo(cfg["logo"])
    icono(area, cfg, l, 192, "icono-192.png", "any")
    icono(area, cfg, l, 512, "icono-512.png", "any")
    icono(area, cfg, l, 512, "icono-mascara-512.png", "mascara")
    icono(area, cfg, l, 180, "apple-touch-icon.png", "apple")


if __name__ == "__main__":
    pedidas = sys.argv[1:] or list(AREAS)
    for a in pedidas:
        if a not in AREAS:
            print(f"área desconocida: {a} (opciones: {', '.join(AREAS)})")
            sys.exit(1)
        generar(a)
