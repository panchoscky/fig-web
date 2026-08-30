# -*- coding: utf-8 -*-
"""
despublicar_fiw.py -- Saca el area FEN Investment Woman del ESPEJO.

Por que existe
---------------
Francisco pidio (2026-08-30) que desde el repo de Manuel -- el que sirve
feninvestmentgroup.com -- **no se pueda acceder al area de mujeres ni sea
visible**. Hasta ahora solo estaban ocultos los ENLACES (`FIW_TEMP_OCULTO`),
que es otra cosa: la pagina seguia respondiendo en /fiw/, el sitemap se la
declaraba a Google, y el area aparecia a la vista en el selector de desks, en
el formulario de postulacion, en la version en ingles y en el nav del 404.

Va como PASO APARTE despues de `sincronizar_espejo.py` y no como una lista de
excepciones dentro de el, por una razon concreta: si estos archivos quedaran en
NO_SE_COPIAN, el espejo dejaria de recibir TODAS las mejoras futuras de
`eventos/`, `postula/`, `valuation/`, `en/` y `404.html` solo para esconder una
seccion. Asi el espejo sigue recibiendo todo y despues se le quita FIW.

Es idempotente: correrlo dos veces sobre el mismo espejo no cambia nada la
segunda vez.

Uso
----
    python sincronizar_espejo.py --aplicar
    python despublicar_fiw.py              # revisa y reporta, no escribe
    python despublicar_fiw.py --aplicar
    cd ../mpazq-afk.github.io && python generar_sitemap.py

LO QUE ESTE SCRIPT NO TOCA, A PROPOSITO
----------------------------------------
1. **Los cargos y biografias de las tres cofundadoras.** Delia Avilan, Gabriela
   Dominguez y Victoria Espinoza figuran en `datos/club.json` como "Co-fundadora
   · FEN Investment Woman", y sus bios cuentan que fundaron el area. Eso no es
   una seccion del sitio: es el merito publico de tres personas reales. Quitar
   un area es una decision de publicacion; reescribirle el curriculum a alguien
   no, y no se hace sin que Francisco lo pida explicitamente. Consecuencia
   honesta: el nombre "FEN Investment Woman" SIGUE siendo visible en la seccion
   Nosotros. Si Francisco quiere eso tambien, hay que decidir con que texto
   quedan las tres, y decidirlo el.
2. **El evento "Encuentro FEN Investment Woman"** del 27-may-2026 en la bitacora
   (`datos/eventos.json`). Es una actividad que ocurrio; borrarla es editar la
   historia del club, no ocultar un area. Se controla con QUITAR_EVENTO, abajo.
3. **Los comentarios de codigo** que nombran fiw/ como referencia tecnica. No
   se ven en pantalla.
"""

from __future__ import annotations
import argparse
import json
import pathlib
import shutil
import sys

ORIGEN = pathlib.Path(__file__).resolve().parent
ESPEJO = ORIGEN.parent / "mpazq-afk.github.io"

# Ponlo en True solo si Francisco pide sacar tambien el evento de la bitacora.
QUITAR_EVENTO = False

# Marcas de que el archivo TODAVIA publica el area como tal. Deliberadamente
# NO incluye el texto "Investment Woman" suelto: eso sigue apareciendo, con
# razon, en el cargo de las tres cofundadoras y en el evento de la bitacora.
RASTROS_DEL_AREA = (
    'fiw/index.html',       # cualquier enlace a la pagina del area
    'data-desk="3"',        # el chip del selector de desks
    'FIW · Comunidad',      # el panel 04
    '>FIW<',                # el nav corto del 404 y de postula
    '<h3>FEN Investment Woman</h3>',   # la tarjeta del one-pager en ingles
)

BORRAR = [
    ("fiw", "la pagina del area: mientras exista, /fiw/ responde por URL directa"),
    ("datos/fiw.json", "solo la usa esa pagina"),
    ("fotos/fiw", "solo las usa esa pagina"),
]

# (archivo, [(buscar, reemplazar, obligatorio)])
# `obligatorio=False` para lo que puede no estar segun como venga el HTML.
EDICIONES = [
("index.html", [
    # Chip del selector de desks (visible, sin enlace pero clicable)
    ("""        <button class="desk-item" role="tab" aria-selected="false" data-desk="3">
          <span class="di-code">FIW</span><span class="di-name">FEN Investment Woman</span><span class="di-arrow">→</span>
        </button>
""", "", True),
    # Panel 04 del area (visible entero)
    ("""        <div class="dp-view" data-view="3" role="tabpanel">
          <span class="dp-num" aria-hidden="true">04</span>
          <span class="mono-tag">FIW · Comunidad</span>
          <h3>Más mujeres en las finanzas</h3>
          <p>La comunidad que impulsa la participación femenina en las finanzas y la inversión, abriendo espacio, referentes y oportunidades dentro de la industria.</p>
          <div class="dp-meta">
            <span class="mono-tag">Fundadora · Delia Avilán</span>
            <span class="mono-tag">Comunidad abierta</span>
          </div>
          <!-- FIW_TEMP_OCULTO <a href="fiw/index.html" class="a-link">Conocer el área <span class="arr">→</span></a> -->
          <div class="dp-bar"><i></i></div>
        </div>
""", "", True),
    # Enumeraciones que nombran el area. El NUMERO de areas no se toca: el club
    # tiene cuatro, y decir "tres" seria falso. Solo se deja de nombrarla.
    ("Portafolio, Trading, Valuation y FEN Investment Woman.",
     "Portafolio, Trading y Valuation, entre otras.", False),
    ("Portafolio, Trading, Valuation y FEN Investment Woman\"",
     "Portafolio, Trading y Valuation, entre otras\"", False),
    ("Comunidad de inversiones de la Facultad de Economia y Negocios. Portafolio, Trading, Valuation y FEN Investment Woman.",
     "Comunidad de inversiones de la Facultad de Economia y Negocios. Portafolio, Trading y Valuation.", False),
    # Restos de enlaces ya comentados: se van del archivo
    ("""      <!-- FIW_TEMP_OCULTO <li><a href="fiw/index.html">FIG Woman</a></li> -->
""", "", False),
    ("""  <!-- FIW_TEMP_OCULTO <a href="fiw/index.html">FIG Woman</a> -->
""", "", False),
    ("""          <!-- FIW_TEMP_OCULTO <li><a href="fiw/index.html">FEN Investment Woman</a></li> -->
""", "", False),
]),
("404.html", [
    ("""      <li><a href="fiw/index.html">FIW</a></li>
""", "", True),
    ("""        <a href="fiw/index.html">FIW</a>
""", "", True),
]),
("eventos/index.html", [
    ("""      <li><a href="../fiw/index.html">FEN Investment Woman</a></li>
""", "", True),
    ("""  <a href="../fiw/index.html">FEN Investment Woman</a>
""", "", True),
]),
("postula/index.html", [
    ("""      <li><a href="../fiw/index.html">FIW</a></li>
""", "", True),
    ("""              <option>FEN Investment Woman</option>
""", "", True),
    ("Portafolio, Trading, Valuation y FEN Investment Woman.",
     "Portafolio, Trading y Valuation.", False),
    ("Postula a Portafolio, Trading, Valuation o FEN Investment Woman.",
     "Postula a Portafolio, Trading o Valuation.", False),
]),
("valuation/index.html", [
    ("Área fundadora de FIG, junto a Portafolio, Trading y FEN Investment Woman.",
     "Área fundadora de FIG, junto a Portafolio y Trading.", True),
]),
("en/index.html", [
    ("""      <div class="card"><span class="tag">Area 04</span><h3>FEN Investment Woman</h3><p>Our community driving women's participation in finance and investing.</p></div>
""", "", True),
    ("""<h2 class="reveal d1">Four areas, <em>one community.</em></h2>""",
     """<h2 class="reveal d1">Our areas of <em>practice.</em></h2>""", True),
    ("Portfolio, Trading, Valuation and FEN Investment Woman.",
     "Portfolio, Trading and Valuation.", False),
]),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Saca FIW del espejo")
    ap.add_argument("--aplicar", action="store_true", help="escribe de verdad")
    args = ap.parse_args()

    if not ESPEJO.exists():
        print(f"No encuentro el espejo en {ESPEJO}")
        return 1

    acciones, faltantes = [], []

    for rel, motivo in BORRAR:
        if (ESPEJO / rel).exists():
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
            elif obligatorio and buscar not in texto:
                # Solo es un problema si el archivo todavia PUBLICA el area. No
                # sirve buscar "Investment Woman" a secas: ese texto sigue ahi
                # legitimamente por las tres cofundadoras (index.html) y por el
                # evento de la bitacora (eventos/), y hacia que el script gritara
                # en cada corrida aunque no quedara nada que quitar.
                if any(m in texto for m in RASTROS_DEL_AREA):
                    faltantes.append(f"{arch}: no encontre -> {buscar.strip()[:70]}")
        if nuevo != texto:
            acciones.append(("editar", arch, f"{len(texto) - len(nuevo)} bytes menos"))
            if args.aplicar:
                datos = nuevo.encode("utf-8")
                previo = f.read_bytes()
                if previo.count(b"\r\n") == previo.count(b"\n") and previo.count(b"\n"):
                    datos = datos.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                f.write_bytes(datos)

    if args.aplicar:
        for rel, _ in BORRAR:
            destino = ESPEJO / rel
            if not destino.exists():
                continue
            # Primero los ARCHIVOS y despues la carpeta: si `rmtree` se topa con
            # un bloqueo de OneDrive sobre el directorio, los archivos de adentro
            # ya se fueron -- que es lo que de verdad importa, porque una carpeta
            # vacia no se sirve ni git la versiona. Antes esto cortaba el script
            # a la mitad y dejaba sin borrar lo que venia despues.
            if destino.is_dir():
                for hijo in sorted(destino.rglob("*"), reverse=True):
                    try:
                        hijo.unlink() if hijo.is_file() else hijo.rmdir()
                    except OSError as e:
                        print(f"  aviso: no pude borrar {hijo}: {e}")
                try:
                    destino.rmdir()
                except OSError:
                    print(f"  aviso: {rel}/ quedo vacia pero bloqueada (OneDrive). "
                          "No importa: git no versiona carpetas vacias.")
            else:
                try:
                    destino.unlink()
                except OSError as e:
                    print(f"  aviso: no pude borrar {rel}: {e}")

    if QUITAR_EVENTO:
        print("QUITAR_EVENTO esta en True: hay que sacar fiw-mayo-2026 de "
              "datos/eventos.json y su carpeta de fotos a mano.")

    if not acciones:
        print("El espejo ya no publica el area FIW. Nada que hacer.")
    else:
        print(f"{'APLICADO' if args.aplicar else 'POR HACER'}:")
        for tipo, rel, det in acciones:
            print(f"  {tipo:<7} {rel:<26} {det}")

    if faltantes:
        print("\nOJO -- revisar a mano:")
        for x in faltantes:
            print(f"  {x}")

    if args.aplicar and acciones:
        print("\nAhora corre, DENTRO del espejo:  python generar_sitemap.py")
        print("(para que /fiw/ deje de estar declarada en sitemap.xml)")
    elif acciones:
        print("\nCorre con --aplicar para hacerlo.")

    print("\nRecuerda: los cargos de las tres cofundadoras en datos/club.json NO "
          "se tocan (ver la cabecera de este archivo).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
