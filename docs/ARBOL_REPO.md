# Arbol del repo fig-web, anotado

> Extraido de `CLAUDE.md` el 2026-09-02 para que no se cargue en cada sesion.
> Consultalo cuando necesites saber que hace un archivo o donde vive un dato.
> Si agregas o quitas un archivo del repo, actualiza este arbol.

## Estructura del repo

```
/
├── index.html              ← sitio principal FIG (hero, áreas, torneo resumen, historia, equipo, eventos resumen)
├── eventos/index.html      ← bitácora de actividades (torneos, visitas, charlas, comunidad)
├── fiw/index.html           ← página de FEN Investment Woman (paleta propia, editable)
├── valuation/index.html     ← página del área Valuation (paleta estándar; responsables + sección de Torneo del área que se activa con datos/valuation.json)
├── portafolio/index.html    ← página del área Portafolio (2026-09-01; YA NO es la plantilla de valuation/: hero con el plano riesgo/retorno del torneo, cinta de datos vivos, tablero del corte y barra de asignación de los 100 puntos — ver la tanda del 2026-09-01 (3))
├── trading/index.html       ← página del área Trading (2026-08-31; MISMA plantilla que valuation/. Su sección de Torneo va `hidden` con `torneo.activo:false`: el desk aún no tiene torneo propio, y por eso tampoco hay ítem "Torneo" en su nav — al encenderlo hay que devolverlo)
├── torneo/index.html        ← ranking oficial del Torneo Portafolio 2026 (con trayectoria por equipo)
├── torneo/pantalla.html      ← PANTALLA para las TV de la facultad (1920x1080, bucle, se alimenta sola de torneo.json)
├── miembros/index.html      ← LA MESA: directiva, organigrama por desk, buscador "Terminal FIG" y ficha por persona (se alimenta de datos/miembros.json)
├── postula/index.html       ← formulario de postulación al club
├── juego/index.html          ← "El Rally del Toro": juego de espera (runner con el toro; vender = asegurar puntaje)
├── desafio/index.html        ← "Desafío FIG": trivia de finanzas (banco en datos/preguntas/, validar con validar_preguntas.py)
├── en/index.html              ← one-pager en INGLÉS para partners internacionales
├── informe/index.html         ← análisis del Torneo Portafolio 2026 ("qué muestran los datos", contra el "quién va ganando" de torneo/index.html). Creada el 2026-08-30 (`a447379`). 8 gráficos SVG dibujados a mano, sin librerías; NINGUNA cifra escrita a mano, ni en la prosa (las calcula el JS desde `../datos/torneo.json`). §Instrumentos lee además `datos/etf.json`. Secciones (`id`): resumen, mercado, distribucion, riesgo, movilidad, puntaje, instrumentos, tabla, metodologia. En sitemap.xml y publicada en el espejo
├── en/informe/index.html      ← versión en INGLÉS de informe/index.html, GENERADA por generar_informe_en.py (no editar a mano: la próxima corrida la pisa). Nace el 2026-08-30 (`944685e`). En sitemap.xml y en el espejo. Estas dos (en/ y en/informe/) son las únicas páginas del sitio en inglés a propósito
├── 404.html                   ← página de error de GitHub Pages: nav corto + panel con enlaces de salida + footer propio. Sus enlaces a `fiw/` están siempre activos en este repo; `despublicar_fiw.py` los quita en el espejo. Confirmado por grep: le faltan el `<span>` de crédito y el beacon de métricas que CLAUDE.md declara obligatorios (ver su fila en ESTADO_PIEZAS.md). NO está en sitemap.xml
├── generar_torneo.py        ← Excel ranking_ordenado → datos/torneo.json (mantiene historial semanal)
├── completar_metricas_historial.py ← INJERTO QUIRÚRGICO: rellena métricas faltantes en semanas ya publicadas del historial, SIN regenerar el JSON (usar esto, nunca `--excels`, para no borrar los integrantes)
├── completar_acwi_historial.py ← INJERTO QUIRÚRGICO hermano del anterior (2026-08-21, `b2b382b`): llena el benchmark `acwi` faltante en datos/torneo.json con precios reales de Bloomberg (ACWI US Equity, serie semanal PX_LAST), calculando el retorno acumulado since-inception hasta cada corte ya publicado. Solo AGREGA entradas de `acwi`; nunca pisa una presente ni toca `equipos`. Dry-run sin `--aplicar`
├── grabar_pantalla_facultad_1_capturar.js ← Paso 1/2 para grabar torneo/pantalla-facultad.html: Chrome headless por CDP crudo (sin Playwright, sin instalar nada), captura fotograma a fotograma a frames/*.png. Necesita un server local corriendo antes (ver su cabecera). Detalle completo más abajo, sección "Pixelación al proyectar"
├── grabar_pantalla_facultad_2_codificar.py ← Paso 2/2: arma el MP4 final desde frames/*.png con PyAV, uno por uno (nunca todos en memoria)
├── incorporar_congelados.py ← **DORMIDO desde el 2026-08-26** (la directiva eliminó en definitiva a los 5 equipos; ver el final de la fila de `torneo/index.html`). Hace no-op si `datos/equipos_congelados.json` está vacío. Cuando tenía equipos: los reinsertaba en `torneo.json` recalculando el puntaje de TODOS vía percentil continuo (réplica de `scoring.py` del repo torneo-bloomberg-oficial), a correr SIEMPRE después de `generar_torneo.py`. Se deja en el repo por si se decide congelar a otro equipo eliminado en el futuro
├── generar_miembros.py      ← club.json (directiva) + Excel del Drive → datos/miembros.json; cruza solo los resultados de torneo y las actividades
├── PLANILLA_MIEMBROS_FIG.md  ← qué columnas debe tener la planilla de miembros del Drive y qué NUNCA se publica (léelo antes de tocar la sección de Miembros)
├── generar_tabla.py         ← datos/torneo.json → datos/torneo-tabla.json (el mismo sin `historial`, 27,7→7,1 KB comprimido) Y datos/torneo-portada.json (el tercer derivado, más liviano aún, para el ticker de index.html). Lo pide primero torneo/index.html para pintar la tabla; el historial se trae aparte
├── generar_paginas_equipo.py ← datos/torneo.json → torneo/e/<id>.html, una micro-página por equipo SOLO para que el link tenga vista previa propia al compartirlo (redirige al ranking real)
├── generar_og_equipos.js     ← Node + Chrome por CDP crudo: og/equipo-<id>.jpg (1200x627), la imagen de esa vista previa. Reusa `drawLi`, la MISMA tarjeta de LinkedIn que ya ofrece la página. Opcional, ver la nota de PESO en su cabecera
├── verificar_paginas.js      ← CHEQUEO EN NAVEGADOR: abre las paginas en Chrome (CDP crudo, ventana de 1400px) y falla si alguna tira un error de consola o pide un archivo que no existe. OJO: los 404 de `fotos/` y `logos/industria/` son el sondeo de deteccion funcionando, no errores
├── verificar_movil.js       ← CHEQUEO EN NAVEGADOR (2026-08-30, `06ab308`), lo que `verificar_paginas.js` no ve porque corre a 1400px: viewport de celular 390x844 — scroll horizontal del documento, qué elementos se desbordan (con su selector), objetivos táctiles bajo 24px (WCAG 2.2) y texto bajo 12px
├── verificar_menu_movil.js  ← CHEQUEO EN NAVEGADOR (2026-08-31, `8af719d`): abre el MENÚ MÓVIL hamburguesa en 3 teléfonos y comprueba que se alcance entero (alto del contenido vs pantalla, si scrollea cuando no entra, qué enlace queda con offset negativo = inalcanzable). Correr al agregar/sacar un enlace de un `.m-menu`, una página por corrida (`--pag=`)
├── generar_sitemap.py        ← sitemap.xml + robots.txt (deja fuera `torneo/e/`, las pantallas y las guias internas)
├── sincronizar_espejo.py     ← copia al espejo lo que corresponde y nunca borra nada allá. NO se copian (el espejo tiene su propia versión): `CLAUDE.md` y `MAPA_CONTENIDO_FIG.html` (en `NO_SE_COPIAN`). Difieren a propósito y se portan a mano solo el bloque tocado: `index.html` y los tres `docs/*.md` (en `DIFIEREN`, tienen encabezado propio en el espejo)
├── despublicar_fiw.py        ← PASO APARTE que va SIEMPRE después de sincronizar_espejo.py y antes de generar_sitemap.py dentro del espejo (`8cce0b2`, decisión de Francisco 2026-08-30): saca FEN Investment Woman del espejo — borra `fiw/` de allá y edita 404.html, eventos/, postula/, valuation/, portafolio/, trading/ y en/ para que el área no sea accesible ni visible. Idempotente. Reescribe 7 archivos del espejo, así que sincronizar_espejo.py siempre los reportará como "por copiar" aunque nada haya cambiado. Aborta si una regla obligatoria ya no calza contra el HTML de origen
├── descargar_fuentes.py      ← baja las 3 familias de Google y arma `fuentes/fig.css` (solo subconjuntos latin/latin-ext)
├── usar_fuentes_locales.py   ← apunta las paginas a `fuentes/fig.css`; NO toca el <link> de la tarjeta descargable de `torneo/index.html`
├── verificar_sitio.py        ← CHEQUEO ANTES DE PUBLICAR (lo corre también el hook pre-push): JSON que parsean; derivados al día (torneo-tabla, torneo-portada, torneo/e/, og/ + huérfanas en og/); menciones escritas a mano de "N equipos/teams" MÁS la semana y la fecha de corte, en español e inglés, contra torneo.json; sitemap.xml vs lo que produciría generar_sitemap.py; que cada página del sitemap declare su canonical apuntando a su propio <loc>; el respaldo embebido `CLUB_DATA` de index.html vs club.json; y creadores que calcen con la directiva. `--arreglar` regenera solo lo DERIVADO
├── generar_informe_en.py     ← escribe `en/informe/index.html` desde `informe/index.html` con una tabla de TRADUCCIONES; FALLA si queda texto en español sin traducir (la fuente de verdad es UNA). Correr cada vez que se toca `informe/index.html`. Creado 2026-08-30
├── generar_imagenes_web.py   ← deriva las versiones ligeras que el sitio realmente sirve (los originales NO se tocan): `fotos/eventos/<ev>/<n>.webp` y `mini/<n>.webp`, `fotos/directiva/<slug>.webp` y `mini/<slug>.webp`, más el manifiesto `datos/fotos.json`. Correr tras subir fotos nuevas. Creado 2026-08-28 (`6f3e8fc`)
├── optimizar_logos.py        ← achica los PNG de `logos/` a paleta de 256 colores SIN cambiar nombre ni formato, y SOLO si la diferencia media contra el original queda bajo `--umbral` (1,0 sobre 255 por defecto) — un logo que no pasa se deja igual. Conserva el canal alfa. Idempotente. No toca los `.jpg` de fotos/. Creado 2026-08-28 (`6f3e8fc`)
├── generar_ics.py           ← datos/eventos.json → eventos/fig.ics (calendario iCal; correr tras editar eventos)
├── optimizar_fotos.py       ← comprime fotos/ automáticamente (máx 2000px, JPG 78%) — correr tras agregar fotos
├── validar_preguntas.py     ← barrera de calidad del banco de preguntas del Desafío FIG
├── HOJA_DE_RUTA_FIG.md      ← LISTA MAESTRA: backlog priorizado + protocolo de continuidad
├── MAPA_CONTENIDO_FIG.html  ← guía visual para Francisco: dónde subir fotos y editar texto de cada página (abrir con doble clic)
├── GUIA_DRIVE_FIG.html       ← guía para el equipo: estructura de la carpeta del Drive, dónde van las fotos, pasos para crear un evento (abrir con doble clic)
├── GUIA_DRIVE_FIG.jpg         ← infografía resumen de la guía anterior (para compartir rápido, ej. WhatsApp)
├── logos/                   ← logos oficiales bajados del Drive (FIG oro/blanco/navy, FEN, Itaú, BlackRock)
│   └── industria/            ← logos de empresas para "FIG en la industria" (ver LEEME.txt de la carpeta)
├── fuentes/                 ← GENERADA por descargar_fuentes.py: las tipografias autoalojadas (.woff2 + fig.css + LICENCIAS.txt). No editar a mano
├── sitemap.xml, robots.txt  ← GENERADOS por generar_sitemap.py
├── og-image.png             ← imagen Open Graph por defecto del sitio (1200×630, ver los `<meta og:image:width/height>` de informe/index.html), referenciada en los `<meta og:image>`/`twitter:image` de las páginas. En git desde la mudanza a la raíz (`ff1daa0`, 2026-07-19)
├── og/                      ← GENERADAS por generar_og_equipos.js: una imagen de vista previa por equipo. No editar a mano
├── torneo/e/                ← GENERADAS por generar_paginas_equipo.py: una micro-página por equipo. No editar a mano (tiene su LEEME.txt)
├── datos/
│   ├── torneo.json           ← EL RANKING REAL del Torneo Portafolio 2026, lo escribe generar_torneo.py desde el Excel del corte y mantiene el `historial` semanal. Hoy: semana 16, corte 28-ago-2026, 48 equipos (`378d99e`, 2026-09-02); ~195 KB. Del que derivan torneo-tabla.json y torneo-portada.json; lo leen torneo/, portafolio/, informe/ e index.html
│   ├── torneo-tabla.json     ← DERIVADO de torneo.json por generar_tabla.py (sin `historial`). No editar a mano; si queda viejo la página lo detecta y se corrige sola, y verificar_sitio.py falla
│   ├── torneo-portada.json   ← DERIVADO de torneo.json por generar_tabla.py (2026-08-28, séptima tanda): el tercero y más liviano — semana, corte, serie `acwi` y los equipos sin las 5 métricas ni el detalle pesado. Lo lee el ticker de index.html. No editar a mano; verificar_sitio.py lo revisa
│   ├── etf.json              ← GENERADO por `src/analisis_etf.py` del repo torneo-bloomberg-oficial desde `salidas/ledger.csv` (ledger al 2026-08-05): totales y desgloses de instrumentos/ETF/bolsas/divisas del torneo. Lo lee §Instrumentos de informe/index.html; su período NO es el del ranking y eso se dice al pie de cada gráfico. `00e1c18`, 2026-08-30
│   ├── fotos.json            ← DERIVADO por generar_imagenes_web.py: manifiesto de qué `.webp` existen y en qué tamaño, por evento y por persona. No editar a mano
│   ├── club.json             ← personas, eventos resumen, historia, URLs del sitio principal. Desde el 2026-08-27 trae también `torneo.creadores`: la lista EXPLÍCITA de quiénes crearon el Torneo Portafolio 2026, que alimenta la sección `#creadores` de `torneo/index.html` (solo nombre + aporte; el cargo, el LinkedIn y la foto se resuelven en vivo contra `personas.directiva`)
│   ├── cv_procesados.json    ← manifiesto anti-relectura de CV del Drive (fileId+modifiedTime, evita reprocesar los que no cambiaron)
│   ├── eventos.json           ← lista completa de eventos (bitácora); campo opcional `area` conecta un evento con la sección "Actividades" de su área (hoy solo valuation)
│   ├── mercado.json            ← calendario de mercado (RPM/IPoM del Banco Central + FOMC de la Fed); fechas oficiales, se actualizan a mano una vez por semestre — se muestran en la misma línea de tiempo que los hitos del torneo y los eventos del club
│   ├── linea_tiempo.json       ← hitos estructurales del Torneo (rebalanceos, cierres, final); se combina con eventos.json en la línea de tiempo de index.html y eventos/index.html — editable desde el Drive (`Linea_Tiempo_Hitos_Torneo` en `00_MAESTRO`)
│   ├── en.json                 ← textos en INGLÉS para en/index.html: SOLO lo que hay que traducir. Los hechos (nombres, fechas, LinkedIn, ranking, cifras) NO van aquí — la página los lee de club.json, eventos.json y torneo-portada.json y se actualizan solos
│   ├── fiw.json                ← textos y equipo de FEN Investment Woman
│   ├── valuation.json           ← textos, responsables y datos del Torneo de Valuation (pegar formUrl del Forms para activar inscripciones)
│   ├── portafolio.json          ← lo mismo para portafolio/index.html
│   ├── trading.json             ← lo mismo para trading/index.html (`torneo.activo:false` hasta que el desk tenga uno; el `_como_editar` explica cómo encenderlo)
│   ├── miembros.json             ← GENERADO por generar_miembros.py (no editar a mano): personas del club con ticker, área, nivel del organigrama y sus resultados de torneo cruzados
│   ├── (miembros.demo.json)        ← BORRADO el 2026-08-28, ya no está en el repo: la base real está cargada. Era el modo `?demo=1` (personas reales con cargos SUPUESTOS + personas que NO EXISTEN, `demo:true`). Se regenera con `python generar_miembros.py --demo` cuando haga falta; mientras no exista, `?demo=1` cae a la base real
│   ├── equipos_congelados.json   ← **VACÍO desde el 2026-08-26** (`{"equipos": []}`): los 5 equipos que estuvieron "en espera" 23→26-ago fueron eliminados en definitiva. Antes traía sus 5 métricas crudas FIJAS (semana 14) + `historial_previo` (semanas 5-14); ese contenido está en git (commit `c7c4f98` y el estado previo a la eliminación). Repoblarlo solo si se congela a otro equipo (ver `incorporar_congelados.py`)
│   └── torneo.json.ejemplo      ← ESQUEMA de referencia del ranking: un corte de muestra (semana 8) que documenta la forma que escribe generar_torneo.py. NO se renombra ni se usa en runtime — el torneo.json real ya existe (arriba). Su `_como_generar` interno todavía dice "renombrar este ejemplo", texto viejo del archivo que no aplica
├── fotos/
│   ├── eventos/<carpeta-evento>/  ← 1.jpg, 2.jpg, 3.jpg… por evento (numeradas, sin saltos)
│   ├── directiva/                  ← retratos de cofundadores: <nombre-slug>.jpg (ver LEEME.txt de la carpeta)
│   ├── miembros/                    ← retratos del resto del club: <id>.jpg (ver LEEME.txt). La página busca acá primero y en directiva/ después, así que a un directivo NO se le copia la foto dos veces
│   ├── fiw/                        ← 1.jpg, 2.jpg, 3.jpg… de la comunidad FIW
│   └── valuation/                   ← 1.jpg, 2.jpg, 3.jpg… para la tira de fondo del hero (aún vacía)
├── LEEME_PAGINAS.md          ← documentación de cómo se conectan las páginas nuevas
├── IDEAS_FIG.md               ← ideas de una sesión (rápidas)
├── IDEAS_GRAN_ESCALA_FIG.md    ← ideas de orquestación/pipeline (para Claude Code)
├── PROMPT_CLAUDE_CODE.md       ← prompt de arranque para la primera sesión de Claude Code en este repo (texto para copiar y pegar como primer mensaje). En git desde `ff1daa0`, 2026-07-19
├── ALERTAS_CONGELADOS.md       ← registro semanal de incorporar_congelados.py: si un equipo eliminado "en espera" sostenía un extremo de una métrica y perturbaba el puntaje del resto, quedaba anotado aquí. Cerrado el 2026-08-26 al eliminar en definitiva a los 5 (`8e03e98`)
├── INFORME_ETF_TORNEO.md       ← anexo de datos sobre el uso de ETF en el torneo, generado el 2026-08-30 para la reunión del área de Portafolio con BlackRock; fuente `torneo-bloomberg-oficial/salidas/ledger.csv` (ledger al 2026-08-05) cruzado con datos/torneo.json. Documento de trabajo interno, NO viaja al espejo (`NO_SE_COPIAN`). `00e1c18`
├── VIDEO_PODIO_GEMINI.md       ← instrucciones paso a paso para pegarle a Gemini (Veo) y armar el Reel del podio del torneo; datos del corte de la semana 13. Documento de trabajo, NO viaja al espejo. `cd6d7f1`, 2026-08-15
├── Q1_INVENTARIO_FINANZAS.md   ← inventario del material de Finanzas del Drive personal de Francisco (2026-07-16): 189 archivos mapeados a ramos/temas, insumo del banco de preguntas del Desafío FIG. Sesión aparte (Haiku). En git desde `ff1daa0`
├── docs/                       ← ESTE archivo (ARBOL_REPO.md), ESTADO_PIEZAS.md y BITACORA.md — extraídos de CLAUDE.md el 2026-09-02 para no cargarlos en cada sesión. Los tres DIFIEREN en el espejo (encabezado propio): se portan a mano solo el bloque tocado
└── documentos/                 ← `Bases_finales_torneo_portafolio_2026.pdf`: el PDF de bases del Torneo Portafolio que enlazan torneo/index.html e index.html (`config.urls.bases`). `50e9656`, 2026-08-23
```

> `__pycache__/` y `*.pyc` están en `.gitignore` y no se versionan.

Todas las páginas comparten: navy `#0A1128` + oro `#D4AF37`, tipografías
Playfair Display + Inter + IBM Plex Mono, reveals on-scroll, y respeto
total a `prefers-reduced-motion` (el cursor circular personalizado que
seguía al mouse se eliminó el 2026-08-02, pedido de Francisco). La página
`fiw/index.html` es la única con paleta propia (oro rosa, variables `--acc*`
al inicio de su `<style>`) — no tocar esos 4 valores sin pedirlo
explícitamente a Francisco, son la identidad visual de esa área.

