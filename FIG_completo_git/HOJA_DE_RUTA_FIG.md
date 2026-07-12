# HOJA DE RUTA — Infraestructura digital de FIG

> **Documento maestro de continuidad.** Si eres una IA (Claude Code u otra)
> retomando este proyecto sin contexto previo — incluyendo un modelo de menor
> capacidad — este archivo + `CLAUDE.md` son TODO lo que necesitas para
> continuar con la misma calidad. Léelos completos antes de tocar nada.
>
> **Protocolo de actualización (obligatorio):** al terminar CUALQUIER bloque
> de trabajo, antes de commitear: (1) marca aquí lo completado con ✅ y fecha,
> (2) agrega lo nuevo que haya surgido al backlog, (3) actualiza la tabla de
> estado de `CLAUDE.md`. Un documento desactualizado es peor que ninguno.

Última actualización: **2026-07-12** (sesión: Desafío FIG + auditoría de
rendimiento — logos redimensionados y guía de compresión de fotos).

---

## 1. Cómo trabajar en este proyecto (reglas de calidad)

Estas reglas hacen que el trabajo de cualquier modelo se vea igual:

1. **Sin build step, jamás.** HTML/CSS/JS planos, ES5 en el JS (funciones
   `function(){}`, `var`, sin arrow functions ni template literals — mira
   cualquier página existente y copia el estilo). Deploy = GitHub Pages.
2. **Datos en JSON, nunca hardcodeados.** Todo lo que cambia (personas,
   eventos, ranking, textos) vive en `datos/*.json`. Las páginas traen datos
   demo embebidos como respaldo y los sobreescriben con `fetch()` del JSON.
3. **Sistema de diseño compartido:** navy `#0A1128` + oro `#D4AF37`,
   Playfair Display + Inter + IBM Plex Mono, cursor crosshair, reveals
   on-scroll, `prefers-reduced-motion` respetado. Al crear una página nueva,
   copia la base de `torneo/index.html` o `postula/index.html`.
   Excepción: `fiw/index.html` tiene paleta propia (variables `--acc*`) — NO
   tocarlas sin permiso explícito de Francisco.
4. **Todo texto de cara al usuario en español.**
5. **Google Drive es SOLO LECTURA para IAs** (regla dura de Francisco).
6. **Verificación mínima antes de commitear:** `node --check` del JS inline
   extraído, `python3 -c "import json; json.load(open(...))"` de cada JSON
   tocado, y servir con `python3 -m http.server` + curl 200 de cada página.
7. **Commits en español, descriptivos, push a la rama designada de la sesión.**

## 2. Mapa del ecosistema

```
FIG_completo_git/
├── index.html               ✅ sitio principal (enlaza a todas las subpáginas)
├── eventos/index.html        ✅ bitácora de actividades (lee datos/eventos.json)
├── torneo/index.html          ✅ ranking del torneo + trayectoria por equipo (lee datos/torneo.json)
├── fiw/index.html              ⚠️ FEN Investment Woman (colores provisionales)
├── postula/index.html            ⚠️ formulario de postulación (falta endpoint)
├── generar_torneo.py              ✅ Excel ranking → datos/torneo.json (mantiene historial)
├── datos/
│   ├── club.json                  ← config.urls + config.postulaEndpoint + personas + eventos resumen + historia
│   ├── eventos.json                ← bitácora completa
│   ├── fiw.json                     ← textos FIW
│   └── torneo.json.ejemplo           ← ESQUEMA del ranking (renombrar a torneo.json con datos reales)
├── fotos/eventos/* , fotos/fiw/     ← 1.jpg, 2.jpg… numeradas sin saltos (vacías aún)
├── CLAUDE.md                        ← contexto vivo del proyecto (mantener al día)
├── HOJA_DE_RUTA_FIG.md              ← ESTE archivo
├── LEEME_PAGINAS.md, IDEAS_FIG.md, IDEAS_GRAN_ESCALA_FIG.md ← contexto adicional
```

Fuera del repo (no reinventar, ver `CLAUDE.md` §"Lo que YA existe"):
sitio en producción del Drive, app `torneo-app` (Vite+TS), overlay OBS
`ranking-video`, GitHub Pages del torneo bajo el usuario `mpazq-afk`.
URLs reales: LinkedIn `linkedin.com/company/fen-investment-group`,
Instagram `instagram.com/fen.investment.group`.

## 3. Estado — hecho ✅

| Fecha | Qué | Detalle |
|---|---|---|
| 2026-07-06 | Sitio principal + eventos + fiw + torneo | 4 páginas completas con datos JSON |
| 2026-07-07 | Enlaces cruzados | index.html → torneo/, eventos/, fiw/ + Instagram/LinkedIn reales en CONFIG y club.json |
| 2026-07-07 | Rendimiento pasado por equipo | Campo `historial` en el esquema del torneo; sección "Trayectoria" (sparkline SVG + stats: mejor posición, mejor score, semanas en top 3) en el overlay de equipo; sparkline también en las tarjetas descargables PNG 1080×1350 y HTML |
| 2026-07-07 | `generar_torneo.py` | Lee hoja `ranking_ordenado` + Excel inscripciones → escribe datos/torneo.json; CONSERVA el historial del JSON anterior y agrega la semana nueva; calcula `delta`; modo `--demo` para probar |
| 2026-07-07 | Formulario de postulación | `postula/index.html` — envía a `config.postulaEndpoint` (Apps Script) definido en club.json; mientras esté vacío muestra banner "en configuración" con envío deshabilitado; CTA "Quiero ser parte" del index ya apunta aquí |
| 2026-07-09 | Logos oficiales | Bajados del Drive a `logos/` (toro FIG en oro/blanco/navy + lockup, Itaú, BlackRock + versión blanca). NO hay logo de FIW en el Drive — pendiente P0 |
| 2026-07-09 | Intros animadas | Todas las páginas abren con logo al centro → nombre (+ área en subpáginas; FIW muestra su nombre + "FEN Investment Group"); 1 vez por sesión por página (sessionStorage), respeta reduced-motion. Logo real en navs/footer |
| 2026-07-11 | El Rally del Toro | `juego/index.html`: runner canvas (toro del logo, velas rojas y burbujas). Mecánica central: el portafolio (USD 10.000 base) crece con multiplicador que sube cada 8 s mientras el mercado se acelera; VENDER (tecla S/botón) asegura el valor en el ranking local (localStorage top-10 con nombre); chocar = pierdes todo lo no vendido. Transmite "un inversionista debe saber cuándo salir". Enlazado desde el banner de postula/ como sala de espera |
| 2026-07-12 | Auditoría de rendimiento | Medido con datos reales: HTML/CSS/JS comprime ~70-75% con gzip (GitHub Pages lo sirve automático); logos redimensionados de 476 KB a 212 KB (venían al tamaño de archivo del Drive, 2000px+, mostrados a 40-150px); riesgo principal identificado: fotos de celular sin comprimir (3-8 MB c/u) — guía de compresión agregada a MAPA_CONTENIDO_FIG.html (máx 1600-2000px, JPG 75-80%, objetivo 150-400 KB/foto) |
| 2026-07-12 | Desafío FIG (infraestructura) | `desafio/index.html`: trivia con modo DESAFÍO (10 preguntas secuenciales sin volver atrás; fase de lectura con cuenta regresiva y luego alternativas cuyo valor decae 100→20 pts en 20 s; malas −25, saltadas 0; revisión final con explicación de cada error/salto; áreas fuerte/débil; ranking localStorage con áreas) y modo ESTUDIO (por tema o por ramo, sin reloj, feedback inmediato). Banco: `datos/preguntas/` (index.json + shards) con 12 preguntas semilla, `validar_preguntas.py` como barrera de calidad y `datos/preguntas/LEEME.md` como guía de autoría para cualquier modelo |
| 2026-07-11 | Mapa de contenido | `MAPA_CONTENIDO_FIG.html`: guía visual para Francisco de dónde subir fotos y editar textos por página |
| 2026-07-09 | Tarjetas v4 | Feed 1080×1350 rediseñada + LinkedIn 1200×627 + HTML autocontenida + VIDEOS Feed/Story con intro animada (MediaRecorder; WebM Chrome / MP4 Safari). Gráfico de 3 líneas: retorno equipo vs promedio vs ACWI; miembros, delta badge, logos colaboradores, RRSS por formato. Esquema: `historial[].ret` + serie `acwi` (generar_torneo.py --acwi); el promedio lo calcula la página. Hook `window.__figCards` |

## 4. Backlog priorizado

Columna **Modelo**: capacidad mínima recomendada para hacerlo bien.
*Haiku* = mecánico/plantilla · *Sonnet* = código con criterio · *Opus/Fable* =
diseño/arquitectura nueva. Si un modelo menor toma una tarea marcada mayor,
que la divida y pida confirmación a Francisco en las decisiones de diseño.

### P0 — Bloqueadores (requieren input de Francisco)

| # | Tarea | Modelo | Detalle |
|---|---|---|---|
| 1 | **Crear el Apps Script de postulaciones** y pegar su URL en `datos/club.json → config.postulaEndpoint` | Sonnet | El formulario ya está listo. El script: Web App de Google Apps Script ligado a una planilla, `doPost(e)` que parsea `JSON.parse(e.postData.contents)` y hace `appendRow` con [fecha, nombre, correo, carrera, anio, area, motivacion, linkedin]. Desplegarlo "Cualquiera puede acceder". Francisco debe crearlo desde SU cuenta (Drive es solo-lectura para IAs) — darle el código listo para pegar |
| 2 | **Primer torneo.json real** | Sonnet | Correr `python3 generar_torneo.py --excel <ranking.xlsx> --inscripciones <insc.xlsx> --semana N --corte "DD · MMM · 2026"`. Si los encabezados del Excel no calzan, ajustar `ALIAS` en el script. Pedir el Excel a Francisco |
| 3 | **Confirmar colores FIW** con Delia | Haiku | Editar solo las 4 variables `--acc*` al inicio del `<style>` de `fiw/index.html` |
| 3b | **Logo oficial de FIW** | Haiku | No existe en el Drive (carpeta FIG WOMEN solo tiene fotos). Pedirlo a Delia; guardarlo en `logos/fiw.png` y reemplazar `fig-blanco.png` en nav+intro de `fiw/index.html` |
| 4 | **URL de las Bases + contacto** en `CONFIG.urls` (`bases`, `contacto`) | Haiku | La de bases probablemente es `https://mpazq-afk.github.io/torneoportafolio2026/documentos/Bases_finales_torneo_portafolio_2026.pdf` (ya usada en torneo/index.html) — confirmar con Francisco y poner en index.html + club.json |
| 5 | **Mapear y curar fotos desde el Drive** | Sonnet | ⏳ EN CURSO (2026-07-12) — mapeo de carpetas YA HECHO (ver tabla abajo), descarga bloqueada por un problema del conector de Drive (ver nota). Retomar: para cada fila de la tabla, bajar los fileId ya elegidos (o rehacer la selección — criterio: spread parejo en el tiempo dentro de la carpeta, priorizando nitidez/que se vea gente), convertir HEIC→JPG con `pillow_heif`, correr `optimizar_fotos.py`, numerar `1.jpg, 2.jpg…` sin saltos, commitear |
| 5b | **Compresión automática de fotos** | ✅ Hecho (Fable, 2026-07-12) | `optimizar_fotos.py`: redimensiona a máx 2000px + JPG calidad 78, idempotente. Correr siempre después de agregar fotos nuevas (a mano o vía tarea #5). Opcional: hook de pre-commit local, instrucciones al final del script |

**Mapeo de carpetas del Drive → eventos** (confianza alta, por nombre de carpeta explícito — no hace falta re-verificar esta parte, solo descargar):

| Evento (`carpeta` en eventos.json) | Carpeta del Drive | folderId | Fotos disponibles |
|---|---|---|---|
| `lanzamiento-club-2025` | Historial Audiovisual/Primavera 2025/Lanzamiento del club/Fotos | `1isnJzHfxkEH9Z5r0jB4ferTqdkQVnyzj` | 44 JPG (Samsung, ~7-9 MB c/u) |
| `charla-colegios-lab-2025` | ACTIVIDADES COLEGIOS/Charlas educativas (visitas de colegios al laboratorio)/Fotos | `1ZnRl_3Y3OibodNUETXRe4rloHVkMuq5G` | ~20 JPG (mezcla DSLR pesadas + WhatsApp livianas) |
| `torneo-primavera-2025` | Historial Audiovisual/Primavera 2025/Torneos/Fotos | `1vMgMjAjaqwkiqA2X37fk270miO571ldk` | 9 JPG (WhatsApp, ~200-350 KB) |
| `visita-santander-2026` | Visitas/Visita santander | `1cF_MK0-001thlqh20gyNPxpcWOOQs5ba` | 50+ (HEIC + JPG + algunos .MOV a ignorar) — tiene más de 50, pedir página siguiente si se quiere ver todo |
| `visita-moneda-2026` | Visitas/Moneda otoño 2026 | `1tjo6sBjv-gqU0goefu00sebsvpDVGKj6` | ~29 HEIC + 1 .MOV a ignorar |
| `clase-edv-2026` | ACTIVIDADES COLEGIOS/Clase EDV | `1mq9LXwmIai037bQRVJ1W_A0vnakhNlcO` | 9 HEIC |
| `fiw-mayo-2026` | FIG WOMEN (raíz) | `108dhOgXayjjleYURNaWkLOPlsgUPqoj_` | ~7 JPG (ya mapeada en sesión anterior) |
| `torneo-portafolio-2026` | **NO ENCONTRADA** | — | Sin carpeta de fotos propia — no confundir con `torneo-primavera-2025`. Preguntar a Francisco dónde están (o si aún no hay) |
| `charla-analisis-tecnico-2025` | **NO ENCONTRADA** | — | Solo hay PPT + formulario de asistencia en MATERIAL ACTIVIDADES, sin carpeta de fotos. Preguntar a Francisco |

**Nota de la sesión 2026-07-12:** el conector de Google Drive dejó de responder a
`download_file_content` específicamente (search/listado siguió funcionando)
después de ~10 descargas — probablemente un límite temporal del conector, no
del contenido. Se alcanzaron a bajar 2 fotos de prueba de `lanzamiento-club-2025`
(guardadas fuera del repo, en el scratchpad de esa sesión, se perdieron al
cerrar). **Recomendación:** descargar de a UNA por vez (nunca en paralelo —
eso fue lo que gatilló el primer corte), y si el error "session expired"
aparece, probar de nuevo en una sesión nueva en vez de reintentar muchas veces
en la misma.

### P1 — Alto valor, sin bloqueos

| # | Tarea | Modelo | Detalle |
|---|---|---|---|
| 6 | **Página de metodología/reglas del torneo ampliada** | Sonnet | Sección o página con las reglas completas de las Bases (rebalanceos, pisos, disputas) para no depender solo del PDF |
| 7 | **Resúmenes de eventos** | Haiku | 8 de 9 eventos en `datos/eventos.json` dicen "[Resumen por completar]" — redactar con Francisco 2-3 líneas por evento |
| 8 | **SEO/social**: og:image + meta tags Open Graph/Twitter en las 5 páginas | Haiku | Generar una og:image estática 1200×630 con el estilo FIG (puede ser canvas→PNG una vez, guardada en fotos/) |
| 9 | **404.html** de GitHub Pages con el estilo FIG | Haiku | Copia de la base de postula/index.html con mensaje + enlaces |
| 10b | **Ranking global del juego** | Sonnet | Hoy el ranking de El Rally del Toro es por navegador (localStorage). Para hacerlo global: mismo patrón del formulario — Apps Script `doPost` que guarda {nombre, valor, fecha} en una planilla y `doGet` que devuelve el top-10; la página cae a localStorage si el endpoint no está configurado |
| 10 | **Archivo semanal del ranking** | Sonnet | `generar_torneo.py` ya guarda historial dentro de torneo.json; opcional: volcar snapshot `datos/torneo/semana-N.json` para auditoría/disputas |

### P0.5 — Perfiles reales desde los CV del Drive

En el Drive ya existe una carpeta `CV` con los currículums de algunos
cofundadores. Objetivo: usarlos para completar `datos/club.json` con
descripciones breves, LinkedIn, y poblar la sección **"FIG en la
industria"** (`personas.industria` en `datos/club.json`).

**✅ C1-C4 completados (2026-07-12) para los 4 CV que había en el Drive
en esa fecha.** Solo algunos cofundadores han subido su CV todavía — es
esperable que más se sumen o actualicen el suyo con el tiempo. Para no
releer los mismos PDF sesión tras sesión, el estado de qué se procesó
vive en **`datos/cv_procesados.json`**: por cada archivo guarda su
`fileId` + `modifiedTime` de Drive. **Protocolo para sesiones futuras:**
antes de leer un CV de la carpeta, comparar su `modifiedTime` actual
contra el que está en `cv_procesados.json` — si coincide, saltárselo (ya
está reflejado en `club.json`); si es nuevo o cambió, procesarlo y
actualizar esa entrada.

| # | Tarea | Modelo | Detalle |
|---|---|---|---|
| C1 | **Inventario de la carpeta CV** | Haiku | ✅ Hecho — 4 CV encontrados: Benjamín Sáez Molina, Jhosep García, Rafael Aliendre (los 3 ya en `personas.directiva`) y Samuel Rodríguez Arnolds (no está en `personas.directiva`). Al reabrir esta tarea en el futuro, comparar `modifiedTime` contra `datos/cv_procesados.json` antes de listar/leer de nuevo |
| C2 | **Descripciones breves + LinkedIn** | Sonnet | ✅ Hecho — se agregó `linkedin` a Benjamín Sáez Molina, Jhosep García y Rafael Aliendre en `personas.directiva`. Los `detalle` existentes ya calzaban con lo que dice cada CV, no se reescribieron |
| C3 | **Poblar "FIG en la industria" con prácticas reales** | Sonnet | ✅ Hecho — se reemplazaron las 3 tarjetas placeholder por: Benjamín Sáez Molina (Itaú · Wealth Management), Rafael Aliendre (CODELCO · Dirección Estrategia e Inteligencia de Mercado) y Samuel Rodríguez Arnolds (MoonValley Capital · Investment Banking Intern). Jhosep García no tiene práctica externa que agregar (solo roles internos FIG/FEN) |
| C4 | **Revisión antes de publicar** | Opus/Fable | ✅ Hecho — se verificó que `personas.*` solo tiene nombre + rol + LinkedIn público; del CV de Samuel se excluyó explícitamente dirección particular y edad (regla dura de `CLAUDE.md`). Falta una segunda pasada humana de Francisco si quiere afinar tono antes de que esto se difunda más |

**⚠️ Pregunta abierta para Francisco (no resuelta por la IA a propósito):**
el CV de Jhosep García se autodescribe como líder del Área Valuation
(coincide con lo que ya dice `club.json`), pero el CV de Samuel Rodríguez
Arnolds también se autodescribe como fundador/líder de Valuation. Son
datos contradictorios entre dos CV — no se decidió a favor de ninguno,
queda para que Francisco lo resuelva. Mientras tanto Samuel NO se agregó
a `personas.directiva` (solo a `personas.industria`, por su práctica
confirmada en MoonValley Capital), justamente para no tomar esa decisión
por él.

**Nota permanente:** el CV de Francisco ya lo subirá él mismo a esta
conversación — cuando llegue, agregar su práctica en el área de Riesgo de
LarraínVial a `personas.industria` (ver tarea C3) sin necesidad de ir al
Drive por ese dato puntual, y registrar el CV en `datos/cv_procesados.json`
igual que los demás.

### P1.5 — Macro repositorio de preguntas (cuando Francisco suba el material al Drive)

Francisco subirá una carpeta al Drive con AÑOS de pruebas y clases de
finanzas (volumen colosal). Objetivo: convertirla en el banco de preguntas
del Desafío FIG. La infraestructura ya existe (`desafio/` + `datos/preguntas/`
+ validador); esto es SOLO producción de contenido, diseñada para repartirse
entre modelos. **Leer `datos/preguntas/LEEME.md` antes de escribir una sola
pregunta — es la guía de autoría y el contrato de calidad.**

| # | Tarea | Modelo | Detalle |
|---|---|---|---|
| Q1 | **Inventario del material** | Haiku | Listar la carpeta nueva del Drive (solo lectura), mapear archivo → ramo → tema(s) propuestos. Salida: tabla en esta hoja de ruta. Proponer temas/ramos nuevos para index.json si el material no calza en los existentes |
| Q2 | **Extracción de preguntas por lotes** | Sonnet | Por archivo del material: leerlo del Drive, redactar 20-40 preguntas según LEEME.md (con `fuente` citando el archivo), guardarlas en el shard del tema, correr `validar_preguntas.py` (debe decir TODO OK), commit por lote. Shards de máx 200 preguntas/150 KB — crear `tema-02.json`… y listarlos en index.json |
| Q3 | **Revisión pedagógica por muestreo** | Opus/Fable | ~10% de cada lote: precisión técnica, distractores plausibles, explicaciones que enseñan. Corregir o eliminar. Sin esta revisión un lote no se considera terminado |
| Q4 | **Balance del banco** | Haiku | `validar_preguntas.py --stats` tras cada tanda: ningún tema raquítico, dificultades ~40/40/20. Anotar huecos aquí |
| Q5 | **Ranking global del Desafío** | Sonnet | Igual que el del Rally (P1-10b): Apps Script doPost/doGet + planilla; la página cae a localStorage si no hay endpoint |
| Q6 | **Preguntas de historia con narrativa** | Fable | El tema historia-mercados admite mini-historias como enunciado (2-3 frases de contexto + pregunta). Requiere redacción fina — no delegar a Haiku |

### P2 — Expansión (ver IDEAS_GRAN_ESCALA_FIG.md antes de empezar)

| # | Tarea | Modelo | Detalle |
|---|---|---|---|
| 11 | **Conectar ranking-video (overlay OBS) a datos/torneo.json** | Sonnet | Hoy lee un CSV de Google Sheets; apuntar al JSON del repo (IDEAS_GRAN_ESCALA §6) |
| 12 | **Newsletter / resumen semanal automático** | Opus | Generar un HTML de resumen semanal del torneo (top movimientos, sube/baja) desde torneo.json — diseño nuevo |
| 13 | **Página de alumni/red de ex-miembros** | Opus | Diseño nuevo; datos en `datos/alumni.json`; requiere aprobación de Francisco sobre qué datos publicar (regla: solo nombre+rol+LinkedIn) |
| 14 | **Dashboard interno de la directiva** | Opus | Métricas del club (asistencia a eventos, postulaciones). Definir alcance con Francisco primero |
| 15 | **Migrar a dominio propio** las páginas nuevas | Sonnet | Coordinar con el GitHub Pages existente (`mpazq-afk`) y feninvestmentgroup.com — decisión de Francisco |

## 5. Decisiones tomadas (no re-litigar)

- **Historial del torneo vive DENTRO de torneo.json** (campo `historial` por
  equipo), no en archivos separados — así la página hace 1 solo fetch y el
  script lo mantiene solo. Snapshots separados son opcionales (tarea #10).
- **El formulario postula por Apps Script + no-cors POST** (patrón estándar
  GitHub Pages sin backend). No agregar backends ni servicios de pago.
- **Las tarjetas descargables se generan 100% en el navegador** (canvas para
  PNG, Blob para HTML). Sin servidor.
- `delta` lo calcula `generar_torneo.py` comparando con la semana anterior
  del propio torneo.json (positivo = sube).

## 6. Qué preguntar a Francisco (pendiente de respuesta)

1. URL del Web App de Apps Script para postulaciones (o pedirle crear uno —
   darle el código listo, ver P0-1).
2. Confirmación de URL de las Bases PDF y correo/URL de contacto.
3. Colores oficiales FIW (vía Delia).
4. Excel oficial del ranking (para el primer torneo.json real).
5. Fotos de eventos y FIW (él las sube, numeradas).
6. ¿Quién lidera el Área Valuation — Jhosep García (Vicepresidente, como
   dice hoy `club.json`) o Samuel Rodríguez Arnolds (su propio CV dice que
   fundó/lidera esa área)? Ver nota en P0.5, no se resolvió adivinando.

## 7. Cómo cambiar de modelo / intensidad (guía para Francisco)

Para ahorrar tokens sin perder calidad, pide el cambio según la tarea:

- **Haiku 4.5** (barato, rápido): tareas P0-3/P0-4, P1-7/8/9 — ediciones
  mecánicas con instrucciones ya escritas aquí.
- **Sonnet** (equilibrio): scripts Python, conectar datos, páginas que copian
  el sistema de diseño existente (P0-1/2, P1-6/10, P2-11/15).
- **Opus / Fable** (máxima capacidad): diseño visual nuevo, arquitectura,
  decisiones de producto (P2-12/13/14) y cualquier cosa que toque el sistema
  de diseño global.

Cualquier modelo que retome: leer `CLAUDE.md` + este archivo primero, seguir
la sección 1, y actualizar ambos documentos al terminar.
