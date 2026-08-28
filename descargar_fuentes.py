"""
descargar_fuentes.py -- Baja las tipografias del sitio y arma fuentes/fig.css.

Por que
--------
Las 14 paginas pedian las 3 familias (12 variantes) a fonts.googleapis.com en
cada carga. Eso cuesta:

  - **render bloqueado**: el <link> a Google es una hoja de estilos, o sea
    bloquea la primera pintada, y antes hay que resolver DNS + TLS de DOS
    dominios nuevos (fonts.googleapis.com para el CSS y fonts.gstatic.com para
    los .woff2). En el 4G de la facultad eso son varios cientos de ms antes de
    que aparezca la primera letra;
  - **privacidad**: cada visita le manda la IP del visitante a Google sin que
    nadie lo haya consentido, en un sitio que no pone ni una cookie;
  - **una dependencia externa** para algo que son 12 archivos estaticos.

Autoalojarlas no rompe la regla de "sin build step": son archivos sueltos que
GitHub Pages sirve igual que una imagen, y el CSS se escribe una vez.

Las tres familias son libres y se pueden redistribuir: Playfair Display e IBM
Plex Mono estan bajo SIL Open Font License 1.1 e Inter bajo la misma OFL. Por
eso el script deja tambien fuentes/LICENCIAS.txt.

Que hace
---------
1. Le pide a Google el CSS de la MISMA URL que tenian las paginas, con un
   User-Agent moderno para que responda woff2 (con uno viejo devuelve ttf).
2. Baja cada .woff2 a fuentes/.
3. Escribe fuentes/fig.css con las mismas reglas @font-face pero apuntando a
   los archivos locales, conservando `unicode-range` -- importante: gracias a
   eso el navegador NO baja el subconjunto latin-ext salvo que la pagina use
   un caracter que lo necesite.

Solo se guardan los subconjuntos LATIN y LATIN-EXT. Google sirve ademas
cirilico, griego y vietnamita: con `unicode-range` no costarian nada en
tiempo de carga (el navegador ni los pide), pero son 63 archivos y 543 KB
versus 24 y ~250 KB, todo eso versionado para siempre en un sitio escrito
integramente en espanol. Si algun dia hay que escribir un nombre en griego,
se agrega el subconjunto a SUBCONJUNTOS y se vuelve a correr.

Uso:
    python descargar_fuentes.py

Es idempotente: vuelve a bajar y reescribe. Correrlo solo si se agrega un peso
o una familia nueva (y ahi hay que actualizar tambien URL_FUENTES aca abajo).
"""

from __future__ import annotations
import pathlib
import re
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent
SALIDA = RAIZ / "fuentes"

# EXACTAMENTE la misma familia/pesos que pedian las paginas.
URL_FUENTES = (
    "https://fonts.googleapis.com/css2"
    "?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600"
    "&family=Inter:wght@400;500;600;700"
    "&family=IBM+Plex+Mono:wght@400;500;600"
    "&display=swap"
)

# Sin un UA moderno, Google devuelve @font-face con .ttf en vez de .woff2
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Google rotula cada @font-face con un comentario /* <subconjunto> */ justo
# encima. Nos quedamos solo con estos.
SUBCONJUNTOS = ("latin", "latin-ext")

LICENCIAS = """Tipografias de este sitio -- todas libres, redistribuibles.

  Playfair Display  SIL Open Font License 1.1  https://fonts.google.com/specimen/Playfair+Display
  Inter             SIL Open Font License 1.1  https://fonts.google.com/specimen/Inter
  IBM Plex Mono     SIL Open Font License 1.1  https://fonts.google.com/specimen/IBM+Plex+Mono

Los .woff2 y fig.css de esta carpeta los genera descargar_fuentes.py desde
Google Fonts. No editarlos a mano: se reescriben enteros.
"""


def filtrar_subconjuntos(css: str) -> str:
    """Deja solo los bloques @font-face de los subconjuntos que usamos."""
    bloques = re.split(r"(?=/\*\s*[a-z0-9-]+\s*\*/)", css)
    salida = []
    for b in bloques:
        m = re.match(r"/\*\s*([a-z0-9-]+)\s*\*/", b.strip())
        if m and m.group(1) not in SUBCONJUNTOS:
            continue
        if b.strip():
            salida.append(b.rstrip())
    return "\n".join(salida) + "\n"


def bajar(url: str) -> bytes:
    pedido = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(pedido, timeout=60) as r:
        return r.read()


def main() -> int:
    SALIDA.mkdir(exist_ok=True)
    print("Pidiendo el CSS a Google Fonts...")
    css = bajar(URL_FUENTES).decode("utf-8")
    css = filtrar_subconjuntos(css)

    urls = sorted(set(re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)))
    if not urls:
        print("ERROR: Google no devolvio ningun .woff2. ¿Cambio el formato del CSS?")
        return 1
    print(f"{len(urls)} archivos de fuente a bajar.")

    mapa: dict[str, str] = {}
    total = 0
    for u in urls:
        # el nombre que da Google no dice nada (v30/xxxx.woff2); se arma uno legible
        nombre = u.rsplit("/", 2)
        legible = f"{nombre[-2]}-{nombre[-1]}".replace("/", "-")
        datos = bajar(u)
        (SALIDA / legible).write_bytes(datos)
        mapa[u] = legible
        total += len(datos)
        print(f"  {legible}  ({len(datos)/1024:.0f} KB)")

    local = css
    for u, nombre in mapa.items():
        local = local.replace(u, nombre)

    cabecera = (
        "/* GENERADO por descargar_fuentes.py -- no editar a mano.\n"
        "   Mismas @font-face que servia Google Fonts, apuntando a los .woff2\n"
        "   de esta carpeta. Se conserva unicode-range: gracias a eso el\n"
        "   navegador solo baja el subconjunto que la pagina realmente usa\n"
        "   (en la practica, latin; latin-ext casi nunca se pide).\n"
        "   Licencias en LICENCIAS.txt de esta misma carpeta. */\n"
    )
    (SALIDA / "fig.css").write_text(cabecera + local, encoding="utf-8")
    (SALIDA / "LICENCIAS.txt").write_text(LICENCIAS, encoding="utf-8")

    caras = local.count("@font-face")
    print(f"\nOK: fuentes/fig.css con {caras} @font-face, {total/1024:.0f} KB en .woff2")
    print("Las paginas deben enlazar fuentes/fig.css (o ../fuentes/fig.css) en vez")
    print("de fonts.googleapis.com -- lo hace usar_fuentes_locales.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
