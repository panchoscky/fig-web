#!/usr/bin/env python3
"""Completa el benchmark ACWI faltante en datos/torneo.json.

Uso:
    python3 completar_acwi_historial.py --precios ruta/a/ACWI_US.csv
    python3 completar_acwi_historial.py --precios ruta/a/ACWI_US.csv --aplicar

Sin `--aplicar` solo informa (dry-run) y no escribe nada.

QUÉ HACE
--------
`acwi` en torneo.json viene vacío desde siempre: ningún Excel oficial visto
hasta ahora trae el benchmark (ver CLAUDE.md, `torneo/index.html` en el
gráfico "RETORNO ACUMULADO SINCE-INCEPTION"). Este script lo llena con datos
reales de Bloomberg — el mismo camino usado para `datos/mercado/precios/
ACWI_US.csv` de `panchoscky/Ordis` (captura semanal, ticker `ACWI US Equity`,
serie semanal `PX_LAST`) — calculando el retorno acumulado desde el inicio
del torneo (2026-05-11) hasta la fecha de cada corte YA publicado.

Igual que `completar_metricas_historial.py`: **solo agrega** entradas de
`acwi` para semanas que no la tienen. Nunca pisa una ya presente, nunca toca
`equipos`. Si algo más cambia, aborta sin escribir.

POR QUÉ NO SE PASA `--acwi` A `generar_torneo.py`
---------------------------------------------------
Ese flag solo acepta UN valor para la semana que se está procesando en ese
momento (ver su `main()`); no hay forma de hacer un backfill de varias
semanas de una sola pasada sin volver a correr el Excel de cada corte. Este
script hace el injerto quirúrgico directo sobre el JSON ya publicado.

FECHAS DE CORTE
----------------
No vienen guardadas explícitamente por semana en torneo.json. Se derivan
programáticamente con la MISMA fórmula que usa el sitio (`semana_de_fecha()`,
floor((fecha-t0)/7)+1) barriendo todos los viernes desde el inicio del
torneo — los cortes son siempre viernes (ver CLAUDE.md, "Flujo semanal").
"""
import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_torneo as g  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "datos" / "torneo.json"
T0 = "2026-05-11"


def mapa_semana_a_viernes(hasta: dt.date, t0_iso: str = T0) -> dict:
    """{semana: fecha_iso} para cada viernes entre el inicio del torneo y `hasta`."""
    t0 = dt.date.fromisoformat(t0_iso)
    # primer viernes >= t0
    dias_hasta_viernes = (4 - t0.weekday()) % 7  # weekday(): lunes=0 ... viernes=4
    viernes = t0 + dt.timedelta(days=dias_hasta_viernes)
    mapa = {}
    while viernes <= hasta:
        mapa[g.semana_de_fecha(viernes.isoformat(), t0_iso)] = viernes.isoformat()
        viernes += dt.timedelta(days=7)
    return mapa


def leer_serie_precios(ruta: Path) -> list[tuple[dt.date, float]]:
    filas = list(csv.DictReader(ruta.open(encoding="utf-8")))
    serie = [(dt.date.fromisoformat(r["fecha"]), float(r["cierre"])) for r in filas]
    serie.sort()
    return serie


def precio_mas_cercano(serie: list[tuple[dt.date, float]], fecha: dt.date):
    return min(serie, key=lambda p: abs((p[0] - fecha).days))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--precios", required=True,
                    help="CSV fecha,cierre del ACWI (ej. ACWI_US.csv de Ordis)")
    ap.add_argument("--max-dias-desfase", type=int, default=3,
                    help="máximo desfase (días) entre el viernes del corte y el "
                         "dato de precio más cercano para aceptarlo sin avisar "
                         "(default 3 — más que eso, se avisa como sospechoso)")
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe datos/torneo.json (sin esto es solo un informe)")
    args = ap.parse_args()

    ruta_precios = Path(args.precios)
    if not ruta_precios.exists():
        sys.exit(f"No existe: {ruta_precios}")

    serie = leer_serie_precios(ruta_precios)
    print(f"Serie ACWI: {len(serie)} puntos, {serie[0][0]} → {serie[-1][0]}")

    datos = json.loads(SALIDA.read_text(encoding="utf-8"))
    antes = json.loads(json.dumps(datos))  # copia profunda para verificar

    semanas_publicadas = sorted({h["semana"] for eq in datos["equipos"]
                                 for h in eq.get("historial", [])})
    if not semanas_publicadas:
        sys.exit("torneo.json no tiene historial — nada que completar.")
    print(f"Semanas publicadas en torneo.json: {semanas_publicadas}")

    mapa = mapa_semana_a_viernes(dt.date.today())
    t0 = dt.date.fromisoformat(T0)
    p0_fecha, p0 = precio_mas_cercano(serie, t0)
    print(f"Baseline (inicio del torneo {T0}): precio del {p0_fecha} = {p0}")

    ya_presentes = {a["semana"] for a in datos.get("acwi", [])}
    nuevas, saltadas = [], []

    for semana in semanas_publicadas:
        if semana in ya_presentes:
            continue
        fecha_corte = mapa.get(semana)
        if fecha_corte is None:
            saltadas.append((semana, "no se pudo derivar la fecha del corte"))
            continue
        fecha_corte_d = dt.date.fromisoformat(fecha_corte)
        pf, precio = precio_mas_cercano(serie, fecha_corte_d)
        desfase = abs((pf - fecha_corte_d).days)
        if desfase > args.max_dias_desfase:
            saltadas.append((semana, f"corte {fecha_corte}, dato más cercano es del "
                                     f"{pf} ({desfase}d de desfase) — no se usa, "
                                     "actualizar la serie de precios primero"))
            continue
        ret = round(precio / p0 - 1, 4)
        nuevas.append({"semana": semana, "ret": ret})
        print(f"  S{semana:<3} corte {fecha_corte}  precio {precio} ({pf}, "
              f"{desfase}d off)  ret={ret:+.4f}")

    if saltadas:
        print(f"\nSALTADAS ({len(saltadas)}) — no se les agrega ACWI:")
        for s in saltadas:
            print("   ", s)

    if not nuevas:
        print("\nNada nuevo que agregar (todo ya presente o sin dato confiable).")
        return

    acwi = list(datos.get("acwi", [])) + nuevas
    acwi.sort(key=lambda a: a["semana"])
    datos["acwi"] = acwi

    if problemas := verificar(antes, datos):
        print(f"\nABORTA — se tocó algo que no correspondía ({len(problemas)}):")
        for p in problemas[:20]:
            print("   ", p)
        sys.exit(1)
    print(f"\nVERIFICACIÓN OK: solo se agregaron {len(nuevas)} entradas a 'acwi'; "
          "nada más cambió.")

    if args.aplicar:
        SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(f"\nESCRITO: {SALIDA}")
    else:
        print("\n(dry-run — nada escrito. Agregar --aplicar para guardar.)")


def verificar(antes, despues):
    """Devuelve la lista de cambios que NO son 'agregar una entrada a acwi'."""
    problemas = []
    if antes["equipos"] != despues["equipos"]:
        problemas.append("cambió 'equipos' — no debería tocarse")
    for campo in antes:
        if campo not in ("acwi", "equipos") and antes[campo] != despues[campo]:
            problemas.append(f"cambió el campo raíz '{campo}'")
    ba = {a["semana"]: a for a in antes.get("acwi", [])}
    bd = {a["semana"]: a for a in despues.get("acwi", [])}
    for sem, v in ba.items():
        if bd.get(sem) != v:
            problemas.append(f"acwi S{sem}: se PISÓ un valor existente "
                             f"({v} → {bd.get(sem)})")
    return problemas


if __name__ == "__main__":
    main()
