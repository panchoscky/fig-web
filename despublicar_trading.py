# -*- coding: utf-8 -*-
"""
despublicar_trading.py -- Saca el area Trading del ESPEJO.

Por que existe
---------------
Francisco aviso (2026-09-10) que la pagina de Trading **todavia no debe estar
publicada en el sitio oficial**. El 10-sep se sincronizo el espejo con los 15
commits acumulados de fig-web y eso subio a produccion, sin querer, la tanda
del 4-sep: la paleta XTB, la cinta de clubes invitados y -- lo mas sensible --
el Alpha Trading Challenge 2026 declarado ACTIVO con fechas concretas
(inscripciones 21-sep al 4-oct, torneo 14-oct al 6-nov) en `datos/trading.json`.
El torneo no tiene bases formales todavia.

Mismo patron que `despublicar_fiw.py` y por la misma razon: va como paso APARTE
despues de `sincronizar_espejo.py`, no como una lista de excepciones adentro de
el. Si `trading/` quedara en NO_SE_COPIAN, el espejo dejaria de recibir para
siempre las mejoras del area; asi en cambio recibe todo y despues se le quita.

Es idempotente: correrlo dos veces sobre el mismo espejo no cambia nada la
segunda vez.

Uso
----
    python sincronizar_espejo.py --aplicar
    python despublicar_fiw.py --aplicar        # el par de siempre
    python despublicar_trading.py              # revisa y reporta, no escribe
    python despublicar_trading.py --aplicar
    cd ../mpazq-afk.github.io && python generar_sitemap.py

COMO SE REVIERTE (cuando Trading SI pueda publicarse)
------------------------------------------------------
Se deja de correr este script y se corre `sincronizar_espejo.py --aplicar`:
el area vuelve entera, porque la fuente de verdad sigue intacta en fig-web.
Este script nunca toca fig-web, solo el espejo.

LO QUE ESTE SCRIPT NO TOCA, A PROPOSITO
----------------------------------------
1. **El chip TRD del selector de desks y su panel.** El desk sigue a la vista,
   pero como `<button>` sin enlace, igual que ADM. NO se borra, y la razon es
   concreta: `data-desk` y `data-view` se emparejan **por orden**, asi que
   sacar el bloque correria la numeracion de Valuation y Administracion y
   dejaria el selector mostrando el panel equivocado. Mismo criterio que ya
   usaba FIW.
2. **El numero de areas.** El sitio dice "cinco desks" en los dos repos
   (decision de Francisco, 2026-09-03) y eso no cambia porque un area no sea
   accesible -- es exactamente el trato que ya tiene FIW.
3. **El nombre "Trading" en el cargo de Manuel Paz** (`datos/club.json`:
   "Director - Trading"). Es el cargo de una persona real, no una seccion del
   sitio. Mismo criterio que las tres cofundadoras de FIW.
4. **Nada que diga "XTB" fuera de trading/.** Ya no queda: las menciones de
   `en/index.html` y `datos/club.json` -- que eran anteriores al 2026-09-02 y
   por eso este script nunca las agarro -- se sacaron de fig-web el 2026-09-11,
   a pedido de Francisco. Se saco la frase del sponsor y la fila "Trading
   Tournament | XTB" de la seccion Partners; la descripcion del torneo quedo,
   sin nombrar al auspiciador. Como se hizo en la FUENTE, vale para los dos
   sitios: fig-web tambien esta publicado, en panchoscky.github.io/fig-web.
5. **Los comentarios de codigo** que nombran trading/ como referencia tecnica
   (portafolio/ y valuation/ lo citan para explicar que comparten plantilla).
   No se ven en pantalla.
"""

from __future__ import annotations
import argparse
import pathlib
import sys

ORIGEN = pathlib.Path(__file__).resolve().parent
ESPEJO = ORIGEN.parent / "mpazq-afk.github.io"

# Marcas de que el archivo TODAVIA publica el area. Solo enlaces navegables:
# la palabra "Trading" suelta sigue apareciendo con razon en el cargo de Manuel,
# en el chip TRD y en los comentarios de codigo.
RASTROS_DEL_AREA = (
    'href="trading/index.html"',
    'href="../trading/index.html"',
)

BORRAR = [
    ("trading", "la pagina del area: mientras exista, /trading/ responde por URL directa"),
    ("datos/trading.json", "solo la usa esa pagina, y trae las fechas del torneo sin bases"),
    ("logos/clubes-trading", "los logos de la cinta de clubes invitados al torneo"),
]

# (archivo, [(buscar, reemplazar, obligatorio)])
EDICIONES = [
("index.html", [
    # Nav de escritorio: el dropdown "Areas"
    ("""          <a href="trading/index.html">Trading</a>
""", "", True),
    # Nav movil
    ("""  <a href="trading/index.html">Trading</a>
""", "", True),
    # Chip del selector: de <a> con enlace a <button> sin enlace, como ADM.
    # El data-desk NO cambia: la numeracion es posicional.
    ("""        <a class="desk-item" role="tab" aria-selected="false" data-desk="1"
           href="trading/index.html" aria-label="Trading — ir a la página del área">
          <span class="di-code">TRD</span><span class="di-name">Trading</span><span class="di-arrow">→</span>
        </a>
""",
     """        <button class="desk-item" role="tab" aria-selected="false" data-desk="1">
          <span class="di-code">TRD</span><span class="di-name">Trading</span><span class="di-arrow">→</span>
        </button>
""", True),
    # "Conocer el area" del panel 02. El panel se queda: describe al desk, no
    # al torneo.
    ("""          <a href="trading/index.html" class="a-link">Conocer el área <span class="arr">→</span></a>
          <div class="dp-bar"><i></i></div>
        </div>
        <div class="dp-view" data-view="2" role="tabpanel">
""",
     """          <div class="dp-bar"><i></i></div>
        </div>
        <div class="dp-view" data-view="2" role="tabpanel">
""", True),
    # Footer: queda el nombre, apuntando al selector de areas, como ADM
    ("""          <li><a href="trading/index.html">Trading</a></li>
""",
     """          <li><a href="#areas">Trading</a></li>
""", True),
]),
("portafolio/index.html", [
    ("""          <a href="../trading/index.html">Trading</a>
""", "", True),
    ("""  <a href="../trading/index.html">Trading</a>
""", "", True),
]),
("valuation/index.html", [
    ("""          <a href="../trading/index.html">Trading</a>
""", "", True),
    ("""  <a href="../trading/index.html">Trading</a>
""", "", True),
]),
]


def escribir_conservando_fin_de_linea(f: pathlib.Path, nuevo: str) -> None:
    """El espejo esta en CRLF y fig-web en LF. Si se escribe en LF, el archivo
    sale como si hubieran cambiado sus 3.000 lineas y el cambio real queda
    invisible en el diff."""
    datos = nuevo.encode("utf-8")
    previo = f.read_bytes()
    if previo.count(b"\r\n") == previo.count(b"\n") and previo.count(b"\n"):
        datos = datos.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    f.write_bytes(datos)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe de verdad; sin esto solo reporta")
    args = ap.parse_args()

    if not ESPEJO.exists():
        print(f"No encuentro el espejo en {ESPEJO}")
        return 1

    # Las reglas se validan contra el ORIGEN, no contra el espejo: si el HTML de
    # fig-web cambio, la regla quedo escrita contra una version que ya no existe
    # y hay que arreglarla ACA antes de que se aplique a produccion a medias.
    desalineadas = []
    for arch, reglas in EDICIONES:
        f = ORIGEN / arch
        if not f.exists():
            desalineadas.append(f"{arch}: no existe en el origen")
            continue
        texto = f.read_text(encoding="utf-8")
        for buscar, _reemplazar, obligatorio in reglas:
            if obligatorio and buscar not in texto:
                desalineadas.append(f"{arch}: la regla ya no calza -> {buscar.strip()[:70]}")
    if desalineadas:
        print("REGLAS DESALINEADAS con el HTML de este repo (arreglar EDICIONES):")
        for x in desalineadas:
            print(f"  {x}")
        return 1

    acciones, faltantes = [], []

    for rel, motivo in BORRAR:
        destino = ESPEJO / rel
        # Una carpeta VACIA no cuenta como publicada: git no la versiona y el
        # servidor no la sirve. OneDrive suele bloquear el rmdir final, asi que
        # sin esto el script reportaria "borrar trading/" para siempre.
        if destino.is_dir():
            if any(destino.rglob("*")):
                acciones.append(("borrar", rel, motivo))
        elif destino.exists():
            acciones.append(("borrar", rel, motivo))

    for arch, reglas in EDICIONES:
        f = ESPEJO / arch
        if not f.exists():
            faltantes.append(arch)
            continue
        texto = f.read_text(encoding="utf-8")
        nuevo = texto
        for buscar, reemplazar, obligatorio in reglas:
            if buscar in nuevo:
                nuevo = nuevo.replace(buscar, reemplazar)
            elif obligatorio and any(m in texto for m in RASTROS_DEL_AREA):
                faltantes.append(f"{arch}: no encontre -> {buscar.strip()[:70]}")
        if nuevo != texto:
            acciones.append(("editar", arch, f"{len(texto) - len(nuevo)} bytes menos"))
            if args.aplicar:
                escribir_conservando_fin_de_linea(f, nuevo)

    if args.aplicar:
        for rel, _ in BORRAR:
            destino = ESPEJO / rel
            if not destino.exists():
                continue
            # Primero los ARCHIVOS y despues la carpeta: si OneDrive tiene el
            # directorio bloqueado, lo de adentro ya se fue, que es lo que
            # importa -- una carpeta vacia no se sirve ni git la versiona.
            if destino.is_dir():
                for hijo in sorted(destino.rglob("*"), reverse=True):
                    try:
                        hijo.unlink() if hijo.is_file() else hijo.rmdir()
                    except OSError as e:
                        print(f"  aviso: no pude borrar {hijo}: {e}")
                try:
                    destino.rmdir()
                except OSError as e:
                    print(f"  aviso: la carpeta {rel} quedo (vacia): {e}")
            else:
                destino.unlink()

    if faltantes:
        print("NO ENCONTRE en el espejo (revisar a mano):")
        for x in faltantes:
            print(f"  {x}")
        print()

    if not acciones:
        print("Nada que hacer: el espejo ya no publica Trading.")
        return 0

    print("APLICADO:" if args.aplicar else "SE HARIA (corre con --aplicar):")
    for verbo, rel, motivo in acciones:
        print(f"  {verbo:7} {rel:28} {motivo}")

    if args.aplicar:
        print()
        print("Ahora corre, DENTRO del espejo:  python generar_sitemap.py")
        print("(para que /trading/ deje de estar declarada en sitemap.xml)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
