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

Última actualización: **2026-07-07** (sesión: enlaces cruzados + historial de
rendimiento + formulario de postulación + este documento).

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
| 4 | **URL de las Bases + contacto** en `CONFIG.urls` (`bases`, `contacto`) | Haiku | La de bases probablemente es `https://mpazq-afk.github.io/torneoportafolio2026/documentos/Bases_finales_torneo_portafolio_2026.pdf` (ya usada en torneo/index.html) — confirmar con Francisco y poner en index.html + club.json |
| 5 | **Fotos reales** en `fotos/eventos/*` y `fotos/fiw/` | — | Solo Francisco (Drive solo-lectura). Numeradas 1.jpg, 2.jpg… sin saltos |

### P1 — Alto valor, sin bloqueos

| # | Tarea | Modelo | Detalle |
|---|---|---|---|
| 6 | **Página de metodología/reglas del torneo ampliada** | Sonnet | Sección o página con las reglas completas de las Bases (rebalanceos, pisos, disputas) para no depender solo del PDF |
| 7 | **Resúmenes de eventos** | Haiku | 8 de 9 eventos en `datos/eventos.json` dicen "[Resumen por completar]" — redactar con Francisco 2-3 líneas por evento |
| 8 | **SEO/social**: og:image + meta tags Open Graph/Twitter en las 5 páginas | Haiku | Generar una og:image estática 1200×630 con el estilo FIG (puede ser canvas→PNG una vez, guardada en fotos/) |
| 9 | **404.html** de GitHub Pages con el estilo FIG | Haiku | Copia de la base de postula/index.html con mensaje + enlaces |
| 10 | **Archivo semanal del ranking** | Sonnet | `generar_torneo.py` ya guarda historial dentro de torneo.json; opcional: volcar snapshot `datos/torneo/semana-N.json` para auditoría/disputas |

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
