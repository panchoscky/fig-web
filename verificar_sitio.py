"""
verificar_sitio.py -- Chequeo rapido antes de publicar.

Por que existe
--------------
Este sitio tiene datos que viven en mas de un lugar a la vez: archivos derivados
que hay que regenerar (datos/torneo-tabla.json, datos/torneo-portada.json,
torneo/e/*.html, og/*.jpg) y
numeros escritos a mano en el HTML que tienen que calzar con el JSON (las meta
etiquetas dicen "54 equipos"). Cada vez que uno de esos se quedo atras hubo que
descubrirlo mirando la pagina: la correccion 63 -> 59 -> 54 se hizo tres veces, a
mano, y siempre quedo alguna mencion suelta (en/index.html estuvo meses con
"Sixty-three").

Esto lo revisa en un segundo. No arregla nada por su cuenta salvo que se lo pidas
con --arreglar, y ahi solo toca lo que es DERIVADO: nunca edita datos ni HTML
escrito por una persona.

Uso
----
    python verificar_sitio.py              # revisa y reporta
    python verificar_sitio.py --arreglar   # ademas regenera los derivados

Devuelve 1 si hay ERRORES (algo objetivamente desincronizado) y 0 si solo hay
AVISOS (cosas que conviene que mire una persona, como una mencion de un numero
en un texto historico que quiza deba quedarse como esta).
"""

from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

# Se reusa para no duplicar a mano la lista de paginas publicas ni la logica de
# fecha_git: el sitemap y su verificacion tienen que salir de la MISMA fuente.
try:
    import generar_sitemap
except Exception:      # pragma: no cover - solo si falta el archivo
    generar_sitemap = None

RAIZ = pathlib.Path(__file__).resolve().parent
DATOS = RAIZ / "datos"

ERRORES: list[str] = []
AVISOS: list[str] = []
BIEN: list[str] = []


def error(msg: str) -> None:
    ERRORES.append(msg)


def aviso(msg: str) -> None:
    AVISOS.append(msg)


def bien(msg: str) -> None:
    BIEN.append(msg)


def rel(p: pathlib.Path) -> str:
    try:
        return str(p.relative_to(RAIZ)).replace("\\", "/")
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------
def revisar_json() -> dict:
    """Todos los .json de datos/ parsean. Devuelve el torneo ya leido."""
    rotos = []
    for ruta in sorted(DATOS.rglob("*.json")):
        try:
            json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            rotos.append(f"{rel(ruta)}: {e}")
    if rotos:
        for r in rotos:
            error(f"JSON invalido -- {r}")
    else:
        bien(f"los {len(list(DATOS.rglob('*.json')))} JSON de datos/ parsean")

    ruta_t = DATOS / "torneo.json"
    if not ruta_t.exists():
        return {}
    try:
        return json.loads(ruta_t.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def revisar_tabla_derivada() -> bool:
    """datos/torneo-tabla.json corresponde al torneo.json actual."""
    fuente = DATOS / "torneo.json"
    derivado = DATOS / "torneo-tabla.json"
    if not fuente.exists():
        return True
    if not derivado.exists():
        aviso("falta datos/torneo-tabla.json -- la pagina carga el archivo completo "
              "(funciona, pero baja ~20 KB de mas). Generalo con generar_tabla.py")
        return False
    try:
        d = json.loads(derivado.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        error("datos/torneo-tabla.json no parsea")
        return False
    sha = hashlib.sha1(fuente.read_bytes()).hexdigest()
    if d.get("_fuenteSha1") != sha:
        error("datos/torneo-tabla.json quedo ATRAS respecto de datos/torneo.json "
              "-- corre generar_tabla.py")
        return False
    bien("datos/torneo-tabla.json al dia")
    return True


def revisar_portada_derivada() -> bool:
    """datos/torneo-portada.json esta al dia Y le alcanza a HERO_TOP.

    La portada dibuja el promedio del "TOP N" con lo que trae este derivado. Si
    alguien sube HERO_TOP en index.html por encima de los equipos que el
    derivado guarda, el grafico promedia MENOS equipos de los que dice el
    rotulo -- y se ve perfecto, que es lo peligroso. Aca se comparan los dos
    numeros; la pagina ademas se cae sola al archivo completo si detecta el
    desajuste en vivo (ver TOP_MIN en index.html), asi que esto avisa de un
    derroche, no de un dato falso.
    """
    fuente = DATOS / "torneo.json"
    derivado = DATOS / "torneo-portada.json"
    if not fuente.exists():
        return True
    if not derivado.exists():
        aviso("falta datos/torneo-portada.json -- la portada baja el archivo "
              "completo (funciona, pero son 200 KB de mas en cada visita). "
              "Generalo con generar_tabla.py")
        return False
    try:
        d = json.loads(derivado.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        error("datos/torneo-portada.json no parsea")
        return False

    if d.get("_fuenteSha1") != hashlib.sha1(fuente.read_bytes()).hexdigest():
        error("datos/torneo-portada.json quedo ATRAS respecto de datos/torneo.json "
              "-- corre generar_tabla.py")
        return False

    top = d.get("topPortada") or len(d.get("equipos", []))
    indice = RAIZ / "index.html"
    if indice.exists():
        m = re.search(r"var HERO_TOP=(\d+)", indice.read_text(encoding="utf-8"))
        if m and int(m.group(1)) > top:
            error(f"index.html pide un TOP {m.group(1)} pero datos/torneo-portada.json "
                  f"solo trae {top} equipos -- subi TOP_PORTADA en generar_tabla.py "
                  "y volve a correrlo (mientras tanto la portada se cae al "
                  "archivo completo, 200 KB de mas por visita)")
            return False

    bien(f"datos/torneo-portada.json al dia (top {top})")
    return True


def revisar_paginas_equipo(torneo: dict) -> bool:
    """torneo/e/<id>.html existe para cada equipo y con el puesto correcto."""
    carpeta = RAIZ / "torneo" / "e"
    equipos = torneo.get("equipos", [])
    if not equipos:
        return True
    if not carpeta.exists():
        aviso("no existe torneo/e/ -- los links por equipo no tienen vista previa "
              "propia. Generalas con generar_paginas_equipo.py")
        return False

    total = len(equipos)
    esperados = {f"{e['id']}.html" for e in equipos}
    actuales = {p.name for p in carpeta.glob("*.html")}

    faltan = esperados - actuales
    sobran = actuales - esperados
    desfasadas = []
    for eq in equipos:
        p = carpeta / f"{eq['id']}.html"
        if not p.exists():
            continue
        texto = p.read_text(encoding="utf-8")
        # el puesto va en el <title>; si cambio, la vista previa miente
        if f"{eq['posicion']}° de {total}" not in texto:
            desfasadas.append(eq["id"])

    if faltan or sobran or desfasadas:
        if faltan:
            error(f"torneo/e/: faltan {len(faltan)} pagina(s) ({', '.join(sorted(faltan)[:3])}...)")
        if sobran:
            error(f"torneo/e/: sobran {len(sobran)} pagina(s) de equipos que ya no estan "
                  f"({', '.join(sorted(sobran)[:3])}...)")
        if desfasadas:
            error(f"torneo/e/: {len(desfasadas)} pagina(s) con el puesto viejo en la vista "
                  f"previa ({', '.join(desfasadas[:3])}...)")
        error("  -> corre generar_paginas_equipo.py")
        return False

    bien(f"torneo/e/: {total} paginas al dia")
    return True


def revisar_imagenes_og(torneo: dict) -> None:
    """og/equipo-<id>.jpg -- son opcionales, asi que esto solo avisa."""
    equipos = torneo.get("equipos", [])
    if not equipos:
        return
    carpeta = RAIZ / "og"
    sin = [e["id"] for e in equipos if not (carpeta / f"equipo-{e['id']}.jpg").exists()]
    # equipo-*.jpg y no *.jpg: si algun dia cae un og generico en la carpeta, no
    # tiene que denunciarse como huerfano.
    esperadas = {f"equipo-{e['id']}.jpg" for e in equipos}
    actuales = {p.name for p in carpeta.glob("equipo-*.jpg")} if carpeta.exists() else set()
    sobran = sorted(actuales - esperadas)
    if not carpeta.exists() or len(sin) == len(equipos):
        aviso("og/: ningun equipo tiene imagen de vista previa propia -- todos usan "
              "og-image.png. Opcional, ver generar_og_equipos.js")
    elif sin:
        aviso(f"og/: {len(sin)} equipo(s) sin imagen propia ({', '.join(sin[:3])}...) "
              "-- corre node generar_og_equipos.js")
    else:
        bien(f"og/: los {len(equipos)} equipos tienen imagen de vista previa")
    if sobran:
        muestra = ", ".join(sobran[:6]) + ("..." if len(sobran) > 6 else "")
        aviso(f"og/: {len(sobran)} imagen(es) de equipos que ya no compiten "
              f"({muestra}). generar_og_equipos.js nunca borra: sacarlas a mano "
              "(tambien del espejo). Son inertes, ninguna pagina las referencia.")


# Numeros escritos EN PALABRAS que aparecen como "N equipos/teams". El bug
# "Sixty-three" que estuvo meses en en/index.html no lo veia el regex de digitos.
_PALABRAS_NUM = {
    "forty-seven": 47, "forty-eight": 48, "forty-nine": 49, "fifty": 50,
    "fifty-two": 52, "fifty-three": 53, "fifty-four": 54, "fifty-five": 55,
    "fifty-nine": 59, "sixty": 60, "sixty-one": 61, "sixty-three": 63,
    "sixty-five": 65,
}

# Fragmentos de texto (NO numeros de linea: miembros.json se regenera y las
# lineas se mueven) que nombran un numero de equipos a proposito -- citas de
# prensa, hechos acumulados, notas historicas -- y no hay que corregir.
EXCEPCIONES_CONTEO = (
    "capacitó a más de 65 equipos",           # bio de Agustin: hecho acumulado
    "54 equipos y más de 150 estudiantes",    # cita de prensa, Capitulo IV de club.json
    "estuvieron EN ESPERA",                   # _nota historica de equipos_congelados.json
    "TRAYECTORIA DISPONIBLE DESDE LA SEMANA",  # rotulo del grafico del torneo
)

_TAG = re.compile(r"<[^>]+>")


def _blanquear_comentarios(texto: str, es_html: bool) -> str:
    """Deja los comentarios en blanco CONSERVANDO los saltos de linea, para que
    los numeros de linea del reporte sigan calzando. Los .json no llevan
    comentarios; el HTML puede traer /* */ dentro de <style>/<script>."""
    def repl(m):
        return "\n" * m.group(0).count("\n")
    if es_html:
        texto = re.sub(r"<!--.*?-->", repl, texto, flags=re.S)
        texto = re.sub(r"/\*.*?\*/", repl, texto, flags=re.S)
    return texto


def revisar_conteo_equipos(torneo: dict) -> None:
    """Las menciones escritas a mano de "N equipos/teams", la semana y la fecha
    de corte calzan con datos/torneo.json. Cubre texto en espanol y en ingles,
    salta comentarios de codigo y las excepciones historicas declaradas."""
    equipos = torneo.get("equipos", [])
    if not equipos:
        return
    n = len(equipos)
    semana = torneo.get("semana")
    corte = torneo.get("corte") or ""

    num_pat = re.compile(r"\b(\d{2,3})\s+(?:equipos|teams)\b", re.IGNORECASE)
    pal_pat = re.compile(r"\b([a-z]+(?:-[a-z]+)?)\s+(?:student\s+)?teams\b", re.IGNORECASE)
    # semana/week N pero SOLO si "cut"/"corte" aparece cerca (asi no se confunde
    # con "disponible desde la semana 2" y otros rotulos sueltos).
    sem_pat = re.compile(
        r"(?:week|semana)\s+(\d{1,2})\b[^\n]{0,25}\b(?:cut|corte)\b"
        r"|\b(?:cut|corte)\b[^\n]{0,25}(?:week|semana)\s+(\d{1,2})\b",
        re.IGNORECASE)

    # Fecha de corte esperada, en las dos formas que usa el sitio.
    MESES = {"ENE": "January", "FEB": "February", "MAR": "March", "ABR": "April",
             "MAY": "May", "JUN": "June", "JUL": "July", "AGO": "August",
             "SEP": "September", "OCT": "October", "NOV": "November", "DIC": "December"}
    fecha_ok = set()
    mc = re.match(r"\s*(\d{1,2})\s*·\s*([A-Z]{3})\s*·\s*(\d{4})", corte)
    if mc:
        dia, mes3, anio = mc.group(1), mc.group(2), mc.group(3)
        fecha_ok = {f"{mes3}", f"{MESES.get(mes3, '')}"}
    fecha_pat = re.compile(r"\(\s*(?:([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})"
                           r"|(\d{1,2})\s*·\s*([A-Z]{3})\s*·\s*(\d{4}))\s*\)")

    malas = []
    for ruta in sorted(list(RAIZ.rglob("*.html")) + list(DATOS.rglob("*.json"))):
        if ".git" in ruta.parts or ruta.name.endswith(".demo.json"):
            continue
        if (RAIZ / "torneo" / "e") in ruta.parents:      # generadas, salen del JSON
            continue
        # miembros.json es DERIVADO de club.json, que ya se escanea aca mismo:
        # revisarlo dos veces solo duplica cada hallazgo.
        if ruta.name == "miembros.json":
            continue
        try:
            crudo = ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        es_html = ruta.suffix.lower() == ".html"
        texto = _blanquear_comentarios(crudo, es_html)
        for linea_n, linea in enumerate(texto.splitlines(), 1):
            plano = _TAG.sub(" ", linea) if es_html else linea
            if any(exc in plano for exc in EXCEPCIONES_CONTEO):
                continue
            for m in num_pat.finditer(plano):
                if int(m.group(1)) != n:
                    malas.append(f'{rel(ruta)}:{linea_n} dice "{m.group(0).strip()}" (son {n})')
            for m in pal_pat.finditer(plano):
                val = _PALABRAS_NUM.get(m.group(1).lower())
                if val is not None and val != n:
                    malas.append(f'{rel(ruta)}:{linea_n} dice "{m.group(0).strip()}" (son {n})')
            if semana:
                for m in sem_pat.finditer(plano):
                    g = m.group(1) or m.group(2)
                    if g and int(g) != semana:
                        malas.append(f'{rel(ruta)}:{linea_n} habla del corte de la '
                                     f'semana {g} (el corte vigente es la {semana})')
            if fecha_ok:
                for m in fecha_pat.finditer(plano):
                    mes = m.group(1) or m.group(5)
                    if mes and mes not in fecha_ok:
                        malas.append(f'{rel(ruta)}:{linea_n} fecha de corte "{m.group(0)}" '
                                     f'no calza con el corte {corte!r}')

    if malas:
        cuerpo = "\n".join(f"    {m}" for m in malas[:12])
        extra = f"\n    ... y {len(malas) - 12} mas" if len(malas) > 12 else ""
        aviso(f"{len(malas)} mencion(es) de conteo/semana/fecha que no calzan con "
              f"torneo.json:\n{cuerpo}{extra}\n    (algunas pueden ser historicas: "
              "si lo son, agregar el fragmento a EXCEPCIONES_CONTEO)")
    else:
        bien(f"conteo de equipos, semana y fecha de corte: todo dice {n} / semana {semana}")


# Techo del HTML de una pagina, en KB de FUENTE (sin comprimir). Todo va inline
# en este sitio -- CSS, JS y datos de respaldo dentro del mismo archivo --, asi
# que el .html es casi todo el peso critico. Es un aviso, no un error: la idea
# es enterarse cuando una pagina crece, no prohibir que crezca.
# Medicion complementaria y mas fiel en verificar_paginas.js, que mide lo que de
# verdad se transfiere en un navegador; esta corre sin Chrome.
TECHO_HTML_KB = 200


def revisar_peso_html() -> None:
    grandes = []
    for ruta in sorted(RAIZ.rglob("*.html")):
        if ".git" in ruta.parts or (RAIZ / "torneo" / "e") in ruta.parents:
            continue
        kb = ruta.stat().st_size / 1024
        if kb > TECHO_HTML_KB:
            grandes.append((kb, rel(ruta)))
    if grandes:
        aviso(f"paginas por sobre {TECHO_HTML_KB} KB de fuente:")
        for kb, r in sorted(grandes, reverse=True):
            aviso(f"    {r}  {kb:.0f} KB")
    else:
        bien(f"ninguna pagina pasa los {TECHO_HTML_KB} KB de fuente")


def _sitemap_esperado() -> tuple[str, dict[str, pathlib.Path]]:
    """{loc: archivo} que produciria generar_sitemap.py en ESTE repo. Cada repo
    (trabajo y espejo) tiene sus propias paginas, asi que esto se calcula, no se
    escribe a mano -- que era de donde salia el AVISO permanente de 'ausentes'
    en el espejo."""
    sitio = generar_sitemap.SITIO_POR_DEFECTO
    club = DATOS / "club.json"
    if club.exists():
        try:
            cfg = json.loads(club.read_text(encoding="utf-8")).get("config") or {}
            sitio = cfg.get("sitio") or sitio
        except json.JSONDecodeError:
            pass
    sitio = sitio.rstrip("/")
    out: dict[str, pathlib.Path] = {}
    for ruta in sorted(RAIZ.rglob("*.html")):
        r = str(ruta.relative_to(RAIZ)).replace("\\", "/")
        if r.startswith("torneo/e/") or r in generar_sitemap.EXCLUIDAS:
            continue
        publica = r[:-len("index.html")] if r.endswith("index.html") else r
        out[f"{sitio}/{publica}"] = ruta
    return sitio, out


def _archivo_de_loc(loc: str, base: str) -> pathlib.Path:
    """loc -> archivo en disco. loc que termina en '/' es una carpeta
    (-> index.html); loc con un .html al final es esa pagina tal cual."""
    ruta = loc[len(base):].lstrip("/")
    if ruta == "" or ruta.endswith("/"):
        return RAIZ / ruta / "index.html"
    return RAIZ / ruta


def revisar_canonicas() -> None:
    """Cada pagina del sitemap declara SU canonical, una sola, apuntando a su
    propio <loc>. La lista de paginas sale del sitemap, no de un dict a mano.

    El sitio se sirve desde dos dominios (produccion y el espejo de GitHub
    Pages). Sin canonical los dos son, para un buscador, dos copias del mismo
    contenido compitiendo entre si -- y el que gane puede ser el equivocado.
    """
    if generar_sitemap is None:
        aviso("no encuentro generar_sitemap.py -- no puedo revisar canonicals")
        return
    sm = RAIZ / "sitemap.xml"
    if not sm.exists():
        aviso("no hay sitemap.xml -- generalo con generar_sitemap.py (sin el no "
              "se revisan los canonicals)")
        return
    texto_sm = sm.read_text(encoding="utf-8")
    base = generar_sitemap.SITIO_POR_DEFECTO
    m0 = re.search(r"<loc>([^<]+?://[^/<]+)", texto_sm)
    if m0:
        base = m0.group(1)
    malas = []
    locs = re.findall(r"<loc>([^<]+)</loc>", texto_sm)
    for loc in locs:
        f = _archivo_de_loc(loc, base)
        if not f.exists():
            malas.append(f"{rel(f)}: en el sitemap pero no existe el archivo")
            continue
        t = f.read_text(encoding="utf-8")
        n = t.count('rel="canonical"')
        esperado = f'<link rel="canonical" href="{loc}">'
        if n == 0:
            malas.append(f"{rel(f)}: sin canonical")
        elif n > 1:
            malas.append(f"{rel(f)}: {n} canonical (debe haber uno solo)")
        elif esperado not in t:
            malas.append(f"{rel(f)}: el canonical no apunta a {loc}")
    if malas:
        error("canonical --\n" + "\n".join(f"    {x}" for x in malas))
        return
    bien(f"las {len(locs)} paginas del sitemap declaran su canonical")


def revisar_datos_estructurados() -> None:
    """Las redes del JSON-LD de index.html calzan con datos/club.json.

    El bloque JSON-LD esta escrito a mano en el <head> (es dato estable), asi
    que puede quedar desfasado sin que se note: no se ve en pantalla, solo lo
    lee un buscador. Esto es lo unico que evita esa deriva silenciosa.
    """
    f = RAIZ / "index.html"
    texto = f.read_text(encoding="utf-8")
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                  texto, re.S)
    if not m:
        aviso("index.html no trae JSON-LD -- el sitio no se describe a los buscadores")
        return
    try:
        ld = json.loads(m.group(1))
    except Exception:
        error("el JSON-LD de index.html no parsea")
        return
    club = json.loads((DATOS / "club.json").read_text(encoding="utf-8"))
    urls = (club.get("config") or {}).get("urls") or {}
    same = set(ld.get("sameAs") or [])
    faltan = [u for u in (urls.get("linkedin"), urls.get("instagram")) if u and u not in same]
    if faltan:
        error("el JSON-LD de index.html no calza con config.urls de club.json: "
              + ", ".join(faltan))
        return
    bien("el JSON-LD de index.html calza con datos/club.json")


def revisar_respaldo_index() -> None:
    """El literal JS CLUB_DATA embebido en index.html no se quedo atras de
    datos/club.json en nombres ni LinkedIn.

    index.html pinta primero ese respaldo y despues lo pisa con club.json, asi
    que un desfase no se ve en vivo -- pero es doble fuente de verdad: cada
    cambio de cargo hay que hacerlo dos veces, y quien lee el HTML para
    verificar un dato lee el viejo (ya causo una afirmacion equivocada). Es
    AVISO, no ERROR: club.json gana al cargar."""
    idx = RAIZ / "index.html"
    club_p = DATOS / "club.json"
    if not idx.exists() or not club_p.exists():
        return
    m = re.search(r"CLUB_DATA\s*=\s*\{(.*?)\n\s*\};", idx.read_text(encoding="utf-8"), re.S)
    if not m:
        aviso("index.html: no encuentro el literal CLUB_DATA para compararlo con club.json")
        return
    blob = m.group(1)
    try:
        club = json.loads(club_p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    directiva = ((club.get("personas") or {}).get("directiva")) or []
    faltan_nombre, faltan_li = [], []
    for p in directiva:
        nom = p.get("nombre") or ""
        if nom and f'nombre:"{nom}"' not in blob and f"nombre:'{nom}'" not in blob:
            faltan_nombre.append(nom)
            continue
        li = p.get("linkedin")
        if li and li not in blob:
            faltan_li.append(nom)
    partes = []
    if faltan_nombre:
        partes.append(f"    sin ficha en el respaldo: {', '.join(faltan_nombre)}")
    if faltan_li:
        partes.append(f"    con LinkedIn en club.json pero no en el respaldo: {', '.join(faltan_li)}")
    if partes:
        aviso("index.html: el respaldo CLUB_DATA quedo atras de club.json "
              "(club.json gana al cargar, pero es doble fuente de verdad):\n"
              + "\n".join(partes))
    else:
        bien(f"index.html: el respaldo CLUB_DATA calza con club.json ({len(directiva)} fichas)")


def revisar_derivados_seo() -> None:
    """sitemap.xml existe, lista EXACTAMENTE las paginas que generar_sitemap.py
    produciria hoy, no incluye las micro-paginas, y sus <lastmod> no van por
    detras del ultimo commit de cada archivo."""
    sm, rb = RAIZ / "sitemap.xml", RAIZ / "robots.txt"
    if not sm.exists() or not rb.exists():
        aviso("faltan sitemap.xml y/o robots.txt -- generalos con generar_sitemap.py")
        return
    texto = sm.read_text(encoding="utf-8")
    if "/torneo/e/" in texto:
        error("sitemap.xml lista las micro-paginas de equipo, que van con noindex "
              "-- corre generar_sitemap.py")
        return

    if generar_sitemap is None:
        aviso("no encuentro generar_sitemap.py -- solo puedo revisar que exista el sitemap")
        bien(f"sitemap.xml ({texto.count('<url>')} URLs) y robots.txt presentes")
        return

    _, esperadas = _sitemap_esperado()
    en_archivo = set(re.findall(r"<loc>([^<]+)</loc>", texto))
    faltan = sorted(set(esperadas) - en_archivo)
    sobran = sorted(en_archivo - set(esperadas))
    if faltan or sobran:
        detalle = []
        if faltan:
            detalle.append("    faltan: " + ", ".join(faltan))
        if sobran:
            detalle.append("    sobran: " + ", ".join(sobran))
        error("sitemap.xml no calza con las paginas del repo -- corre "
              "generar_sitemap.py:\n" + "\n".join(detalle))
        return

    # <lastmod> por detras del git: el sitemap quedo viejo.
    bloques = re.findall(r"<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?", texto)
    atrasadas = []
    for loc, lastmod in bloques:
        ruta = esperadas.get(loc)
        if not ruta:
            continue
        commit = generar_sitemap.fecha_git(ruta)
        if commit and (not lastmod or lastmod < commit):
            atrasadas.append(f"    {loc}: sitemap {lastmod or '(sin fecha)'} < commit {commit}")
    if atrasadas:
        aviso("sitemap.xml tiene <lastmod> mas viejos que el ultimo commit "
              "(regeneralo con generar_sitemap.py):\n" + "\n".join(atrasadas))
    else:
        bien(f"sitemap.xml ({len(en_archivo)} URLs, fechas al dia) y robots.txt")


def revisar_creadores() -> None:
    """Cada nombre de torneo.creadores tiene ficha en personas.directiva."""
    ruta = DATOS / "club.json"
    if not ruta.exists():
        return
    try:
        club = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    creadores = ((club.get("torneo") or {}).get("creadores")) or []
    if not creadores:
        aviso("datos/club.json no trae torneo.creadores -- la seccion #creadores "
              "de torneo/index.html queda oculta")
        return
    directiva = {p.get("nombre") for p in ((club.get("personas") or {}).get("directiva") or [])}
    huerfanos = [c["nombre"] for c in creadores if c.get("nombre") not in directiva]
    if huerfanos:
        error("torneo.creadores tiene nombres sin ficha en personas.directiva "
              f"(su tarjeta NO se dibuja): {', '.join(huerfanos)}")
    else:
        bien(f"los {len(creadores)} creadores calzan con personas.directiva")


# --------------------------------------------------------------------------
def arreglar() -> None:
    """Regenera SOLO los archivos derivados. Nunca toca datos ni HTML a mano."""
    for script in ("generar_tabla.py", "generar_paginas_equipo.py", "generar_sitemap.py"):
        ruta = RAIZ / script
        if not ruta.exists():
            continue
        print(f"\n$ python {script}")
        subprocess.run([sys.executable, str(ruta)], cwd=RAIZ, check=False)
    print("\n(las imagenes og/ no se regeneran solas: necesitan Chrome y un server "
          "local -- ver node generar_og_equipos.js)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arreglar", action="store_true",
                    help="regenera los archivos derivados y vuelve a revisar")
    args = ap.parse_args()

    torneo = revisar_json()
    revisar_tabla_derivada()
    revisar_portada_derivada()
    revisar_paginas_equipo(torneo)
    revisar_imagenes_og(torneo)
    revisar_conteo_equipos(torneo)
    revisar_creadores()
    revisar_derivados_seo()
    revisar_canonicas()
    revisar_datos_estructurados()
    revisar_respaldo_index()
    revisar_peso_html()

    if args.arreglar and (ERRORES or AVISOS):
        arreglar()
        ERRORES.clear(); AVISOS.clear(); BIEN.clear()
        print("\n--- de nuevo, ya regenerado ---")
        torneo = revisar_json()
        revisar_tabla_derivada()
        revisar_portada_derivada()
        revisar_paginas_equipo(torneo)
        revisar_imagenes_og(torneo)
        revisar_conteo_equipos(torneo)
        revisar_creadores()
        revisar_derivados_seo()
        revisar_canonicas()
        revisar_datos_estructurados()
        revisar_peso_html()

    print()

    def _emitir(etiqueta: str, msg: str) -> None:
        lineas = msg.split("\n")
        print(f"  {etiqueta:<5} {lineas[0]}")
        for cont in lineas[1:]:
            print(f"        {cont}")

    for b in BIEN:
        _emitir("OK", b)
    for a in AVISOS:
        _emitir("AVISO", a)
    for e in ERRORES:
        _emitir("ERROR", e)

    print()
    if ERRORES:
        print(f"{len(ERRORES)} error(es). No publiques asi.")
        return 1
    if AVISOS:
        print(f"Sin errores, {len(AVISOS)} aviso(s) para mirar.")
        return 0
    print("Todo en orden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
