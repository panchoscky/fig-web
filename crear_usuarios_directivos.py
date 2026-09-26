"""Arma las cuentas de las apps "FIG Directivos" SIN que las claves pasen por
el repo, por el chat ni por ningún otro lado que no sea este PC.

Paso 1:  python crear_usuarios_directivos.py --plantilla
         Escribe directivos_cuentas.local.csv con los 15 directivos de
         datos/miembros.json y su usuario ya armado (área + código de 3 letras
         de Miembros: PRT + FVA = PRTFVA). Tú llenas `correo` y `clave`.

Paso 2:  python crear_usuarios_directivos.py
         Lee ese CSV y escribe directivos_propiedades.local.txt con las 3
         propiedades que se pegan en el Apps Script (Configuración del
         proyecto → Propiedades de la secuencia de comandos). Ahí no va
         ninguna clave, solo su hash: HMAC-SHA256(pimienta, sal + ":" + clave),
         el mismo cálculo que hashClave_() en apps_script/Codigo.gs.

Los dos archivos *.local.* están en .gitignore. Cuando termines de pegar las
propiedades, BORRA los dos (o al menos las claves del CSV): el servidor ya no
las necesita.

Correrlo de nuevo genera sal, pimienta y secreto NUEVOS: hay que volver a
pegar las 3 propiedades, y todos los directivos tienen que volver a entrar
(y pierden la clave que se hayan cambiado desde la app, vuelven a la del CSV).
"""
import csv
import hashlib
import hmac
import json
import re
import secrets
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CSV = RAIZ / "directivos_cuentas.local.csv"
SALIDA = RAIZ / "directivos_propiedades.local.txt"
CAMPOS = ["usuario", "nombre", "area", "correo", "clave", "admin"]
AREAS = ["PRT", "TRD", "VAL", "FIW", "ADM"]
ADMINS = {"PRTFVA"}   # puede publicar para cualquier área y ocultar lo de todos


def normalizar(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def directiva():
    d = json.loads((RAIZ / "datos" / "miembros.json").read_text(encoding="utf-8"))
    return [m for m in d["miembros"] if m.get("fuente") == "club.json"]


def plantilla():
    if CSV.exists():
        sys.exit(f"{CSV.name} ya existe; no lo piso (puede tener claves). Bórralo a mano si quieres uno nuevo.")
    with CSV.open("w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig: Excel lee bien las tildes
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for m in directiva():
            u = m["area"] + m["ticker"]
            w.writerow({"usuario": u, "nombre": m["nombre"], "area": m["area"],
                        "correo": "", "clave": "", "admin": "si" if u in ADMINS else ""})
    print(f"Escrito {CSV.name} con {len(directiva())} directivos. Llena `correo` y `clave` y corre sin --plantilla.")


def hash_clave(pimienta, sal, clave):
    return hmac.new(pimienta.encode(), f"{sal}:{clave}".encode("utf-8"), hashlib.sha256).hexdigest()


def generar():
    if not CSV.exists():
        sys.exit(f"No existe {CSV.name}: corre primero con --plantilla.")
    texto = CSV.read_bytes()
    try:
        texto = texto.decode("utf-8-sig")
    except UnicodeDecodeError:          # Excel lo guardó como "CSV (delimitado por comas)" en ANSI
        texto = texto.decode("cp1252")
    # Excel en español guarda con ";" en vez de ","
    sep = ";" if texto.splitlines()[0].count(";") > texto.splitlines()[0].count(",") else ","
    filas = list(csv.DictReader(texto.splitlines(), delimiter=sep))

    pimienta = secrets.token_hex(32)
    usuarios, errores = {}, []
    for i, r in enumerate(filas, start=2):
        u, clave, area = normalizar(r.get("usuario", "")), r.get("clave", ""), r.get("area", "").strip().upper()
        if not u and not clave:
            continue
        if not clave:
            errores.append(f"fila {i} ({u}): sin clave — queda FUERA")
            continue
        if len(clave) < 8:
            errores.append(f"fila {i} ({u}): clave de menos de 8 caracteres")
        if area not in AREAS or not u.startswith(area):
            errores.append(f"fila {i} ({u}): el área '{area}' no calza con el usuario")
        if u in usuarios:
            errores.append(f"fila {i}: usuario repetido {u}")
        sal = secrets.token_hex(16)
        usuarios[u] = {"n": r.get("nombre", "").strip(), "a": area, "c": r.get("correo", "").strip(),
                       "s": sal, "h": hash_clave(pimienta, sal, clave), "v": 1}
        if r.get("admin", "").strip().lower() in ("si", "sí", "x", "1", "true"):
            usuarios[u]["admin"] = True

    for e in errores:
        print("  ⚠", e)
    if any("no calza" in e or "repetido" in e for e in errores):
        sys.exit("Corrige el CSV y vuelve a correr. No se escribió nada.")

    SALIDA.write_text(
        "Pegar en script.google.com → ⚙ Configuración del proyecto → Propiedades de la secuencia de comandos.\n"
        "Una propiedad por bloque: el nombre a la izquierda, el valor (la línea de abajo, entera) a la derecha.\n\n"
        f"FIG_USUARIOS\n{json.dumps(usuarios, ensure_ascii=False, separators=(',', ':'))}\n\n"
        f"FIG_PIMIENTA\n{pimienta}\n\n"
        f"FIG_SECRETO\n{secrets.token_hex(32)}\n",
        encoding="utf-8")
    por_area = {}
    for v in usuarios.values():
        por_area[v["a"]] = por_area.get(v["a"], 0) + 1
    print(f"{len(usuarios)} usuarios → {SALIDA.name}  {por_area}")
    print("Pega las 3 propiedades y después BORRA los dos archivos .local.")


def copiar():
    """Pone cada valor en el portapapeles, uno por uno, para pegarlo en el Apps Script
    sin arriesgar copiar a medias la línea larguísima de FIG_USUARIOS."""
    import subprocess
    if not SALIDA.exists():
        sys.exit(f"No existe {SALIDA.name}: corre primero sin argumentos.")
    lineas = SALIDA.read_text(encoding="utf-8").splitlines()
    for nombre in ("FIG_USUARIOS", "FIG_PIMIENTA", "FIG_SECRETO"):
        valor = lineas[lineas.index(nombre) + 1]
        subprocess.run("clip", input=valor.encode("utf-16-le"), check=True)
        input(f"\nPropiedad:  {nombre}\nValor:      COPIADO ({len(valor)} caracteres). Pégalo con Ctrl+V y presiona Enter acá...")
    subprocess.run("clip", input="".encode("utf-16-le"), check=True)   # no dejar el secreto en el portapapeles
    print("\nListo: las 3 propiedades. Portapapeles vaciado. Ahora borra los dos archivos .local.")


if __name__ == "__main__":
    if "--plantilla" in sys.argv:
        plantilla()
    elif "--copiar" in sys.argv:
        copiar()
    else:
        generar()
