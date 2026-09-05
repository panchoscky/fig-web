# CLAUDE.md — Contexto del proyecto Web FIG

> Este archivo lo lee Claude Code automáticamente al abrir esta carpeta, **en cada
> sesión**. Por eso es corto a propósito: solo lo que aplica SIEMPRE.
> El detalle vive en `docs/` y se consulta cuando hace falta.
>
> **Reestructurado el 2026-09-02**: antes eran 2063 líneas (~30 mil tokens en cada
> conversación). El contenido no se perdió, se movió — ver los punteros de abajo.

## Dónde está cada cosa

| Necesitas… | Lee |
|---|---|
| Qué hace un archivo, dónde vive un dato | `docs/ARBOL_REPO.md` |
| El estado de una página antes de tocarla | `docs/ESTADO_PIEZAS.md` |
| Por qué algo quedó como quedó | `docs/BITACORA.md` |
| El backlog priorizado y el protocolo de continuidad | `HOJA_DE_RUTA_FIG.md` |
| Qué columnas debe traer la planilla de miembros | `PLANILLA_MIEMBROS_FIG.md` |

**Al cerrar una tanda de trabajo, escríbela en `docs/BITACORA.md`, no acá.** Este
archivo solo cambia si cambia una regla, la rutina o el estado general.

## Qué es esto

El ecosistema web de **FEN Investment Group (FIG)**, club de inversiones de la FEN —
Universidad de Chile. Páginas HTML autocontenidas (sin build step, sin framework,
compatibles con GitHub Pages) que comparten un sistema de diseño y se alimentan de
JSON como capa de datos, para que el contenido se edite sin tocar código.

**Filosofía no negociable:** Excel/Drive es la fuente de verdad → un script Python lo
convierte a JSON → las páginas HTML leen ese JSON y se renderizan solas. Nunca
hardcodear datos que van a cambiar (rankings, personas, fotos, textos) en el HTML/JS.
Si algo cambia seguido, va en un `.json` bajo `datos/`.

**Paleta y tipografías**: navy `#0A1128` + oro `#D4AF37`, Playfair Display + Inter +
IBM Plex Mono (autoalojadas en `fuentes/`), reveals on-scroll, respeto total a
`prefers-reduced-motion`. **Tres páginas tienen paleta propia** y no siguen esa base:
`fiw/index.html` (oro rosa), `portafolio/index.html` (azul `#08213F` + naranja
`#EC7000` de Itaú, por el sponsor del Torneo Portafolio; 2026-09-02) y
`trading/index.html` (rojo `#FF0000` + `#18181E` de XTB, por el Alpha Trading
Challenge; 2026-09-04). En las tres los NOMBRES de las variables son los mismos que
en el resto del sitio (`--acc`, `--acc-light`…): cambia el valor, nunca el token.
No tocar esos valores sin pedírselo a Francisco.
El grafito `#22252B` de BlackRock **ya no existe**: era el token `--graph` y su
único uso eran las tarjetas de §Responsables de `portafolio/`, donde un gris neutro
sobre el navy se leía como una mancha pegada encima. Pasaron a `--navy-panel` el
2026-09-04 y el token se fue con ellas.

## Estado general (2026-09-02)

- **19 páginas** en `fig-web`; el espejo publica menos a propósito.
- **Torneo: 48 equipos, semana 16 (corte 28-ago-2026)**, ACWI al día.
- **Cinco desks**: PRT · Portafolio (Francisco), TRD · Trading (Manuel Paz),
  VAL · Valuation (Jhosep García), FIW · FEN Investment Woman (Delia Avilán),
  ADM · Administración (Benjamín Sáez).
- Dos repos: este (`panchoscky/fig-web`) y el **espejo** de Manuel
  (`mpazq-afk.github.io`), que recibe menos contenido.

## Reglas duras (no romper)

- **Google Drive es de solo lectura por defecto** (instrucción directa de Francisco).
  Excepción acotada: se puede **crear** un archivo/carpeta nuevo solo si Francisco lo
  pide explícitamente en ese momento y confirma antes de ejecutar. Una vez creado por
  una IA, ese mismo archivo sí se puede editar después. **Nunca** editar ni borrar algo
  que ya existía en el Drive antes de la sesión. Después de crear o editar, avisarle
  qué se hizo.
- **FIG Woman NO se publica en el repo de Manuel.** `despublicar_fiw.py` lo saca del
  espejo. Ver "El espejo" más abajo.
- **Nunca** commitear datos personales más allá de nombre + rol + LinkedIn público.
- **Sin build step**: HTML/CSS/JS planos, sin npm ni bundler.
- Todo texto de cara al usuario va en **español**. Única excepción: `en/` (y
  `en/informe/`), que van en inglés a propósito.
- Las páginas llevan al pie el crédito **"Creado por Francisco Valenzuela y Manuel
  Paz"**, cada nombre enlazado a su LinkedIn. Al crear una página, copiar ese `<span>`.
- Las páginas llevan el **beacon de métricas anónimas** (sin cookies) que envía con
  `tipo:"visita"` a `config.figEndpoint`. Al crear una página, copiar ese snippet.
- **Un solo Apps Script para todo el sitio** (`config.figEndpoint` en `club.json`):
  postulaciones, ranking del juego y métricas comparten Web App y planilla. No crear un
  endpoint por feature — sumar un `tipo` más al `doPost`/`doGet`.
- Antes de escribir un `generar_X.py` nuevo, revisar si el patrón ya existe: todos
  siguen la misma forma (leer Excel → validar → volcar JSON con esquema documentado).

## La rutina semanal

```
python generar_torneo.py --excel <Excel del corte>          # DRY-RUN: revisa el resumen
python generar_torneo.py --excel <Excel del corte> --aplicar # escribe (deduce semana y corte del nombre del Excel)
python generar_tabla.py                  # escribe torneo-tabla.json Y torneo-portada.json
node generar_og_equipos.js               # OPCIONAL: imágenes de vista previa (pesan)
python generar_paginas_equipo.py
python generar_informe_en.py             # dry-run SIEMPRE (falla si algo quedó en español)
python generar_informe_en.py --aplicar   # SOLO si el dry-run marcó cambios en informe/
python generar_sitemap.py
python verificar_sitio.py                # datos y derivados (lo corre también el hook pre-push)
python -m http.server 8000               # en otra terminal
node verificar_paginas.js                # las páginas en un navegador de verdad
node verificar_movil.js                  # teléfono
node verificar_menu_movil.js --pag=<página>   # SOLO si se tocó un menú móvil (una página por corrida)
python sincronizar_espejo.py --aplicar
python despublicar_fiw.py --aplicar      # SIEMPRE después del anterior
cd ../mpazq-afk.github.io && python generar_sitemap.py
```

> `generar_torneo.py` ya no escribe sin `--aplicar`: sin el flag muestra el
> resumen del corte (semana, equipos que entran/salen, ACWI que se conserva) y
> no toca `datos/torneo.json`. `--semana` y `--corte` se deducen de la fecha del
> nombre del Excel; pásalos a mano solo si el Excel llega sin fecha.
>
> Hay un hook **`pre-push`** instalado (no se versiona, hay que copiarlo a mano
> en cada clon) que corre `verificar_sitio.py` y corta el push si da error.

Pasos extra, solo al subir imágenes: `python generar_imagenes_web.py` (fotos nuevas) y
`python optimizar_logos.py --aplicar` (logos nuevos).

`verificar_sitio.py --arreglar` regenera los derivados por su cuenta (nunca toca datos
ni HTML escrito por una persona).

## Trampas conocidas (destiladas de todas las tandas)

Cada una costó tiempo al menos una vez. El registro completo está en `docs/BITACORA.md`.

### Datos del torneo

- **`generar_torneo.py --excels` BORRA los integrantes.** `procesar_multiples()` hace
  `eq["miembros"] = insc.get(eq["id"], [])` sin conservar lo anterior: sin
  `--inscripciones` deja a todos sin integrantes, y con `--inscripciones` los reescribe
  pisando correcciones hechas a mano. Úsalo solo para reconstruir el historial desde
  cero. Para rellenar una métrica en semanas ya publicadas usa el injerto quirúrgico
  `completar_metricas_historial.py`.
- **En un corte normal, nunca pases `--inscripciones`**: el script conserva los
  integrantes del `torneo.json` anterior, que es lo que quieres.
- **Un equipo ausente del Excel del corte desaparece por completo**, incluido su
  historial de semanas pasadas. Francisco confirmó aceptar ese comportamiento; el dato
  sigue en el historial de git.
- **En las 5 métricas de Bloomberg PORT gana el valor MÁS ALTO**, incluso en `var95` y
  `mdd` (vienen negativos: el más cercano a cero perdió menos). La única fila invertida
  es POSICIÓN, donde 1° gana. Y un IR o Sharpe negativos no se premian aunque sean el
  mejor de la tabla.
- **El orden de cada semana sale de la `posicion` guardada**, no de ordenar por puntos:
  hay empates exactos cuyo desempate no coincide con el orden descendente.
- **Hay DOS medidas de "le gana al índice" y no calzan**: `ret − acwi` contra `exc`
  (= `retRel`, el que alimenta el puntaje). Dan números muy distintos. No está
  documentado con qué base los calcula PORT. **Pendiente que el área de Portafolio
  confirme cuál es la oficial** antes de comunicarlo afuera.

### Verificar un texto del sitio

- **Mira el JSON que lo alimenta, nunca el fallback embebido en el HTML.** `club.json`
  pisa en runtime al literal JS `CLUB_DATA` y a las tarjetas estáticas: pueden decir
  cosas distintas y lo que se ve es el JSON. Esto ya causó una afirmación equivocada.
- **`grep -i` no hace case-folding de acentos** en este shell: buscar `élite` no
  encuentra "Élite". Para buscar texto con tildes en este repo, usa Python en UTF-8.
- El respaldo embebido de `index.html` tiene **12 personas** y `club.json` tiene **15**.
  No se nota en vivo, pero significa que a los 3 que faltan no se les puede aplicar un
  cambio en el respaldo.

### El espejo (`mpazq-afk.github.io`)

- **`index.html` NUNCA se copia entero** (es la única entrada "solo `index.html`" de
  `DIFIEREN`): allá el nav no tiene Miembros y FIG Woman está oculta. Para portar un
  cambio hay que llevar **solo el bloque tocado** y verificar después que el nav del
  espejo siga intacto. Un cambio en `index.html` suele tocar **tres tramos** —el
  `<style>`, el markup y el `<script>`—; portar solo uno deja el espejo a medias (ya
  pasó: las cifras del hero llegaron sin su CSS). `torneo/index.html` **sí** se copia
  entero (hoy es idéntico en los dos repos), y `informe/` + `en/informe/` **sí** se
  publican en el espejo desde el 2026-08-30. Lo que le falta al espejo es `miembros/`.
  Los `docs/*.md` y el `CLAUDE.md` del espejo tienen encabezado propio: `sincronizar_espejo.py`
  ya los marca (`CLAUDE.md` en `NO_SE_COPIAN`, los tres `docs/` en `DIFIEREN`).
- **`sincronizar_espejo.py` y `despublicar_fiw.py` son un PAR**, en ese orden, y después
  `generar_sitemap.py` DENTRO del espejo. Como el segundo reescribe 7 archivos
  (404, eventos, postula, valuation, portafolio, trading y en/), el primero **siempre**
  los reportará como "por copiar" aunque nada haya cambiado: no es un error.
- El espejo está en **CRLF** y este repo en LF. El script ya lo respeta; si lo tocas, no
  rompas `copiar_conservando_fin_de_linea()` o cada archivo saldrá como si hubieran
  cambiado sus 3.000 líneas.
- `config.sitio` está **vacío a propósito** acá: con eso se usa el origen del navegador.
  Llenarlo haría que un server local generara links de producción.

### Chequeos y navegador

- **Este sitio hace 404 a propósito**: las fotos y logos se detectan SONDEANDO rutas
  hasta que una carga. Esos 404 van en `RUTAS_SONDEADAS` de `verificar_paginas.js` y no
  son errores.
- **Para capturar una sección hay que scrollearla a la vista y esperar >0.9s**: los
  `.reveal` reciben la clase `in` recién cuando el IntersectionObserver los ve entrar.
  Si no, capturas un rectángulo navy vacío y parece que la sección está rota.
- El `clip` de `Page.captureScreenshot` va en **coordenadas del documento**, no del
  viewport: hay que sumarle `scrollY` al `getBoundingClientRect()`.
- **`chrome --headless --virtual-time-budget --dump-dom` baja igual las imágenes
  `loading="lazy"`.** Sirve para comprobar que algo se DIBUJA, no que algo se APLAZA.
- **Para mirar el sitio en teléfono hay que capturar por CDP con `mobile:true`.** Un
  `--window-size=390` sin emulación móvil da una imagen engañosa.
- Medir una página sola con `--solo=` **paga todo lo que comparte con las demás** (ej.
  `torneo.json`). Que dé más que en el barrido completo no es una regresión.

### CSS y HTML de este sitio

- **`.p-card:hover` reemplaza el `box-shadow` completo**, así que toda variante con
  filete (`--lead`, `--area`, y la combinada `--lead.--area`) tiene que repetirlo en su
  `:hover` o el filete desaparece al pasar el cursor. Mismo patrón en `.cre--*`.
- **`[hidden]` pierde contra una clase con `display`.** Por eso va
  `[hidden]{display:none!important}` en todas las páginas. La trampa vuelve cada vez que
  alguien le pone `display` a algo que también usa `hidden`.
- **El orden de los desks vive en CINCO lugares** y hay que tocarlos todos o el sitio se
  desalinea: `club.json` (`liderArea`), `AREAS` de `generar_miembros.py`,
  `config.areas` de `miembros.json`, §Áreas de `index.html` (la lista de tabs **y** su
  `.dp-view`, en el mismo orden — el conmutador trabaja por índice), y `AC={...}` de
  `miembros/index.html`. Ese último era **dos** veces hasta el 2026-09-04: el
  generador de la tarjeta PNG repetía el mapa de colores entero y ahora deriva de
  `ac(m)`. Junto a `AC` vive `AC_LITE`, la variante clara para texto chico.
- **`valuation/` y `trading/` son la MISMA plantilla**: al cambiar una, mirar si aplica
  a la otra. `portafolio/` ya se separó a propósito y no sigue la plantilla.
- **Al agregar o sacar enlaces de cualquier `.m-menu`, correr
  `node verificar_menu_movil.js --pag=<página>`**: un flex centrado sin scroll empuja
  los primeros ítems fuera del viewport y no hay barra que arrastrar.
- **El preload de fuentes está PROBADO Y DESCARTADO** (856 ms sin él contra 1684 ms con
  él). El modo `--preload` quedó escrito y documentado para que nadie lo reintente a
  ciegas. No usarlo.
- **Al cambiar una paleta hay que cambiar también la COPIA que nombra el color.**
  `portafolio/index.html` decía "la línea dorada es la frontera" en dos textos que
  ve el visitante y en seis comentarios; el oro ya no existía ahí. Después de tocar
  los tokens, buscar `dorad`/`oro` en la página (con Python en UTF-8, no `grep -i`).
- **Una rampa de color que lleva texto encima no se elige por gusto.** Los 5 tonos de
  `AL_TONOS` (barra de asignación) llevan texto tinta: la primera rampa naranja caía
  más oscura que la dorada que reemplazaba y rompía el contraste en los 2 últimos
  segmentos (4.25 y 2.93, bajo el mínimo de 4.5). Hay que replicar el PERFIL DE
  LUMINOSIDAD de la rampa anterior, no solo cambiarle el tono.
- **Un cambio de paleta deja navy viejo escondido en formato `rgba()`.** Los tokens
  se cambian en `:root`, pero `rgba(10,17,40,.78)` y compañía son el mismo color
  escrito a mano y no se mueven solos. Buscar también el hex del `<meta theme-color>`
  (pinta la barra del navegador en teléfono) y los colores dentro del JS que dibuja SVG.
- Un `--` dentro de un comentario XML lo vuelve mal formado (mordió al primer sitemap).

### Miembros

- **El área se deduce del TEXTO**, no de un campo: `area_de_texto(rol, detalle)` lee
  solo `rol` y `detalle`, **nunca la bio**, y descarta `liderArea` si no calza con el
  área deducida. Si alguien dirige un desk, su **detalle** tiene que nombrarlo.
- **`datos/miembros.json` está parchado a mano.** 145 de sus 160 fichas vienen de un
  Excel del Drive que no está en el repo: regenerar sin `--excel` las borraría. Cuando
  el Excel esté a mano, correr `generar_miembros.py --excel <ruta>`.
- El calce con el torneo no puede ser literal (nombre civil completo vs. forma corta).
  Si el subconjunto de tokens calza con más de un equipo no se asigna nada: un dato
  ambiguo es peor que uno ausente.

## Cómo se edita cada tipo de contenido

*(Para explicárselo a Francisco, no lo hagas tú directamente salvo que te lo pida.)*

- **Texto/personas/eventos** → Francisco edita un Excel → un `generar_*.py` produce el
  JSON en `datos/`.
- **Fotos** → se suben a la carpeta correcta en `fotos/`, numeradas `1.jpg, 2.jpg…` sin
  saltos. Las páginas las detectan solas. No requiere tocar ningún JSON.
- **Ranking del torneo** → sale del pipeline del repo `torneo-bloomberg-oficial` y entra
  por `generar_torneo.py`.

## Pendientes y decisiones abiertas

Bloqueadores que dependen de Francisco o del club:

1. **`contacto` sigue apuntando a `#`** — falta que Francisco defina correo o formulario.
2. **Colores oficiales de FIW** con Delia → variables `--acc*`.
3. **Fotos reales** en `fotos/eventos/*` (faltan 2 eventos) y `fotos/fiw/` (vacía).
4. **Cuál es la medida oficial de "le gana al índice"** (ver Trampas) — área de
   Portafolio.
5. **Si las bases permitían ETF fuera de iShares**: hay 23 compras que no lo son,
   incluidas 2 de IBM, que es una acción individual. Detalle en `INFORME_ETF_TORNEO.md`.
6. **Verificar en vivo** que una corrida del juego llegue a la planilla (el form de
   postulación YA se verificó — Francisco confirmó el 2026-09-03 que una postulación real
   llega bien).
7. **Textos históricos que quedaron con cifras viejas** y son decisión de Francisco, no
   nuestra: el "Capítulo IV" de `club.json` dice "59 equipos". (El "Capítulo II" y el
   "Four areas" de `en/index.html` se resolvieron el 2026-09-03: el sitio dice **cinco**
   áreas en los dos repos, y `en/index.html` pasó a "Our areas of practice".)
   (cambiarlo obliga a tocar `despublicar_fiw.py`, que busca ese texto exacto).
8. **`fotos/` pesa 17 MB** en el repo. Hoy no molesta; si sigue creciendo hay que
   decidir si los originales siguen versionados o pasan al Drive.

## Contexto externo (no reinventar)

- Ya existe un **sitio FIG distinto en producción** en el Drive
  (`WEB/fen-investments-web/`). URLs reales confirmadas: LinkedIn
  `linkedin.com/company/fen-investment-group`, Instagram `instagram.com/fen.investment.group/`,
  torneo `feninvestmentgroup.com/torneoportafolio2026/`. No inventar URLs de Drive:
  pedírselas a Francisco.
- Ya existe una **app del torneo** (`torneo-app`, Vite+TS+Tailwind) y un **generador de
  overlay para OBS** (`ranking-video`) que hoy lee un CSV de Google Sheets — candidato a
  conectarse a `datos/torneo.json` (ver `IDEAS_GRAN_ESCALA_FIG.md` §6).
- **Hardware de Francisco** (relevante para cualquier script pesado): Intel Pentium Gold
  7505, 2 núcleos/4 hilos, **3.8 GB de RAM**, GPU integrada. Por eso el repo evita
  Playwright/Puppeteer (bajan ~300 MB de Chromium) y usa Chrome por CDP crudo, y por eso
  ningún script acumula fotogramas en memoria.
