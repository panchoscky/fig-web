"""
sincronizar_espejo.py -- Copia lo que corresponde a mpazq-afk.github.io.

Por que existe
---------------
Hay dos repos: `fig-web` (donde se trabaja) y `mpazq-afk.github.io` (el que
tiene el CNAME y sirve feninvestmentgroup.com). Hasta ahora el espejo se
actualizaba copiando archivos a mano, y **ya divergio sin que nadie lo notara**:
las fotos de eventos del espejo eran las de julio, anteriores a la
renormalizacion del 23-ago, o sea que la produccion estaba sirviendo imagenes
viejas. Copiar a mano tambien es peligroso al reves: copiar `index.html` entero
le borraria al espejo su nav adaptado.

Este script hace explicito lo que hasta ahora vivia en la cabeza de alguien:
que se copia, que NO se copia, y que difiere a proposito.

Uso
----
    python sincronizar_espejo.py              # revisa y reporta, no escribe
    python sincronizar_espejo.py --aplicar    # copia

Nunca borra nada del espejo. Si aparece un archivo que solo existe alla, lo
reporta para que lo mire una persona.
"""

from __future__ import annotations
import argparse
import filecmp
import pathlib
import shutil
import sys

ORIGEN = pathlib.Path(__file__).resolve().parent
ESPEJO = ORIGEN.parent / "mpazq-afk.github.io"

# --------------------------------------------------------------------------
# Lo que NO viaja al espejo. Cada entrada con su motivo: si alguna vez hay que
# revisar por que algo no esta publicado, la respuesta esta aca y no en un chat.
NO_SE_COPIAN = {
    "miembros/": "la pagina de Miembros todavia no se publica en produccion",
    "datos/miembros.json": "solo la usa miembros/",
    "datos/miembros.demo.json": "datos de demostracion, nunca se publican",
    "fotos/miembros/": "solo las usa miembros/",
    "generar_miembros.py": "genera datos que el espejo no tiene",
    "PLANILLA_MIEMBROS_FIG.md": "documento de trabajo del equipo",
    "completar_metricas_historial.py": "herramienta de datos, no del sitio",
    "completar_acwi_historial.py": "herramienta de datos, no del sitio",
    "grabar_pantalla_facultad_1_capturar.js": "herramienta de video",
    "grabar_pantalla_facultad_2_codificar.py": "herramienta de video",
    "optimizar_fotos.py": "herramienta local sobre fotos/ ya optimizadas",
    "descargar_fuentes.py": "se corre una vez en el repo de trabajo",
    "usar_fuentes_locales.py": "se corre una vez en el repo de trabajo",
    "sincronizar_espejo.py": "no tiene sentido dentro del espejo",
    "GUIA_DRIVE_FIG.html": "guia interna del equipo",
    "GUIA_DRIVE_FIG.jpg": "guia interna del equipo",
    "VIDEO_PODIO_GEMINI.md": "documento de trabajo",
    # El espejo tiene su PROPIA version, con dos scripts extra que limpian la
    # URL (le sacan /index.html y el #). Copiar la de aca se los borraria.
    "MAPA_CONTENIDO_FIG.html": "guia interna; el espejo tiene su version con scripts propios",
    "frames/": "salida temporal del grabador de video",
}

# Difieren a proposito y NUNCA se pisan.
DIFIEREN = {
    "index.html": ("el nav del espejo no tiene Miembros ni FIG Woman, asi que "
                   "'Comunidad' quedo como 'Equipo' suelto. Para portar un "
                   "cambio hay que llevar solo el bloque que se toco, no el "
                   "archivo entero"),
}

# Existen solo en el espejo y estan bien asi.
SOLO_ESPEJO = {"CNAME": "es lo que apunta el dominio propio a ese repo"}

IGNORADOS = (".git", "__pycache__", "node_modules", ".DS_Store")


def excluido(rel: str) -> str | None:
    for clave, motivo in NO_SE_COPIAN.items():
        if rel == clave or (clave.endswith("/") and rel.startswith(clave)):
            return motivo
    return None


def archivos(raiz: pathlib.Path) -> set[str]:
    out = set()
    for p in raiz.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(raiz).as_posix()
        if any(part in IGNORADOS for part in p.relative_to(raiz).parts):
            continue
        out.add(rel)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true", help="copia de verdad")
    args = ap.parse_args()

    if not ESPEJO.exists():
        print(f"No encuentro el espejo en {ESPEJO}")
        return 1

    del_origen = archivos(ORIGEN)
    del_espejo = archivos(ESPEJO)

    copiar, nuevos, saltados, protegidos = [], [], [], []
    for rel in sorted(del_origen):
        motivo = excluido(rel)
        if motivo:
            saltados.append((rel, motivo))
            continue
        if rel in DIFIEREN:
            protegidos.append(rel)
            continue
        destino = ESPEJO / rel
        if not destino.exists():
            nuevos.append(rel)
        elif not filecmp.cmp(ORIGEN / rel, destino, shallow=False):
            copiar.append(rel)

    solo_alla = sorted(r for r in del_espejo - del_origen if r not in SOLO_ESPEJO)

    def resumir(titulo, items, limite=12):
        if not items:
            return
        print(f"\n{titulo} ({len(items)})")
        for x in items[:limite]:
            print(f"  {x}")
        if len(items) > limite:
            print(f"  ... y {len(items) - limite} mas")

    resumir("NUEVOS en el espejo", nuevos)
    resumir("ACTUALIZADOS (distintos)", copiar)
    if protegidos:
        print(f"\nNO SE TOCAN, difieren a proposito ({len(protegidos)})")
        for r in protegidos:
            print(f"  {r}\n      {DIFIEREN[r]}")
    if solo_alla:
        print(f"\nOJO -- solo existen en el espejo ({len(solo_alla)}). No se borra "
              "nada; miralos a mano:")
        for r in solo_alla[:12]:
            print(f"  {r}")
    print(f"\n{len(saltados)} archivo(s) que no viajan al espejo a proposito "
          "(ver NO_SE_COPIAN en este script).")

    total = len(nuevos) + len(copiar)
    if not total:
        print("\nEl espejo ya esta al dia.")
        return 0

    if not args.aplicar:
        print(f"\n{total} archivo(s) por copiar. Corre con --aplicar para hacerlo.")
        return 0

    for rel in nuevos + copiar:
        destino = ESPEJO / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ORIGEN / rel, destino)
    print(f"\nOK: {total} archivo(s) copiados al espejo.")
    print("Falta revisar el diff y commitear alla.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
