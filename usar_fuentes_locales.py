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

EL PRELOAD: MEDIDO Y DESCARTADO (2026-08-28)
---------------------------------------------
    NO uses --preload en este sitio. Se probo y sale PEOR. El modo queda
    porque el resultado no es obvio y sin esta nota alguien lo va a volver
    a intentar.

Medido en Chrome emulando 4G lento (1.6 Mbps) y CPU 4x, cuatro corridas por
variante sobre la portada, mediana de la primera pintada:

    sin preload            856 ms   (dos corridas en 600 ms)
    solo el titular       1768 ms
    las tres criticas     1684 ms

O sea que precargar UNA sola fuente ya cuesta casi un segundo. El motivo es
particular de este sitio: cada pagina es un HTML monolitico de 150 KB con
TODO su CSS adentro, asi que la primera pintada depende de que ese archivo
termine de llegar. El `<link rel=preload>` lo descubre el parser a mitad de
la descarga y se pone a competir por el mismo ancho de banda que le falta al
HTML. En un sitio con hoja de estilos aparte el calculo daria distinto.

Lo que se pierde al no precargarlas es solo el salto de tipografia: con
`font-display: swap` el texto se lee desde el primer momento con la fuente
del sistema y cambia a la buena cuando llega. Un segundo de pantalla en
blanco es peor que un cambio de tipografia a los 900 ms.

Como estaba antes de esta nota
-------------------------------
Autoalojarlas quito los dos dominios ajenos, pero dejo una cadena de tres
pasos igual de bloqueante: el navegador baja el HTML, ahi descubre
`fuentes/fig.css`, lo baja y lo parsea, y RECIEN ahi se entera de que existe
un .woff2 que pedir. Con `font-display: swap` eso no deja la pagina en blanco
— se pinta con la tipografia del sistema y salta a la buena despues —, pero
ese salto es visible y cae justo sobre el titular del hero.

`--preload` agrega un `<link rel="preload" as="font">` por cada una de las
TRES variantes que aparecen en la primera pantalla de cualquier pagina del
sitio: Playfair normal (los titulares), Playfair italica (la palabra dorada
que todos los heroes llevan en cursiva) e Inter regular (el parrafo). Asi se
piden en paralelo con la hoja de estilos en vez de despues de ella.

Las otras nueve variantes NO se precargan a proposito: `unicode-range` y
`font-display` ya las traen cuando hacen falta, y precargar de mas compite por
ancho de banda con lo que si esta en pantalla. `crossorigin` es obligatorio
aunque el archivo sea del mismo origen — las fuentes se piden en modo CORS y
sin ese atributo el navegador baja el archivo DOS veces.

Uso:
    python usar_fuentes_locales.py            # revisa y reporta
    python usar_fuentes_locales.py --aplicar  # escribe
    python usar_fuentes_locales.py --preload --aplicar   # + los preload

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


# Las tres variantes que se ven en la primera pantalla de cualquier pagina.
# Los nombres los fija descargar_fuentes.py; si se regeneran las fuentes hay
# que revisar que sigan siendo estos (el script avisa si alguno no existe).
CRITICAS = [
    ("v40-nuFiD-vYSZviVYUb_rj3ij__anPXDTzYgA.woff2", "Playfair Display, titulares"),
    ("v40-nuFkD-vYSZviVYUb_rj3ij__anPXDTnogkk7.woff2", "Playfair Display italica, la palabra dorada del hero"),
    ("v20-UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2", "Inter, el cuerpo de texto"),
]
MARCA_PRELOAD = "<!-- Adelanto de las tres variantes"


def bloque_preload(prefijo: str) -> str:
    """Los <link rel=preload> que van JUSTO ANTES de la hoja de estilos."""
    lineas = [f'{MARCA_PRELOAD} que se ven en la primera pantalla: sin esto el',
              '     navegador no sabe que existen hasta haber bajado y parseado fig.css.',
              '     `crossorigin` es obligatorio aunque sean del mismo origen. -->']
    for archivo, para_que in CRITICAS:
        lineas.append(f'<link rel="preload" as="font" type="font/woff2" crossorigin '
                      f'href="{prefijo}fuentes/{archivo}">  <!-- {para_que} -->')
    return "\n".join(lineas) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="escribe los cambios")
    ap.add_argument("--preload", action="store_true",
                    help="ademas, adelanta las 3 fuentes criticas con <link rel=preload>")
    args = ap.parse_args()

    if args.preload:
        faltan = [a for a, _ in CRITICAS if not (RAIZ / "fuentes" / a).exists()]
        if faltan:
            print("Estos .woff2 no existen en fuentes/ -- revisa CRITICAS:")
            for f in faltan:
                print("   ", f)
            return 1

    if not CSS_LOCAL.exists():
        print("Falta fuentes/fig.css -- corre antes: python descargar_fuentes.py")
        return 1

    cambiadas, ya, sin_fuentes, precargadas = [], [], [], []
    for ruta in sorted(RAIZ.rglob("*.html")):
        if ".git" in ruta.parts or (RAIZ / "torneo" / "e") in ruta.parents:
            continue
        texto = ruta.read_text(encoding="utf-8")
        rel = str(ruta.relative_to(RAIZ)).replace("\\", "/")

        if "fuentes/fig.css" in texto and URL_SITIO not in texto:
            # ya migrada: lo unico que puede faltarle es el adelanto
            if args.preload and MARCA_PRELOAD not in texto:
                prefijo = "../" * (len(ruta.relative_to(RAIZ).parts) - 1)
                enlace = f'<link href="{prefijo}fuentes/fig.css" rel="stylesheet">'
                if enlace in texto:
                    precargadas.append(rel)
                    if args.aplicar:
                        ruta.write_text(texto.replace(enlace, bloque_preload(prefijo) + enlace, 1),
                                        encoding="utf-8")
                    continue
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
    for r in precargadas:
        print(f"  {'PRELOAD' if args.aplicar else 'preload a poner'}  {r}")
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
