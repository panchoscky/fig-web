#!/usr/bin/env python3
"""Completa métricas faltantes en el historial de datos/torneo.json.

Uso:
    python3 completar_metricas_historial.py --excels a.xlsx,b.xlsx,...
    python3 completar_metricas_historial.py --excels ... --aplicar

Sin `--aplicar` solo informa (dry-run) y no escribe nada.

QUÉ HACE
--------
Lee los Excels semanales oficiales indicados, calcula a qué semana corresponde
cada uno por la fecha de su nombre de archivo (misma fórmula que usa la página)
y **agrega al historial de torneo.json únicamente las claves de métrica que
falten**. Nunca modifica un valor ya presente, ni crea o borra semanas, equipos
o cualquier otro campo. Si detecta que algo más cambió, aborta sin escribir.

POR QUÉ NO SE USA `generar_torneo.py --excels`
----------------------------------------------
Ese modo REGENERA el JSON completo, y en el camino `procesar_multiples()` hace
`eq["miembros"] = insc.get(eq["id"], [])`: sin `--inscripciones` deja a los 59
equipos sin integrantes, y con `--inscripciones` los reescribe desde el Excel,
pisando las correcciones a mano que se hicieron en 4 equipos. Además recalcula
`acwi`, `delta`, `retRel` y las posiciones, que hoy ya están correctos. Cuando
lo único que falta es rellenar una métrica en semanas ya publicadas, regenerar
todo es desproporcionado: este script hace el injerto quirúrgico.

Caso real que lo motivó (2026-08-16): las 5 métricas de Bloomberg (IR, exceso,
Sharpe, VaR, MDD) se empezaron a guardar por semana recién en el corte del
7-ago-2026, así que las semanas 5 a 12 solo tenían posición/puntos/retorno y el
gráfico "Evolución por métrica" del replay graficaba 2 de 10 semanas. Se
recargaron los 8 Excels de esas semanas y quedaron las 8 series completas.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_torneo as g  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "datos" / "torneo.json"
METRICAS = ("ir", "exc", "sharpe", "var95", "mdd")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--excels", required=True,
                    help="Excels semanales separados por coma. El nombre debe traer "
                         "la fecha del corte (ej. Excel_Oficial_FIG_PORT_2026_2026-06-19.xlsx)")
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe datos/torneo.json (sin esto es solo un informe)")
    args = ap.parse_args()

    rutas = [Path(r.strip()) for r in args.excels.split(",") if r.strip()]
    for r in rutas:
        if not r.exists():
            sys.exit(f"No existe: {r}")

    datos = json.loads(SALIDA.read_text(encoding="utf-8"))
    antes = json.loads(json.dumps(datos))  # copia profunda para la verificación

    indice = {eq["id"]: {h["semana"]: h for h in eq.get("historial", [])}
              for eq in datos["equipos"]}

    agregadas = puntos_tocados = 0
    sin_calce, discrepancias = [], []

    for ruta in sorted(rutas, key=lambda p: g.FECHA_EN_NOMBRE.search(p.stem).group(0)
                       if g.FECHA_EN_NOMBRE.search(p.stem) else ""):
        m = g.FECHA_EN_NOMBRE.search(ruta.stem)
        if not m:
            sys.exit(f"No pude leer la fecha del nombre de archivo: {ruta}")
        fecha = m.group(0)
        semana = g.semana_de_fecha(fecha)
        equipos_excel = g.leer_ranking(str(ruta))
        tocados = 0

        for eq in equipos_excel:
            hist = indice.get(eq["id"])
            if hist is None:
                sin_calce.append((fecha, eq["id"], "el equipo no está en torneo.json"))
                continue
            punto = hist.get(semana)
            if punto is None:
                sin_calce.append((fecha, eq["id"], f"sin punto de historial en S{semana}"))
                continue

            # Integridad: lo ya guardado debe calzar con el Excel. Si no calza se
            # informa, pero NO se corrige — eso sería otra decisión, no esta.
            if punto.get("posicion") != eq["posicion"]:
                discrepancias.append((fecha, eq["id"], "posicion",
                                      punto.get("posicion"), eq["posicion"]))
            if round(float(punto.get("puntos") or 0), 2) != round(eq["puntos"], 2):
                discrepancias.append((fecha, eq["id"], "puntos",
                                      punto.get("puntos"), eq["puntos"]))

            nuevas = 0
            for k in METRICAS:
                v = (eq.get("metricas") or {}).get(k)
                if v is None or k in punto:
                    continue  # ausente en el Excel, o ya guardada: no se pisa jamás
                punto[k] = v
                nuevas += 1
            if nuevas:
                agregadas += nuevas
                tocados += 1

        puntos_tocados += tocados
        print(f"  {fecha}  S{semana:<3} equipos en el Excel: {len(equipos_excel):<3} "
              f"puntos de historial completados: {tocados}")

    print(f"\nClaves de métrica agregadas: {agregadas} (en {puntos_tocados} puntos del historial)")

    if sin_calce:
        print(f"\nSIN CALCE ({len(sin_calce)}):")
        for x in sin_calce[:20]:
            print("   ", x)
    if discrepancias:
        print(f"\nDISCREPANCIAS con lo ya guardado ({len(discrepancias)}) — NO se corrigieron:")
        for x in discrepancias[:20]:
            print("   ", x)

    if problemas := verificar(antes, datos):
        print(f"\nABORTA — se tocó algo que no correspondía ({len(problemas)}):")
        for p in problemas[:20]:
            print("   ", p)
        sys.exit(1)
    print("\nVERIFICACIÓN OK: solo se agregaron claves de métrica; ningún valor previo cambió.")

    faltan = {}
    for eq in datos["equipos"]:
        for h in eq["historial"]:
            if [k for k in METRICAS if k not in h]:
                faltan[h["semana"]] = faltan.get(h["semana"], 0) + 1
    print("Semanas con equipos aún sin métricas completas:", faltan or "ninguna")

    if args.aplicar:
        SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(f"\nESCRITO: {SALIDA}")
    else:
        print("\n(dry-run — nada escrito. Agregar --aplicar para guardar.)")


def verificar(antes, despues):
    """Devuelve la lista de cambios que NO son 'agregar una clave de métrica'."""
    problemas = []
    for e_a, e_d in zip(antes["equipos"], despues["equipos"]):
        for campo in e_a:
            if campo != "historial" and e_a[campo] != e_d[campo]:
                problemas.append(f"{e_a['id']}: cambió el campo '{campo}'")
        ha, hd = e_a.get("historial", []), e_d.get("historial", [])
        if len(ha) != len(hd):
            problemas.append(f"{e_a['id']}: cambió la cantidad de semanas")
            continue
        for pa, pd in zip(ha, hd):
            for k in pa:
                if pa[k] != pd[k]:
                    problemas.append(f"{e_a['id']} S{pa['semana']}: se PISÓ '{k}' "
                                     f"({pa[k]} → {pd[k]})")
            for k in pd:
                if k not in pa and k not in METRICAS:
                    problemas.append(f"{e_a['id']} S{pa['semana']}: clave inesperada '{k}'")
    for campo in antes:
        if campo != "equipos" and antes[campo] != despues[campo]:
            problemas.append(f"cambió el campo raíz '{campo}'")
    return problemas


if __name__ == "__main__":
    main()
