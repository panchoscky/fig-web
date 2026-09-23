"""Conecta las páginas públicas a la app instalable (manifest + service worker).

Agrega en el <head> el enlace al manifiesto y el ícono de iPhone, y antes de
</body> el registro del service worker. Es idempotente: una página que ya
tiene `rel="manifest"` se salta. Aborta sin escribir nada si alguna página
no tiene exactamente un </head> y un </body>.

Quedan fuera a propósito: 404.html (se sirve desde cualquier ruta y los
enlaces relativos apuntarían mal), torneo/e/ (solo redirigen al ranking), los
documentos internos (GUIA_DRIVE_FIG, MAPA_CONTENIDO_FIG) y estudio-personal/,
que no es contenido del club.

Uso: python aplicar_pwa.py            (muestra qué haría)
     python aplicar_pwa.py --aplicar  (escribe)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PAGINAS = [
    "index.html", "desafio/index.html", "en/index.html",
    "eventos/index.html", "fiw/index.html", "informe/index.html",
    "en/informe/index.html", "juego/index.html", "miembros/index.html",
    "portafolio/index.html", "postula/index.html", "torneo/index.html",
    "torneo/pantalla.html", "torneo/pantalla-facultad.html",
    "trading/index.html", "valuation/index.html",
]

CABEZA = """<link rel="manifest" href="{r}manifest.webmanifest">
<link rel="apple-touch-icon" href="{r}iconos/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="FIG">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
</head>"""

PIE = """<script>if("serviceWorker" in navigator){{addEventListener("load",function(){{navigator.serviceWorker.register("{r}sw.js").catch(function(){{}});}});}}</script>
</body>"""


def main():
    aplicar = "--aplicar" in sys.argv
    cambios, saltadas = {}, []
    for rel in PAGINAS:
        ruta = RAIZ / rel
        with open(ruta, encoding="utf-8", newline="") as f:
            texto = f.read()
        if 'rel="manifest"' in texto:
            saltadas.append(rel)
            continue
        # Solo cuentan las etiquetas que abren su propia línea: torneo/index.html
        # trae otro </head></body> dentro de un string de JS que arma una imagen.
        eol = "\r\n" if "\r\n" in texto else "\n"
        th, tb = eol + "</head>", eol + "</body>"
        n_head, n_body = texto.count(th), texto.count(tb)
        assert n_head == 1 and n_body == 1, f"{rel}: {n_head} </head> y {n_body} </body> en línea propia, se esperaba 1 y 1"
        r = "../" * rel.count("/")
        nuevo = (texto.replace(th, eol + CABEZA.format(r=r).replace("\n", eol), 1)
                      .replace(tb, eol + PIE.format(r=r).replace("\n", eol), 1))
        cambios[rel] = nuevo

    for rel in saltadas:
        print(f"  = {rel} (ya conectada)")
    for rel in cambios:
        print(f"  + {rel}")
    if not aplicar:
        print(f"\n{len(cambios)} páginas por conectar. Nada escrito: agrega --aplicar.")
        return
    for rel, nuevo in cambios.items():
        # newline="" conserva el fin de línea que ya tenía cada archivo.
        with open(RAIZ / rel, "w", encoding="utf-8", newline="") as f:
            f.write(nuevo)
    print(f"\n{len(cambios)} páginas conectadas.")


if __name__ == "__main__":
    main()
