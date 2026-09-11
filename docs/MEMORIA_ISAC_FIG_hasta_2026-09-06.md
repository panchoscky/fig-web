# Memoria de Isac sobre fig-web — archivo hasta el 2026-09-06

> Extraido de la ficha de memoria `project_fig_web.md` el 2026-09-11, cuando
> tenia **921 lineas** y se habia vuelto una bitacora en vez de una memoria.
> Se archiva aca **tal cual**: nada se perdio.
>
> **Esto es historia, no estado.** Varias cosas de aca ya NO son ciertas: se
> escribio entre agosto y el 6 de septiembre, y dice cosas como "semana 14,
> 59 equipos" o "54 equipos" (hoy son 48 y semana 16). Para el estado vigente
> esta la ficha nueva; para el POR QUE de una decision, `docs/BITACORA.md`,
> que cubre las mismas tandas con el registro del repo.
>
> **Una advertencia concreta**: aca aparece como pendiente "habilitar el link
> de FIW en el nav del repo de Manuel". Eso quedo **invertido** el 2026-08-30,
> cuando Francisco decidio que FIG Woman NO se publica en el espejo, y hoy hay
> un script dedicado a sacarla (`despublicar_fiw.py`). No lo "resuelvas".

**Repo:** `fig-web`, clonado en
`C:\Users\fcova\OneDrive\Documentos\GitHub\fig-web`.

Sitio web de **FEN Investment Group (FIG)**, club de inversiones de la FEN —
Universidad de Chile. Francisco es cofundador (junto a Manuel Paz, crédito
en el footer de todas las páginas). HTML/CSS/JS planos sin build step ni
framework (compatibilidad GitHub Pages), datos en JSON bajo `datos/`
generados desde Excel/Drive vía scripts Python — nunca hardcodear datos que
cambian seguido directo en el HTML.

Piezas principales: `index.html` (sitio principal), `eventos/` (bitácora),
`torneo/` (ranking en vivo del Torneo Portafolio 2026, 48 equipos, con
gráficos, comparador de equipos, replay animado, y `pantalla.html` para TVs
de la facultad), `valuation/` y `trading/` (páginas de área, las dos la MISMA plantilla — al
cambiar una, mirar si aplica a la otra). `portafolio/` se separó de esa
plantilla a propósito y desde el 2026-09-02 tiene **paleta propia**: azul
`#08213F` + naranja `#EC7000` de Itaú (decisión de la directiva). **El grafito
`#22252B` de BlackRock que tuvo al principio ya no existe**: era el token `--graph`
y se eliminó el 2026-09-04 (ver más abajo). Desde ese día son **tres** las páginas
con paleta propia: `fiw/`, `portafolio/` y `trading/` (rojo XTB). Solo se publicó
en fig-web; el espejo no se tocó.
`fiw/` (FIG Woman, aún con enlaces deshabilitados a la espera de colores
de marca), `postula/`
(postulación al club), `juego/` (runner "El Rally del Toro") y `desafio/`
(trivia de finanzas, 348 preguntas).

**Why:** la documentación del repo trae un historial día a día muy
detallado de decisiones y pedidos de Francisco — es la fuente de verdad del
estado del proyecto, más confiable que lo que yo recuerde de memoria.

**How to apply:** Antes de tocar el repo, leer `CLAUDE.md` y
`HOJA_DE_RUTA_FIG.md` (lista maestra de backlog) para no repetir trabajo ni
contradecir decisiones ya tomadas. Ver también [[project-ordis]] para el
otro repo activo de Francisco.

> ⚠️ **`CLAUDE.md` se partió el 2026-09-02** (commit `cac21ca`). Eran 2063
> líneas que se cargaban enteras en cada sesión (~30 mil tokens); quedó en
> 251 (~4 mil). **Todas las referencias de este archivo a "la sección X del
> `CLAUDE.md` del repo" ahora apuntan a `docs/BITACORA.md`**, que tiene las
> tandas fechadas tal cual (nada se perdió, cobertura verificada 2063/2063).
> También hay `docs/ARBOL_REPO.md` (qué hace cada archivo) y
> `docs/ESTADO_PIEZAS.md` (estado página por página). El `CLAUDE.md` nuevo
> conserva reglas duras, rutina semanal, pendientes y una sección
> **"Trampas conocidas"** que destila las lecciones vigentes de las tandas.
> Ver [[herramientas-claude-fig]].

## Segundo repo: espejo de Manuel Paz (deploy real)

Existe un **segundo repo**, público, `mpazq-afk/mpazq-afk.github.io`
(tiene el `CNAME` — es el que realmente sirve la web en producción bajo
dominio propio, vía GitHub Pages). `panchoscky/fig-web` es el repo de
trabajo de Francisco; Manuel es dueño del repo de deploy. Se puede clonar
sin token (es público) pero **no siempre hay permiso de push** ahí —
depende de la sesión/cuenta.

La sincronización entre ambos repos es manual y unidireccional por tramos
(a veces fig-web → repo de Manuel, a veces al revés si Manuel corrigió algo
ahí primero, ej. un bug de integrantes duplicados en `generar_torneo.py`
que solo estaba arreglado en el repo de Manuel). **Antes de sobrescribir
archivos entre ambos repos, comparar de nuevo — no asumir que uno es
siempre la fuente de verdad.**

**Why:** confundir cuál repo es la fuente de verdad de un archivo dado
puede pisar un fix que solo existe en el otro lado.

**How to apply:** si Francisco pide "actualizar la web" o "subir esto a
producción", preguntar/verificar si aplica a `panchoscky/fig-web`, al repo
de Manuel, o a ambos.

**Desde el 2026-08-28 hay `sincronizar_espejo.py` en fig-web: usarlo, no
copiar archivos a mano.** Sabe qué se copia, qué no y qué difiere a
propósito, y nunca borra nada del espejo. Lo escribí porque el espejo ya
había divergido sin que nadie lo notara (producción servía fotos de julio).
Dos archivos NUNCA se pisan: `index.html` (el nav del espejo no tiene
Miembros ni FIG Woman) y `MAPA_CONTENIDO_FIG.html` (tiene scripts propios).
**Al portar un cambio de `index.html` a mano, ojo: casi siempre toca TRES
tramos separados — el `<style>`, el markup y el `<script>` — y portar solo
uno deja producción a medias.** Me pasó: las cifras del hero llegaron sin su
CSS ni su markup, y lo detectó un `curl` al sitio publicado, no una prueba
local.

## Corte semanal del torneo: cómo se publica (verificado 2026-08-14)

Un corte se publica **solo con el Excel oficial**, sin Bloomberg ni el
`data.json` del repo de [[project-torneo-bloomberg]]:

```
python generar_torneo.py --excel <Excel_Oficial_FIG_PORT_AAAA-MM-DD.xlsx> \
    --semana N --corte "DD · MMM · AAAA"
```
**Sin `--inscripciones`** (el script conserva los integrantes del `torneo.json`
anterior; pasarlo reintroduce el bug de duplicados ya corregido a mano).
Después: commit en `panchoscky/fig-web` **y copiar el mismo `datos/torneo.json`
a `mpazq-afk.github.io`**, que es el que sirve producción. El 2026-08-14 sí
hubo permiso de push a ese repo.

Semanas publicadas hasta el **2026-08-14: semana 14** (corte 14-ago, 59
equipos, historial s5→s14).

**El paso `incorporar_congelados.py` YA NO aplica** (era obligatorio 23→26-ago).
El 2026-08-26 la directiva eliminó en definitiva a los 5 equipos; el script quedó
dormido y `equipos_congelados.json` vacío. Un corte normal ahora es solo
`generar_torneo.py` → 54 equipos. Ver §"Los 5 equipos 'en espera'" abajo.

**Python en esta máquina (actualizado 2026-09-03):** Python 3.12.10 en
`%LOCALAPPDATA%\Programs\Python\Python312\` con `openpyxl` 3.1.5, `av` 18.1.0 y
`Pillow` 12.3.0. El **2026-09-03 Francisco instaló el "Python Install Manager"**
(PyManager, MSIX de python.org, v26.3) que puso **`python`, `python3` y `py` en
el PATH** — ya NO hace falta la ruta completa, basta `python script.py`. Las tres
apuntan hoy al 3.12 con las deps. Comandos de gestión: `pymanager install <ver>`,
`pymanager list`. **Ojo**: si algún día se instala otra versión con `pymanager` y
pasa a ser la default, `python` pelado apuntaría a un runtime SIN esas deps —
las deps viven en el 3.12. **`PYTHONUTF8=1` ya está en el `env` de `~/.claude/settings.json`** (agregado
2026-09-03), así que TODO `python …` en la tool Bash sale en UTF-8 sin prefijo —
ya no hace falta `PYTHONUTF8=1 python …`. (Si Francisco corre `! python` en su
propia consola sí lo necesita, o `setx PYTHONUTF8 1` una vez.)

## Informes de traspaso entre sesiones

Francisco guarda informes de traspaso de sesiones remotas de Claude Code en
`C:\Users\fcova\OneDrive\Documentos\Claude Francisco\` (ej.
`informe_traspaso_sesion.md`). Vale la pena revisar esa carpeta al empezar
a trabajar en fig-web — puede traer decisiones pendientes, ramas sin PR, o
trabajo a medio terminar que no está en `HOJA_DE_RUTA_FIG.md` todavía.

Del informe del 2026-08-14 (puede estar desactualizado, verificar contra
el repo):
- Rama `claude/video-pantalla-facultad` (video para TVs de la facultad,
  `torneo/pantalla-facultad.html`) — **sin PR abierto**, esperando visto
  bueno de Francisco.
- ~~Evento "Charla con Roberto Bonifaz" (2026-08-11) pendiente de replicar
  al repo de Manuel~~ — **HECHO el 2026-08-14**: se copiaron las 18 fotos de
  `fotos/eventos/charla-roberto-bonifaz-2026/` (más `logos/fen.png`, que
  faltaba y usa `torneo/pantalla.html`) y se pushearon a `mpazq-afk` main.
  Sí hubo permiso de push esa vez.
- Decisión pendiente: extender el fix de limpieza de `/index.html` en la
  URL (hoy solo en `juego/index.html` y `desafio/index.html`) a las otras
  9 páginas del sitio — Francisco no ha confirmado si quiere eso.
- Post de LinkedIn sobre la charla, redactado pero no publicado, texto
  solo vive en el historial de esa conversación (no en un archivo).

## Fix del link roto de "Bases del Torneo Portafolio" (2026-08-23)

El botón "Descargar las bases" / "Bases de evaluación (PDF)" apuntaba a
`https://mpazq-afk.github.io/torneoportafolio2026/documentos/Bases_finales_torneo_portafolio_2026.pdf`,
una ruta que **nunca existió** en el repo de deploy (404). Francisco subió
el PDF real a Drive, en `WEB/fen-investments-web/torneoportafolio2026/documentos/`
del Drive — que en la estructura de `FIG Web — Contenido editable` corresponde
a `02_Areas/PORTAFOLIO/Bases_finales_torneo_portafolio_2026.pdf` (Drive file id
`1b-P5qcStC2rtDXRAQ2Rs6VqQ7kwVqUBp`). Se copió a `documentos/` en el repo
`panchoscky/fig-web` (ruta local) y se corrigieron 3 referencias:
`CONFIG.urls.bases` en `index.html`, `config.urls.bases` en `datos/club.json`
(que es lo que realmente pisa el CONFIG hardcodeado en runtime — ver
`applyLinks()` e `index.html:1816-1820`), y el `<a href>` directo en
`torneo/index.html`. **Ya committeado y pusheado a ambos repos** (Francisco
confirmó) — `panchoscky/fig-web` commit `50e9656`, `mpazq-afk/mpazq-afk.github.io`
commit `861638b`, ambos a `main`. Sí hubo permiso de push a `mpazq-afk` esta vez.

**Why:** era la tarea P0-4 / #6b del backlog (`HOJA_DE_RUTA_FIG.md`), pendiente
desde hace semanas por falta del PDF real.

**How to apply:** si Francisco reporta más "botones que no muestran nada al
apretar", sospechar primero de un link hardcodeado a una URL externa muerta
(patrón ya visto acá) antes de asumir un bug de JS. Recordar copiar el fix
también a `mpazq-afk.github.io` si aplica (ver sección de arriba sobre los
dos repos), preguntando permiso de push primero ([[feedback-permisos]]).

## Fotos de directivos subidas a Drive (2026-08-23, sin procesar aún)

Francisco subió fotos nuevas a la carpeta `Fotos` de Drive (id
`1aY8l-qUl_ISmYiljVBtiPtJoLX2r5nWy`, dentro de `CV/`): incluyen fotos de
directivos **ya existentes** en el club (vistos: "Rafa", "Delia", "Benja sa",
"Agustin", + 2 fotos sin nombrar "WhatsApp Image..."), y también fotos de
**personas nuevas** que Francisco pidió ignorar por el momento. No se tocó
nada del sitio con esto — falta que confirme si quiere que se actualicen las
fotos de los directivos existentes (`datos/club.json` / `miembros/`) ahora o
más adelante. Ver regla dura del repo: fotos reales de personas se suben
"solo Francisco" (P0-5 en `CLAUDE.md`).

**Actualización 2026-08-23 (mismo día, más tarde):** Francisco confirmó
subirlas. Las 4 fotos nombradas (Rafa/Delia/Benja sa/Agustin) mapean 1:1 a
archivos existentes en `fotos/directiva/` por convención de nombre (ver
`fotos/directiva/LEEME.txt`: nombre-apellido en minúsculas sin tildes):
`rafael-aliendre.jpg`, `delia-avilan.jpg`, `benjamin-saez-molina.jpg`,
`agustin-arriagada.jpg`. Se reemplazaron, se corrió `optimizar_fotos.py`
(requirió instalar Pillow, confirmado con Francisco antes) — el script
también renormalizó (mismos bytes casi idénticos, sin cambio visual) las
fotos de eventos existentes, es su comportamiento idempotente normal, no
un bug. Committeado y pusheado a ambos repos: `fig-web` commit `4d97b40`,
`mpazq-afk.github.io` commit `45e5151` (ahí NO se corrió el script de
optimización de nuevo, solo se copiaron los 4 archivos ya optimizados,
para no generar diffs de ruido en sus fotos de eventos). Las 2 fotos
"WhatsApp Image..." sin nombre de esa misma subida se dejaron intactas
(personas nuevas, Francisco pidió ignorarlas por ahora).

## Auditoría de diferencias fig-web vs. repo de Manuel (2026-08-23)

Comparé todo el árbol de ambos repos (`diff -rq`, y diffs normalizados con
Python para los JSON) y le presenté a Francisco una lista de 18 diferencias
reales, agrupadas: (A) features que fig-web tiene y Manuel's no, (B) texto
desactualizado en Manuel's ("59 equipos"/"590M" vs. el dato real 54/"540M"
que ya trae `torneo.json` en ambos), (C) donde Manuel's va adelante
(`MAPA_CONTENIDO_FIG.html` tiene un script de limpieza de URL que fig-web no
tiene ahí — parece que se aplicó primero del lado de Manuel), (D) bajo
impacto (CNAME, `sitio`/`liderArea` en club.json, docs internas
CLAUDE.md/HOJA_DE_RUTA_FIG.md).

**Aplicó los puntos 3–11** (todo excepto la página nueva "Miembros" [pt.1]
y habilitar el nav de FIW [pt.2], que Francisco dejó pendientes a propósito):
gráfico hero con datos reales, backfill ACWI en `torneo.json`,
`generar_torneo.py` persistiendo métricas Bloomberg por semana, pestaña
"Evolución por métrica" en el replay, tratamiento "podio" oro/plata/bronce
en tarjetas/video, video con bitrate optimizado + MP4 nativo, logos de
colaboradores más grandes, hashtag quitado del pie de tarjetas, y el texto
"54 equipos"/"540M" corregido en 6 archivos. Los archivos sin nada de
Miembros/FIW (`torneo/index.html`, `torneo/pantalla.html`,
`datos/torneo.json`, `generar_torneo.py`) se copiaron completos; los que sí
mezclaban Miembros/FIW (`index.html`, `datos/club.json`,
`datos/eventos.json`, `eventos/index.html`) se editaron quirúrgicamente para
no arrastrar esos dos puntos excluidos. Committeado y pusheado a
`mpazq-afk/mpazq-afk.github.io`: commit `77e3b8e`.

**Pendiente de decisión de Francisco** (puntos 1, 2 y 12, no aplicados):
la página "Miembros" completa (archivos que ni existen en el repo de
Manuel: `miembros/`, `datos/miembros.json`, `generar_miembros.py`,
`fotos/miembros/`), habilitar el link de FIW en el nav de Manuel's (sigue
`FIW_TEMP_OCULTO` ahí — en fig-web ya está activo), y traer a fig-web el
script de limpieza de URL que Manuel's tiene en `MAPA_CONTENIDO_FIG.html`
(sentido inverso, Manuel's → fig-web).

**Why:** confirmar antes de asumir que un repo es la fuente de verdad —
ver la sección de arriba sobre los dos repos y su sync manual.

**How to apply:** si Francisco pide más adelante "aplica el resto" o
menciona Miembros/FIW, son los puntos 1 y 2 de esta lista.

## Base consolidada de miembros cargada (2026-08-23)

La planilla "Miembros_FIG" del Drive (`02_Areas` → en realidad vive en
`00_MAESTRO`, buscar por nombre) ya estaba **completa**: los 132
participantes actuales del Torneo Portafolio 2026 (verificado contra
`datos/torneo.json`) ya estaban ahí, cero faltantes — no hizo falta
agregar a nadie. Lo que faltaba era correr el pipeline: se descargó la
planilla, se convirtió a `.xlsx` (el script no lee `.csv`), y se corrió
`generar_miembros.py --excel`. Resultado: `datos/miembros.json` pasó de
15 personas (solo directiva) a **160** (136 con resultado real del
torneo cruzado — posición, puntos, retorno). Committeado y pusheado
**solo a `panchoscky/fig-web`** (Francisco pidió explícitamente "en mi
repo", no en el de Manuel esta vez) — commit `4af3ebb`.

**Nota de consentimiento:** la columna `muestra` (qué autoriza a
publicar cada persona) venía vacía para las 145 personas de la
planilla — por regla del propio `PLANILLA_MIEMBROS_FIG.md` eso activa
el default `foto; bio; torneo; actividades`. Francisco confirmó
explícitamente (2026-08-23) que quienes se inscribieron en el torneo
aceptaron el uso y publicación de sus datos, así que se publicó con
ese default sin restringir nada.

**13 personas "sin equipo"** en el cruce (ej. "Alberto Muñoz Molina" →
dice pertenecer a "Market Moggers" en la planilla, pero ese equipo no
la trae en su lista de miembros dentro de `torneo.json`) — verificado
que no es bug del cruce (se buscó directo en el JSON, no aparece en
ningún equipo). Probablemente esos equipos cambiaron de integrantes y
`torneo.json` no se actualizó. **No se tocó, queda pendiente si
Francisco quiere investigarlo.**

**Why:** era la continuación directa de [[project-fig-web]] §Miembros —
la página y el script ya estaban construidos (tarea #27), solo faltaba
la base de datos real.

**How to apply:** esta función (`miembros/`, `datos/miembros.json`,
`generar_miembros.py`) sigue existiendo **solo en `fig-web`**, no en el
repo de Manuel (ver punto 1 de la auditoría de arriba, deliberadamente
no sincronizado). Si Francisco pide sincronizar de nuevo con el repo de
Manuel, incluir esto como parte del punto 1 pendiente.

## Los 5 equipos "en espera" — ELIMINADOS EN DEFINITIVA (2026-08-26)

El 2026-08-26 Francisco lo habló con el resto de la directiva de FIG y
**acordaron eliminar en definitiva** a los 5 (Fencashticos, Free Riders,
Market Moggers, Mosqueteros, Pink Capital). Se deshizo la reincorporación
del 23-ago: `datos/torneo.json` se restauró al commit `b2b382b` (54 equipos,
semana 15, ACWI ya backfilleado), las menciones "59 equipos"/"USD 590M"
volvieron a "54"/"USD 540M" en todo el sitio (salvo el párrafo histórico
"Capítulo IV" de `club.json` y `miembros.demo.json`, dejados a propósito),
`equipos_congelados.json` quedó `{"equipos": []}` e `incorporar_congelados.py`
quedó dormido (guard: no-op si el JSON está vacío). Commiteado y pusheado a
**ambos** repos: `panchoscky/fig-web` `8e03e98`, `mpazq-afk.github.io`
`57a48f5` (los dos a `main`, con permiso de Francisco).

**Capítulo IV: RESUELTO** (commit `53ea8c7`) — el párrafo de `datos/club.json`
ya dice "54 equipos y más de 150 estudiantes". Verificado el 2026-08-28.

## Cargos del área Portafolio y sección de creadores (2026-08-27)

**Solo Francisco es "Director · Portafolio".** Eran 5 con ese cargo; Manuel
Paz, Agustín Arriagada, Benjamín Disi y Benjamín Solís pasaron a
**"Directivo · Portafolio"** (rótulo que eligió él, sobre "Administrador").
Cambiado en `rol`, primer `hito` y bio de cada uno, en `datos/club.json`,
`index.html` (HTML estático + literal JS `CLUB_DATA`) y `datos/miembros.json`.
Los 3 **"Director · Trading" NO se tocaron** — no venía pedido.

**Benjamín Sáez (presidente) NO cofundó el área de Portafolio**: cofundó el
**club**, igual que el resto de la directiva. Corregido de "Co-fundador ·
Área Portafolio" a "Co-fundador de FEN Investment Group", y su bio dejó de
decir "Lidera el área Portafolio".

**Sección `#creadores` nueva en `torneo/index.html`** (después de Metodología,
con enlace en el nav). Los 6 creadores: Sáez, Francisco, Disi, Solís,
Arriagada y Paz. La **lista** vive en `datos/club.json` → `torneo.creadores`
(nombre + `aporte`) y es explícita a propósito — crear el torneo es un hecho
histórico, no un cargo vigente. El **cargo, LinkedIn y foto** se resuelven en
vivo contra `personas.directiva` calzando por nombre, así que un cambio de
cargo se refleja solo. Commits `9e8739a` (fig-web) y `fa107ee` (deploy).

**How to apply:** para agregar o sacar un creador, editar
`torneo.creadores` en `club.json` de **ambos** repos — no tocar el HTML.
`aporte` es **opcional**: si falta, no se dibuja el párrafo (así quedó Solís).

### Segunda tanda del 2026-08-27: jerarquía visual

**Tres niveles de marco** en §Nosotros de `index.html` y en las tarjetas de
creadores: presidencia (`destacado:true`) → filete dorado **arriba**; quien
**dirige** un área (`liderArea`) → filete **al costado** + chip "Dirige el
área"; el resto sin marca. Líderes declarados: Francisco (PRT), **Delia
Avilán (FIW)** y **Samuel Rodríguez Arnolds (VAL)**. Trading sin marcar —
ver [[estructura-areas-fig]].

**Trampa de CSS**: `.p-card:hover` reemplaza el `box-shadow` completo, así que
`.p-card--lead:hover` y `.p-card--area:hover` tienen que **repetir el filete**
además de la sombra o desaparece al pasar el cursor. Igual en
`.cre--lead`/`.cre--area` de `torneo/index.html`.

**Correcciones de crédito propagadas a todo el sitio** (no solo a la sección
de creadores): **Solís no diseñó la arquitectura** del torneo, y **Francisco
no es "co-creador"** — todos los del área lo son, así que destacarlo solo a
él engañaba; su crédito pasó a "infraestructura digital y plataforma web".
Agustín pasó de "capacitación en Bloomberg" a "infraestructura digital y
datos de Bloomberg". Commits `0a32471` (fig-web) y `f4dfcac` (deploy).

**Desfase previo que conviene saber**: el respaldo embebido de `index.html`
(literal JS `CLUB_DATA` + tarjetas estáticas) tiene **12 personas** y
`club.json` tiene **15** — faltan Samuel, Gabriela Domínguez y Victoria
Espinoza. No se nota en vivo porque `club.json` pisa el respaldo al cargar.

**Trampa al verificar secciones de este sitio con Chrome headless/CDP**
(costó tiempo): el `clip` de `Page.captureScreenshot` va en coordenadas del
**documento**, hay que sumarle `scrollY` al `getBoundingClientRect()`; y hay
que scrollear la sección a la vista y esperar **>0.9s** antes de capturar,
porque los `.reveal` recién reciben la clase `in` cuando el
IntersectionObserver los ve — si no, sale un rectángulo navy vacío y parece
que la sección está rota cuando no lo está.

**How to apply:** la infraestructura de congelados sigue en el repo por si
otra eliminación futura se quiere mantener en espera — repoblar
`equipos_congelados.json` con las últimas métricas reales del equipo y
correr `incorporar_congelados.py` después de `generar_torneo.py`. Si no,
ignorarla: un corte normal es solo `generar_torneo.py`.

### Contexto original (decisión de Francisco, 2026-08-23) — ya revertido

El corte de la semana 15 (21-ago) eliminó a 5 equipos (Fencashticos, Free
Riders, Market Moggers, Mosqueteros, Pink Capital) — 59→54. Se armó primero
un artefacto de análisis contrafactual ("El Corte Contrafactual") comparando
ambos rankings, y con esos datos reales sobre la mesa Francisco pidió
**reinsertarlos de verdad en el sitio público**, no solo en el análisis — su
decisión, sin necesidad de coordinarlo con Agustín/el equipo organizador
(confirmado explícitamente con `AskUserQuestion` el 2026-08-23).

**Mecanismo — no es "congelar el puntaje"**: Francisco fue explícito en que
el PUNTAJE de estos 5 debe poder variar semana a semana según cómo le vaya
al resto del campo, aunque el DATO (sus 5 métricas Bloomberg) quede fijo en
el último corte real que jugaron (semana 14) porque ya no operan. Esto es
posible porque el motor de scoring oficial (`src/scoring.py` del repo
torneo-bloomberg-oficial de Agustín) puntúa cada métrica por **percentil
continuo** entre el MIN/MAX de todos los equipos activos ese corte — no una
fórmula fija por equipo. Se replicó esa fórmula (pesos 30/25/15/15/15,
piso en negativo para IR/Exceso/Sharpe, sin piso en VaR/MDD) en
`incorporar_congelados.py`.

**Piezas nuevas en `panchoscky/fig-web`**:
- `datos/equipos_congelados.json` — los 5, con `metricas` fijas (semana 14)
  y `historial_previo` (semanas 5-14) rescatado del commit `c7c4f98` (el
  último ANTES de la eliminación — ya traía las 5 métricas por semana
  backfileadas por `completar_metricas_historial.py`; el commit `350c0a9`
  que se había usado primero para el artefacto de análisis NO las traía).
- `incorporar_congelados.py` — se corre SIEMPRE después de
  `generar_torneo.py` (nunca antes: necesita el snapshot fresco de los 54
  activos de ese corte). Recalcula puntaje/posición/puntosDetalle de los
  **59** (54 reales + 5 congelados), sobreescribe `torneo.json`, y marca
  a los 5 con `"congelado": true`.
- `ALERTAS_CONGELADOS.md` — registro semanal: si algún congelado pasa a
  sostener el mínimo o máximo de alguna métrica ("genera ruido"), y qué
  equipos reales se movieron de puntaje por su presencia. Primera corrida
  (semana 15): Free Riders sostiene el mínimo de MDD de los 59 (-19.2%),
  movió el puntaje de 50/54 equipos reales entre +0.05 y +0.79 puntos —
  pequeño pero real, hay que seguir revisando esto cada corte.

**Reversión de texto**: las 7 menciones de "54 equipos"/"USD 540M" que se
habían corregido el 2026-08-21 volvieron a "59 equipos"/"USD 590M" en
`index.html`, `eventos/index.html`, `torneo/pantalla.html`,
`torneo/index.html` (meta tags), `datos/club.json`, `datos/eventos.json`,
`datos/miembros.json`. De paso se corrigió `en/index.html`, que tenía
"Sixty-three" sin actualizar desde ANTES de la corrección 63→59 del
2026-08-02 (nunca se había tocado en ninguna corrección de conteo previa).

**Pendiente**: no hay ninguna marca visual en la UI (tarjetas, comparador,
replay, pantallas de la facultad) que distinga a estos 5 de un equipo activo
normal — solo el campo `congelado:true` en el JSON, que ningún HTML/JS lee
todavía. Francisco no ha pedido esto explícitamente; preguntar si lo quiere
antes de construirlo.

**Why:** con el scoring por percentil, la composición del pool de equipos
activos no es cosmética — cambia el puntaje de TODOS, no solo de quien
entra o sale. Cualquier cambio futuro a qué equipos están "adentro" del
ranking (otra eliminación, otro reingreso) debe pasar por este mismo
mecanismo de recalculo, no por edición a mano de `torneo.json`.

**How to apply:** si Francisco pide sacar a alguno de los 5 de la espera
(reincorporado de verdad al pipeline oficial, o retirado en definitiva),
basta con borrarlo de `datos/equipos_congelados.json` y volver a correr
`incorporar_congelados.py` — no tocar `torneo.json` a mano. Si pide agregar
a un equipo nuevo a la espera (otra eliminación futura), el patrón es
exactamente el mismo: agregarlo a `equipos_congelados.json` con sus últimas
métricas reales y correr el script.

## Segunda tanda del 2026-08-23: nav, ACWI en pantallas, video, bug 404

En la misma sesión de la reincorporación de arriba, Francisco pidió una
ronda de revisión y ajustes — todo ya pusheado a ambos repos:

- **Bug 404 real**: el botón "Torneo 2026" del nav de `eventos/index.html`
  apuntaba a un sitio externo viejo y muerto
  (`feninvestmentgroup.com/torneoportafolio2026/`, verificado con curl).
  Corregido a `../torneo/index.html`.
- **Nav de `index.html` reordenado**: de 11 ítems planos a 6, agrupados en
  desplegables (Áreas▾, Comunidad▾, Actividades▾, Jugar▾) — detalle técnico
  y la trampa del hash duplicado con el link activo del nav en el
  `CLAUDE.md` de fig-web, sección "Cambios del 2026-08-23 (segunda tanda)".
  En el repo de Manuel "Comunidad" no existe como desplegable (quedaría
  vacío ahí: sin Miembros, con FIG Woman oculta) — "Equipo" queda suelto.
- **ACWI real en `torneo/pantalla.html` y `pantalla-facultad.html`**: antes
  solo comparaban cada equipo contra el promedio del torneo; Francisco pidió
  explícitamente que aparezcan LAS DOS líneas (ACWI + promedio), no
  reemplazar una por la otra. El ACWI a veces atrasa un corte (depende de
  que Agustín lo capture de Bloomberg) — la línea simplemente no llega hasta
  la última semana cuando falta, no se rompe nada.
- **`pantalla-facultad.html` agrandado**: nombres de integrantes, intro
  (logo/título/kicker), tras verlo proyectado con el equipo del club.
- **Video pixelado al proyectar — script de grabación reconstruido
  (2026-08-23), TODAVÍA NO SE HA CORRIDO**: el script viejo
  (`scratchpad/grabar_pantalla_facultad.py`) vivía en el scratchpad efímero
  de una sesión anterior y se perdió al cerrarla. El nuevo queda **en la
  raíz de `fig-web`, no en un scratchpad** (para que no se vuelva a perder):
  `grabar_pantalla_facultad_1_capturar.js` (Node, maneja el Chrome ya
  instalado por CDP crudo, sin Playwright/Puppeteer — cero instalaciones
  nuevas) + `grabar_pantalla_facultad_2_codificar.py` (Python + `av`/PyAV,
  **instalado el 2026-08-23** con permiso de Francisco). Uso completo,
  hardware de su máquina y estimados de tiempo/peso están en el `CLAUDE.md`
  de fig-web, sección "Pixelación al proyectar". **Pendiente**: correrlo de
  verdad — Francisco pidió armar el script pero no correrlo todavía en esa
  sesión.

**Why:** todo esto salió de una sola ronda de "revisa X, Y, Z" tras la
reincorporación — quedó documentado junto porque comparten la misma sesión
y varias decisiones de diseño se tocan entre sí (ej. el nav se reordenó
usando el mismo mecanismo de desplegable que ya existía para "Jugar").

**How to apply:** si Francisco pide grabar el video semanal de nuevo,
primero preguntar si instala las dependencias que falten (`av`, y revisar
si hace falta Playwright o si el patrón CDP+Node ya usado para verificar
`miembros/index.html` alcanza) — no asumir que el script viejo se puede
recuperar, hay que reescribirlo.

**Actualización 2026-08-23 (mismo día, más tarde) — grabar desde el PC del
laboratorio en vez del suyo**: el PC de Francisco es muy débil para esto
(Pentium Gold 2 núcleos, 3.8GB RAM — ver hardware completo en
[[user-profile]]). Se agregó un gancho en `torneo-bloomberg-oficial`
(repo de Agustín, ver [[project-torneo-bloomberg]]) que al final de un
corte normal ofrece grabar el video ahí mismo, si detecta un `fig-web`
clonado al lado con ese corte ya aplicado — ese PC "tiene varias veces la
potencia" de la suya, según Francisco. Necesita las mismas dos piezas
(`grabar_pantalla_facultad_1_capturar.js` + `_2_codificar.py`) presentes
en el `fig-web` clonado ahí, más Node.js y `av`/Pillow instalados en esa
máquina — si el PC del laboratorio no tiene fig-web clonado todavía, hay
que clonarlo ahí primero.

## Tanda de rendimiento del 2026-08-28 — SIN COMMIT, esperando su revisión

Ronda de optimización (PC y teléfono) + ajustes de diseño móvil. **Todo está
aplicado en el clon local de `panchoscky/fig-web` y sin commitear** — Francisco
eligió explícitamente revisarlo él antes. Si retoma el tema, lo primero es
`git status` ahí: 28 archivos modificados y 61 nuevos.

Resultados medidos: la portada pasó de 2284 KB a 173 KB y `eventos/` de
2122 KB a 70 KB; la primera pintada en teléfono bajó de 2,5-2,8 s a ~0,7 s en
torneo, eventos y miembros.

Dos scripts nuevos en la raíz del repo: `generar_imagenes_web.py` (deriva
WebP + miniaturas de `fotos/`, deja los originales intactos) y
`optimizar_logos.py` (achica los PNG de `logos/` solo si la diferencia visual
queda bajo un umbral medido).

**El detalle completo está en la sección "Sexta tanda del 2026-08-28" del
`CLAUDE.md` del repo**, incluidos dos resultados contraintuitivos que conviene
no re-descubrir: el `<link rel=preload>` de fuentes **empeora** la primera
pintada en este sitio (856 ms → 1684 ms, porque el CSS va inline en un HTML de
150 KB), y la mesa de `miembros/` **no** está cortada aunque lo parezca.

**Why:** es trabajo terminado y verificado que todavía no está publicado; sin
esta nota, una sesión nueva podría rehacerlo o pisarlo.

**How to apply:** si Francisco dice "publica lo de la optimización", el camino
es commit en `panchoscky/fig-web` y después `sincronizar_espejo.py --aplicar`,
recordando que `index.html` no se copia entero al espejo (ver la sección de
arriba sobre los dos repos) — esta tanda le tocó TRES tramos separados.

## DOS tandas de optimizacion SIN COMMITEAR (2026-08-28)

Estado al cerrar la sesion del 28-ago: **28 archivos modificados y 62 nuevos en
el working tree de `fig-web`, nada commiteado, en `main`.** Son dos tandas
seguidas de rendimiento y diseno (la "sexta" y la "septima" del `CLAUDE.md` del
repo, que las documenta en detalle — leerlas ahi, no reconstruirlas de memoria).

Muy en corto: la sexta bajo el PESO (WebP + miniaturas via
`generar_imagenes_web.py`, `optimizar_logos.py`, `no-store` -> `no-cache`,
diseno de telefono, objetivos tactiles WCAG). La septima bajo la CANTIDAD DE
PEDIDOS (`datos/torneo-portada.json` como tercer derivado, `window.figJSON()`
memoizador, miniaturas que dejan de sondear y pasan a `loading="lazy"` de
verdad, la tira de fotos del hero aplazada a `requestIdleCallback`).

**Francisco lo reviso en el navegador el 28-ago y tiene comentarios de cambios
que todavia NO alcanzo a darme.** Ese es el proximo paso al retomar: pedirle
los comentarios ANTES de commitear nada. No commitear ni pushear por cuenta
propia — ver [[feedback-permisos]].

Verificado antes de cerrar: `verificar_sitio.py` sin errores (solo los 3 avisos
historicos de conteo de equipos), las 15 paginas cargan sin errores de consola,
y en emulacion movil real la portada no tiene scroll lateral y los 15 avatares
cargan bien.

**Why:** es trabajo grande sin commitear; si se pierde el working tree se
pierden las dos tandas enteras.

**How to apply:** al retomar, `git status` y `git diff` en el repo, y leer las
dos ultimas secciones de su `CLAUDE.md`. Para publicar despues hacen falta el
commit en `panchoscky/fig-web` y `python sincronizar_espejo.py --aplicar`, con
el cuidado de siempre con `index.html` (nunca se copia entero al espejo).


## Estado al 2026-08-28: fig-web al dia, espejo deliberadamente atras

Commit `6f3e8fc` en `panchoscky/fig-web` main (pusheado, con permiso de
Francisco) junta las tres tandas que estaban sin commitear: las dos de
optimizacion (peso de imagenes y logos, derivados de torneo.json, menos
pedidos) y una tercera de arreglos que salio de un bug que reporto el —
"al apretar en un area de Miembros aparecia un marco blanco".

**Francisco pidio explicitamente NO tocar el repo de Manuel todavia**
(`mpazq-afk/mpazq-afk.github.io`) — esto **ya se resolvio el 2026-08-30**,
ver la seccion del final.

Dos trampas de CSS que aparecieron acá y valen para todo el sitio:
- Un fondo en `::before{position:absolute}` dentro de un contenedor con
  `overflow:auto` **se va con el scroll**. El fondo va en el elemento
  mismo: el de un scroller no scrollea con su contenido.
- `[hidden]` es solo `display:none` de la hoja del navegador, asi que
  cualquier regla propia que fije `display` lo anula sin avisar. Las 15
  paginas ya llevan `[hidden]{display:none!important}`.

**Lo que quedo pendiente y depende de Francisco o de la planilla**: de las
160 personas de `miembros.json`, 146 no tienen `area` y ninguna tiene
`generacion`, bio ni foto — por eso los 4 desks solo muestran a la
directiva. Es dato, no codigo. Ver tambien [[estructura-areas-fig]]
(Trading sin lider declarado) y la decision sobre si `fotos/` (17 MB)
sigue versionada entera.


## Estado al 2026-08-30: los DOS repos al dia y publicados

Ya no hay espejo atrasado. Ese dia se corrio por primera vez de verdad
`sincronizar_espejo.py --aplicar` (existia hacia semanas pero nunca se
habia aplicado: el espejo estaba 137 archivos atras) y se pusheo a los dos:
`panchoscky/fig-web` en `8cce0b2` y `mpazq-afk/mpazq-afk.github.io` en
`6dc80a1`. Produccion verificada en vivo.

**Decision de Francisco: FIG Woman NO se publica en el repo de Manuel.**
No basta con ocultar los enlaces (lo que hacia `FIW_TEMP_OCULTO`): la
pagina seguia respondiendo en `/fiw/`, el sitemap se la declaraba a Google
y el area se veia en el selector de desks, el panel 04, el `<option>` de
postulacion, la version en ingles y el nav del 404. Ahora hay
**`despublicar_fiw.py`** en fig-web, que corre SIEMPRE despues de
`sincronizar_espejo.py` y borra el area del espejo. Los dos scripts son un
par; el primero siempre reportara 5 archivos "por copiar" porque el segundo
se los reescribe, y eso no es un error.

**Lo que NO se toca, confirmado por Francisco: los cargos de las tres
cofundadoras** (Delia Avilan, Gabriela Dominguez, Victoria Espinoza), que
figuran como "Co-fundadora · FEN Investment Woman" en `club.json`. Ocultar
un area es una decision de publicacion; reescribirle el curriculum a una
persona no. Consecuencia asumida: el nombre sigue visible en §Nosotros del
espejo. Tampoco se borra el evento del 27-may de la bitacora (es historia
del club; hay un flag `QUITAR_EVENTO` en el script si algun dia cambia).

**`miembros/` sigue sin publicarse.** El `informe/` SI se publica desde mas
tarde ese mismo dia, en sus dos idiomas -- ver la seccion siguiente.

**Trampa que costo tiempo y vale para siempre:** el espejo esta en **CRLF**
y fig-web en **LF**. Copiar a lo bruto hacia que git mostrara cada archivo
como si hubieran cambiado sus 3.000 lineas. `sincronizar_espejo.py` ahora
preserva el fin de linea del destino y compara ignorandolo — sin lo segundo
reportaria los mismos 30 archivos como pendientes para siempre.

**Why:** este repo se revisa entre personas (Francisco y Manuel), asi que un
diff legible no es cosmetico.


## Cierre del 2026-08-30 (segunda mitad de la sesion)

Lo que cambio despues de lo de arriba, todo pusheado a los dos repos y
verificado en vivo:

**El informe SI se publica**, en `feninvestmentgroup.com/informe/` y
`/en/informe/`. `torneo/index.html` salio de `DIFIEREN` (sus enlaces al
informe ya son validos alla). El unico archivo que sigue portandose a mano al
espejo es `index.html`, por su nav propio.

**El lema del club cambio**: "Forjando la Élite del Mañana" -> "Forjando los
Líderes del Mañana", en 14 lugares. **Trampa que costo un error mio:**
`grep -i` en Git Bash NO hace case-folding de acentos, asi que "Élite" con
mayuscula acentuada no aparecia y llegue a decirle a Francisco que no quedaban
menciones. **Para buscar texto con acentos en este repo, usar Python en UTF-8.**

**Scripts nuevos en fig-web, todos con `--aplicar` y modo seco:**
- `generar_informe_en.py` -- genera `en/informe/index.html` desde el informe en
  espanol con una tabla de traduccion. **Correrlo cada vez que se toca
  `informe/index.html`.** Falla si queda texto en espanol.
- `despublicar_fiw.py` -- saca FIG Woman del espejo. Va SIEMPRE despues de
  `sincronizar_espejo.py`; son un par.
- `verificar_movil.js` -- mide las paginas a 390x844 con emulacion movil real.
- `analisis_etf.py` + `clasificacion_etf.csv` viven en el repo de Agustin y
  siguen SIN COMMITEAR (ver [[subsistema-ordis-en-torneo]]).

**Trampa de medicion en movil:** `chrome --screenshot --window-size=390,...`
SIN emulacion movil da una imagen enganosa (salia texto cortado en una pagina
sin ningun desborde). Hay que capturar por CDP con `mobile:true`.

**Why:** las tres trampas de arriba me hicieron dar por bueno algo que no lo
estaba, cada una una vez. Son especificas de este entorno, no de este repo.

## 2026-08-31: dato de gestora fuera del informe (PUBLICADO)

Francisco pidio **sacar del informe el dato de que no todo lo comprado fue en
ETF de iShares** (el "96,4% de las operaciones"), porque el informe es para la
reunion con **BlackRock**. Se elimino en dos lugares de `informe/index.html`
(la tarjeta de estadistica y la frase final del pie del grafico de ETF), se
ajusto la tabla de `generar_informe_en.py` y se regenero el espejo en ingles.
Despues se corrio el par `sincronizar_espejo.py --aplicar` +
`despublicar_fiw.py --aplicar` y `generar_sitemap.py` dentro del espejo.

**Publicado el 2026-08-31 en los dos repos**: fig-web `9e0a521` y espejo
`2462fc9`. El push al espejo fue RECHAZADO la primera vez porque Manuel habia
pusheado cambios de roles; se resolvio con `git pull --rebase` (archivos
disjuntos, sin conflicto). **Antes de pushear al espejo, siempre fetch primero:
Manuel trabaja directo sobre produccion.**

Detalles que importan si se retoma:
- Al sacar la tarjeta, el bloque `#stEtf` quedo con **3 tarjetas y no 4**. En
  movil `.stats` es un grid de 2 columnas fijas, asi que la ultima fila queda
  con una tarjeta sola. Se le ofrecio rellenar con otro dato de `etf.json`
  (monto comprado ~USD 615M o las 642 compras) y **no respondio**.
- `INFORME_ETF_TORNEO.md` (interno, no viaja al espejo) y dos lineas de
  `CLAUDE.md` **todavia mencionan** las 23 compras fuera del universo iShares.
  Se le pregunto si tambien las saca y no respondio.
- **No hay dato de TER / expense ratio en ningun repo.** Francisco pidio
  reemplazar el dato eliminado por "lo recaudado por mantencion de los ETF";
  se le explico que no existe la fuente y que ademas las carteras son
  simuladas (no hubo recaudacion real), y **decidio no agregarlo**. Si vuelve
  a pedirlo, el camino es bajar `FUND_TOTAL_EXPENSE_RATIO` de Bloomberg y
  calcular sobre nocional x tiempo, nunca sobre el monto comprado acumulado.

**Propuestas para el informe enviadas por correo** (31-ago, a su Gmail): seis,
todas calculadas sobre los datos actuales. Las tres fuertes: 83% de las compras
fueron en mayo y una sola en agosto (`cronologia` de `etf.json` esta cargado y
**no se usa** en la pagina); los equipos que le ganan al ACWI caen de 87% a 50%
justo cuando el indice acelera; y la correlacion entre puntaje y numero de ETF
es -0,04 (diversificar mas no dio puntos). Ninguna esta implementada.

**Sincronizado el 2026-08-31** (fig-web `d271e79`): se bajaron de produccion
los cambios de rol de Manuel Paz y Juan Jose Limari (ver
[[estructura-areas-fig]]). `club.json` quedo identico al del espejo; de
`index.html` se portaron SOLO las 4 lineas de rol (2 del markup de p-card y 2
del `CLUB_DATA` embebido), porque ese archivo difiere a proposito por el nav.

**Receta para portar del espejo hacia fig-web** (el sentido inverso al de
`sincronizar_espejo.py`, que no esta automatizado): el espejo guarda todo en
**CRLF** y fig-web en **LF**. Copiar un archivo tal cual mete un diff de cientos
de lineas; hay que normalizar `

` -> `
` al copiar. Y en Python de Windows,
`pathlib.read_text()` NO acepta `newline=`: usar `io.open(..., newline='')`
para no destrozar los finales de linea al reescribir.

**`datos/miembros.json` de fig-web NO se toco** y sigue con los roles viejos (8
"Directivo · Portafolio", 6 "Director · Trading") y el `lidera:"TRD"` de Limari.
Lo genera `generar_miembros.py` y no viaja al espejo, asi que no afecta a
produccion, pero la pagina de Miembros contradice al resto del sitio.

## 2026-09-02: corte semana 16 publicado en AMBOS repos

Corte del 28-ago (semana 16) del repo de Agustin, ver [[project-torneo-bloomberg]].
**El torneo quedo en 48 equipos** (6 eliminados por inactividad; decision de
Francisco: eliminarlos, mismo criterio que las 5 de la semana 15, sin congelar
— `equipos_congelados.json` sigue vacio).

- **fig-web** commit `378d99e` (main, pusheado): `generar_torneo.py` con el
  Excel del 28-ago + `completar_acwi_historial.py --aplicar` con
  `benchmark_acwi_precios.csv` (backfill ACWI semanas 15 y 16 de una vez) +
  derivados. Menciones vigentes de "54 equipos"/"USD 540M" → "48"/"USD 480M"
  en 8 archivos; intactas las historicas (Capitulo IV en pasado de
  `club.json:413`, "65 equipos" acumulado de la bio de Agustin).
- **espejo `mpazq-afk`** commit `f1f28f0` (main, pusheado): **solo el corte**,
  NO el `sincronizar_espejo.py` completo. Motivo: el espejo estaba varios
  commits atras y una sincronizacion normal habria arrastrado tambien la
  reestructuracion de "5 desks" (Administracion, paginas Portafolio/Trading,
  nav) que Francisco pidio publicar aparte. Se copio a mano solo
  `torneo.json` + derivados + `torneo/e/` + las ediciones de texto 54→48.
  `index.html` se edito directo (nunca se copia entero al espejo).

## 2026-09-02 (mismo dia, mas tarde): 5 desks publicados al espejo

Francisco autorizo llevar la reestructuracion al espejo. Commit `194bdbb`
en `mpazq-afk` main (pusheado). `sincronizar_espejo.py --aplicar` +
`despublicar_fiw.py --aplicar` + `generar_sitemap.py` (12 URLs ahora).

- Paginas nuevas en produccion: `portafolio/index.html`, `trading/index.html`
  (+ `datos/portafolio.json`, `datos/trading.json`, `verificar_menu_movil.js`).
- `club.json` (sincronizado): Benjamin Saez dirige Administracion
  (`liderArea:"ADM"`, primero que preside Y dirige a la vez), Jhosep VAL,
  Manuel TRD; Rafael/Limari/JD/David pasan a rol "Directivo".
- **`index.html` portado A MANO** (nunca se copia entero al espejo). Lo que
  se llevo: nav Areas + menu movil (+Portafolio +Trading), fix de
  `.m-menu` con scroll, regla CSS `.p-card--lead.p-card--area` (dos filetes),
  seccion de desks (PRT/TRD/VAL a `<a>`, +panel ADM), footer col Areas,
  CLUB_DATA (respaldo JS) con los roles nuevos.
- **Adaptaciones del espejo (FIW oculta)**: ADM es `data-desk/view="3"`, no
  "4" (el espejo no tiene panel FIW). El stat "5 Areas especializadas" de
  fig-web **NO se aplico**: el espejo publica **4** (PRT/TRD/VAL/ADM), y el
  h-sec sigue "Cuatro desks". En `portafolio/` y `trading/` la frase "junto
  a ... y FEN Investment Woman" se cambio a "entre otras".
- Cargos de las 3 cofundadoras FIW (Delia etc.) y el evento del 27-may
  siguen visibles en el espejo — exclusiones deliberadas de siempre.

Verificado: `verificar_sitio.py` sin errores, `verificar_paginas.js` las 16
paginas sin errores de consola. **Los dos repos vuelven a estar al dia.**

**Ojo**: el corte semana 16 al espejo (`f1f28f0`) NO paso por
`sincronizar_espejo.py`; el de 5 desks (`194bdbb`) SI. De aca en adelante el
espejo esta sincronizado por el script otra vez.

## 2026-09-04: Trading — paleta propia XTB, cinta de clubes, torneo activo (PUBLICADO en fig-web, espejo pendiente)

Manuel lanzó el **Alpha Trading Challenge 2026** (alianza FIG + XTB, ver
[[proyecto-torneo-trading-alpha-challenge]]) y subió material al Drive.
A pedido de Francisco, `trading/index.html` pasó a tener **paleta propia**:
navy sin cambios + `--acc` rojo XTB `#FF0000` (con `--acc-light`/`--acc-deep`
recalculados, contraste medido 4.67/7.33/7.20 AA-AAA). **`trading/` y
`valuation/` DEJAN de compartir plantilla de color** desde hoy (siguen
compartiendo estructura/JS) — es la tercera página con paleta propia después
de `fiw/` y `portafolio/`.

Se agregó una cinta de logos (mismo mecanismo que `.marq`, duplicado para
loop infinito) con los clubes invitados, bajados del Drive y guardados en
`logos/clubes-trading/`. De los 8 logos que subió Manuel solo se pudieron
bajar 6 limpios (UAI, PUC, UANDES, DuocUC, Beauchef, FAE); **UDD y el propio
"Club de Finanzas FEN" quedaron pendientes** (SVG demasiado grandes para
bajar por el MCP de Drive sin gastar contexto). Dos de los 6 (UAI, DuocUC)
eran SVG de "reconstrucción vectorial de raster" de >1MB cada uno — se
recortaron y pasaron a PNG con Chrome headless antes de subirlos.

Se activó `torneo.activo:true` en `datos/trading.json` con las fechas
confirmadas del Drive (inscripciones 21-sep al 4-oct, torneo 14-oct al
6-nov) y se agregó "Torneo" al nav/menú móvil, siguiendo el mismo patrón que
ya usa `valuation/index.html`. **`formUrl` y `basesUrl` quedaron vacíos a
propósito**: el flyer trae un QR de inscripción que no se pudo decodificar
(sin librería de QR en la máquina), y el único documento de "bases" que
existe es el Brief FIG-XTB, que es un brief de marketing interno, no un
reglamento formal — no se etiquetó como "bases" para no confundir a un
visitante real del sitio.

**Publicado en `panchoscky/fig-web` main**: commit `e41e09e` (el cambio en
sí) + `cb23a64` (sitemap regenerado, avisado por el hook `pre-push`). De
paso se pusheó junto el commit `d216e57` que ya estaba listo desde el
2026-09-03 (limpieza P1-P6 de la paleta de `portafolio/`) — ver
[[propuestas-diseno-portafolio]], ese pendiente del fin de semana ya está
resuelto.

**NO se corrió `sincronizar_espejo.py`** — el espejo de Manuel sigue sin
este cambio. Si Francisco pide publicarlo ahí también, aplica el mismo
cuidado de siempre con `index.html` (nunca se copia entero) aunque en este
caso el cambio está contenido en `trading/index.html` + `datos/trading.json`
+ `logos/clubes-trading/`, ninguno de los "intocables".

**Why:** Francisco pidió explícitamente comitear y pushear esto; se hizo
sin pedir confirmación de nuevo porque el pedido ya era la autorización
para esa acción puntual — ver [[feedback-permisos]].

**How to apply:** si se consigue el link del Google Form o un documento de
bases formal más adelante, solo hay que llenar `formUrl`/`basesUrl` en
`datos/trading.json` — el HTML no necesita tocarse (el patrón ya está
armado, igual que en `valuation/`). Si Manuel sube los 2 logos que faltan
(UDD, Club de Finanzas FEN) en un formato más liviano, agregarlos a
`CLUB_LOGOS` en `trading/index.html` y a `logos/clubes-trading/`.

---

## Sesión del 2026-09-04 (tarde/noche) — cuatro tandas, todas pusheadas a `main`

Commits: `f4e2590`, `7bf8952`, `ffd15e5`, `5c9dff1`.

**1. Portadas y fondos de Trading y Portafolio.** Trading estrena "la sesión" como
fondo del hero (velas OHLC, EMA(9) real, niveles y volumen), generada por
`FIG_herramientas/gen_sesion_trading.py` y estática en el HTML. **La serie es
sintética a propósito y por eso la figura no lleva ni un rótulo ni una cifra.**
Francisco la miró y pidió la línea más gruesa y con movimiento más suave: 2.6px y
`ease-in-out` en 32s (iba con `var(--ease)`, un ease-out que arranca de golpe).
En Portafolio se cerró P11/P12 con un **velo de lectura** bajo la columna de texto,
sin tocar el SVG del campo de fronteras.

**2. Auspiciadores y cierre de la revisión de diseño (P1–P13).** Franja "Auspician el
torneo" al pie de la tarjeta de §Torneo — **ahí y no en el hero porque auspician el
TORNEO, no el área**. El respaldo ya estaba en `datos/club.json`. P8 mandó las
tarjetas de §Responsables de `--graph` a `--navy-panel` y **el token `--graph`
desapareció del sitio**. P13 resultó **falso positivo**: no había halo en los avatares.

**3. La mesa de `miembros/`** — ver [[mesa-miembros-fig]], que tiene el detalle y
cómo verificarla.

**Manuel Paz ya NO es "Director · Portafolio y Trading"**: es `Director · Trading`, y
en Portafolio `Directivo · Portafolio`. Corregido en 13 lugares. Ojo, esto arregló una
inconsistencia de fondo: `generar_miembros.py` deduce el área del TEXTO del rol, así
que el rol viejo lo mandaba a PRT mientras `miembros.json` decía TRD — **quien corriera
el generador rompía la mesa**.

**Herramientas nuevas en `FIG_herramientas/`** (fuera del repo): `gen_sesion_trading.py`,
`verificar_mesa.js` (mide solapes en la mesa) y `ver_estado_mesa.js` (captura la página
tras un click).

**Pendientes que quedaron abiertos:** falta `logos/xtb.png` (ver [[pendiente-logo-xtb]]);
los textos de `datos/cupos.json` son borradores míos a la espera de que Francisco los
corrija; y **el espejo sigue sin sincronizar** desde `d216e57`.

## 2026-09-05: nav entre áreas + Portafolio cambia a paleta "Itaú terminal"

Francisco reportó dos bugs de UX y pidió revisar los colores de Portafolio.
Todo verificado por CDP (la extensión de Chrome sigue sin conectar) antes de
tocar nada, y con `verificar_sitio.py` limpio después. Tres commits en
`panchoscky/fig-web` main: `9043bf6`, `2162390`, `41df999`.

- **Tipografía del nav "distinta" entre páginas — investigado, NO es un bug.**
  Las seis páginas revisadas (index, portafolio, trading, valuation, torneo,
  miembros) definen las mismas variables de fuente y cargan la misma hoja
  autoalojada. Es casi seguro el destello de `font-display:swap` sin precarga
  (decisión ya tomada y documentada en `CLAUDE.md`: precargar empeoraba el
  tiempo de pintado). No se tocó nada de esto — quedó explicado, no arreglado.
- **Bug real confirmado**: Portafolio, Trading y Valuation solo enlazaban de
  vuelta a secciones de Inicio, ninguno a los otros dos desks — para pasar de
  uno a otro había que volver siempre a Inicio primero. Fix: dropdown
  "Áreas ▾" en el nav de los tres (mismo patrón que ya usa `index.html`),
  con sus links propios en el menú móvil también.
- **Paleta de Portafolio revisitada** (ver [[propuestas-diseno-portafolio]]):
  se armó una vitrina de 5 lecturas de color, todas ancladas a Itaú y al
  ACWI (nunca al margen del sponsor), y Francisco eligió **"Itaú terminal"**
  — navy más saturado (`#061A33`) y el naranja de marca sin atemperar
  (`#FF7A00`), para un desk que compite en vivo contra un índice.
  **El azul del benchmark (`--bmk`) NO se tocó**: sigue igual a como lo usan
  index.html, torneo/pantalla.html, pantalla-facultad.html e informe/ — se
  encontraron y re-tiñeron ~180 literales de color hardcodeados en rgba()/hex
  (favicon, theme-color, y el SVG del gráfico dibujado por JS que no puede
  usar `var()`), con los nuevos `--acc-deep`/`--acc-chroma` re-medidos para
  seguir pasando WCAG AA sobre `--paper`.

**Espejo de Manuel: ahora son 12 commits acumulados sin sincronizar** desde
`d216e57` (antes eran 9). Falta `sincronizar_espejo.py --aplicar` +
`despublicar_fiw.py --aplicar`.

**Why:** confirmar antes de tocar código evitó "arreglar" algo que no estaba
roto (la tipografía) y encontró rápido lo que sí lo estaba (la navegación).
Retinar toda una paleta a mano es exactamente la trampa que el `CLAUDE.md`
del repo advierte ("un cambio de paleta deja navy viejo escondido en
formato rgba()") — barrer también las formas decimales, no solo el hex,
fue lo que evitó dejar colores viejos escondidos.

**How to apply:** si Francisco pide más adelante retocar otra paleta propia
del sitio (`fiw/`, `trading/`), repetir el mismo método: listar TODAS las
formas del color viejo (hex y decimal, con y sin `#`/espacios) antes de
reemplazar, no solo los tokens de `:root`.

## 2026-09-06: pedido de mapa de largo plazo (para DESPUÉS del 30-sep)

Francisco se enteró de que **el Club de Finanzas de la FEN (rival de FIG) está
haciendo su nueva página web**. Para él fig-web es un proyecto personal que
disfruta y le preocupa la **continuidad de FIG** a futuro. Pidió crear un
**mapa/documento vivo de largo plazo** con todas las mejoras, renovaciones e
implementaciones posibles, en todos los ámbitos — una auditoría por áreas
(exactitud de datos, diseño, rendimiento, accesibilidad, SEO, **resiliencia y
continuidad**, automatización, features nuevas), más grande que el `HOJA_DE_RUTA_FIG.md`
y que [[baul-mejoras-futuras]]. **Acordado arrancarlo después de la solemne de
Micro 3 (30-sep)**, junto con el cronograma del examen de grado ([[project-fen]]).
Al hacerlo, mirar qué está montando el club rival.
