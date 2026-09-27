---
title: "BUG-009 — ADR-003 pidió árbol con `Own` y `Total` y fila raíz: el código tiene una sola columna y descarta la raíz"
aliases:
  - "BUG-009 ADR-003 sin Own ni Total"
project: tokmd
document_type: bug
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
  - bug
related_documents:
  - "[[ADR-003-parseo-de-secciones]]"
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
  - "[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
---

# BUG-009 — El árbol no tiene `Own` ni `Total` ni fila raíz, contra lo que decidió ADR-003

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación. Lo levantó Fabián: *«ACÁ HAY UN PROBLEMA MUY GRANDE, EL ADR-003 YA ESPECIFICABA QUE ESTE COMPORTAMIENTO TENÍA QUE EXISTIR»*. Verificado contra el ADR y el código. |

## 1. Clasificación

- **Título:** El render tiene una sola columna numérica (el acumulado) y descarta la fila raíz, cuando ADR-003 decidió `Own` **y** `Total` por nodo, más subtotales.
- **Estado:** `confirmed`
- **Tipo:** `product-defect`
- **Severidad:** `2-high` — es una decisión arquitectónica aceptada por el owner que nunca llegó al código, y su ausencia es la que dejó pasar `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`.
- **PBI relacionado:** `[[PBI-001-parser-de-secciones]]` y `[[PBI-005-render-de-salida]]` (ninguno lo pidió) · se corrige en `[[PBI-009-defaults-del-cli-y-total]]`
- **Registro en Kiwi:** **Bug `pk=10`**, severidad `High`, estado abierto, build
  `d9c42ff` (registrado 2026-09-27).
- **Casos de Kiwi relacionados:** `TOK-009-C10` (id 385), `TOK-009-C11` (id 386) y
  `TOK-009-C12` (id 387), `PROPOSED`, en el plan **30** «PBI-009 - Defaults del
  CLI y total».
- **Reportado por:** Fabián Ferdgelis, owner
- **Fecha de detección:** 2026-09-27

## 2. Contexto reproducible

- **Build/commit:** `97b71ea` (y `v1.0.0` en PyPI — **está en producción**)
- **Canal de QA:** ninguno. Los nueve criterios de aceptación de PBI-001 y PBI-005 pasaron en verde **sin cubrir esto**. Ver la sección 6.
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`
- **Precondiciones:** cualquier archivo Markdown con encabezados.

## 3. Reproducción

```
uvx tokmd "claude.md" --platform codex --encoding cl100k_base
```

La salida tiene **una sola** columna de números, y no hay ninguna fila que
informe el total del archivo. Lo que ADR-003 decidió es dos números por nodo
(`Own` y `Total`) y un árbol con subtotales que arranca en la raíz.

## 4. Impacto

**Lo que ADR-003 dice, textual, en la opción que Fabián aceptó tal cual el
2026-09-25:**

> «Árbol completo: todos los niveles de encabezado, anidados, cada nodo con su
> propio texto (`Own`) y el acumulado con sus hijos (`Total`).»

Y en el contexto del mismo ADR:

> «Fabián pidió expresamente **árbol completo con subtotales**, no un corte plano
> de un solo nivel.»

**Lo que falta, concretamente:**

| ADR-003 decidió | El código hace |
|---|---|
| Cada nodo con su **`Own`** (su propio texto) | No existe. `Row` tiene un único campo `tokens`. |
| Cada nodo con su **`Total`** (acumulado con hijos) | Existe — es el único que hay. |
| Árbol con subtotales, o sea la raíz también | `render()` emite *«root's children (not root itself)»*. **La raíz se descarta.** |

**Por qué esto importa más que una columna que falta:** `Own` y `Total` juntos
son el mecanismo que hace visible la diferencia entre «esta sección pesa» y
«esta sección tiene hijos que pesan». Sin `Own`, una sección cuyo encabezado
ocupa 41 tokens y cuyo cuerpo está vacío es indistinguible de una sección
genuinamente vacía: **las dos salen `0`.** Eso es exactamente lo que Fabián vio
y lo que hizo aparecer `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`.

Con `Own` implementado, BUG-008 se habría visto el primer día que alguien corrió
la herramienta sobre un archivo con encabezados.

## 5. Evidencia

`src/tokmd/render.py`, la definición de la fila:

```python
@dataclass(frozen=True)
class Row:
    """One visible line: a section's title, its nesting level, and its
    accumulated token count (own text plus every descendant's)."""

    title: str
    level: int
    tokens: int
```

Un solo campo numérico, y el docstring confirma que es el acumulado.

La raíz, descartada en dos lugares:

```python
def _build_rows(section, count_fn, sort):
    _, rows = _accumulate_and_flatten(section, count_fn, sort)
    return rows[1:]          # <- rows[0] es la fila raiz, con el total
```

y el docstring de `render()`:

```
"""Render `root`'s children (not `root` itself) as `fmt`.
```

El total del documento **se calcula y se tira dos veces**: el primer elemento de
la tupla (`_`) y `rows[0]`.

Las cabeceras de las cuatro salidas confirman la única columna:

```python
writer.writerow(["level", "title", "tokens"])
json.dumps([{"title": r.title, "level": r.level, "tokens": r.tokens} for r in rows])
```

## 6. Causa

**No es que se implementó mal: nunca se pidió.** Los criterios de aceptación de
los dos PBI que cubren esta zona no mencionan `Own`, ni `Total` como par, ni la
fila raíz:

**`[[PBI-005-render-de-salida]]`** — cuatro AC, todos en verde:
JSON parseable, indentación por nivel, `--depth 2` con acumulados intactos,
`--sort tokens` ordenando hermanos.

**`[[PBI-001-parser-de-secciones]]`** — cinco AC:
front matter, preámbulo, salto de nivel, `#` dentro de bloque de código,
archivo sin encabezados o vacío.

Nueve criterios que cubren todo lo periférico del ADR y **omiten su punto
central**. La cadena falló en el eslabón de traducción: **el ADR se aceptó y
nadie convirtió su decisión principal en un criterio verificable.** QA pasó en
verde legítimamente, porque probó lo que los AC pedían.

### El patrón, que es el hallazgo real

Tres decisiones aceptadas que el código no cumple, y las tres son justamente los
tres mecanismos que habrían delatado el error de conteo:

| Decisión | Dónde | Estado en el código |
|---|---|---|
| `Own` separado del `Total` por nodo | ADR-003 | **No existe** (este bug) |
| Fila raíz con el total del archivo | ADR-003 | **No existe** (este bug) |
| Línea `boundary drift: ±N` cuando la suma no cierra | ADR-002 | **No existe** (`[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]`) |

Los tres son instrumentos de control. Ninguno se implementó. Por eso
`[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` sobrevivió desde PBI-001
hasta que el owner usó la herramienta a mano, ocho PBI después y con `v1.0.0`
ya publicado en PyPI.

**Un test que nunca podía fallar no prueba nada** — es el paso 10 de los doce
pasos. Acá el problema es anterior: el test no existía porque el criterio no
existía.

## 7. Corrección

**Sin implementar.** Se corrige junto con
`[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` y
`[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]` dentro de
`[[PBI-009-defaults-del-cli-y-total]]`, porque son la misma zona de código y
arreglar uno sin los otros deja números que no cierran.

Lo que hay que agregar:

1. `Row` con **dos** campos numéricos: `own` y `total`.
2. Las cuatro salidas (`table`, `md`, `json`, `csv`) mostrando los dos.
3. La **fila raíz** con el total del archivo, que es lo que Fabián describe como
   *«al principio, como es el raíz `\` de todo el archivo, debería tener el
   número de tokens totales»*.

**Atención — hay un conflicto medido entre este arreglo y el requisito de que
«el parser y el total den el mismo valor».** No es aditivo: ver la sección 4 del
PBI-009, «la no-aditividad medida». Restar el marco una sola vez y sumar las
filas da **17.590** contra **17.375** del archivo contado de una pasada: 215
tokens de deriva de borde real, 1,24 %. Esa decisión es del owner y necesita ADR.

## 8. Verificación independiente

- **Verificado por:** pendiente.
- **Evidencia:** las citas de la sección 5 son literales del código en `97b71ea`,
  y las de la sección 4 literales de `[[ADR-003-parseo-de-secciones]]`.
- **Registrado en Kiwi el 2026-09-27** (Bug `pk=10`), con los casos cargados como
  `PROPOSED` **antes** de arreglar nada.
- **Pendiente:** que los tests los escriba TDD y no Desarrollo
  (`[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]`), que QA los corra
  independiente, y linkear este Bug a la Test Execution con `Bug.add_execution`
  cuando exista el Test Run.
