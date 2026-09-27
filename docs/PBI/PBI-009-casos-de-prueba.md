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
| 2026-09-27 | 0.2.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Se agregan **TOK-009-C14** (la suma de `Own` es exactamente el total, ya medido en 17 archivos) y **TOK-009-C15** (conectores de árbol, variante B aprobada por Fabián). Quince casos. El apartado que decía que la igualdad no se podía verificar quedó desmentido por medición. |
| 2026-09-27 | 0.3.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Se agregan **TOK-009-C16** y **TOK-009-C17**, regresión de `[[BUG-011-salida-unicodeencodeerror-cp1252-windows]]` (encontrado por la sesión TTOK-05, Fabián decidió sumarlo al alcance del PBI-009). Diecisiete casos. |

## Para qué sirve este documento

Es la fuente de la que se cargan los casos a Kiwi, y se escribe **antes** de
tocar el código. Cada caso lleva una columna **«qué falla caza»**: la
modificación concreta del código que tiene que hacerlo fallar. Un caso que no
puede fallar no prueba nada — es el paso 10 de los doce pasos, y es lo que faltó
en PBI-001 y PBI-005 y dejó pasar los tres bugs.

**Estado: CARGADOS en Kiwi el 2026-09-27**, los quince como `PROPOSED`, en el plan
**30** «PBI-009 - Defaults del CLI y total», ids **376 a 391** (sin el 380: fue
`TOK-009-C05` con un texto que se corrigió después, y quedó dado de baja — el id
vigente de `TOK-009-C05` es **391**, ver la nota de idempotencia más abajo).
Script:
`tools/kiwi/cargar_pbi009_y_bugs.py` (idempotente). Los tres bugs quedaron
registrados como Bug `pk=9`, `pk=10` y `pk=11`.

**Cobertura:** los criterios de aceptación de
`[[PBI-009-defaults-del-cli-y-total]]` más la regresión de los tres bugs.
**Diecisiete casos.**

## Los tres bugs que estos casos tienen que cazar

| Bug | Qué está mal hoy |
|---|---|
| `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` | El texto del encabezado no se cuenta en ninguna fila: 1.472 tokens, 8,5 % del `CLAUDE.md` global |
| `[[BUG-009-adr-003-arbol-sin-own-ni-total]]` | Falta la columna `Own` y falta la fila raíz con el total, que ADR-003 decidió |
| `[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]` | La línea `boundary drift: ±N` que ADR-002 promete no existe |

## Datos dorados (los números de referencia)

> **Actualizado el 2026-09-27, después de la aceptación del ADR-007.** El costo
> fijo por trozo (`ADR-002` lo llamaba `FRAME`) es **5**, no 6, y el total **no**
> lo resta — se cuenta crudo, de una sola pasada, y coincide exacto con lo que
> cobra la API de Anthropic (medido por TTOK-05: **17.381**, no 17.375/17.376).

Medidos el 2026-09-27 sobre `C:\Users\fferdgelis\.claude\CLAUDE.md`
(38.185 bytes) con tokenizador de Claude familia `4.8`:

| Dato | Valor |
|---|---|
| **El total** — archivo crudo de una sola pasada, igual a lo que cobra la API | **17.381** |
| Suma de las 44 filas (`Own`, con el título, marco restado una vez por fila) | 17.376 |
| … más el marco del mensaje, una vez (renglón propio, no restado del total) | + 5 = **17.381** ✓ |
| Suma de las 44 filas **sin** el título (lo que hace hoy, el bug) | 15.903 |
| Deriva del total contra la suma de `Own`, con el costo fijo correcto | **0** |
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
| **TOK-009-C05** | El total es el del archivo de una pasada y coincide con la API | El `CLAUDE.md` global sin editar desde la medición | `tokmd CLAUDE.md` | **17.381** exacto (lo que cobra la API; no restar el marco) | Calcular el total sumando filas: daría 17.590 o 15.903; restar el marco del total: daría 17.376 |
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

## El caso que faltaba, y ahora sí se puede escribir

> **Actualizado el 27/09/2026.** La versión 0.1.0 de este documento decía que el
> requisito de Fabián —«el parser y el total tienen que dar el mismo valor»— no se
> podía verificar porque la tokenización no era aditiva. **La medición lo
> desmintió:** lo que parecía deriva de borde era el marco contado una vez por
> sección, y vale 5, no 6. Ver
> `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]`.

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C14** | La suma de `Own` es **exactamente** el total, en cualquier archivo | Cualquiera de los 17 archivos medidos, con y sin front matter | `tokmd <archivo> --sections` | `boundary drift` = **`+0`** exacto | Restar el costo fijo por sección en vez de por corte; usar 6 en vez de 5; no absorber las líneas en blanco al front matter |
| **TOK-009-C15** | El desglose usa conectores de árbol | `sample.md.fixture` | `tokmd <fixture> --sections` | Las filas anidadas se dibujan con `├─`, `└─` y `│`, no con espacios | Volver a la indentación por espacios |

**C14 es el caso más importante de los quince**, porque es el único que verifica
el requisito del owner de punta a punta y porque **ya está medido que pasa**: 17
archivos, residuo 0 en todos, antes de escribir una línea de código.

**C15** cubre la variante B de presentación, que Fabián aprobó el 27/09/2026.

## Bloque F — regresión de BUG-011, sumado el 27/09/2026

Bug de la sesión **TTOK-05**, en paralelo sobre este mismo worktree. Fabián
decidió que entra en el alcance del PBI-009.

| Caso | Título | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-009-C16** | La salida no revienta por encoding en Windows | Fixture con un título `## Flecha → «comillas» — guion`; salida redirigida a archivo (no consola), sin `PYTHONUTF8` en el entorno | `tokmd <fixture> --sections > salida.txt` en cada `--format` | Código de salida 0, `salida.txt` completo, sin `UnicodeEncodeError` | Dejar `click.echo`/`sys.stdout` sin `reconfigure(encoding="utf-8")` al arrancar el CLI |
| **TOK-009-C17** | El carácter no se reemplaza, se preserva | Mismo fixture que C16 | `tokmd <fixture> --sections > salida.txt` | `salida.txt` contiene `→ «comillas» —` **tal cual**, no `?` ni ningún carácter de repuesto | Usar `errors="replace"` en vez de UTF-8 real |

Dieciséis casos ahora, no quince.

## Registro en Kiwi — hecho el 2026-09-27

| Qué | Id |
|---|---|
| Producto | `tokmd`, id 6 |
| Plan | **30** — «PBI-009 - Defaults del CLI y total» |
| Casos | **376–379, 381–393**, los diecisiete como `PROPOSED` (el 380 se dio de baja, ver abajo) |
| Build | **33** — `d9c42ff` |
| Bug BUG-008 | `pk=9`, `High`, abierto |
| Bug BUG-009 | `pk=10`, `High`, abierto |
| Bug BUG-010 | `pk=11`, `Medium`, abierto |
| Bug BUG-011 | `pk=13`, `High`, abierto |

Script: `tools/kiwi/cargar_pbi009_y_bugs.py`, idempotente — pero **no** por el
texto completo del `summary` (ver la trampa 4 de abajo), sino por el prefijo fijo
de cada id (`TOK-009-CNN -` o `BUG-0NN:`).

**Pendiente:** linkear los tres Bug a su Test Execution con `Bug.add_execution`
cuando exista el Test Run, o sea después de que el arreglo esté hecho y QA lo
corra.

### Cuatro trampas pagadas en esta carga (27/09/2026)

1. **El contenedor publica su 8443 en el puerto 443 de Windows.** El default
   `port=8443` de `rpc_client.connect` sirve **sólo corriendo adentro del
   contenedor** (de ahí el `sys.path.insert(0, "/tmp/work")` de los scripts
   viejos). Desde Windows hay que pasar `port=443`, o da
   `ConnectionRefusedError 10061`.
2. **El método es `Severity.filter`, no `BugSeverity.filter`.** El segundo no
   existe y devuelve `Method not found`.
3. **`Bug.create` espera el *id* del Build, no su nombre.** Pasarle el commit
   corto como string da `Select a valid choice. That choice is not one of the
   available choices.` Hay que resolver o crear el `Build` primero.
4. **Filtrar la idempotencia por el `summary` completo es frágil, y se rompió en
   esta misma sesión.** Un número (17.376) se corrigió a otro (17.381) en la
   descripción de `TOK-009-C05`, el filtro dejó de matchear el texto viejo, y se
   creó un caso duplicado (`id=391`) en vez de actualizar el existente
   (`id=380`). Peor con `Bug.filter`: Kiwi guarda el `summary` con las comillas
   HTML-escapadas (`&#x27;`), así que comparar contra el string crudo del lado
   del cliente **nunca matchea** — eso duplicó `BUG-010` (`pk=11` y `pk=12`) en
   la misma corrida. **Arreglo:** identificar por el prefijo fijo del id
   (`TOK-009-CNN -`, `BUG-0NN:`), que nunca cambia, y consultarlo contra el
   servidor en vez de comparar strings del lado del cliente. Los dos duplicados
   (`id=380`, `pk=12`) se borraron y se verificó una tercera corrida: 15
   actualizados, 0 creados.

### Lo de antes, que sigue valiendo

`cargar_casos.py` lee la contraseña **cruda** por stdin; `crear_run.py`,
`registrar_resultados.py` y `confirmar_casos.py` esperan **JSON**. El script
nuevo sigue la convención de `cargar_casos.py`: contraseña cruda por stdin.
