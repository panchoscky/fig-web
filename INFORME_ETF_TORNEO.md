# Uso de ETF en el Torneo Portafolio 2026 — anexo de datos

> Generado el 2026-08-30 para la reunión del área de Portafolio con BlackRock.
> **Fuente:** `torneo-bloomberg-oficial/salidas/ledger.csv` (operaciones reales
> capturadas desde Bloomberg) cruzado con `fig-web/datos/torneo.json` (ranking
> oficial, semana 15).
> Script de clasificación: ver "Cómo se reproduce" al final.

## Alcance y advertencias (leer antes de citar cualquier cifra)

1. **El ledger llega hasta el 2026-08-05**, no hasta el corte vigente
   (semana 15, 21-ago). Cubre el arranque y las dos primeras ventanas de
   rebalanceo. La ventana III es el 5 de octubre. Si alguien pregunta "¿y
   qué compraron después?", la respuesta honesta es que ese dato todavía no
   está capturado.
2. **Se cuentan 54 equipos**, los oficiales del ranking. El ledger crudo
   trae 59 porque incluye a los 5 eliminados el 26-ago (Fencashticos, Free
   Riders, Market Moggers, Mosqueteros, Pink Capital); están excluidos de
   todo lo que sigue.
3. **La unidad principal es la operación de compra y el número de equipos
   que usó cada instrumento**, no el peso en cartera. El ledger registra
   transacciones, no posiciones a una fecha: un equipo que compró y vendió
   aparece igual que uno que mantuvo.
4. **Los montos en USD son aproximados.** 28 operaciones se hicieron en 7
   divisas distintas y se convirtieron con un tipo de cambio fijo estimado
   (los tickers de Londres cotizados en peniques se dividieron por 100). No
   usar estas cifras como dato financiero; sirven para dimensionar, no para
   reportar.
5. **La clasificación por sector, factor, mercado y tema la hice yo** a
   partir del ticker. No viene etiquetada en el ledger. Es sólida para los
   ETF grandes y conocidos; en los muy marginales (1 operación) puede haber
   algún error de detalle que no mueve ningún agregado.

## Totales

| Dato | Valor |
|---|---|
| Equipos | 54 |
| Operaciones de compra | 642 |
| Operaciones de venta | 170 |
| Instrumentos distintos | 200 (199 ETF + 1 acción individual) |
| Bolsas distintas | 14 |
| Divisas distintas | 7 |
| Monto comprado (USD aprox.) | ~615 millones |

## Gestora

| Gestora | Operaciones | % | Equipos |
|---|---|---|---|
| iShares (BlackRock) | 619 | 96,4% | 54 (100%) |
| Otras gestoras | 21 | 3,3% | 12 (22%) |
| Acción individual (IBM) | 2 | 0,3% | 2 (4%) |

## Clase de activo

| Clase | Operaciones | % | Equipos |
|---|---|---|---|
| Renta variable | 564 | 87,9% | 54 (100%) |
| Renta fija | 43 | 6,7% | 29 (54%) |
| Commodities | 34 | 5,3% | 27 (50%) |
| Cripto (IBIT) | 1 | 0,2% | 1 (2%) |

## Mercados

| Mercado | Operaciones | % | Equipos |
|---|---|---|---|
| Estados Unidos | 328 | 51,1% | 54 (100%) |
| Global | 128 | 19,9% | 47 (87%) |
| Asia-Pacífico | 66 | 10,3% | 35 (65%) |
| Emergentes | 46 | 7,2% | 35 (65%) |
| Global desarrollado | 30 | 4,7% | 20 (37%) |
| Europa | 24 | 3,7% | 14 (26%) |
| Latinoamérica | 13 | 2,0% | 7 (13%) |
| Canadá | 7 | 1,1% | 4 (7%) |

## Los 15 ETF más usados

| Ticker | Qué es | Operaciones | Equipos | % del torneo |
|---|---|---|---|---|
| SOXX | Semiconductores | 41 | 35 | 65% |
| IAU | Oro | 27 | 23 | 43% |
| IVV | S&P 500 | 22 | 20 | 37% |
| IEMG | Emergentes (core) | 20 | 16 | 30% |
| QUAL | Factor calidad | 19 | 15 | 28% |
| EWY | Corea del Sur | 17 | 15 | 28% |
| ITA | Defensa y aeroespacial | 16 | 14 | 26% |
| MTUM | Factor momentum | 16 | 14 | 26% |
| USMV | Mínima volatilidad | 15 | 14 | 26% |
| IYW | Tecnología EE.UU. | 13 | 12 | 22% |
| EEM | Emergentes | 11 | 11 | 20% |
| BAI | Inteligencia artificial | 11 | 10 | 19% |
| IXN | Tecnología global | 11 | 8 | 15% |
| EWT | Taiwán | 11 | 7 | 13% |
| IEFA | Desarrollados ex-EE.UU. | 10 | 9 | 17% |

## Sectores (204 operaciones, 32% del total)

| Sector | Operaciones | Equipos | % del torneo |
|---|---|---|---|
| Semiconductores | 45 | 36 | 67% |
| Tecnología | 41 | 24 | 44% |
| Salud | 24 | 17 | 31% |
| Financiero | 19 | 15 | 28% |
| Energía | 19 | 14 | 26% |
| Defensa | 17 | 14 | 26% |
| Infraestructura | 12 | 10 | 19% |
| Industrial | 9 | 6 | 11% |
| Materiales | 8 | 7 | 13% |
| Comunicaciones | 3 | 3 | 6% |
| Consumo | 3 | 3 | 6% |
| Utilities | 3 | 2 | 4% |
| Inmobiliario | 1 | 1 | 2% |

## Factores (77 operaciones, 12% del total)

| Factor | Operaciones | Equipos | % del torneo |
|---|---|---|---|
| Calidad | 23 | 16 | 30% |
| Mínima volatilidad | 19 | 15 | 28% |
| Momentum | 19 | 15 | 28% |
| Valor | 9 | 7 | 13% |
| Rotación activa (DYNF) | 4 | 3 | 6% |
| Defensivo | 2 | 2 | 4% |
| Tamaño | 1 | 1 | 2% |

## Temáticos (47 operaciones, 7% del total)

| Tema | Operaciones | Equipos | % del torneo |
|---|---|---|---|
| Inteligencia artificial | 20 | 15 | 28% |
| Energía limpia | 13 | 9 | 17% |
| Robótica y automatización | 4 | 4 | 7% |
| Tecnología disruptiva | 2 | 2 | 4% |
| Genómica | 2 | 2 | 4% |
| Baterías y almacenamiento | 2 | 2 | 4% |
| Vehículo eléctrico, espacio, cuántica, minería | 1 c/u | 1 c/u | 2% |

## Apuestas país (86 operaciones, 13% del total)

| País | Operaciones | Equipos | % del torneo |
|---|---|---|---|
| Corea del Sur | 18 | 16 | 30% |
| Japón | 14 | 12 | 22% |
| Taiwán | 11 | 7 | 13% |
| India | 10 | 8 | 15% |
| Brasil | 8 | 5 | 9% |
| China | 7 | 6 | 11% |
| España | 3 | 3 | 6% |
| **Chile** | 3 | 2 | 4% |
| Italia | 2 | 2 | 4% |
| Finlandia, Austria, Alemania, Polonia, Perú, Reino Unido, Turquía, Tailandia, Hong Kong, Canadá | 1 c/u | 1 c/u | 2% |

## Qué hicieron distinto los que van ganando

Los 54 equipos partidos en tercios según su posición en el ranking oficial:

| | Tercio superior | Tercio medio | Tercio inferior |
|---|---|---|---|
| Retorno relativo medio | +7,20% | -4,86% | -15,05% |
| Sharpe medio | 1,98 | 0,75 | 0,12 |
| Caída máxima media | -4,61% | -7,35% | -11,40% |
| ETF distintos por equipo | 9,7 | 11,5 | 10,6 |
| Operaciones por equipo | 10,3 | 13,5 | 11,9 |
| Ventas por equipo | 2,9 | 3,6 | 3,0 |
| % en renta variable | 90% | 86% | 84% |

**Diversificación contra resultado** (posición media en el ranking):

| ETF distintos | Equipos | Posición media | Retorno relativo medio |
|---|---|---|---|
| 4 a 6 | 5 | 34,6 | -8,29% |
| **7 a 10** | **26** | **24,2** | **-1,81%** |
| 11 o más | 23 | 29,7 | -6,10% |

Ni concentrarse mucho ni diversificar mucho funcionó: el punto dulce fue
entre 7 y 10 ETF. Ojo con no sobrevender esto — son 54 observaciones y la
diferencia entre 24,2 y 29,7 no es estadísticamente concluyente.

**Cronología de la actividad** (todas las operaciones, 54 equipos):

| Mes | Compras | Ventas |
|---|---|---|
| Mayo 2026 | 534 | 47 |
| Junio 2026 | 93 | 89 |
| Julio 2026 | 14 | 30 |
| Agosto 2026 (al día 5) | 1 | 4 |

El torneo se decidió en mayo. Después casi nadie tocó su cartera: el 83% de
las compras ocurrió en el primer mes.

## Tres cosas que hay que resolver ANTES de mostrar esto afuera

### 1. Cuál es la medida oficial de "le ganó al índice"

Ya está anotado en `informe/index.html`, pero acá importa más porque es lo
primero que va a preguntar BlackRock. Hay dos cuentas y no calzan:

- `ret` − `acwi` (retorno acumulado menos el del índice): **29 de 54**
  equipos por delante en la semana 14.
- `exc` / `retRel` (retorno en exceso que entrega Bloomberg PORT, el que
  alimenta el puntaje): **15 de 54**.

Para Beta capital en la semana 14 la primera da +7,45% y la segunda +18,92%.
La presentación usa la segunda (que es la del puntaje oficial), pero **hay
que confirmarlo** — decir "54% del torneo le ganó al índice" y "16 de 54 le
ganaron al índice" en la misma reunión sería un problema.

### 2. Las 23 operaciones fuera del universo iShares

23 de 642 compras (3,6%), en 13 equipos, no fueron ETF de iShares:

| Instrumento | Gestora | Equipo | Fecha |
|---|---|---|---|
| GLD, XLV | SPDR | Beta capital | 2026-05-20 |
| ARKX, AIQ (×2), PPH, ROBO, GRID | varias | Black Bulls | 2026-05-19/21 |
| PPA, CRUD | Invesco / WisdomTree | VNM Capital Partners | 2026-05-20 / 06-18 |
| POWR (×2) | — | Malaga Capital Partners | 2026-05-15/19 |
| GRID, TAN | First Trust / Invesco | Jose | 2026-05-20 |
| PSI | Invesco | Athena | 2026-05-19 |
| DRAM | — | Alpha Partners | 2026-06-16 |
| HYDR | Global X | DFS CAPITAL | 2026-05-15 |
| QANT | — | EDP | 2026-05-15 |
| SEMI | — | Indarra Investments | 2026-05-14 |
| SX7PEX | Xtrackers | Optimo Investment | 2026-05-20 |
| SPCX | AXS | Sharpe Fox | 2026-06-16 |
| **IBM (acción individual)** | — | Cimientos financieros | 2026-06-17 |
| **IBM (acción individual)** | — | VNM Capital Partners | 2026-05-19 |

Hay que contrastarlo con las bases (`documentos/Bases_finales_torneo_portafolio_2026.pdf`)
antes de la reunión. Tres escenarios y ninguno es grave, pero conviene saber
cuál es:

- Si las bases **permiten** cualquier ETF: no pasa nada, y de hecho el dato
  se vuelve un argumento a favor (con libertad de elegir, el 96,4% eligió
  iShares).
- Si las bases **exigen** solo iShares: son 13 equipos con una operación
  fuera de norma que nadie detectó, y es mejor que lo sepamos nosotros
  primero.
- Si las bases no lo dicen: es una lección para las bases 2027.

**Nota:** EDP está en esta lista y va 8° con la mayor remontada del torneo
(+44 puestos). Vale la pena mirarlo antes de destacarlo en la final.

### 3. No hay ningún premio documentado

Revisé todo el repo: los únicos premios registrados son los del Valuation
Challenge (práctica en Itaú, práctica en BDO) y los del Torneo de Trading
(XTB). **Para el Torneo Portafolio no hay nada escrito en ninguna parte**, ni
en las bases, ni en `club.json`, ni en la hoja de ruta. Si mañana se habla de
premios, se parte de cero — que puede ser exactamente la oportunidad.

## Cómo se reproduce

Los dos scripts están en el scratchpad de la sesión:
`clasificar.py` (mapa de 202 tickers → gestora/clase/mercado/tema, y los
agregados) y `oficial.py` (los mismos agregados restringidos a los 54
equipos del ranking). Si esto se va a repetir cada corte, conviene moverlos
al repo `torneo-bloomberg-oficial` junto al resto del pipeline y alimentar
un `datos/etf.json` que la web pueda leer sola, igual que el resto del sitio.
