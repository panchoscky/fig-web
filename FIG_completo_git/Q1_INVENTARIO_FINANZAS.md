# Q1 — Inventario del Material Finanzas (Completado)

**Fecha:** 2026-07-16  
**Fuente:** Carpeta `Finanzas-20260716T225443Z-1-001/Finanzas/` en Google Drive personal  
**Total de archivos:** 189 (153 PDFs + 22 DOCs + 11 XLSs + 3 PPTs)

---

## Resumen de contenido

| Carpeta (Ramo) | Archivos | PDFs | Docs | Excels | PPTs | Estado |
|---|---|---|---|---|---|---|
| **Finanzas I** | 70 | 61 | 8 | 1 | — | ✅ |
| **Finanzas II** | 45 | 35 | 2 | 8 | — | ✅ |
| **Intro a Finanzas** | 67 | 50 | 12 | 2 | 3 | ✅ |
| **APF** | 7 | 7 | — | — | — | ✅ |
| **TOTAL** | **189** | **153** | **22** | **11** | **3** | — |

---

## Ramos identificados

| Ramo | ID propuesto | Estado | Ubicación Drive |
|---|---|---|---|
| Finanzas I | `finanzas-i` | ✅ Existe en index.json | `Finanzas I/` |
| Finanzas II | `finanzas-ii` | 🆕 NUEVO | `Finanzas II/` |
| Intro a Finanzas | `intro-finanzas` | 🆕 NUEVO | `Intro a Finanzas/` |
| APF | `apf` | 🆕 NUEVO | `APF/` |

---

## Mapeo propuesto: Temas × Ramos

### Finanzas I (70 archivos)
**Contenido:** Valoración, modelos de portfolio, derivados básicos, casos reales (LATAM)

**Temas asignados:**
- `renta-variable` ✅ (existente)
- `renta-fija` ✅ (existente)
- `historia-mercados` ✅ (existente)

**Ejemplos de archivos:** Solucionario del Hull, Guía Futuros y Forward, Resumen Solemne, Ejercicios Opciones, CAPM & Modelo Índice, Ayudantías (40+)

---

### Finanzas II (45 archivos)
**Contenido:** Opciones avanzadas, futuros, derivados complejos, estrategias

**Temas asignados:**
- `renta-variable` ✅ (existente)
- `derivados-opciones` 🆕 (NUEVO)
- `derivados-futuros` 🆕 (NUEVO)

**Ejemplos de archivos:** Black-Scholes, Opciones binomiales, Estrategias de opciones, Put-Call, Replica de opciones, Letras Griegas (6 XLSXs de ejercicios)

---

### Intro a Finanzas (67 archivos)
**Contenido:** Conceptos fundamentales, matemáticas financieras, introducción a modelos

**Temas asignados:**
- `macroeconomia` ✅ (existente)
- `matematica-financiera` 🆕 (NUEVO)

**Ejemplos de archivos:** Pauta Solemne 1 Bonilla, Modelo de Dos Periodos, Matemáticas Financieras (AFP), Pensiones, Seguros (50+ PDFs educativos)

---

### APF — Análisis y Planificación Financiera (7 archivos)
**Contenido:** Casos reales (LATAM), riesgo de crédito, análisis de estados financieros

**Temas asignados:**
- `renta-fija` ✅ (existente)
- `riesgo-crediticio` 🆕 (NUEVO)

**Ejemplos de archivos:** Examen APF Otoño 2019, Solemne APF, Pauta Solemne 2 APF (todos con análisis de casos reales y riesgos)

---

## Cambios necesarios en `index.json`

### Ramos nuevos a agregar
```json
{
  "id": "finanzas-ii",
  "nombre": "Finanzas II"
},
{
  "id": "intro-finanzas",
  "nombre": "Introducción a Finanzas"
},
{
  "id": "apf",
  "nombre": "Análisis y Planificación Financiera"
}
```

### Temas nuevos a agregar
```json
{
  "id": "derivados-opciones",
  "nombre": "Derivados: Opciones"
},
{
  "id": "derivados-futuros",
  "nombre": "Derivados: Futuros"
},
{
  "id": "matematica-financiera",
  "nombre": "Matemática Financiera"
},
{
  "id": "riesgo-crediticio",
  "nombre": "Riesgo de Crédito"
}
```

---

## Notas importantes (Q2 en adelante)

1. **Excels ignorados:** Se encontraron 11 archivos XLS/XLSX. Como per instrucciones, no se procesarán para preguntas (son mayormente ejercicios con datos numéricos).

2. **Volumen de contenido:** 153 PDFs + 22 DOCs = 175 documentos de texto procesables. Es un volumen muy alto (colosal, como se esperaba).

3. **Calidad del material:** Mezcla de:
   - Solucionarios y pautas (muy valiosos para preguntas)
   - Apuntes de cátedra (contenido pedagógico)
   - Guías de ejercicios (buena fuente de distractores plausibles)
   - Casos reales (para historia-mercados)

4. **Recomendación de orden Q2:** Comenzar con `Intro a Finanzas` (contenido más estructurado pedagógicamente) → `Finanzas I` (volumen mayor, más diversidad de temas) → `Finanzas II` (especializado, derivados) → `APF` (casos complejos para revisión pedagógica final).

---

## Estado

- ✅ **Q1 completado:** 2026-07-16 23:35
- 🔄 **Q2 en curso:** 22 lotes hechos (2026-07-17) — `finanzas-01.json` a `finanzas-22.json`, **287 preguntas totales** cubriendo 12 temas: matemática financiera, análisis de ratios, renta fija (incl. duración/convexidad avanzada), riesgo financiero (incl. VaR, Basilea vs RiskMetrics), evaluación de proyectos, CAPM/portafolios/CML avanzado (incl. Sharpe/Treynor/Jensen, eficiencia de mercado), estructura de capital, historia de mercados, macroeconomía, fundamentos/gobierno corporativo, y **derivados-futuros**/**derivados-opciones** (forwards, futuros, cobertura, opciones, Black-Scholes, árboles binomiales, delta hedging, CDS). Desde 67 archivos distintos entre "Intro a Finanzas" y "Finanzas I". 4 archivos descartados. Antes de extraer se hace siempre un escaneo rápido de calidad — de los últimos 40 archivos de "Finanzas I" escaneados en 4 rondas, casi todos resultaron aprovechables. Queda material de opciones avanzadas/Black-Scholes con letras griegas sin escanear en "Finanzas I" (70 archivos totales), más el resto de "Intro a Finanzas" + "Finanzas II" (45) + APF (7)
- ⏳ **Q3 pendiente:** Revisión pedagógica (Opus/Fable, muestreo ~10%)
- ⏳ **Q4 pendiente:** Balance del banco

---

**Generado por:** Claude Code (Haiku 4.5)  
**Sesión:** claude/material-finanzas-roadmap-vmd3lw
