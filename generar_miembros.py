#!/usr/bin/env python3
"""Genera datos/miembros.json, la capa de datos de la sección de Miembros.

Uso:
    python3 generar_miembros.py                          # solo la directiva (semilla)
    python3 generar_miembros.py --excel Miembros_FIG.xlsx
    python3 generar_miembros.py --excel ... --candidatos # además lista a quién falta

FILOSOFÍA (la misma del resto del repo)
---------------------------------------
Nada que se pueda derivar se escribe a mano. Este script FUNDE tres fuentes que
ya existen y una nueva, y ninguna de ellas se duplica:

  1. `datos/club.json` → la DIRECTIVA. Sigue siendo su única fuente de verdad;
     acá solo se lee. Si mañana cambia un rol allá, se refleja acá al regenerar.
  2. El Excel de miembros (Drive) → el resto del club. Es lo único nuevo que
     hay que mantener a mano, y solo trae lo que no se puede derivar.
  3. `datos/torneo.json` → los RESULTADOS de torneo de cada persona, cruzados
     por nombre normalizado y LinkedIn contra los integrantes de cada equipo.
  4. `datos/eventos.json` → las ACTIVIDADES en las que participó, cruzadas
     contra el campo `participantes` de cada evento.

REGLA DURA DE PRIVACIDAD
------------------------
El sitio es público e indexable. Acá NUNCA se escribe RUT, correo, teléfono,
dirección, carrera, año de ingreso a la universidad ni nada que exceda lo que
el proyecto ya tiene aprobado (nombre + rol + LinkedIn público). Si el Excel
trae esas columnas, el script las IGNORA a propósito: existen para que el club
las use puertas adentro en el Drive, no para publicarlas. Y no se alojan PDFs
de CV — decisión de Francisco (2026-08-16): la ficha del miembro ES su CV
público. Un CV real trae RUT y teléfono; publicarlo sería filtrar datos de 60+
personas de una sola vez.

Además cada persona controla qué se muestra con la columna `muestra` (ver
PLANILLA_MIEMBROS_FIG.md). Lo que no esté autorizado no se escribe al JSON —
no basta con ocultarlo en la página, porque el JSON también es público.

EL TICKER
---------
Cada miembro tiene un ticker de 3 letras, como un instrumento. No es un adorno:
es la clave con que se le busca en la página y el ancla de su URL
(`miembros/#FVA`), o sea el link que la persona comparte en LinkedIn. Se deriva
del nombre y el script garantiza que sea único — las iniciales de 2 letras que
usa `club.json` YA colisionan hoy (Benjamín Sáez Molina y Benjamín Solís son
ambos "BS"), y con 60+ personas eso solo empeora.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from generar_torneo import leer_hoja_con_encabezado, normalizar, slug  # noqa: E402

DATOS = RAIZ / "datos"
SALIDA = DATOS / "miembros.json"

# Las 5 áreas, en el mismo orden y con los mismos códigos que los desks de
# §Áreas en index.html. `pagina` solo la tienen las que ya tienen página propia.
# ADM nació el 2026-08-31 y todavía no tiene página ni líder declarado: por
# decisión de Francisco nadie lleva el chip "Dirige el área" en ese desk.
AREAS = [
    {"codigo": "PRT", "nombre": "Portafolio", "pagina": "portafolio/index.html",
     "resumen": "Construcción y gestión de carteras con disciplina de benchmark. Dirige el Torneo Portafolio."},
    {"codigo": "TRD", "nombre": "Trading", "pagina": "trading/index.html",
     "resumen": "Ejecución, análisis técnico y operación en el Laboratorio Bloomberg."},
    {"codigo": "VAL", "nombre": "Valuation", "pagina": "valuation/index.html",
     "resumen": "Research y valorización de compañías reales con metodologías de la industria."},
    {"codigo": "FIW", "nombre": "FEN Investment Woman", "pagina": "fiw/index.html",
     "resumen": "Comunidad de mujeres de FIG: mentoría, referentes y actividades propias."},
    {"codigo": "ADM", "nombre": "Administración",
     "resumen": "Gestión interna, alianzas y la operación que sostiene al resto de los desks."},
]
# Cómo se reconoce el área en el texto libre de `rol`/`detalle` de club.json.
PISTAS_AREA = {
    "PRT": ("portafolio",),
    "TRD": ("trading",),
    "VAL": ("valuation",),
    "FIW": ("fen investment woman", "investment woman", "fiw"),
    "ADM": ("administración", "administracion", "administrativa"),
}
# Orden jerárquico. Determina cómo se apila el organigrama y el orden por defecto.
JERARQUIA = ["Presidente", "Vicepresidente", "Fundador", "Director",
             "Coordinador", "Miembro", "Alumni"]

# NIVELES — los estratos que dibuja el organigrama.
#   0  Núcleo: presidencia, cofundadores y los líderes de cada desk. Es la
#      mesa directiva, siempre visible.
#   1  Dirección del desk: quienes acompañan al líder dentro de su área.
#   2  Segunda línea: analistas junior, encargados administrativos.
#   3  Miembros sin cargo. NO se dibujan en el organigrama a propósito: con
#      200 personas el diagrama vuelve a ser ilegible. Cada desk cierra con
#      una barra "+N miembros" que salta al buscador filtrado por ese desk.
#      El organigrama muestra estructura; el buscador muestra personas.
NIVEL_NUCLEO, NIVEL_DIR, NIVEL_SEGUNDA, NIVEL_BASE = 0, 1, 2, 3
NIVEL_NOMBRE = {0: "Núcleo", 1: "Dirección del desk", 2: "Segunda línea", 3: "Miembros"}

# Cómo se deduce el nivel del texto libre del cargo, en orden de prioridad.
# Se puede sobrescribir con la columna `nivel` de la planilla.
PISTAS_NIVEL = [
    (NIVEL_NUCLEO,  ("presidente", "presidenta", "vicepresidente", "vicepresidenta")),
    (NIVEL_SEGUNDA, ("junior", "analista", "asistente", "ayudante", "administrativo",
                     "practicante", "aprendiz")),
    (NIVEL_DIR,     ("director", "directora", "encargado", "encargada", "subdirector",
                     "subdirectora", "coordinador", "coordinadora", "jefe", "jefa",
                     "lider", "líder", "fundador", "fundadora")),
]

# Columnas que el script lee del Excel. Cualquier otra se ignora en silencio:
# es lo que protege de publicar RUT/correo/teléfono si alguien los agrega.
# Van en forma normalizada (minúsculas, sin tildes, guion bajo por separador),
# porque mapear_columnas() compara contra normalizar(encabezado).
ALIAS_MIEMBROS = {
    "nombre":     ["nombre", "nombre_completo", "miembro", "integrante"],
    "rol":        ["rol", "cargo"],
    "area":       ["area", "desk", "codigo_area"],
    "generacion": ["generacion", "ano_de_ingreso", "ano_ingreso", "ingreso", "cohorte"],
    "estado":     ["estado", "situacion"],
    "linkedin":   ["linkedin", "url_linkedin", "perfil_linkedin"],
    "bio":        ["bio", "biografia", "descripcion", "resena"],
    "hitos":      ["hitos", "trayectoria", "logros"],
    "extras":     ["extras", "aporte", "aportes", "personalizado", "lo_que_quiere_mostrar"],
    "muestra":    ["muestra", "consentimiento", "autoriza", "autorizacion"],
    "ticker":     ["ticker", "sigla"],
    "nivel":      ["nivel", "estrato", "linea"],
    "lidera":     ["lidera", "lider", "encargado_de", "jefatura"],
}
# Lo que cada persona puede autorizar. Sin autorización explícita se asume el
# mínimo: nombre, rol, área y LinkedIn (lo ya aprobado por el proyecto).
MUESTRA_VALIDA = {"foto", "torneo", "actividades", "bio", "extras"}
MUESTRA_POR_DEFECTO = {"foto", "torneo", "actividades", "bio"}

PARTICULAS = {"de", "del", "la", "las", "los", "da", "dos", "van", "von", "y", "san"}


def partes_nombre(nombre):
    """['Juan','Pablo','Díaz','Cerda'] sin partículas ni iniciales sueltas."""
    fuera = []
    for p in re.split(r"\s+", str(nombre or "").strip()):
        p = p.strip(".")
        if not p or p.lower() in PARTICULAS or len(p) == 1:
            continue
        fuera.append(p)
    return fuera


def sin_tildes(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def ticker_base(nombre):
    """3 letras derivadas del nombre. Con 3+ partes, una inicial de cada una
    (Benjamín Sáez Molina → BSM); con 2, la inicial del nombre más las dos
    primeras letras del apellido (Manuel Paz → MPA). Nunca menos de 3."""
    ps = [sin_tildes(p).upper() for p in partes_nombre(nombre)]
    if not ps:
        return "XXX"
    if len(ps) >= 3:
        t = ps[0][0] + ps[1][0] + ps[2][0]
    elif len(ps) == 2:
        t = ps[0][0] + ps[1][:2]
    else:
        t = ps[0][:3]
    t = re.sub(r"[^A-Z]", "", t)
    return (t + "XXX")[:3]


def asignar_tickers(miembros):
    """Ticker único para todos. Ante choque, prueba las siguientes letras del
    último apellido antes de caer a un dígito, para que siga leyéndose como
    sigla y no como código de inventario."""
    usados, fijos = set(), {}
    for m in miembros:  # los tickers puestos a mano en el Excel mandan
        t = (m.get("ticker") or "").strip().upper()
        if t and re.fullmatch(r"[A-Z]{2,4}", t) and t not in usados:
            fijos[m["id"]] = t
            usados.add(t)

    for m in miembros:
        if m["id"] in fijos:
            m["ticker"] = fijos[m["id"]]
            continue
        base = ticker_base(m["nombre"])
        if base not in usados:
            m["ticker"] = base
            usados.add(base)
            continue
        ps = [sin_tildes(p).upper() for p in partes_nombre(m["nombre"])]
        cola = re.sub(r"[^A-Z]", "", ps[-1][1:]) if ps else ""
        for letra in cola + "".join(chr(c) for c in range(65, 91)):
            cand = base[:2] + letra
            if cand not in usados:
                m["ticker"] = cand
                usados.add(cand)
                break
        else:
            for n in range(2, 100):  # red de seguridad, no debería llegar acá
                cand = base[:2] + str(n)
                if cand not in usados:
                    m["ticker"] = cand
                    usados.add(cand)
                    break
    return miembros


def area_de_texto(*textos):
    """Deduce el código de área leyendo el rol/detalle libre de club.json."""
    t = normalizar(" ".join(x or "" for x in textos)).replace("_", " ")
    for codigo, pistas in PISTAS_AREA.items():
        for pista in pistas:
            if normalizar(pista).replace("_", " ") in t:
                return codigo
    return None


def rol_base(rol):
    """'Director · Portafolio' → 'Director'. 'Fundadora' → 'Fundador' (el orden
    jerárquico se calcula sobre la forma canónica, no sobre el género)."""
    r = re.split(r"[·|-]", str(rol or ""))[0].strip()
    canon = {"fundadora": "Fundador", "directora": "Director",
             "presidenta": "Presidente", "vicepresidenta": "Vicepresidente",
             "coordinadora": "Coordinador", "miembra": "Miembro"}
    return canon.get(normalizar(r).replace("_", " "), r or "Miembro")


def orden_jerarquia(rol):
    try:
        return JERARQUIA.index(rol_base(rol))
    except ValueError:
        return len(JERARQUIA)


def nivel_de(rol_completo, explicito=None):
    """En qué estrato del organigrama va esta persona.

    Se lee del texto libre del cargo porque nadie va a llenar una columna
    'nivel' a mano en una planilla de 150 filas — pero si la llena, manda."""
    if explicito not in (None, ""):
        try:
            return max(0, min(NIVEL_BASE, int(explicito)))
        except (TypeError, ValueError):
            pass
    t = normalizar(rol_completo).replace("_", " ")
    for nivel, pistas in PISTAS_NIVEL:
        for p in pistas:
            if normalizar(p).replace("_", " ") in t:
                return nivel
    return NIVEL_BASE


def marcar_lideres(miembros):
    """Elige un líder por desk y lo sube al núcleo.

    El líder es el puente entre las dos lecturas del organigrama: aparece en la
    mesa directiva Y es la raíz de su desk, así que de él bajan los cables. Si
    la planilla no lo dice explícito ('lidera'/'líder'/'encargado de'), se toma
    a la persona de menor nivel y mayor jerarquía del área — con un aviso,
    porque adivinar quién manda es justo lo que no se debe hacer en silencio."""
    for codigo in [a["codigo"] for a in AREAS]:
        del_area = [m for m in miembros if m.get("area") == codigo]
        if not del_area:
            continue
        explicitos = [m for m in del_area if m.get("lidera")]
        if explicitos:
            lider = explicitos[0]
            if len(explicitos) > 1:
                print(f"  AVISO: {codigo} tiene {len(explicitos)} personas marcadas como "
                      f"líder; se usa {lider['nombre']}")
        else:
            # La presidencia NO lidera un desk por el solo hecho de pertenecer a
            # él: preside el club. Si el presidente además dirige un área, hay
            # que decirlo explícito en la planilla.
            candidatos = [m for m in del_area
                          if rol_base(m["rolCompleto"]) not in ("Presidente", "Vicepresidente")]
            if not candidatos:
                for m in del_area:
                    m["lidera"] = None
                continue
            lider = sorted(candidatos, key=lambda m: (m["nivel"],
                                                      orden_jerarquia(m["rolCompleto"]),
                                                      m["nombre"]))[0]
        for m in del_area:
            m["lidera"] = codigo if m is lider else None
        lider["nivel"] = NIVEL_NUCLEO

    # Los cofundadores que no dirigen un desk igual pertenecen al núcleo: el
    # club es suyo aunque no tengan área. Si quedaran en nivel 1 sin desk no se
    # dibujarían en ninguna parte del organigrama, que es peor que cualquier
    # discusión sobre dónde ponerlos.
    for m in miembros:
        if not m.get("area") and rol_base(m["rolCompleto"]) in ("Fundador", "Presidente",
                                                                "Vicepresidente"):
            m["nivel"] = NIVEL_NUCLEO
    return miembros


def parse_lista(v):
    """Un campo del Excel con varios valores: separados por ';' o por salto."""
    if v is None:
        return []
    return [x.strip() for x in re.split(r"[;\n]+", str(v)) if x.strip()]


def desde_club_json():
    """La directiva. `club.json` sigue siendo su fuente de verdad: acá solo se
    lee, nunca se escribe, para no terminar con dos listas que se contradicen."""
    club = json.loads((DATOS / "club.json").read_text(encoding="utf-8"))
    fuera = []
    for p in club.get("personas", {}).get("directiva", []):
        rol = p.get("rol", "")
        detalle = p.get("detalle", "")
        # `liderArea` es un campo opcional de club.json: quien dirige un desk
        # de verdad no se puede adivinar por jerarquia/orden alfabetico (eso
        # fue lo que eligio mal a Agustin Arriagada en vez de a Francisco
        # Valenzuela como lider de Portafolio). Se declara explicito ahi,
        # persona por persona, y solo aplica si calza con su propia area.
        lider_area = p.get("liderArea")
        area_persona = area_de_texto(rol, detalle)
        fuera.append({
            "id": slug(p["nombre"]),
            "nombre": p["nombre"].strip(),
            "rol": rol_base(rol),
            "rolCompleto": rol,
            "nivel": nivel_de(rol + " " + detalle),
            "lidera": lider_area if lider_area == area_persona else None,
            "area": area_persona,
            "detalle": detalle,
            "generacion": None,
            "estado": "activo",
            "linkedin": p.get("linkedin", ""),
            "perfil": p.get("perfil") or {},
            "extras": [],
            "muestra": sorted(MUESTRA_POR_DEFECTO | {"extras"}),
            "fuente": "club.json",
            "ticker": p.get("ticker", ""),
        })
    return fuera


def desde_excel(ruta):
    """El resto del club. Solo se leen las columnas de ALIAS_MIEMBROS: si la
    planilla trae RUT, correo o teléfono, no llegan nunca al JSON."""
    filas, mapa = leer_hoja_con_encabezado(str(ruta), None, ALIAS_MIEMBROS)
    if not filas:
        sys.exit(f"No pude leer filas de {ruta}. ¿La primera hoja tiene encabezados?")
    ignoradas = [k for k in ALIAS_MIEMBROS if k not in mapa]
    if ignoradas:
        print(f"  AVISO: columnas no encontradas en el Excel (quedan vacías): {ignoradas}")

    fuera = []
    for fila in filas:
        def val(k, f=fila, m=mapa):
            v = f[m[k]] if k in m and m[k] < len(f) else None
            return str(v).strip() if v not in (None, "") else ""
        nombre = val("nombre")
        if not nombre:
            continue
        muestra = {x.lower() for x in parse_lista(val("muestra"))} & MUESTRA_VALIDA
        gen = re.search(r"\d{4}", val("generacion"))
        rol = val("rol") or "Miembro"
        estado = normalizar(val("estado")).replace("_", " ") or "activo"
        fuera.append({
            "id": slug(nombre),
            "nombre": nombre,
            "rol": rol_base(rol),
            "rolCompleto": rol,
            "nivel": nivel_de(rol, val("nivel")),
            "lidera": val("area").upper()[:3] if normalizar(val("lidera")) in
                      ("si", "x", "1", "true", "lidera") else None,
            "area": (val("area").upper()[:3] or area_de_texto(rol)) or None,
            "detalle": "",
            "generacion": int(gen.group(0)) if gen else None,
            "estado": estado if estado in ("activo", "alumni", "pausa") else "activo",
            "linkedin": val("linkedin"),
            "perfil": {"bio": val("bio"), "hitos": parse_lista(val("hitos"))},
            "extras": [{"texto": x} for x in parse_lista(val("extras"))],
            "muestra": sorted(muestra or MUESTRA_POR_DEFECTO),
            "fuente": "excel",
            "ticker": val("ticker"),
        })
    return fuera


def tokens(nombre):
    """{'jhosep','garcia'} — para comparar nombres escritos de formas distintas."""
    return {sin_tildes(p).lower() for p in partes_nombre(nombre)}


def indice_torneo():
    """Los 149 integrantes inscritos, indexados de tres formas.

    El calce NO puede ser literal: el Excel de inscripciones trae la
    capitalización despareja ('Isabel rojas aravena') y, sobre todo, el nombre
    civil completo, mientras `club.json` usa la forma corta con que la persona
    se presenta. Caso real: Jhosep García está inscrito como 'Jhosep Gabriel
    García Suarez'. Por eso además del calce exacto y del LinkedIn hay un tercer
    intento por subconjunto de tokens (ver calzar_torneo)."""
    ruta = DATOS / "torneo.json"
    if not ruta.exists():
        return {}, {}, []
    t = json.loads(ruta.read_text(encoding="utf-8"))
    por_nombre, por_linkedin, inscritos = {}, {}, []
    for eq in t.get("equipos", []):
        dato = {"equipo": eq["nombre"], "equipoId": eq["id"],
                "posicion": eq["posicion"], "puntos": eq["puntos"],
                "retRel": eq.get("retRel"), "semana": t.get("semana"),
                "corte": t.get("corte")}
        for m in eq.get("miembros", []):
            nombre = (m.get("nombre") or "").strip()
            n = normalizar(nombre)
            if n:
                por_nombre.setdefault(n, dato)
                inscritos.append((nombre, tokens(nombre), dato))
            li = (m.get("linkedin") or "").rstrip("/").lower()
            if li:
                por_linkedin.setdefault(li, dato)
    return por_nombre, por_linkedin, inscritos


def calzar_torneo(miembro, por_nombre, por_linkedin, inscritos):
    """Devuelve (dato_del_equipo, cómo_calzó) o (None, motivo).

    El tercer intento exige que TODOS los tokens del nombre corto estén en el
    nombre largo y que el primer nombre sea el mismo. Sin esa exigencia,
    compartir un apellido común bastaría: 'Manuel Paz' calzaría con 'Victoria
    Paz Tapia Rivera' y 'Francisco Valenzuela' con 'Lucas Daniel Valenzuela
    Pavez' — dos errores que este criterio efectivamente descarta. Si el
    subconjunto calza con más de un inscrito, no se asigna nada: un dato
    ambiguo es peor que un dato ausente."""
    n = normalizar(miembro["nombre"])
    if n in por_nombre:
        return por_nombre[n], "nombre exacto", miembro["nombre"]

    li = (miembro.get("linkedin") or "").rstrip("/").lower()
    if li and li in por_linkedin:
        return por_linkedin[li], "linkedin", None

    mis = tokens(miembro["nombre"])
    if len(mis) < 2:
        return None, "nombre demasiado corto para calzar sin riesgo", None
    primero = sin_tildes(partes_nombre(miembro["nombre"])[0]).lower()
    cands = [(nom, dato) for nom, toks, dato in inscritos
             if mis <= toks and sin_tildes(nom.split()[0]).lower() == primero]
    equipos = {d["equipoId"] for _, d in cands}
    if len(equipos) == 1:
        return cands[0][1], f"subconjunto de «{cands[0][0]}»", cands[0][0]
    if len(equipos) > 1:
        return None, f"AMBIGUO: calza con {sorted(equipos)}", None
    return None, "no está inscrito", None


def indice_eventos():
    """{nombre_normalizado: [ids de evento]}. Hoy `participantes` está vacío en
    los 10 eventos, así que esto no devuelve nada todavía — el cruce queda listo
    y las fichas se llenan solas en cuanto alguien complete ese campo."""
    ruta = DATOS / "eventos.json"
    if not ruta.exists():
        return {}
    e = json.loads(ruta.read_text(encoding="utf-8"))
    eventos = e.get("eventos", e) if isinstance(e, dict) else e
    fuera = {}
    for ev in eventos:
        for p in ev.get("participantes") or []:
            nombre = p.get("nombre") if isinstance(p, dict) else p
            n = normalizar(nombre or "")
            if n:
                fuera.setdefault(n, []).append(ev["id"])
    return fuera


def enriquecer(miembros, verbose=False):
    """Cuelga de cada miembro lo que se puede derivar de los otros JSON."""
    por_nombre, por_linkedin, inscritos = indice_torneo()
    ev = indice_eventos()
    con_torneo = con_actividades = 0
    bitacora, representados = [], set()
    for m in miembros:
        if "torneo" in m["muestra"]:
            dato, como, inscrito = calzar_torneo(m, por_nombre, por_linkedin, inscritos)
            if dato:
                m["torneo"] = dato
                con_torneo += 1
            if inscrito:
                representados.add(normalizar(inscrito))
            bitacora.append((m["nombre"], como if dato else "—", dato))
            if "AMBIGUO" in como:
                print(f"  AVISO: {m['nombre']} → {como} (no se le asignó equipo)")
        if "actividades" in m["muestra"] and ev.get(normalizar(m["nombre"])):
            m["actividades"] = ev[normalizar(m["nombre"])]
            con_actividades += 1
        if "bio" not in m["muestra"]:
            m["perfil"] = {}
        if "extras" not in m["muestra"]:
            m["extras"] = []
    if verbose:
        print("\n  CALCE CON EL TORNEO (auditoría):")
        for nombre, como, dato in bitacora:
            eq = f"{dato['equipo']} ({dato['posicion']}°)" if dato else "sin equipo"
            print(f"    {nombre:30s} {eq:32s} {como}")
    return con_torneo, con_actividades, representados


def candidatos_sin_ficha(miembros, representados=frozenset()):
    """Integrantes del torneo que todavía no están en la base de miembros.
    Sirve para que la planilla del Drive no arranque en blanco: son personas
    reales, con nombre tal como lo escribieron al inscribirse.

    `representados` trae los nombres inscritos que ya calzaron con una ficha
    aunque estén escritos distinto (ej. 'Jhosep Gabriel García Suarez' ya es
    Jhosep García), para no proponerlos como si faltaran."""
    conocidos = {normalizar(m["nombre"]) for m in miembros} | set(representados)
    t = json.loads((DATOS / "torneo.json").read_text(encoding="utf-8"))
    fuera = {}
    for eq in t.get("equipos", []):
        for m in eq.get("miembros", []):
            n = normalizar(m.get("nombre", ""))
            if n and n not in conocidos and n not in fuera:
                fuera[n] = (m["nombre"].strip(), eq["nombre"], m.get("linkedin", ""))
    return sorted(fuera.values(), key=lambda x: x[0].lower())


# ---------------------------------------------------------------------------
# MODO DEMO — para ver cómo se verá el organigrama cuando el club esté cargado
# ---------------------------------------------------------------------------
# Escribe datos/miembros.demo.json, un archivo APARTE que la página solo carga
# con ?demo=1. Nada de esto entra jamás a datos/miembros.json: la regla dura
# del repo es que no se publica nada inventado, y este archivo mezcla personas
# reales con personas que no existen. Cada ficticia lleva `demo:true`, la
# página les pinta un distintivo FICTICIO y muestra un aviso permanente.
#
# Los cargos de las personas REALES en este archivo tampoco son oficiales: son
# el supuesto que pidió Francisco el 2026-08-16 para poder ver el diseño
# (él como líder de Portafolio, Agustín en dirección técnica, Samuel en
# Valuation, Delia en FIG Woman). No usarlos como fuente de nada.

CARGOS_DEMO = {
    "francisco-valenzuela":     ("Director · Portafolio", "PRT", 0, True),
    "agustin-arriagada":        ("Director Técnico · Portafolio", "PRT", 1, False),
    "benjamin-solis":           ("Director de Torneo · Portafolio", "PRT", 1, False),
    "benjamin-disi":            ("Director Académico · Portafolio", "PRT", 1, False),
    "jhosep-garcia":            ("Vicepresidente", "VAL", 0, True),
    "samuel-rodriguez-arnolds": ("Directivo · Valuation", "VAL", 1, False),
    "delia-avilan":             ("Encargada · FEN Investment Woman", "FIW", 0, True),
    "gabriela-dominguez":       ("Directora de Comunidad · FIW", "FIW", 1, False),
    "victoria-espinoza":        ("Directora de Mentorías · FIW", "FIW", 1, False),
    "manuel-paz":               ("Director · Portafolio y Trading", "TRD", 0, True),
    "rafael-aliendre":          ("Directivo · Trading", "TRD", 1, False),
    "juan-pablo-diaz-cerda":    ("Directivo · Trading", "TRD", 1, False),
    # Juan José Limari ya no pertenece a Trading (2026-08-31): queda como
    # fundador sin desk, así que no va en esta tabla.
    "benjamin-saez-molina":     ("Presidente", "ADM", 0, False),
}
# (nombre, cargo, área, nivel). Personas que NO existen.
FICTICIOS_DEMO = [
    ("Camila Ossandón Vera",   "Analista Junior · Portafolio",      "PRT", 2),
    ("Tomás Iriarte Prado",    "Analista Junior · Portafolio",      "PRT", 2),
    ("Josefa Meneses Lira",    "Coordinadora Administrativa · ADM", "ADM", 2),
    ("Ignacio Ferrada Soto",   "Analista Junior · Trading",         "TRD", 2),
    ("Antonia Bulnes Reyes",   "Asistente de Mesa · Trading",       "TRD", 2),
    ("Martín Zúñiga Alcaíno",  "Analista Junior · Valuation",       "VAL", 2),
    ("Emilia Cortés Vidal",    "Analista Junior · Valuation",       "VAL", 2),
    ("Florencia Aguirre Ruiz", "Coordinadora de Mentorías · FIW",   "FIW", 2),
    ("Isidora Palma Correa",   "Analista Junior · FIW",             "FIW", 2),
    # Base sin cargo: no se dibujan en el organigrama, alimentan el contador
    # "+N miembros" de cada desk. Están para probar justamente ese corte.
    ("Diego Salazar Muñoz",    "Miembro", "PRT", 3),
    ("Javiera Rojas Peña",     "Miembro", "PRT", 3),
    ("Nicolás Vergara Toro",   "Miembro", "PRT", 3),
    ("Catalina Núñez Silva",   "Miembro", "PRT", 3),
    ("Matías Herrera Lagos",   "Miembro", "TRD", 3),
    ("Fernanda Castro Díaz",   "Miembro", "TRD", 3),
    ("Joaquín Pinto Salas",    "Miembro", "VAL", 3),
    ("Valentina Soto Cáceres", "Miembro", "VAL", 3),
    ("Amanda Riquelme Ortiz",  "Miembro", "FIW", 3),
]


def demo(miembros):
    """Devuelve una copia de la lista con los cargos supuestos y las personas
    ficticias agregadas. No toca la lista original."""
    import copy
    out = copy.deepcopy(miembros)
    for m in out:
        m["demo"] = False
        m["lidera"] = None  # se vuelve a decidir con los cargos supuestos
        if m["id"] in CARGOS_DEMO:
            rol, area, nivel, lidera = CARGOS_DEMO[m["id"]]
            m["rolCompleto"] = rol
            m["rol"] = rol_base(rol)
            m["area"] = area
            m["nivel"] = nivel
            m["lidera"] = area if lidera else None
        if not m.get("generacion"):
            m["generacion"] = 2025  # supuesto, solo para ver el chip en la ficha
    for nombre, rol, area, nivel in FICTICIOS_DEMO:
        out.append({
            "id": slug(nombre), "nombre": nombre,
            "rol": rol_base(rol), "rolCompleto": rol,
            "nivel": nivel, "lidera": None, "area": area, "detalle": "",
            "generacion": 2026 if nivel >= 2 else 2025, "estado": "activo",
            "linkedin": "", "perfil": {"bio": "", "hitos": []}, "extras": [],
            "muestra": sorted(MUESTRA_POR_DEFECTO), "fuente": "demo",
            "ticker": "", "demo": True,
        })
    return out


def ordenar(miembros):
    """Núcleo primero, después por desk, nivel, jerarquía y nombre."""
    miembros.sort(key=lambda m: (m.get("nivel", NIVEL_BASE),
                                 orden_jerarquia(m["rolCompleto"]),
                                 m.get("area") or "ZZZ", m["nombre"]))
    return miembros


def volcar(miembros, es_demo=False):
    datos = {
        "actualizado": date.today().isoformat(),
        "demo": es_demo,
        "config": {
            "areas": AREAS,
            "jerarquia": JERARQUIA,
            "niveles": NIVEL_NOMBRE,
            "nota": ("ARCHIVO DE DEMOSTRACIÓN: mezcla personas reales con cargos "
                     "SUPUESTOS y personas que NO EXISTEN (`demo:true`). Solo se carga "
                     "con ?demo=1 y sirve para ver el diseño del organigrama lleno. "
                     "No usar como fuente de nada." if es_demo else
                     "Generado por generar_miembros.py. No editar a mano: los cambios "
                     "se pierden al regenerar. La directiva se edita en club.json; "
                     "el resto, en el Excel de miembros del Drive."),
        },
        "miembros": miembros,
    }
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--excel", help="Excel de miembros del Drive (ver PLANILLA_MIEMBROS_FIG.md)")
    ap.add_argument("--candidatos", action="store_true",
                    help="lista los integrantes del torneo que aún no tienen ficha")
    ap.add_argument("--auditar", action="store_true",
                    help="muestra cómo calzó cada miembro con el torneo")
    ap.add_argument("--csv-candidatos", metavar="RUTA",
                    help="escribe los candidatos como CSV con las columnas de la "
                         "planilla ya puestas, para abrirlo en Sheets y completarlo. "
                         "Guardarlo FUERA del repo: trae 145 nombres y LinkedIn que "
                         "todavía no han autorizado publicación")
    ap.add_argument("--demo", action="store_true",
                    help="escribe TAMBIÉN datos/miembros.demo.json con cargos supuestos "
                         "y personas ficticias, para ver el organigrama lleno "
                         "(la página lo carga solo con ?demo=1)")
    args = ap.parse_args()

    miembros = desde_club_json()
    print(f"  directiva desde club.json: {len(miembros)}")
    if args.excel:
        ruta = Path(args.excel)
        if not ruta.exists():
            sys.exit(f"No existe: {ruta}")
        extra = desde_excel(ruta)
        conocidos = {m["id"] for m in miembros}
        nuevos = [m for m in extra if m["id"] not in conocidos]
        # Si alguien está en ambos lados manda club.json, pero el Excel puede
        # completarle los datos que allá no existen (generación, estado, extras).
        por_id = {m["id"]: m for m in miembros}
        for m in extra:
            base = por_id.get(m["id"])
            if not base:
                continue
            for campo in ("generacion", "estado", "extras", "muestra"):
                if m.get(campo):
                    base[campo] = m[campo]
        miembros += nuevos
        print(f"  miembros desde el Excel: {len(extra)} ({len(nuevos)} nuevos)")

    asignar_tickers(miembros)
    marcar_lideres(miembros)
    ordenar(miembros)
    con_torneo, con_act, representados = enriquecer(miembros, verbose=args.auditar)

    SALIDA.write_text(volcar(miembros), encoding="utf-8")

    print(f"\n  total: {len(miembros)} miembros")
    print(f"  con resultado de torneo cruzado: {con_torneo}")
    print(f"  con actividades cruzadas: {con_act}"
          + ("  (el campo `participantes` de eventos.json está vacío)" if not con_act else ""))
    por_area = {}
    for m in miembros:
        por_area[m.get("area") or "sin área"] = por_area.get(m.get("area") or "sin área", 0) + 1
    print(f"  por área: {por_area}")
    print(f"\nESCRITO: {SALIDA}")

    if args.demo:
        d = demo(miembros)
        asignar_tickers(d)
        marcar_lideres(d)
        ordenar(d)
        enriquecer(d)
        ruta = DATOS / "miembros.demo.json"
        ruta.write_text(volcar(d, es_demo=True), encoding="utf-8")
        ficticios = sum(1 for m in d if m.get("demo"))
        print(f"\nESCRITO: {ruta}")
        print(f"  {len(d)} personas ({ficticios} FICTICIAS, {len(d)-ficticios} reales "
              f"con cargos supuestos)")
        for codigo in [a["codigo"] for a in AREAS]:
            g = [m for m in d if m.get("area") == codigo]
            lid = next((m["nombre"] for m in g if m.get("lidera")), "—")
            niveles = {}
            for m in g:
                niveles[m["nivel"]] = niveles.get(m["nivel"], 0) + 1
            print(f"  {codigo}: lidera {lid:26s} niveles {dict(sorted(niveles.items()))}")
        print("  Verlo en: miembros/index.html?demo=1")

    if args.candidatos or args.csv_candidatos:
        cands = candidatos_sin_ficha(miembros, representados)
        if args.candidatos:
            print(f"\nINTEGRANTES DEL TORNEO SIN FICHA ({len(cands)}) — insumo para la planilla:")
            for nombre, equipo, li in cands:
                print(f"  {nombre:38s} | {equipo:28s} | {li}")
        if args.csv_candidatos:
            escribir_csv_candidatos(Path(args.csv_candidatos), cands)


def escribir_csv_candidatos(ruta, cands):
    """CSV con los encabezados que espera generar_miembros.py --excel, para
    abrirlo en Sheets, completar las columnas vacías y devolverlo como planilla.

    Se escribe con BOM (utf-8-sig) porque si no, Excel en Windows abre las
    tildes rotas y alguien "arregla" los nombres a mano.

    OJO: este archivo NO va al repo. Son 145 personas que aún no han
    autorizado nada; hasta que llenen su columna `muestra`, el listado es un
    insumo interno del club y vive en el Drive, no en un sitio público."""
    import csv
    columnas = ["nombre", "rol", "area", "generacion", "estado", "linkedin",
                "bio", "hitos", "extras", "muestra", "ticker"]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(columnas + ["equipo_torneo_2026"])
        for nombre, equipo, li in cands:
            w.writerow([nombre, "", "", "", "activo", li, "", "", "", "", "", equipo])
    print(f"\nESCRITO: {ruta}  ({len(cands)} filas)")
    print("  Ábrelo en Google Sheets, completa las columnas vacías y súbelo al Drive.")
    print("  La columna equipo_torneo_2026 es solo de referencia: el script la ignora")
    print("  y el equipo lo vuelve a cruzar solo desde torneo.json.")


if __name__ == "__main__":
    main()
