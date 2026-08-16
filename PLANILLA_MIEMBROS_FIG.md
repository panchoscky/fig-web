# La planilla de miembros de FIG

> Para Francisco y quien mantenga la base del club. Esto explica **qué
> planilla hay que armar en el Drive** para que la sección de Miembros del
> sitio se llene sola, y **qué NO se debe poner nunca** en ella si esa
> columna va a terminar publicada.

La sección de Miembros no se edita tocando código. Funciona igual que el
resto del sitio: **planilla en el Drive → `generar_miembros.py` → `datos/miembros.json` → la página se dibuja sola.**

---

## 1. Antes que nada: qué se publica y qué no

El sitio es **público e indexable por Google**. Todo lo que llegue a
`datos/miembros.json` queda visible para cualquiera, aunque la página no lo
muestre en pantalla — el JSON se puede abrir directo.

**Nunca va al repo:** RUT, correo, teléfono, dirección, fecha de nacimiento,
carrera, notas, ni PDFs de CV.

Esas columnas **sí pueden existir en la planilla del Drive** (al club le
sirven puertas adentro): el script simplemente no las lee. Lo único que
cruza al sitio son las columnas de la tabla de abajo.

**Sobre los CV** (decisión tomada el 2026-08-16): no se alojan PDFs. Un CV
real trae RUT y teléfono, y publicarlos sería filtrar los datos de 60+
personas de una sola vez. En cambio, **la ficha del miembro en el sitio ES
su CV público**: bio, hitos, trayectoria en FIG, resultados de torneo y
LinkedIn. Se ve mejor que un PDF y no expone nada sensible.

---

## 2. Las columnas de la planilla

Una fila por persona. La primera fila son los encabezados. El orden de las
columnas da lo mismo, y las que falten simplemente quedan vacías.

| Columna | Obligatoria | Qué va | Ejemplo |
|---|---|---|---|
| `nombre` | **sí** | Nombre completo, como la persona quiere que se lea | `Camila Pérez Soto` |
| `rol` | | Cargo en el club. Si va en blanco se asume `Miembro` | `Director · Trading` |
| `area` | | Código del desk: `PRT`, `TRD`, `VAL` o `FIW` | `TRD` |
| `generacion` | | Año en que entró al club | `2025` |
| `estado` | | `activo`, `alumni` o `pausa`. En blanco = `activo` | `activo` |
| `linkedin` | | URL pública de su perfil | `https://linkedin.com/in/...` |
| `bio` | | 2-3 líneas en primera o tercera persona | `Analista del desk de Trading...` |
| `hitos` | | Logros, separados por `;` | `Práctica en Itaú; 3° Torneo 2026` |
| `extras` | | **Lo que la persona pidió incorporar.** Texto libre, separado por `;` | `Autor del research de litio; Mentor FIW` |
| `muestra` | | **Qué autorizó a publicar** (ver abajo) | `foto; torneo; bio` |
| `ticker` | | Solo si quiere elegir su sigla a mano | `CPS` |
| `lidera` | | `sí` solo en **una** persona por desk: la que lo dirige | `sí` |
| `nivel` | | Fuerza el estrato del organigrama (ver abajo). Normalmente se deduce solo del `rol` | `2` |

### Los niveles del organigrama

El organigrama se dibuja por estratos. **No hace falta llenar la columna
`nivel`**: se deduce del texto del cargo. Solo llénala si el cargo no lo deja
claro.

| Nivel | Quiénes | Se deduce de palabras como |
|---|---|---|
| `0` | **Núcleo**: presidencia, cofundadores y el líder de cada desk | `Presidente`, `Vicepresidente` — o la columna `lidera` |
| `1` | **Dirección del desk**: quienes acompañan al líder | `Director`, `Encargado`, `Coordinador`, `Jefe` |
| `2` | **Segunda línea**: analistas junior, administrativos | `Junior`, `Analista`, `Asistente`, `Administrativo` |
| `3` | **Miembros sin cargo** | cualquier otra cosa, o `Miembro` |

**Los del nivel 3 no se dibujan en el organigrama, y es a propósito.** Con 200
personas el diagrama vuelve a ser ilegible. Cada desk cierra con una barra
"+N miembros" que salta al buscador filtrado por ese desk. El organigrama
muestra **estructura**; el buscador muestra **personas**.

La presidencia **no** lidera un desk por el solo hecho de pertenecer a él. Si
el presidente además dirige un área, hay que marcarlo con `lidera`.

### La columna `muestra` — el consentimiento

Lista, separada por `;`, con lo que la persona autoriza:

| Valor | Habilita |
|---|---|
| `foto` | Que se busque y muestre su retrato |
| `bio` | Su biografía e hitos |
| `torneo` | Su resultado en el Torneo Portafolio |
| `actividades` | En qué actividades del club participó |
| `extras` | El bloque libre que ella misma pidió |

Si la celda va vacía se asume el mínimo razonable
(`foto; bio; torneo; actividades`). **Lo que no esté autorizado no se
escribe al JSON**, no basta con esconderlo en la página.

---

## 3. Cómo se genera

```bash
# solo la directiva (lo que ya funciona hoy, sin planilla)
python3 generar_miembros.py

# con la planilla ya armada
python3 generar_miembros.py --excel "Miembros_FIG.xlsx"

# además, ver cómo calzó cada persona con el torneo
python3 generar_miembros.py --excel "Miembros_FIG.xlsx" --auditar
```

### Para no partir de una hoja en blanco

```bash
python3 generar_miembros.py --candidatos
```

Lista a **las 149 personas inscritas en el Torneo Portafolio 2026** que
todavía no tienen ficha, con su nombre tal como lo escribieron al
inscribirse y su equipo. Es el mejor punto de partida para armar la
planilla: son personas reales y sus nombres ya están escritos.

---

## 4. Lo que el script deriva solo (no lo escribas a mano)

| Dato | De dónde sale |
|---|---|
| **La directiva** (15 personas) | `datos/club.json`. Sigue siendo su única fuente de verdad: si cambia un rol allá, se refleja acá al regenerar. **No los repitas en la planilla** — solo agrégalos si quieres completarles generación, estado o extras |
| **El ticker** | Se deriva del nombre y se garantiza único (`Benjamín Sáez Molina → BSM`) |
| **Resultados de torneo** | Se cruza contra `datos/torneo.json`: equipo, posición, puntos y retorno |
| **Actividades** | Se cruza contra el campo `participantes` de `datos/eventos.json` |
| **La foto** | Se busca sola en `fotos/miembros/<id>.jpg` y luego en `fotos/directiva/<id>.jpg` (ver el LEEME de esas carpetas) |
| **El orden** | Por jerarquía, después por área y nombre |

### Dos cosas pendientes que dependen del club, no del código

1. **`participantes` está vacío en los 10 eventos** de `datos/eventos.json`.
   Mientras siga así, ninguna ficha va a mostrar actividades. El cruce ya
   está escrito y funciona: falta que alguien complete quién fue a qué.
2. **Los nombres del torneo vienen del Excel de inscripciones**, donde la
   gente escribió su nombre civil completo. El script calza igual — Jhosep
   García aparece inscrito como "Jhosep Gabriel García Suarez" y lo
   encuentra — pero si alguien no calza, la forma más rápida de arreglarlo
   es poner su LinkedIn en la planilla: ese calce es exacto.

---

## 5. El ticker, y por qué existe

Cada miembro tiene una sigla de 3 letras, como un instrumento en pantalla.
No es un adorno:

- Es lo que se escribe en el buscador de la página para llegar a alguien.
- Es el ancla de su URL: `miembros/#CPS`. **Ese es el link que la persona
  comparte en LinkedIn**, y es lo que hace que la sección se llene sola.
- Se lee bien en una tarjeta, en una pantalla del laboratorio y en un chat.

Las iniciales de 2 letras que usa `club.json` hoy ya chocan (Benjamín Sáez
Molina y Benjamín Solís son ambos "BS"), y con 60+ personas eso empeora. Por
eso el script usa 3 y verifica que no se repitan.
