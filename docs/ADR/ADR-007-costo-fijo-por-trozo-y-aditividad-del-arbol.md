---
title: "ADR-007 — Costo fijo por trozo y aditividad del árbol: la suma de `Own` tiene que dar el total real"
aliases:
  - "ADR-007 aditividad del arbol"
project: tokmd
document_type: adr
status: proposed
version: 0.1.0
created: 2026-09-27
updated: 2026-09-27
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-opus-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-opus-5 / Claude Code / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - adr
related_documents:
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
  - "[[ADR-003-parseo-de-secciones]]"
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
  - "[[BUG-009-adr-003-arbol-sin-own-ni-total]]"
  - "[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
---

# ADR-007 — Costo fijo por trozo y aditividad del árbol

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Borrador a pedido de Fabián, con cuatro opciones. La medición cambió la conclusión sobre la marcha: lo que parecía deriva de borde irreducible es el marco contado N veces, y su requisito de igualdad exacta **sí** se puede cumplir. |
| 2026-09-27 | 0.2.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Cabo suelto cerrado, también a pedido de Fabián: el −1 no era el front matter sino cualquier trozo que empieza con `\n`. Arreglo de una línea en `FRONT_MATTER_RE`, verificado sobre 17 archivos con residuo 0 en todos. Se cumple la condición que este ADR se puso para poder aceptarse. |
| 2026-09-27 | 0.3.0 | Anthropic / claude-opus-5 / Claude Code / subscription | **Corrección de un error propio, traído por la sesión TTOK-05:** el total no lleva el marco restado. La v0.2.0 decía 17.376 y la API cobra **17.381**; `ctok` crudo coincide exacto con la API. El marco pasa a mostrarse como renglón propio en vez de descontarse. El hallazgo del costo 5 por corte queda confirmado por una segunda medición independiente. |
| 2026-09-27 | 0.4.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | **Aceptado por Fabián.** Estado a `accepted`. Corregido en consecuencia `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` (v0.3.0), cuya definición de `FRAME` y afirmación de deriva de borde quedaban desmentidas por este ADR. |

## Estado

`accepted`. **Aceptado por Fabián Ferdgelis el 2026-09-27**, opción D: costo fijo
5 restado por trozo, total contado de una pasada sin restar el marco, línea de
deriva como control (`+0` esperado siempre). Deja de bloquear
`[[PBI-009-defaults-del-cli-y-total]]`.

## Contexto

Fabián pidió, el 27/09/2026, que *«tanto el parser como el total tengan que dar
el mismo valor y ese valor tenga que ser el valor real, no un invento»*.

Hoy eso no pasa, por tres defectos encadenados:
`[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` (el título del encabezado no
se cuenta), `[[BUG-009-adr-003-arbol-sin-own-ni-total]]` (no hay `Own` ni fila
raíz, contra lo que decidió ADR-003) y
`[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]` (la línea de deriva
que ADR-002 prometió nunca se escribió).

Al medir la magnitud del problema apareció algo que **contradice el supuesto de
`[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]`**, y es el motivo de este ADR.

### La medición que cambió el diagnóstico

Primera medición, sobre `C:\Users\fferdgelis\.claude\CLAUDE.md`, con la partición
verificada byte a byte:

| | Tokens |
|---|---|
| El archivo contado de una sola pasada | 17.375 |
| Suma de las 44 filas con el título incluido, `FRAME=6` restado una vez | 17.590 |
| Diferencia | −215 |

Eso parecía ser **deriva de borde**: la pérdida de fusiones de un tokenizador BPE
(el que junta caracteres vecinos en un token) al cortar el texto en trozos. Si
fuera eso, sería irreducible y la igualdad exacta sería imposible.

**No es eso.** Al medir once archivos reales de tamaños muy distintos, la
diferencia resultó **constante por corte**:

| Archivo | Trozos | Diferencia | Por corte |
|---|---|---|---|
| `CLAUDE.md` global | 44 | −215 | **−5,00** |
| `README.md` | 14 | −65 | **−5,00** |
| `README.es.md` | 14 | −65 | **−5,00** |
| `CHANGELOG.md` | 3 | −10 | **−5,00** |
| `ROADMAP.md` | 6 | −26 | −5,20 |
| `ADR-002` | 10 | −46 | −5,11 |
| `ADR-003` | 10 | −46 | −5,11 |
| `PBI-009` | 24 | −116 | −5,04 |
| `BUG-008` | 14 | −66 | −5,08 |
| `dev-log 2026-09-26` | 9 | −41 | −5,12 |
| `sample.md.fixture` | 5 | −21 | −5,25 |
| `no_headings.md.fixture` | 1 | **0** | **0** |

143 cortes en total, −717 tokens, promedio **−5,01 por corte**. El signo es
negativo en los once archivos que tienen cortes, y cero en el que no tiene
ninguno. **Una deriva de tokenización no se comporta así: no es un número
redondo, no es constante, y no tiene siempre el mismo signo.**

Control directo, partiendo textos a mano:

| Corte | Juntos | Partidos | Costo del corte |
|---|---|---|---|
| `'# Titulo\n'` + `'texto abajo\n'` | 17 | 22 | **5** |
| `'linea uno\n'` + `'linea dos\n'` | 15 | 20 | **5** |
| `'---\nk: v\n---\n'` + `'# H1\ncuerpo\n'` | 23 | 28 | **5** |
| `'hola mundo'` + `' chau mundo'` (corte en medio de una frase) | 16 | 23 | 7 |

**Conclusión: el costo fijo de un mensaje es 5, y cortar en un límite de línea no
pierde ninguna fusión.** La tokenización del texto **es aditiva** cuando los
cortes caen en saltos de línea, que es exactamente donde el parser corta. El 7
del último caso confirma que la deriva de borde existe, pero sólo cuando se corta
en medio de una frase — algo que este parser nunca hace.

### El error de `FRAME` en ADR-002

`[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` define
`FRAME = token_count("", version)` y mide **6** para la familia `4.8`. Pero el
costo marginal real de un trozo adicional es **5**. `token_count("")` incluye un
token extra del bloque de contenido vacío, así que **`FRAME` mide 6 lo que cuesta
5**.

Verificación con `K=5` como costo fijo por trozo, aplicando
`total == Σ c(trozo) − (N−1)·5`:

| Archivos | Residuo |
|---|---|
| **Sin** front matter (4 archivos) | **0 — exacto** |
| **Con** front matter (7 archivos) | **−1 — constante** |

Y el resultado de aplicarlo al `CLAUDE.md` global, que no tiene front matter:
**total contado de una pasada = 17.376, suma de los `Own` = 17.376, diferencia =
0.**

### El dato incómodo

Restar `FRAME=6` una vez por sección —que es aritméticamente incorrecto, porque
el marco es un costo del mensaje y no de cada sección— venía **compensando por
casualidad** el costo de los cortes: 44 × 6 = 264 de sobrerresta contra 215 de
costo real. Se cancelan casi. **El número que la herramienta informa hoy parecía
razonable por una coincidencia numérica, no por diseño.**

## Opciones

### Opción A — El total es la suma de las filas

El total informado pasa a ser la suma de los `Own`, tal como se calculan hoy.

- Los dos números cierran por construcción.
- **El total deja de ser el valor real.** Informaría 17.590 cuando el archivo
  cuesta 17.376. Contradice de frente el requisito de Fabián.
- Descartada.

### Opción B — Repartir la diferencia entre las filas

Se calcula el total real y la diferencia se distribuye entre las secciones, en
proporción a su tamaño.

- Los dos números cierran y el total es real.
- **Las filas pasan a ser un invento:** a cada sección se le asigna una parte de
  una diferencia que no le pertenece. Contradice el «no un invento».
- Descartada.

### Opción C — Declarar la diferencia y no tocar el cálculo

El total se cuenta de una pasada (valor real), las filas quedan como están, y una
línea informa `boundary drift: −215`.

- Es exactamente lo que `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` ya
  decidió, y cumple `[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]`.
- Honesto: no esconde nada.
- **Pero deja el error adentro.** Ahora que está medido que la diferencia es el
  marco mal restado y no un límite del tokenizador, declarar 215 tokens de deriva
  sería **declarar un error propio como si fuera una propiedad de la herramienta**.
  Los dos números siguen sin coincidir, cuando pueden coincidir.
- Era la recomendación antes de la medición. **Queda descartada por la
  medición.**

### Opción D — Corregir el costo fijo: restarlo por corte, no por sección

1. El costo fijo por trozo se define como **5** para la familia `4.8` (y se
   remide por familia), en vez de `token_count("")`.
2. `own` de cada nodo = `token_count(su_texto_con_encabezado) − 5`.
3. El **total** se cuenta de una sola pasada, **crudo y sin restar nada**:
   `token_count(archivo)`. Ver la corrección de abajo: el marco **es** parte de
   lo que la API cobra, así que restarlo deja el total por debajo del valor real.
4. El marco se muestra como **renglón propio**, no se esconde ni se descuenta:

   ```
   suma de Own            17.376
   marco del mensaje           5
   ─────────────────────────────
   TOTAL                  17.381   <- lo que cobra la API
   ```

5. La línea de deriva **se implementa igual** (`[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]`),
   como red de seguridad: tiene que dar `+0`, y si algún día no da 0, se ve.

### Corrección del 27/09/2026: el total no lleva el marco restado

**La v0.2.0 de este ADR decía que el total era `token_count(archivo) − 5`, o sea
17.376. Estaba 5 tokens abajo.** Lo corrige la sesión **TTOK-05** (Claude Fable
5.1), que midió el mismo archivo **contra la API real de Anthropic** —cosa que
este ADR no había hecho— y dejó el resultado en
`docs/investigation/20260927-count-tokens-api-vs-tokmd-ctok-ttok.md`:

| Fuente | Tokens |
|---|---|
| `POST /v1/messages/count_tokens`, Sonnet 5 / Opus 5 / Opus 4.8 | **17.381** |
| `ctok.token_count(archivo, "4.8")` **crudo, sin restar nada** | **17.381** |
| `Σ token_count(trozo) − 43 × 5` (los 44 trozos de este ADR) | **17.381** |
| Lo que decía la v0.2.0 (`crudo − 5`) | 17.376 → **−5 contra la API** |

**Lo que esto enseña, y contradice a `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]`
en un punto más:** el marco del mensaje **no es overhead a descontar, es parte de
lo que Anthropic cobra**, porque el archivo viaja como `content` de un mensaje
real. `ctok` crudo es exacto contra la API. Restarlo —que es lo que ADR-002
decidió— da un número que **nadie factura**.

Las dos mediciones son consistentes y se refuerzan: TTOK-05 confirma por su lado
que el costo por trozo es 5 («coincide con la sonda de esta sesión:
`58 = 38 + 25 − 5`»), medido sin conocer este ADR.

**El hallazgo central de este ADR no cambia** —el costo por corte es 5, la
tokenización es aditiva, la suma cierra exacto—; lo que cambia es **contra qué
número cierra**: 17.381, el que cobra la API, no 17.376.

- **Los dos números coinciden exactamente y los dos son el valor real.** Medido:
  17.376 = 17.376, deriva `+0`.
- Cumple el requisito de Fabián literalmente, sin inventar nada.
- La línea de deriva pasa de ser una excusa a ser un **control**: mientras diga
  `+0`, el árbol está sano.
- **Costo:** cambia el número que la herramienta informa para todo archivo (un
  token por sección menos de sobrerresta), así que hay que remedir **todos** los
  datos dorados. Y hay que corregir `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]`,
  cuya definición de `FRAME` queda desmentida.
- **Cabo suelto conocido:** los archivos con front matter YAML quedan en **−1**,
  constante. Ver «Verificación» abajo.

## Decisión propuesta

**Opción D.**

Es la única que cumple las dos mitades del requisito a la vez —«el mismo valor»
y «el valor real»— y la única que no requiere elegir entre honestidad y
exactitud. Las otras tres piden resignar una de las dos.

Además convierte los tres instrumentos que ADR-002 y ADR-003 habían decidido y
que nunca se implementaron (`Own`, la fila raíz, la línea de deriva) en lo que
tenían que ser: **un control que se verifica solo en cada corrida.** Si la suma
de `Own` deja de dar el total, la línea de deriva lo grita. Es el mecanismo que
habría cazado `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` el primer día.

### Lo que hay que cambiar en ADR-002

`[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` queda **parcialmente
desmentido por medición** y hay que corregirlo, no borrarlo:

| Lo que dice ADR-002 | Lo que mide este ADR |
|---|---|
| `FRAME = token_count("", version)` | Mide 6; el costo marginal real es **5** |
| «restarlo de cada sección» | Hay que restarlo **una vez por trozo menos uno**, o equivalentemente una vez por sección y una vez al total |
| «posible deriva de borde de tokenización en los límites entre secciones» | **No existe** cuando se corta en saltos de línea: residuo 0 |
| «la deriva crece aproximadamente con `(N-1) × FRAME`» | **Correcto en la forma, con el número equivocado:** es `(N-1) × 5`, y no es deriva: es el marco |

La investigación `docs/investigation/20260924-ctok-marco-y-deriva.md` llegó a
`(N-1) × FRAME` como orden de magnitud y lo llamó «deriva estructural». Estaba a
un paso: era el marco, no deriva, y el coeficiente es 5.

## Consecuencias

- **El número que informa `tokmd` cambia para todo archivo.** Más alto que hoy,
  porque hoy sobre-resta. Para el `CLAUDE.md` global: de 15.903 a **17.381**
  (+9,3 %), que es **exactamente lo que cobra la API**. Es un motivo más para la
  `2.0.0` que Fabián ya decidió.
- **Hay que remedir todos los datos dorados** de `tests/test_tokenizers.py`,
  `tests/test_sections.py` y `tests/test_render.py`.
- **Las mediciones anteriores del proyecto quedan desactualizadas**, incluida la
  de PBI-008 que está en `framework-multi-ai`
  (`docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md`, 15.877) y que
  Fabián estaba usando para decidir qué recortar. **El valor correcto es 17.381**,
  medido contra la API por TTOK-05 y reproducido por `ctok` crudo.
- El costo fijo pasa a ser un dato medido por familia, con su propio test, no una
  llamada a `token_count("")`.
- `--verify` hereda el mismo tratamiento: `measure_frame` mide contra la API el
  equivalente del costo fijo, y hoy lo resta por sección igual que el camino
  offline. Hay que revisarlo con el mismo criterio.

## Verificación y reversibilidad

**Datos dorados de este ADR** (familia `4.8`, medidos el 27/09/2026):

| Dato | Valor |
|---|---|
| Costo fijo por trozo | **5** |
| `token_count("")` (lo que ADR-002 llamaba `FRAME`) | 6 |
| **`CLAUDE.md` global, lo que cobra la API** (oráculo, TTOK-05) | **17.381** |
| `CLAUDE.md` global, `ctok` crudo de una pasada | **17.381** ✓ coincide |
| `CLAUDE.md` global, `Σ ctok(trozo) − 43 × 5` | **17.381** ✓ coincide |
| `CLAUDE.md` global, suma de los `Own` (cada trozo − 5) | 17.376 |
| … más el marco del mensaje, una vez | + 5 = **17.381** ✓ |
| Deriva resultante | **+0** |
| Archivos verificados con residuo 0, con `FRONT_MATTER_RE` corregida | **17 de 17** |
| Costo de cortar en un salto de línea | **5** |
| Costo de cortar en medio de una frase (el parser nunca lo hace) | 7 |
| Familias de tokenizador que expone la API | 2: desde Opus 4.7, y la anterior |
| El mismo archivo en la familia anterior (Sonnet 4.6 / Haiku 4.5) | 13.076 |

**Cómo se verifica que sigue sano:** el criterio `AC-15` de
`[[PBI-009-defaults-del-cli-y-total]]` y el caso `TOK-009-C13`. La línea de
deriva tiene que dar `+0` para **todo** archivo, con front matter o sin él.
**Si algún día no da 0, hay un defecto nuevo.** Eso convierte los tres
instrumentos que ADR-002 y ADR-003 decidieron y nadie implementó en un control
que se verifica solo en cada corrida.

### El cabo suelto del −1: cerrado, y no era el front matter

**Investigado a pedido de Fabián el 27/09/2026. La causa es otra y el arreglo es
de una línea.**

Localizado con residuo **incremental** —comparando el prefijo de los primeros `k`
trozos contado junto contra la suma de esos `k` trozos— sobre
`ADR-003-parseo-de-secciones.md`:

| k | Trozo agregado | Residuo | Salto |
|---|---|---|---|
| 1 | `(front matter)` | 0 | +0 |
| 2 | `(preamble)` | **−1** | **−1 ← acá** |
| 3 | `# ADR-003 — Parseo de secciones…` | −1 | +0 |
| … | (los siete restantes) | −1 | +0 |

El salto ocurre **una sola vez**, al agregar el trozo `(preamble)`, cuyo contenido
completo es **un único `"\n"`**. Nada más aporta residuo.

Control aislado con textos sintéticos:

| Corte | Costo |
|---|---|
| `'---\nk: v\n---\n'` + `'# H1\ncuerpo\n'` | **5** ✓ |
| `'---\nk: v\n---\n'` + `'\n# H1\ncuerpo\n'` | **6** ✗ |
| `'---\nk: v\n---\n\n'` + `'# H1\ncuerpo\n'` | **5** ✓ |
| `'xxx\nk: v\nyyy\n'` + `'# H1\ncuerpo\n'` | **5** ✓ |
| `'texto comun\n'` + `'# H1\ncuerpo\n'` | **5** ✓ |

**La causa:** no tiene nada que ver con el front matter —un bloque `xxx/yyy` con
la misma forma cuesta 5—. **Es que el trozo siguiente empieza con `\n`.** En el
texto junto, el `\n` final de un trozo y el `\n` inicial del siguiente forman
`\n\n`, que es **un solo token**; partidos son dos. Un token de más, una vez.

**Por qué sólo aparece con front matter:** `FRONT_MATTER_RE` termina en `\r?\n?`
**opcional**, así que consume el `---\n` de cierre pero **deja afuera la línea en
blanco que le sigue**. Esa línea se convierte en un trozo `(preamble)` de un solo
`\n`, y ese trozo empieza con `\n`. Un archivo sin front matter nunca tiene un
trozo así: los trozos de encabezado empiezan con `#`.

**El arreglo — que el front matter absorba las líneas en blanco que le siguen:**

```python
FRONT_MATTER_RE = re.compile(
    r"\A---\r?\n(?:.*?\r?\n)?---[ \t]*\r?\n(?:[ \t]*\r?\n)*",
    re.DOTALL,
)
```

**Verificado sobre 17 archivos reales** (los 11 anteriores más los documentos
nuevos de esta sesión), con la partición recompuesta byte a byte en cada uno:

| | Archivos con residuo ≠ 0 |
|---|---|
| Expresión actual | **12** |
| Expresión corregida | **0** |

**Residuo 0 en todos, sin excepciones.** La suma de los `Own` da el total real
exacto para cualquier archivo. El cabo suelto queda cerrado y la condición para
aceptar este ADR, cumplida.

### Un defecto adicional que salió de la misma investigación

`src/tokmd/sections.py` descarta el preámbulo cuando está en blanco:

```python
if preamble_text.strip():
    root.children.append(Section(title="(preamble)", ...))
```

O sea que en el árbol real de `tokmd` ese `\n` **no entra en ningún `own_text` y
no lo cuenta nadie**. Es el mismo defecto de fondo que
`[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` —texto del archivo que no
figura en ninguna fila— con otro carácter. Quedó anotado en la sección 6 de ese
bug en vez de abrir un registro nuevo, porque **el arreglo de la expresión de
arriba lo resuelve de paso**: sin trozo en blanco, no hay nada que descartar.

**Reversibilidad:** el cambio es un número y dónde se resta. Volver atrás es
volver a `FRAME = token_count("")` restado por sección, con el efecto de
sub-informar cada archivo. Cambiar esta decisión requiere reemplazar este ADR y
corregir ADR-002 otra vez.

## Lo que este ADR NO decide

- **La presentación del árbol.** Fabián aprobó el 27/09/2026 la **variante B**,
  con conectores (`├─`, `└─`, `│`), sobre la indentación por espacios. Es
  presentación y no cálculo, así que va en
  `[[PBI-009-defaults-del-cli-y-total]]`, no acá.
- **Si `--sections` y `--tree` son un flag o dos.** Todo lo que Fabián describió
  para `--tree` es lo que ADR-003 ya manda para el desglose, así que con uno
  alcanza; la única diferencia era el dibujo, y ya está decidido.
- **Qué recortar del `CLAUDE.md` global** con el número corregido. Es de Fabián.
