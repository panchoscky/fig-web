# Video del podio para Instagram — instrucciones para Gemini

> **Para quién es este archivo:** para pegarle instrucciones a Gemini (Veo) y
> armar el Reel del podio del Torneo Portafolio 2026. Está escrito paso a paso
> y sin ambigüedades a propósito: Gemini sigue bien las órdenes literales, pero
> improvisa mal. **No le pidas que "sea creativo": las decisiones creativas ya
> están tomadas acá.**
>
> Datos del corte usado: **semana 13 · 07 · AGO · 2026**. Si generas el video en
> otro corte, actualiza los números de la sección 6 desde `datos/torneo.json`.

---

## 0. La regla que no se puede romper

**Gemini NO debe generar ningún texto, número, letra, logo ni marca dentro del
video.** Los modelos de video deforman e inventan el texto: escribiría
"92.Z7 pnts" o algo peor, y eso arruina la pieza.

Por eso el video se arma en **dos capas**:

| Capa | Quién la hace | Qué contiene |
|---|---|---|
| **Fondo** | Gemini (Veo) | Imagen cinematográfica abstracta, SIN texto |
| **Encima** | Nosotros | Todos los textos, cifras, nombres y el logo FIG |

Si en algún clip aparece texto, **descártalo y vuelve a generarlo**. No lo
intentes arreglar con otro prompt encima.

---

## 1. Qué video vamos a hacer

- **Formato:** Reel vertical de Instagram, **1080 × 1920**, 9:16.
- **Duración total:** 20 segundos.
- **Sin voz en off.** Se ve en silencio, como se ve Instagram.
- **Idea central:** *Tres formas de ganar.* Los tres del podio llegaron ahí
  por caminos completamente distintos, y eso se nota en sus datos.

**El gancho** es un dato real y muy fuerte: el retorno promedio de los 59
equipos es **−5,89 %**, y los tres del podio están en positivo.

---

## 2. Paleta y estética (repetir en TODOS los prompts)

- Azul marino casi negro: **#0A1128**
- Dorado: **#D4AF37**
- Dorado claro: **#EBD388**
- Marfil: **#F7F4EC**

Estética: sobria, elegante, financiera. **Nada de:** confeti, emojis, flechas
de caricatura, gráficos "de stock", personas mirando pantallas, banderas,
trofeos de plástico, monedas de Bitcoin.

---

## 3. Los 4 clips que le vas a pedir a Gemini

Genera **4 clips de 5 segundos cada uno**, verticales 9:16, sin texto.
Pega cada prompt **tal cual**, uno a la vez.

### Clip 1 — El gancho (0 a 5 s)

```
Cinematic vertical video, 9:16 aspect ratio, 1080x1920.
An abstract dark navy void, color #0A1128, filled with dozens of thin
descending light lines falling slowly downward like rain, all in dim cold
grey. Suddenly three golden lines, color #D4AF37, begin rising upward against
the falling grey ones, glowing softly, leaving faint golden trails.
Slow camera push-in. Volumetric haze. Anamorphic lens flare, very subtle.
Extremely elegant, minimal, financial, premium.
NO text, NO numbers, NO letters, NO logos, NO people, NO charts, NO user
interface. Pure abstract motion graphics.
```

### Clip 2 — El regreso (5 a 10 s) · para CLB

```
Cinematic vertical video, 9:16 aspect ratio, 1080x1920.
A single glowing golden line, color #D4AF37, on a dark navy background
#0A1128. The line plunges steeply down into darkness, hesitates at the
bottom, then climbs back upward in a fast dramatic ascent, overtaking dim
grey lines on its way up. Golden particles trail behind it. Dark, cinematic,
volumetric light. Slow motion feel.
NO text, NO numbers, NO letters, NO logos, NO people, NO charts, NO user
interface. Pure abstract motion graphics.
```

### Clip 3 — La paciencia (10 a 15 s) · para Aconcagua Capital

```
Cinematic vertical video, 9:16 aspect ratio, 1080x1920.
A single golden line, color #D4AF37, rising in a steady, patient, unwavering
diagonal across a dark navy field #0A1128. Around it, other dim grey lines
oscillate erratically up and down, unstable. The golden line never wavers.
Soft golden glow, fine dust particles floating in the light. Calm, controlled,
confident. Slow steady camera drift upward.
NO text, NO numbers, NO letters, NO logos, NO people, NO charts, NO user
interface. Pure abstract motion graphics.
```

### Clip 4 — El dominio y el cierre (15 a 20 s) · para Beta capital

```
Cinematic vertical video, 9:16 aspect ratio, 1080x1920.
A brilliant golden horizontal beam of light, color #EBD388, holding perfectly
straight and steady at the top of a dark navy frame #0A1128, unshaken, while
everything below it churns in dim grey turbulence. The beam intensifies and
slowly blooms into a warm golden glow that fills the frame, then settles back
into deep navy darkness.
Luxurious, cinematic, restrained. Anamorphic lens flare.
NO text, NO numbers, NO letters, NO logos, NO people, NO charts, NO user
interface. Pure abstract motion graphics.
```

---

## 4. Si Gemini se equivoca (pasa seguido)

| Qué pasó | Qué hacer |
|---|---|
| Aparecen letras o números | Descartar y regenerar. Agregar al final: `Absolutely no typography of any kind.` |
| Aparecen personas o manos | Regenerar agregando: `No humans, no hands, no faces.` |
| Salió horizontal | Regenerar. Repetir `vertical 9:16` al principio Y al final del prompt. |
| Se ve como gráfico de Excel | Regenerar agregando: `Not a chart, not a graph, not a dashboard. Abstract light only.` |
| Los colores no calzan entre clips | Regenerar el clip que desentona. No corregir con filtros. |

**Regla práctica:** si un clip no queda bien en 3 intentos, cambia el clip por
un fondo de navy con partículas doradas suaves. Es preferible un fondo simple
y limpio a uno vistoso que pelea con el texto que va encima.

---

## 5. Cómo se arma el video (orden exacto)

1. Descargar los 4 clips de Gemini.
2. Abrirlos en **CapCut** (gratis, celular o escritorio).
3. Crear proyecto **9:16, 1080×1920**.
4. Poner los 4 clips en orden: 1 → 2 → 3 → 4.
5. Recortar cada uno a **5 segundos exactos**. Total: 20 s.
6. Entre clip y clip, transición **"Fundido a negro" de 0,3 s**. Nada más.
7. Encima va la capa de texto de la sección 6.
8. Música: pista instrumental sobria de la biblioteca de CapCut, sin voz.
   Volumen al 40 %. Bajarla a 0 en el último segundo.
9. Exportar: **1080×1920, 30 fps, calidad alta**.

---

## 6. Los textos que van encima (copiar EXACTO)

> Estos números salen de `datos/torneo.json`, corte semana 13.
> **No los cambies ni los redondees.** Si el corte cambia, hay que actualizarlos.

**Tipografía:** títulos en **Playfair Display**; cifras y etiquetas en **IBM Plex
Mono**. Si CapCut no las tiene: títulos en cualquier serif elegante, cifras en
cualquier monoespaciada. Color de texto: marfil `#F7F4EC`; cifras destacadas en
dorado `#D4AF37`.

### Segundo 0,5 → 2,5 (sobre el clip 1)
```
El promedio del torneo
pierde 5,89 %
```

### Segundo 2,8 → 4,8 (sobre el clip 1)
```
Ellos no.
```

### Segundo 5,3 → 9,7 (sobre el clip 2)
```
3er LUGAR
CLB
Llegó a estar 40°.
Hoy es tercero.
+6,54 %
```

### Segundo 10,3 → 14,7 (sobre el clip 3)
```
2do LUGAR
Aconcagua Capital
Cayó al 19° en la semana 6.
Nunca más bajó del 2°.
+15,05 %
```

### Segundo 15,3 → 18,5 (sobre el clip 4)
```
CAMPEÓN
Beta capital
Nueve semanas.
Jamás bajó del segundo lugar.
+23,77 %
```

### Segundo 18,5 → 20,0 (cierre)
```
TORNEO PORTAFOLIO 2026
Semana 13 de 25

[logo FIG dorado]
@fen.investment.group
```

---

## 7. Verificación antes de publicar

Marcar todo antes de subir:

- [ ] El video dura 20 segundos y es vertical 1080×1920.
- [ ] **No aparece ningún texto generado por Gemini** (solo el nuestro).
- [ ] Los tres nombres están bien escritos: **CLB**, **Aconcagua Capital**,
      **Beta capital** (con "capital" en minúscula, así se llama).
- [ ] Las cifras dicen exactamente **5,89 % · 6,54 % · 15,05 % · 23,77 %**.
- [ ] El orden es 3° → 2° → 1°, terminando en el campeón.
- [ ] El logo de FIG es el archivo real (`logos/fig-oro.png`), no uno dibujado
      por la IA.
- [ ] Se entiende con el sonido apagado.

---

## 8. Alternativa mejor, si hay tiempo

En vez de escribir los textos a mano en CapCut, se pueden generar los overlays
directamente desde el mismo motor que dibuja las tarjetas del torneo
(`torneo/index.html`, funciones `drawStory` / `drawBadges` / `podio`). Eso
garantiza la tipografía, la paleta y los datos **exactos y automáticos**, y el
podio ya tiene su tratamiento oro/plata/bronce hecho.

Ventaja: se puede repetir cada semana sin rehacer nada a mano.
Pídeselo a Claude Code cuando quieran ese paso.
