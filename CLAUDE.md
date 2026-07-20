# CLAUDE.md — Contexto del proyecto Web FIG

> Este archivo lo lee Claude Code automáticamente al abrir esta carpeta.
> No lo borres ni lo muevas. Mantenlo actualizado: cuando algo cambie de
> estado (una página deja de ser demo, se conecta un enlace, etc.), edita
> la sección correspondiente en vez de dejar que quede desactualizado.

## Qué es esto

El ecosistema web de **FEN Investment Group (FIG)**, club de inversiones de
la FEN — Universidad de Chile. Un conjunto de páginas HTML autocontenidas
(sin build steps, sin framework, compatibles con GitHub Pages) que comparten
un mismo sistema de diseño y se alimentan de archivos JSON como capa de
datos, para que el contenido se edite sin tocar código.

**Filosofía no negociable de este proyecto:** Excel/Drive es la fuente de
verdad → un script Python lo convierte a JSON → las páginas HTML leen ese
JSON y se renderizan solas. Nunca hardcodear datos que van a cambiar
(rankings, personas, fotos, textos) directamente en el HTML/JS de una
página. Si algo cambia seguido, va en un `.json` bajo `datos/`.

## Estructura del repo

```
/
├── index.html              ← sitio principal FIG (hero, áreas, torneo resumen, historia, equipo, eventos resumen)
├── eventos/index.html      ← bitácora de actividades (torneos, visitas, charlas, comunidad)
├── fiw/index.html           ← página de FEN Investment Woman (paleta propia, editable)
├── torneo/index.html        ← ranking oficial del Torneo Portafolio 2026 (con trayectoria por equipo)
├── postula/index.html       ← formulario de postulación al club
├── juego/index.html          ← "El Rally del Toro": juego de espera (runner con el toro; vender = asegurar puntaje)
├── desafio/index.html        ← "Desafío FIG": trivia de finanzas (banco en datos/preguntas/, validar con validar_preguntas.py)
├── en/index.html              ← one-pager en INGLÉS para partners internacionales (única página en inglés del sitio)
├── generar_torneo.py        ← Excel ranking_ordenado → datos/torneo.json (mantiene historial semanal)
├── generar_ics.py           ← datos/eventos.json → eventos/fig.ics (calendario iCal; correr tras editar eventos)
├── optimizar_fotos.py       ← comprime fotos/ automáticamente (máx 2000px, JPG 78%) — correr tras agregar fotos
├── validar_preguntas.py     ← barrera de calidad del banco de preguntas del Desafío FIG
├── HOJA_DE_RUTA_FIG.md      ← LISTA MAESTRA: backlog priorizado + protocolo de continuidad
├── MAPA_CONTENIDO_FIG.html  ← guía visual para Francisco: dónde subir fotos y editar texto de cada página (abrir con doble clic)
├── logos/                   ← logos oficiales bajados del Drive (FIG oro/blanco/navy, Itaú, BlackRock)
│   └── industria/            ← logos de empresas para "FIG en la industria" (ver LEEME.txt de la carpeta)
├── datos/
│   ├── club.json             ← personas, eventos resumen, historia, URLs del sitio principal
│   ├── cv_procesados.json    ← manifiesto anti-relectura de CV del Drive (fileId+modifiedTime, evita reprocesar los que no cambiaron)
│   ├── eventos.json           ← lista completa de eventos (bitácora)
│   ├── fiw.json                ← textos y equipo de FEN Investment Woman
│   └── torneo.json.ejemplo      ← ESQUEMA del ranking (ver "Pendiente" abajo — aún no existe torneo.json real)
├── fotos/
│   ├── eventos/<carpeta-evento>/  ← 1.jpg, 2.jpg, 3.jpg… por evento (numeradas, sin saltos)
│   ├── directiva/                  ← retratos de cofundadores: <nombre-slug>.jpg (ver LEEME.txt de la carpeta)
│   └── fiw/                        ← 1.jpg, 2.jpg, 3.jpg… de la comunidad FIW
├── LEEME_PAGINAS.md          ← documentación de cómo se conectan las páginas nuevas
├── IDEAS_FIG.md               ← ideas de una sesión (rápidas)
├── IDEAS_GRAN_ESCALA_FIG.md    ← ideas de orquestación/pipeline (para Claude Code)
├── MAPEO_DRIVE_FIG.md           ← mapeo completo de la carpeta de Google Drive del club (solo lectura)
└── ACTIVIDADES_FIG.md            ← bitácora de actividades históricas extraída del Drive
```

Todas las páginas comparten: navy `#0A1128` + oro `#D4AF37`, tipografías
Playfair Display + Inter + IBM Plex Mono, cursor crosshair personalizado,
reveals on-scroll, y respeto total a `prefers-reduced-motion`. La página
`fiw/index.html` es la única con paleta propia (oro rosa, variables `--acc*`
al inicio de su `<style>`) — no tocar esos 4 valores sin pedirlo
explícitamente a Francisco, son la identidad visual de esa área.

## Estado actual de cada pieza (revisar y actualizar esta sección seguido)

| Pieza | Estado | Detalle |
|---|---|---|
| `index.html` | ✅ Producción | Sitio principal completo. Orden de secciones (2026-07-19, pedido de Francisco): inicio → nosotros → **eventos** → áreas → torneo → historia → equipo. Nav con ese mismo orden + enlace **FIG Woman** + menú **"Jugar ▾"** (desplegable hover/focus con El Rally del Toro y el Desafío FIG; en móvil van como enlaces directos). Fondos claros SIN cuadrícula gris (se eliminó el patrón de líneas de 72px, solo queda el glow radial dorado). Ticker bursátil al pie con el top 5 del torneo — aparece solo cuando exista `datos/torneo.json` real (hoy oculto). Footer enlaza `en/index.html`. **Expediente de cofundadores**: clic en cualquier tarjeta de §Nosotros abre un overlay con ficha completa (bio + trayectoria desde `perfil` en `club.json`, foto grande si existe en `fotos/directiva/<slug>.jpg` — ver `fotos/directiva/LEEME.txt` —, monograma dorado si no), flechas ←/→ para recorrer el grupo, ✕/Esc para cerrar, navegable por teclado. **Miniaturas con foto real** en la grilla de §Nosotros (mismo `probeFoto()`, ahora en alcance global). **"FIG en la industria"** agrupada por empresa (no por persona): logo real si existe `logos/industria/<slug>.*` (ver `logos/industria/LEEME.txt`) o chip de iniciales si no, tooltip al hover/foco con quiénes de FIG han pasado por esa empresa enlazados a su LinkedIn. **Tira de fotos reales de eventos en movimiento** detrás del hero y de §Historia (`.photo-marquee`, detectadas solas desde `datos/eventos.json` + `fotos/eventos/`, opacidad baja para no tapar el texto, respeta reduced-motion) — no está en §Áreas porque esa sección ya tiene sus propias fotos y se veía recargado |
| `eventos/index.html` | ✅ Producción | 9 eventos reales con resúmenes completos en `datos/eventos.json`; filtros por tipo Y año; botón de calendario `fig.ics` (regenerar con `generar_ics.py`); modo proyección `?pantalla=1` (fotos fullscreen para TVs, enlazado en el footer) |
| `en/index.html` | ✅ Producción | One-pager en inglés para partners (BlackRock, bancos): áreas + torneo con solo datos verificados. Única página del sitio con texto en inglés — es su propósito |
| `fiw/index.html` | ⚠️ Placeholder | Estructura y datos completos, pero **colores de marca aún no confirmados** por Delia Avilán/FIW — usa un oro rosa provisional. Sin fotos en `fotos/fiw/` todavía |
| `torneo/index.html` | ⚠️ Modo DEMO | 8 equipos ficticios. **Falta `datos/torneo.json` real**. Overlay con gráfico de 3 líneas (retorno equipo/promedio/ACWI). Tarjetas: Feed PNG, **Story PNG**, LinkedIn PNG, HTML y **videos animados** Feed/Story con intro (logo→nombre→colaboradores→ficha). En celular, los botones de tarjetas **comparten directo con el panel nativo del sistema** (`navigator.share`, Instagram queda a un toque) en vez de forzar una descarga; en iPhone la tarjeta Story además intenta abrir Instagram directo en el compositor de Historias (truco de portapapeles + `instagram-stories://`, con fallback automático). Grabación de video a 24fps con progreso visible en el botón. Logos de colaboradores en hero y tarjetas. La línea temporal de §Metodología integra las actividades del club desde `datos/eventos.json` (tags por tipo + descripción al hover, tarea #16 ✅) |
| Enlaces cruzados | ✅ Conectados | `index.html` ya enlaza a `eventos/`, `fiw/`, `torneo/` y `postula/` (CTAs, footer, `CONFIG.urls` y `datos/club.json`) |
| `generar_torneo.py` | ✅ Escrito | Lee `ranking_ordenado` + Excel de inscripciones → escribe `datos/torneo.json`, conserva el `historial` semanal y calcula `delta`. Probar con el Excel real (ajustar `ALIAS` si los encabezados no calzan). Modo `--demo` disponible |
| `postula/index.html` | ✅ Endpoint conectado (sin verificar en vivo) | Formulario de postulación completo; envía (con `tipo:"postulacion"`) a `config.figEndpoint` (el Apps Script COMPARTIDO del sitio) de `datos/club.json` — la URL ya está pegada (2026-07-18), pero nadie ha confirmado aún que una postulación real llegue a la planilla (este entorno no puede alcanzar `script.google.com`); Francisco debe probarlo una vez |
| `desafio/index.html` | ✅ Funcional (banco real) | Trivia: modo desafío (secuencial, puntaje decae, malas descuentan, revisión con explicaciones, áreas fuerte/débil, ranking local) y modo estudio (por tema o ramo, sin reloj). Banco en `datos/preguntas/` — **300 preguntas reales en 12 temas** extraídas del material de finanzas del Drive (P1.5 Q2, lotes 1-23; validar siempre con `validar_preguntas.py`). Idea pendiente de Francisco: selector de dificultad (1/2/3) en el juego — el campo `dificultad` ya existe en todas las preguntas |
| `juego/index.html` | ✅ Funcional | "El Rally del Toro": runner canvas con un **toro dorado dibujado a mano** (silueta embistiendo inspirada en el logo, galope de 4 patas, cola y cuernos animados — ya no se usa la imagen del logo en el canvas); velas rojas y burbujas como obstáculos; sparkline "TU RUN" con la curva de equity de la corrida; VENDER asegura el puntaje y ofrece **descargar una tarjeta PNG 1080×1350** del resultado (monto, % ganancia, el toro, cita del club) — filosofía "saber cuándo salir". Ranking: lee `config.figEndpoint` de `datos/club.json` (el Apps Script COMPARTIDO del sitio, código listo en `HOJA_DE_RUTA_FIG.md` P0-1) y muestra "Ranking global"; si el endpoint está vacío o el fetch falla, cae automático a localStorage por navegador. **Endpoint ya conectado (2026-07-18)**, pendiente de que Francisco confirme que una corrida real llega a la pestaña `Ranking` de la planilla |
| Fotos de eventos | ⚠️ Parcial | 7 de 9 eventos con fotos curadas y comprimidas (ver `HOJA_DE_RUTA_FIG.md` tarea #5). Faltan `torneo-portafolio-2026` y `charla-analisis-tecnico-2025` (sin carpeta en el Drive) y más variedad en `lanzamiento-club-2025` (fotos Samsung de 7-9 MB, por encima del límite del conector de Drive) |
| Fotos de la directiva | ⚠️ Parcial (10/13) | `fotos/directiva/` ya tiene foto real de Benjamín Sáez Molina, Jhosep García, Francisco Valenzuela (2026-07-19: reemplazada por una foto vertical real de mayor resolución que subió Francisco, ya no depende de upscale), Manuel Paz, Benjamín Disi, Rafael Aliendre, David González Cañon, Samuel Rodríguez Arnolds, Juan Pablo Díaz Cerda y Benjamín Solís. Faltan Agustín Arriagada, Juan José Limari y Delia Avilán — siguen mostrando el monograma dorado hasta que suban la suya (ver `fotos/directiva/LEEME.txt`). Nota: Samuel Rodríguez Arnolds se sumó a `personas.directiva` el 2026-07-18 (co-encargado de Valuation junto a Jhosep, confirmado por Francisco) — antes solo estaba en `personas.industria` |

## Lo que YA existe fuera de esta carpeta (contexto crítico, no reinventar)

- **Ya existe un sitio FIG distinto, en producción real**, en el Drive
  (`WEB/fen-investments-web/`), con URLs reales confirmadas:
  - LinkedIn: `https://www.linkedin.com/company/fen-investment-group`
  - Instagram: `https://www.instagram.com/fen.investment.group/`
  - Torneo (GitHub Pages): `https://feninvestmentgroup.com/torneoportafolio2026/`
  - Form de postulación (Apps Script): endpoint documentado en `MAPEO_DRIVE_FIG.md`
  Antes de inventar una URL nueva para algo, revisar si ya existe una real
  en ese mapeo.
- **Ya existe una app real del torneo** (`torneo-app`, Vite+TS+Tailwind) y
  un **generador de overlay de video para OBS** (`ranking-video`) que hoy
  lee un CSV público de Google Sheets — candidato a conectarse a
  `datos/torneo.json` en vez de al CSV (ver `IDEAS_GRAN_ESCALA_FIG.md` §6).
- El repo de GitHub Pages del torneo vive bajo el usuario `mpazq-afk`.
- Todo el detalle de assets, logos, ids de Drive y hallazgos está en
  `MAPEO_DRIVE_FIG.md` — léelo antes de pedir a Francisco un logo o una URL
  que probablemente ya está mapeada ahí.

## Cómo se edita cada tipo de contenido (para explicarle esto a Francisco, no lo hagas tú directamente salvo que te lo pida)

- **Texto/personas/eventos** → Francisco edita un Excel → un script
  `generar_*.py` (algunos existen, otros hay que crearlos) produce el JSON
  correspondiente en `datos/`.
- **Fotos** → se suben directo a la carpeta correcta en `fotos/`, numeradas
  `1.jpg, 2.jpg, 3.jpg…` sin saltos. Las páginas las detectan solas
  (`probeFotos()` en el JS de cada página prueba extensiones y números
  hasta fallar). No requiere tocar ningún JSON.
- **Ranking del torneo** → sale del pipeline semanal ya existente
  (`ordenar_tmsg.py` → `reconstruir_nav.py` → `build_outputs.py`) — falta
  el último eslabón `generar_torneo.py` que traduzca `ranking_ordenado` al
  esquema de `datos/torneo.json.ejemplo`.

## Pendiente / próximos pasos conocidos

**La lista maestra vive en `HOJA_DE_RUTA_FIG.md`** (backlog priorizado,
decisiones tomadas, protocolo de continuidad entre sesiones/modelos —
leerla SIEMPRE al retomar el proyecto y actualizarla al terminar).
Resumen de bloqueadores:

1. ✅ **Endpoint COMPARTIDO del sitio** — Francisco lo creó y desplegó
   (2026-07-18), URL ya pegada en `config.figEndpoint` de `datos/club.json`.
   Pendiente: que confirme en vivo que las 3 pestañas reciben datos (ver
   `HOJA_DE_RUTA_FIG.md` P0-1).
2. **Primer `datos/torneo.json` real** con `generar_torneo.py` + Excel
   oficial (P0-2).
3. **Colores oficiales de FIW** con Delia → variables `--acc*` (P0-3).
4. **URLs de `bases` y `contacto`** en `CONFIG.urls` / `club.json` (P0-4).
5. **Fotos reales** en `fotos/eventos/*` y `fotos/fiw/` (P0-5, solo Francisco).

## Reglas duras (no romper)

- **Nunca** tocar Google Drive en modo escritura — es explícitamente
  solo lectura para cualquier IA en este proyecto (instrucción directa de
  Francisco). Si hace falta un archivo del Drive, pedírselo a él o dejar
  instrucciones claras de qué bajar y dónde ponerlo.
- **Nunca** commitear datos personales sensibles más allá de nombre + rol +
  LinkedIn público (eso sí está aprobado para el torneo).
- Mantener las páginas **sin build step**: HTML/CSS/JS planos, sin npm ni
  bundler, porque así es como se despliegan a GitHub Pages hoy.
- Todo texto de cara al usuario va en **español** (única excepción:
  `en/index.html`, el brief para partners internacionales — ese va en inglés
  a propósito).
- Las 8 páginas llevan al pie del footer el crédito **"Creado por
  Francisco Valenzuela y Manuel Paz"** (en inglés en `en/index.html`:
  "Made by... and..."), cada nombre enlazado a su LinkedIn real. Al
  agregar una página nueva, copiar ese `<span>` del footer de cualquier
  página existente.
- Las 8 páginas llevan un **beacon de métricas anónimas** (sin cookies:
  página + fecha + origen) que envía con `tipo:"visita"` al mismo
  `config.figEndpoint` compartido, y queda inerte mientras esté vacío.
  Al agregar una página nueva, copiar el snippet del final de cualquier
  página existente.
- **Un solo Apps Script para todo el sitio** (`config.figEndpoint` en
  `club.json`): postulaciones, ranking del Rally del Toro y métricas de
  visitas comparten el mismo Web App y la misma planilla (3 pestañas). No
  crear un endpoint nuevo por feature — sumar un `tipo` más al `doPost`/
  `doGet` existente (código completo en `HOJA_DE_RUTA_FIG.md`, P0-1).
- Antes de escribir un script nuevo `generar_X.py`, revisar si el patrón ya
  existe para otro dato (todos siguen la misma forma: leer Excel → validar
  → volcar JSON con el esquema documentado en el propio archivo o en su
  `.ejemplo`).
