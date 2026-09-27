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

## Estado

`proposed`. **Bloquea `[[PBI-009-defaults-del-cli-y-total]]`.** Pendiente de
decisión de Fabián Ferdgelis.

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
3. El **total** se cuenta de una sola pasada: `token_count(archivo) − 5`.
4. La línea de deriva **se implementa igual** (`[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]`),
   como red de seguridad: tiene que dar `+0`, y si algún día no da 0, se ve.

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
  porque hoy sobre-resta. Para el `CLAUDE.md` global: de 15.903 a **17.376**
  (+9,3 %). Es un motivo más para la `2.0.0` que Fabián ya decidió.
- **Hay que remedir todos los datos dorados** de `tests/test_tokenizers.py`,
  `tests/test_sections.py` y `tests/test_render.py`.
- **Las mediciones anteriores del proyecto quedan desactualizadas**, incluida la
  de PBI-008 que está en `framework-multi-ai`
  (`docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md`, 15.877) y que
  Fabián estaba usando para decidir qué recortar. El valor correcto es **17.376**.
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
| `CLAUDE.md` global, total de una pasada | **17.376** |
| `CLAUDE.md` global, suma de los `Own` | **17.376** |
| Deriva resultante | **+0** |

**Cómo se verifica que sigue sano:** el criterio `AC-15` de
`[[PBI-009-defaults-del-cli-y-total]]` y el caso `TOK-009-C13`. La línea de
deriva tiene que dar `+0` para todo archivo sin front matter. **Si algún día no
da 0, hay un defecto nuevo.**

**El cabo suelto que hay que cerrar antes de aceptar este ADR:** los archivos con
front matter YAML dan **−1**, en los siete medidos, sin excepción. Es constante y
chico, pero es un token que no se explica. **No se acepta este ADR sin saber de
dónde sale**, porque un residuo inexplicado de 1 token es exactamente la clase de
cosa que después resulta ser otro `FRAME` mal medido. Hipótesis a probar: el
trozo de front matter termina en `---\n` y el bloque siguiente arranca en `#`;
puede que `markdown-it` no incluya alguna línea en blanco del límite, o que el
front matter como primer trozo se tokenice distinto.

**Reversibilidad:** el cambio es un número y dónde se resta. Volver atrás es
volver a `FRAME = token_count("")` restado por sección, con el efecto de
sub-informar cada archivo. Cambiar esta decisión requiere reemplazar este ADR y
corregir ADR-002 otra vez.

## Lo que este ADR NO decide

- **Los conectores de árbol** (`├─`, `└─`) contra la indentación por espacios: es
  presentación, no cálculo. Va en el PBI si Fabián lo quiere.
- **Si `--sections` y `--tree` son un flag o dos.** Todo lo que Fabián describió
  para `--tree` es lo que ADR-003 ya manda para el desglose, así que con uno
  alcanza; la única diferencia posible es el dibujo.
- **Qué recortar del `CLAUDE.md` global** con el número corregido. Es de Fabián.
