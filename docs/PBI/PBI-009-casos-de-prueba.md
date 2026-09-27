---
title: "PBI-009 — casos de prueba para Kiwi (defaults del CLI, total, y regresión de BUG-008/009/010)"
aliases:
  - "PBI-009 casos de prueba"
project: tokmd
document_type: test-plan
status: active
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
  - qa
related_documents:
  - "[[PBI-009-defaults-del-cli-y-total]]"
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
  - "[[BUG-009-adr-003-arbol-sin-own-ni-total]]"
  - "[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]"
---

# PBI-009 — casos de prueba

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación, a pedido de Fabián: *«el bug 008 tiene que estar ASAP en kiwi y con el detalle de casos que se van a correr para el testeo del buen funcionamiento»*. Pendiente de cargar a Kiwi como PROPOSED. |

## Para qué sirve este documento

Es la fuente de la que se cargan los casos a Kiwi, y se escribe **antes** de
tocar el código. Cada caso lleva una columna **«qué falla caza»**: la
modificación concreta del código que tiene que hacerlo fallar. Un caso que no
puede fallar no prueba nada — es el paso 10 de los doce pasos, y es lo que faltó
en PBI-001 y PBI-005 y dejó pasar los tres bugs.

**Estado:** `PROPOSED`, sin cargar todavía. Falta la credencial de la bóveda para
`tools/kiwi/cargar_casos.py`.

**Cobertura:** los diez criterios de aceptación de
`[[PBI-009-defaults-del-cli-y-total]]` más la regresión de los tres bugs. Trece
casos.

## Los tres bugs que estos casos tienen que cazar

| Bug | Qué está mal hoy |
|---|---|
| `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` | El texto del encabezado no se cuenta en ninguna fila: 1.472 tokens, 8,5 % del `CLAUDE.md` global |
| `[[BUG-009-adr-003-arbol-sin-own-ni-total]]` | Falta la columna `Own` y falta la fila raíz con el total, que ADR-003 decidió |
| `[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]` | La línea `boundary drift: ±N` que ADR-002 promete no existe |

## Datos dorados (los números de referencia)

Medidos el 2026-09-27 sobre `C:\Users\fferdgelis\.claude\CLAUDE.md`
(38.185 bytes) con tokenizador de Claude familia `4.8`, `FRAME=6`:

| Dato | Valor |
|---|---|
| Archivo contado **de una sola pasada** (el valor real) | **17.375** |
| Suma de las 44 filas **con** el título, marco restado una vez | **17.590** |
| Suma de las 44 filas **sin** el título (lo que hace hoy) | **15.903** |
| Deriva de borde real entre las dos primeras | **−215 (1,24 %)** |
| Encabezados en el archivo | 44 (20 de nivel 1) |
| Secciones que hoy salen `0` teniendo encabezado con texto | 18 |

**Estos números valen para este archivo en este estado.** Si Fabián edita su
`CLAUDE.md`, hay que remedirlos. Los casos que los usan lo dicen.

## Fixtures que hay que crear

| Fixture | Para qué |
|---|---|
| `tests/fixtures/headings_sin_cuerpo.md.fixture` | Varios `#` seguidos sin texto entre ellos, replicando el bloque de comentarios de estilo shell del `CLAUDE.md` de Fabián. Es el caso que destapó BUG-008. |
| `tests/fixtures/empty.md.fixture` | Ya existe. |
| `tests/fixtures/no_headings.md.fixture` | Ya existe. |
| `tests/fixtures/sample.md.fixture` | Ya existe. Hay que **remedir** sus datos dorados. |

## Los casos

### Bloque A — los defaults del CLI (lo que Fabián pidió)

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C01** | `tokmd archivo.md` corre sin ninguna opción | `tokmd` instalado, un `.md` válido | `tokmd sample.md` | Código de salida **0**. Ninguna mención de «Missing option». | Volver `--platform` a `required=True` |
| **TOK-009-C02** | Sin `--platform`, la plataforma resuelta es `claude-code` | ídem | `tokmd sample.md` y comparar contra `tokmd sample.md --platform claude-code` | **Idéntica** salida | Cambiar el default a `codex` o a cualquier otro |
| **TOK-009-C03** | La salida por defecto es el total, no la tabla | ídem | `tokmd sample.md` | **Una** línea con el total. **No** aparece el desglose por secciones | Dejar la tabla como salida por defecto |
| **TOK-009-C04** | `--platform codex` explícito sigue funcionando | ídem | `tokmd sample.md --platform codex` | Resuelve el tokenizador de OpenAI, sin regresión de PBI-004 | Que el default de `claude-code` pise el valor explícito |

### Bloque B — el total tiene que ser el valor real

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C05** | El total es el del archivo de una pasada, no la suma de filas | El `CLAUDE.md` global sin editar desde la medición | `tokmd CLAUDE.md` | **17.375** exacto | Calcular el total sumando filas: daría 17.590 o 15.903 |
| **TOK-009-C06** | Archivo vacío | `empty.md.fixture` | `tokmd empty.md.fixture` | Informa `0`, código de salida 0, **sin traceback** | Que el camino del total no maneje texto vacío |
| **TOK-009-C07** | Archivo sin ningún encabezado | `no_headings.md.fixture` | `tokmd no_headings.md.fixture` | Informa el total sin fallar | Que el total dependa de que exista al menos un encabezado |

### Bloque C — regresión de BUG-008: los encabezados se cuentan

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C08** | Una sección cuyo encabezado tiene texto **no** puede dar 0 | `headings_sin_cuerpo.md.fixture` | `tokmd <fixture> --sections` | **Ninguna** fila con encabezado no vacío informa `Own = 0` | Volver `content_start` a `token.map[1]` — el arreglo de BUG-008 revertido |
| **TOK-009-C09** | El título del encabezado está contado en su propia sección | fixture con un único encabezado de texto conocido y cuerpo conocido | `tokmd <fixture> --sections` | El `Own` de esa fila **incluye** los tokens del título | ídem C08, y también contar el título en el padre en vez de en la sección |

### Bloque D — regresión de BUG-009: el árbol que decidió ADR-003

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C10** | Cada fila muestra `Own` **y** `Total`, separados | `sample.md.fixture` | `tokmd <fixture> --sections` | Dos columnas numéricas distinguibles por fila | Volver `Row` a un solo campo `tokens` |
| **TOK-009-C11** | Hay una fila raíz con el total del archivo | ídem | `tokmd <fixture> --sections` | Una fila raíz (nivel 0) cuyo `Total` es el total del archivo | Volver a `return rows[1:]`, que descarta la raíz |
| **TOK-009-C12** | `Own` ≠ `Total` en una sección con hijos que pesan | fixture con un padre de cuerpo corto y un hijo de cuerpo largo | `tokmd <fixture> --sections` | En la fila del padre, `Own` < `Total` | Hacer que `Own` sea igual a `Total` (o sea, no implementar `Own` de verdad) |

### Bloque E — regresión de BUG-010: la deriva se reporta

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C13** | Si la suma de `Own` no coincide con el total, se informa | El `CLAUDE.md` global, donde la deriva medida es −215 | `tokmd CLAUDE.md --sections` | Sale una línea con la deriva y su signo, **no** se esconde | Borrar la línea de deriva; o imprimirla siempre en 0 sin calcularla |

## Casos de no regresión que ya existen y hay que volver a correr

No son nuevos, pero el cambio los toca y tienen que seguir en verde:

- `--format json` sigue devolviendo JSON parseable (**con los campos nuevos**).
- `--format csv` sigue teniendo cabecera y una fila por sección.
- `--depth N` sigue filtrando sin cambiar el cálculo.
- `--sort tokens` sigue ordenando hermanos, no la lista plana.
- `#` dentro de un bloque de código sigue **sin** contar como encabezado.
- `(front matter)` y `(preamble)` siguen apareciendo como filas propias.
- `--verify` sigue funcionando igual que hoy.
- Un archivo que no existe sigue dando error legible y código de salida ≠ 0.

## Lo que estos casos NO cubren, y hay que decidir antes

**El requisito de Fabián de que «el parser y el total den el mismo valor» no
está entre los casos, porque está medido que no se puede cumplir exactamente:**
la tokenización no es aditiva y quedan 215 tokens (1,24 %) de deriva de borde
real. Ver la sección 4 de `[[PBI-009-defaults-del-cli-y-total]]`.

Hasta que el owner decida qué hacer con esa deriva —reportarla (C13), repartirla,
o declarar que el total manda y las filas son desglose aproximado— **no se puede
escribir un caso que verifique la igualdad**, porque no se sabe contra qué
comparar. C05 y C13 son la versión que sí se puede verificar hoy: el total es el
valor real, y la diferencia se declara en vez de esconderse.

## Registro en Kiwi

- **Producto:** tokmd
- **Plan:** el del PBI-009, a crear con `tools/kiwi/crear_planes.py`
- **Casos:** trece, como `PROPOSED`, con `tools/kiwi/cargar_casos.py`
- **Bugs a registrar** como registros Bug, y a linkear a la Test Execution
  cuando exista: BUG-008, BUG-009 y BUG-010
- **Recordatorio de la trampa ya pagada:** `cargar_casos.py` lee la contraseña
  **cruda** por stdin; `crear_run.py`, `registrar_resultados.py` y
  `confirmar_casos.py` esperan **JSON**
- **Estado:** pendiente. Falta la credencial de la bóveda.
