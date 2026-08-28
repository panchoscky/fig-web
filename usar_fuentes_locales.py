"""
usar_fuentes_locales.py -- Apunta las paginas a fuentes/fig.css en vez de a
Google Fonts.

Reemplaza, en cada .html del sitio, el bloque de tres lineas

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">

por un solo <link> a la hoja local, con la profundidad relativa que le
corresponde a esa pagina (`fuentes/fig.css` en la raiz, `../fuentes/fig.css` en
una subcarpeta). El porque esta en descargar_fuentes.py.

LO QUE NO TOCA, a proposito
----------------------------
1. La tarjeta HTML que `torneo/index.html` genera para descargar (funcion
   `descargarHtml`) lleva su propio <link> a Google Fonts dentro de un string
   de JavaScript. Ese archivo se abre suelto en el computador de quien lo baja,
   donde `../fuentes/` no existe: tiene que seguir pidiendole las fuentes a
   Google para verse bien. Se distingue sola porque usa OTRA URL (menos pesos),
   y este script solo reemplaza la URL completa del sitio.
2. `torneo/e/*.html`, que no usan tipografia propia.

Uso:
    python usar_fuentes_locales.py            # revisa y reporta
    python usar_fuentes_locales.py --aplicar  # escribe

Es idempotente: una pagina ya migrada se salta.
"""

from __future__ import annotations
import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
CSS_LOCAL = RAIZ / "fuentes" / "fig.css"

# La URL EXACTA que usan las paginas del sitio. La tarjeta descargable usa otra
# (menos pesos) y por eso no entra aca.
URL_SITIO = ("https://fonts.googleapis.com/css2"
             "?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600"
             "&family=Inter:wght@400;500;600;700"
             "&family=IBM+Plex+Mono:wght@400;500;600&display=swap")

# preconnect (0..2 lineas) + el link de la hoja, en un solo bloque
PATRON = re.compile(
    r'[ \t]*<link rel="preconnect" href="https://fonts\.googleapis\.com">\n?'
    r'[ \t]*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n?'
    r'[ \t]*<link href="' + re.escape(URL_SITIO) + r'" rel="stylesheet">'
)


def reemplazo_para(ruta: pathlib.Path) -> str:
    profundidad = len(ruta.relative_to(RAIZ).parts) - 1
    prefijo = "../" * profundidad
    return ('<!-- Tipografias autoalojadas: antes esto eran dos preconnect y una\n'
            '     hoja de estilos de fonts.googleapis.com, que bloqueaba la primera\n'
            '     pintada y le mandaba la IP de cada visitante a Google. Las genera\n'
            '     descargar_fuentes.py; no editar fuentes/ a mano. -->\n'
            f'<link href="{prefijo}fuentes/fig.css" rel="stylesheet">')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="escribe los cambios")
    args = ap.parse_args()

    if not CSS_LOCAL.exists():
        print("Falta fuentes/fig.css -- corre antes: python descargar_fuentes.py")
        return 1

    cambiadas, ya, sin_fuentes = [], [], []
    for ruta in sorted(RAIZ.rglob("*.html")):
        if ".git" in ruta.parts or (RAIZ / "torneo" / "e") in ruta.parents:
            continue
        texto = ruta.read_text(encoding="utf-8")
        rel = str(ruta.relative_to(RAIZ)).replace("\\", "/")

        if "fuentes/fig.css" in texto and URL_SITIO not in texto:
            ya.append(rel)
            continue
        if not PATRON.search(texto):
            if URL_SITIO in texto:
                print(f"  OJO {rel}: tiene la URL del sitio pero no el bloque esperado")
            else:
                sin_fuentes.append(rel)
            continue

        nuevo = PATRON.sub(lambda _m: reemplazo_para(ruta), texto, count=1)
        cambiadas.append(rel)
        if args.aplicar:
            ruta.write_text(nuevo, encoding="utf-8")

    print()
    for r in cambiadas:
        print(f"  {'MIGRADA' if args.aplicar else 'a migrar'}  {r}")
    for r in ya:
        print(f"  ya estaba  {r}")
    for r in sin_fuentes:
        print(f"  sin fuentes propias  {r}")

    print(f"\n{len(cambiadas)} pagina(s) {'migradas' if args.aplicar else 'por migrar'}.")
    if cambiadas and not args.aplicar:
        print("Corre de nuevo con --aplicar para escribir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
