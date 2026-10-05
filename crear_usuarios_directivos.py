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

AGREGAR GENTE SIN TOCAR A LOS QUE YA ESTÁN (2026-10-03):
         python crear_usuarios_directivos.py --plantilla   (si no existe el CSV)
         → llenar `correo` y `clave` SOLO de los nuevos; las filas sin clave se ignoran
         python crear_usuarios_directivos.py --agregar
         → pide copiar FIG_USUARIOS y FIG_PIMIENTA desde el Apps Script (los lee
           del portapapeles), suma a los nuevos con la MISMA pimienta y escribe
           solo FIG_USUARIOS. Nadie pierde su clave ni su sesión: FIG_PIMIENTA y
           FIG_SECRETO no se tocan. Un usuario que ya existe no se pisa.
         python crear_usuarios_directivos.py --copiar
         → copia la FIG_USUARIOS nueva para pegarla encima de la vieja.

UN DIRECTIVO OLVIDÓ SU CLAVE (2026-10-04):
         → escribir la clave nueva SOLO en la fila de esa persona (columna `clave`)
         python crear_usuarios_directivos.py --restablecer TRDRAL
         → mismo flujo que --agregar (copiar FIG_USUARIOS y FIG_PIMIENTA), pero cambia
           la clave de ese usuario y sube su versión de sesión (sus tokens viejos dejan de
           servir). Los demás no se tocan. Luego --copiar y pegar FIG_USUARIOS.
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
        # ";" porque el Excel en español separa columnas con punto y coma: con ","
        # abre cada fila entera en la columna A (pasó el 2026-10-03)
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        w.writeheader()
        for m in directiva():
            u = m["area"] + m["ticker"]
            w.writerow({"usuario": u, "nombre": m["nombre"], "area": m["area"],
                        "correo": "", "clave": "", "admin": "si" if u in ADMINS else ""})
    print(f"Escrito {CSV.name} con {len(directiva())} directivos. Llena `correo` y `clave` y corre sin --plantilla.")


def hash_clave(pimienta, sal, clave):
    return hmac.new(pimienta.encode(), f"{sal}:{clave}".encode("utf-8"), hashlib.sha256).hexdigest()


def leer_csv():
    if not CSV.exists():
        sys.exit(f"No existe {CSV.name}: corre primero con --plantilla.")
    texto = CSV.read_bytes()
    try:
        texto = texto.decode("utf-8-sig")
    except UnicodeDecodeError:          # Excel lo guardó como "CSV (delimitado por comas)" en ANSI
        texto = texto.decode("cp1252")
    # Excel en español guarda con ";" en vez de ","
    sep = ";" if texto.splitlines()[0].count(";") > texto.splitlines()[0].count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=sep))


def portapapeles():
    import subprocess
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"],
                       capture_output=True, check=True)
    return r.stdout.decode("utf-8").strip()


def vaciar_portapapeles():
    import subprocess
    subprocess.run("clip", input="".encode("utf-16-le"), check=True)


def pedir_actuales_y_pimienta():
    """Pide copiar FIG_USUARIOS y FIG_PIMIENTA del Apps Script; los lee del portapapeles."""
    print("En script.google.com → ⚙ Configuración del proyecto → Propiedades de la secuencia de comandos:")
    input("\n1) Copia el VALOR completo de FIG_USUARIOS (clic en el valor, Ctrl+A, Ctrl+C) y presiona Enter acá...")
    try:
        actuales = json.loads(portapapeles())
        assert isinstance(actuales, dict) and actuales
    except Exception:
        vaciar_portapapeles()
        sys.exit("Lo copiado no es la FIG_USUARIOS (no es un JSON con usuarios). No se escribió nada.")
    input(f"   OK: {len(actuales)} usuarios actuales.\n\n2) Ahora copia el VALOR de FIG_PIMIENTA y presiona Enter...")
    pimienta = portapapeles()
    vaciar_portapapeles()
    if not re.fullmatch(r"[0-9a-f]{64}", pimienta):
        sys.exit("Lo copiado no parece la FIG_PIMIENTA (64 caracteres hexadecimales). No se escribió nada.")
    return actuales, pimienta


def restablecer(usuario):
    """Pone una clave nueva a UN usuario que ya existe (olvidó la suya). La clave se
    toma de la columna `clave` de su fila en el CSV; los demás no se tocan."""
    u = normalizar(usuario)
    fila = next((r for r in leer_csv() if normalizar(r.get("usuario", "")) == u), None)
    if not fila:
        sys.exit(f"{u} no está en {CSV.name}. No se escribió nada.")
    clave = fila.get("clave", "")
    if len(clave) < 8:
        sys.exit(f"{u}: llena su clave (mínimo 8 caracteres) en la columna `clave` de {CSV.name}. No se escribió nada.")
    actuales, pimienta = pedir_actuales_y_pimienta()
    if u not in actuales:
        sys.exit(f"{u} no existe en FIG_USUARIOS: para un usuario nuevo usa --agregar. No se escribió nada.")
    r = actuales[u]
    r["s"] = secrets.token_hex(16)
    r["h"] = hash_clave(pimienta, r["s"], clave)
    r["v"] = r.get("v", 1) + 1          # invalida sus tokens viejos, igual que cambiarClave_ del Apps Script
    SALIDA.write_text(
        "Pegar en script.google.com → ⚙ Configuración del proyecto → Propiedades de la secuencia de comandos.\n"
        "Solo cambia FIG_USUARIOS: reemplaza su valor entero. FIG_PIMIENTA y FIG_SECRETO NO se tocan.\n\n"
        f"FIG_USUARIOS\n{json.dumps(actuales, ensure_ascii=False, separators=(',', ':'))}\n",
        encoding="utf-8")
    print(f"\nClave de {u} restablecida (los otros {len(actuales) - 1} no se tocaron) → {SALIDA.name}")
    print("Siguiente: python crear_usuarios_directivos.py --copiar  y pega FIG_USUARIOS encima de la vieja.")


def agregar():
    filas = leer_csv()
    actuales, pimienta = pedir_actuales_y_pimienta()

    nuevos, avisos = [], []
    for i, r in enumerate(filas, start=2):
        u, clave, area = normalizar(r.get("usuario", "")), r.get("clave", ""), r.get("area", "").strip().upper()
        if not clave:
            continue                                  # sin clave = no se agrega en esta pasada
        if u in actuales:
            avisos.append(f"{u} ya tiene cuenta: no se toca (para cambiarle la clave, que lo haga desde la app)")
            continue
        if len(clave) < 8:
            sys.exit(f"fila {i} ({u}): la clave tiene menos de 8 caracteres. No se escribió nada.")
        if area not in AREAS or not u.startswith(area):
            sys.exit(f"fila {i} ({u}): el área '{area}' no calza con el usuario. No se escribió nada.")
        sal = secrets.token_hex(16)
        actuales[u] = {"n": r.get("nombre", "").strip(), "a": area, "c": r.get("correo", "").strip(),
                       "s": sal, "h": hash_clave(pimienta, sal, clave), "v": 1}
        if r.get("admin", "").strip().lower() in ("si", "sí", "x", "1", "true"):
            actuales[u]["admin"] = True
        nuevos.append(u)

    for a in avisos:
        print("  ⚠", a)
    if not nuevos:
        sys.exit("No hay nadie nuevo para agregar (¿llenaste la clave de los que faltan?). No se escribió nada.")
    SALIDA.write_text(
        "Pegar en script.google.com → ⚙ Configuración del proyecto → Propiedades de la secuencia de comandos.\n"
        "Solo cambia FIG_USUARIOS: reemplaza su valor entero. FIG_PIMIENTA y FIG_SECRETO NO se tocan.\n\n"
        f"FIG_USUARIOS\n{json.dumps(actuales, ensure_ascii=False, separators=(',', ':'))}\n",
        encoding="utf-8")
    print(f"\nAgregados {len(nuevos)}: {', '.join(nuevos)}  →  total {len(actuales)} usuarios en {SALIDA.name}")
    print("Siguiente: python crear_usuarios_directivos.py --copiar  y pega FIG_USUARIOS encima de la vieja.")


def generar():
    filas = leer_csv()

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
    nombres = [n for n in ("FIG_USUARIOS", "FIG_PIMIENTA", "FIG_SECRETO") if n in lineas]   # --agregar solo trae la primera
    for nombre in nombres:
        valor = lineas[lineas.index(nombre) + 1]
        subprocess.run("clip", input=valor.encode("utf-16-le"), check=True)
        input(f"\nPropiedad:  {nombre}\nValor:      COPIADO ({len(valor)} caracteres). Pégalo con Ctrl+V y presiona Enter acá...")
    vaciar_portapapeles()   # no dejar el secreto en el portapapeles
    print(f"\nListo: {len(nombres)} propiedad(es). Portapapeles vaciado. Ahora borra los dos archivos .local.")


if __name__ == "__main__":
    if "--plantilla" in sys.argv:
        plantilla()
    elif "--agregar" in sys.argv:
        agregar()
    elif "--restablecer" in sys.argv:
        i = sys.argv.index("--restablecer")
        if i + 1 >= len(sys.argv):
            sys.exit("Falta el usuario: python crear_usuarios_directivos.py --restablecer TRDRAL")
        restablecer(sys.argv[i + 1])
    elif "--copiar" in sys.argv:
        copiar()
    else:
        generar()
