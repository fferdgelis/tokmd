---
title: "BUG-008 — El texto de los encabezados no se cuenta en ninguna fila: tokmd subestima todo archivo con encabezados"
aliases:
  - "BUG-008 encabezados sin contar"
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
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
  - "[[ADR-003-parseo-de-secciones]]"
  - "[[PBI-001-parser-de-secciones]]"
---

# BUG-008 — El texto de los encabezados no se cuenta en ninguna fila

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación. Lo detectó Fabián usando `tokmd` sobre su `CLAUDE.md` global como usuario final. Medido: 1472 tokens no contados, 8,5 % del archivo. |

## 1. Clasificación

- **Título:** El texto de los encabezados (`# Título`) no se cuenta en ninguna fila, así que la suma de secciones subestima el archivo.
- **Estado:** `confirmed`
- **Tipo:** `product-defect`
- **Severidad:** `2-high` — es el número que la herramienta existe para dar, y está bajo por un 8,5 % en el archivo real del owner.
- **PBI relacionado:** `[[PBI-001-parser-de-secciones]]` (origen del defecto) · **bloquea** `[[PBI-009-defaults-del-cli-y-total]]`
- **Caso de Kiwi relacionado:** **pendiente de registrar**
- **Reportado por:** Fabián Ferdgelis, owner, usando la herramienta como usuario final
- **Fecha de detección:** 2026-09-27

## 2. Contexto reproducible

- **Build/commit:** `25eed2b` (y `v1.0.0`, publicado en PyPI — **el defecto está en producción**)
- **Canal de QA:** pendiente. Lo encontró el owner en uso real, no una corrida de QA.
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`
- **Precondiciones:** cualquier archivo Markdown que tenga por lo menos un encabezado.

## 3. Reproducción

Lo que corrió Fabián:

```
uvx tokmd "claude.md" --platform codex --encoding cl100k_base
```

Y vio, entre otras, estas filas:

```
  REGLA CERO — SILENCIO OPERATIVO (23/09/2026, REGLA ESTRICTA): 0
  Mientras ejecutás, no narrás. Por cada paso, UNA sola línea y nada más:: 0
  salió bien  → «OK, seguimos.»: 0
```

Su observación, textual: *«las líneas que arrancan con numeral simple no están
contabilizadas como tokens que se consumen… los encabezados de sección,
subsección y subsubsección tienen peso y consumen tokens»*.

**Tiene razón.** Un `# Título` ocupa lugar en el archivo, viaja en el prompt y
se factura. Hoy `tokmd` no lo cuenta en ninguna parte.

## 4. Impacto

**Medido sobre `C:\Users\fferdgelis\.claude\CLAUDE.md`** (38.185 bytes, tokenizador
de Claude familia `4.8`, `FRAME=6`):

| Medición | Tokens |
|---|---|
| **Total real** (una sola pasada sobre el archivo entero) | **17.375** |
| **Suma de lo que reporta `tokmd`** (`own_text` de cada sección) | **15.903** |
| **Diferencia: tokens que `tokmd` nunca cuenta** | **1.472** |
| | **8,5 % del archivo** |

Desglose: 44 encabezados, cuyos títulos solos suman **1.376 tokens**. El resto
de la diferencia es la deriva estructural del `FRAME` que ya documenta
`[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` (se resta una vez por
sección en vez de una vez por documento).

**El error escala con la cantidad de encabezados**, así que castiga más a los
archivos bien estructurados — que son exactamente los que un usuario de esta
herramienta va a analizar.

**Consecuencia concreta y ya materializada:** la medición de PBI-008 dijo que el
`CLAUDE.md` global cuesta **15.877 tokens**, y ese número está en
`framework-multi-ai`, en
`docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md`, esperando que
Fabián decida qué recortar. **Ese número también está subestimado por este mismo
bug**, porque `count_verified` suma `own_text` por sección igual que el camino
offline. El archivo cuesta cerca de **17.300**, no 15.877.

## 5. Evidencia

Script de medición:
`C:\Users\FFERDG~1\AppData\Local\Temp\claude\C--IA-Projects-Claude-Tokenizer\ce58477c-5ea2-4ef0-8fe7-ddb107b0eda8\scratchpad\medir_encabezados.py`
(temporal; el resultado transcrito arriba es la evidencia).

Salida de las primeras filas, mostrando el título que no se cuenta:

```
  H1 own=     0  titulo_no_contado= 41  'REGLA CERO — SILENCIO OPERATIVO (23/09/2026, REGLA ESTRICTA)'
  H1 own=     0  titulo_no_contado= 34  'Mientras ejecutás, no narrás. Por cada paso, UNA sola línea y '
  H1 own=     0  titulo_no_contado= 16  'salió bien  → «OK, seguimos.»'
  ...
  H1 own=   211  titulo_no_contado= 17  'Configuración global — Fabián Ferdgelis'
```

## 6. Causa

`src/tokmd/sections.py`, en `parse_sections`:

```python
own_text = "".join(lines[content_start:end_line])
```

`content_start` viene de `token.map[1]` de `markdown-it`, que es **la línea
siguiente al encabezado**. O sea que `own_text` arranca *después* de la línea
del `#`, y el texto del título queda afuera de todo `own_text` del árbol.

Después, `src/tokmd/render.py`:

```python
total = count_fn(section.own_text) if section.own_text else 0
```

`count_fn` sólo ve `own_text`. **El título no se le pasa nunca a ningún
tokenizador.** No es que se cuente mal: no se cuenta.

`Section.own_text` está documentado como *«the section's own content, excluding
its children's text»*. El defecto es que también excluye su propio encabezado, y
nadie más lo recoge.

### Por qué Fabián vio 19 filas con 0, y por qué eso es dos problemas y no uno

1. **El bug de arriba:** el título no se cuenta, así que una sección sin cuerpo
   queda en 0 aunque su encabezado ocupe 41 tokens.
2. **Y algo que no es un defecto de `tokmd`:** el `CLAUDE.md` de Fabián arranca
   con un bloque donde `#` se usa como **comentario** de shell:

   ```
   # REGLA CERO — SILENCIO OPERATIVO (23/09/2026, REGLA ESTRICTA)
   # Mientras ejecutás, no narrás. Por cada paso, UNA sola línea y nada más:
   ```

   En Markdown, `# texto` es un **encabezado H1**. `tokmd` usa un parser
   CommonMark de verdad (`markdown-it-py`, por `[[ADR-003-parseo-de-secciones]]`)
   y lo lee bien: son 19 H1 seguidos, cada uno sin cuerpo. **El parser no está
   equivocado; el archivo dice eso.** Vale saberlo aparte del bug: cualquier
   herramienta que lea ese `CLAUDE.md` como Markdown ve 19 encabezados de nivel 1.

## 7. Corrección

**Sin implementar.** Pendiente de que Fabián elija, porque las dos opciones dan
números distintos y una cambia el contrato de `Section`:

- **(a) Incluir la línea del encabezado en `own_text`** (`content_start` pasa a
  ser `heading_line`). Cada sección cuenta su propio título, el árbol vuelve a
  ser aditivo y la fila de una sección sin cuerpo deja de ser 0. **Es la que
  recomiendo:** arregla la causa. Rompe los datos dorados de
  `tests/test_tokenizers.py` y `tests/test_sections.py`, que hay que remedir.
- **(b) Dejar el parser como está y agregar una fila de total** contada de una
  sola pasada sobre el archivo. El total queda correcto, pero la tabla sigue
  sin contar títulos y total ≠ suma de filas — vuelve la deriva que ADR-002 ya
  decidió *reportar y no esconder*, y que hoy **no se reporta** (ver abajo).

**Lo correcto son las dos**: (a) arregla las filas, y el total de una pasada del
`[[PBI-009-defaults-del-cli-y-total]]` es correcto por construcción.

### Defecto vecino, del mismo lugar

`[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` dice que `tokmd` tiene que
imprimir una línea `boundary drift: ±N` cuando la suma de filas no coincide con
el archivo completo. **Ese código no existe** (`grep -rn "boundary drift" src/`:
cero resultados). Si esa línea existiera, este bug se habría visto el primer día
que alguien corrió la herramienta sobre un archivo con encabezados. Va aparte o
adentro de la corrección de este bug, a criterio de quien lo tome.

## 8. Verificación independiente

- **Verificado por:** pendiente. Lo midió Desarrollo con un script propio, que
  **no** es QA independiente.
- **Evidencia:** la medición de la sección 4, reproducible con el script de la
  sección 5.
- **Pendiente:** registrar el bug en Kiwi y cargar el caso de regresión como
  `PROPOSED` **antes** de arreglarlo, con el test escrito por TDD y no por
  Desarrollo (`[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]`).
