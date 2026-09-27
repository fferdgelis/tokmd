---
title: "BUG-010 — ADR-002 promete imprimir `boundary drift: ±N` y ese código no existe"
aliases:
  - "BUG-010 boundary drift inexistente"
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
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
  - "[[BUG-009-adr-003-arbol-sin-own-ni-total]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
---

# BUG-010 — La línea `boundary drift: ±N` que promete ADR-002 no existe

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación. Detectado al verificar afirmaciones de los motores en la consulta de la ronda 2: dos de ellos afirmaron que la deriva «se reporta al usuario», leyendo el ADR y creyendo que describía el código. |

## 1. Clasificación

- **Título:** ADR-002 decide que `tokmd` imprima `boundary drift: ±N` cuando la suma de filas no coincide con el archivo completo; ese código nunca se escribió.
- **Estado:** `confirmed`
- **Tipo:** `product-defect` (con componente `documentation-defect`: el ADR describe algo que no pasa)
- **Severidad:** `3-medium` por sí solo. Sube a `2-high` leído junto a `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`, porque este instrumento era el que lo habría detectado.
- **PBI relacionado:** `[[PBI-002-tokenizador-claude]]` (origen) · se corrige en `[[PBI-009-defaults-del-cli-y-total]]`
- **Registro en Kiwi:** **Bug `pk=11`**, severidad `Medium`, estado abierto, build
  `d9c42ff` (registrado 2026-09-27).
- **Caso de Kiwi relacionado:** `TOK-009-C13` (id 388), `PROPOSED`, en el plan
  **30** «PBI-009 - Defaults del CLI y total».
- **Reportado por:** Desarrollo, verificando afirmaciones de los motores en la ronda 2 de la consulta
- **Fecha de detección:** 2026-09-27

## 2. Contexto reproducible

- **Build/commit:** `97b71ea` (y `v1.0.0` en PyPI)
- **Canal de QA:** ninguno. Ver sección 6.
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`
- **Precondiciones:** ninguna. La funcionalidad no existe en ningún camino.

## 3. Reproducción

```
grep -rn "boundary drift" src/
```

Cero resultados. Ninguna salida de `tokmd` —`table`, `md`, `json` ni `csv`—
informa la deriva en ninguna circunstancia.

## 4. Impacto

**Lo que ADR-002 dice, textual, en un ADR con estado `accepted` desde el
2026-09-25:**

> «**Deriva de borde:** si `sum(Own de todas las filas) != token_count(archivo
> completo) − FRAME`, tokmd imprime una línea `boundary drift: ±N` en vez de
> esconder la diferencia. Se documenta como limitación conocida, no como bug.»

Dos consecuencias, y la segunda ya se materializó:

1. **El usuario no tiene forma de saber que la suma no cierra.** La deriva real
   medida sobre el `CLAUDE.md` global es de **215 tokens (1,24 %)** entre sumar
   las filas y contar el archivo de una pasada. La herramienta no lo dice.
2. **El ADR indujo a error a lectores reales.** En las dos rondas de consulta del
   PBI-009 diferido, Kimi K3 afirmó que la deriva *«está medida en el proyecto y
   se reporta al usuario en vez de ocultarse»*. Leyó el ADR, que es un documento
   `accepted` y fuente de verdad, y concluyó razonablemente que describía el
   comportamiento. **Un ADR aceptado que describe código inexistente convierte la
   documentación en una trampa.**

Y la consecuencia de fondo: esta línea era un **instrumento de control**. Si
existiera, `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` —1.472 tokens sin
contar, 8,5 % del archivo— habría disparado la alarma la primera vez que alguien
corrió `tokmd` sobre un archivo con encabezados, en PBI-001.

## 5. Evidencia

```
$ grep -rn "boundary drift" src/
(sin resultados)
```

Las únicas apariciones de «drift» en `src/` son comentarios sobre otra cosa:

```
src/tokmd/render.py:9:   the indentation, since a level-2 row would drift away from its level-1
src/tokmd/tokenizers.py:58:    sections with zero drift.
```

Medición de la deriva que debería reportarse, sobre
`C:\Users\fferdgelis\.claude\CLAUDE.md` con tokenizador de Claude `4.8`:

| | Tokens |
|---|---|
| Archivo contado de una pasada | 17.375 |
| Suma de las 44 filas con el título incluido, marco restado una vez | 17.590 |
| **Deriva de borde real** | **−215 (1,24 %)** |

## 6. Causa

El ADR se aceptó y **ningún PBI convirtió esa cláusula en un criterio de
aceptación.** `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]`, en su sección
de verificación, dice:

> «PBI-002 mide `FRAME` real por familia y la deriva sobre los fixtures de
> prueba; los valores quedan congelados como datos dorados en
> `tests/test_tokenizers.py`.»

O sea que PBI-002 verificó **medir** la deriva, y eso se hizo —está en
`docs/investigation/20260924-ctok-marco-y-deriva.md`—, pero nunca verificó
**mostrarla**. Medir y reportar son dos cosas, y el ADR pedía las dos.

Es el mismo agujero que `[[BUG-009-adr-003-arbol-sin-own-ni-total]]`, con otro
ADR: **la decisión llegó al documento y no al criterio de aceptación.** Ver la
sección 6 de BUG-009 para el patrón completo.

## 7. Corrección

**Sin implementar.** Dos caminos, y la elección es del owner porque cambian lo
que la herramienta promete:

- **(a) Implementar la línea**, como manda el ADR. Con `[[BUG-009-adr-003-arbol-sin-own-ni-total]]`
  arreglado (o sea con `Own` y la fila raíz existiendo) la comparación es
  trivial: `sum(own) != total_del_archivo` → imprimir la diferencia.
- **(b) Corregir el ADR-002** si se decide que la deriva se resuelve de otra
  forma (por ejemplo que el total sea siempre el del archivo de una pasada y las
  filas se declaren explícitamente como desglose aproximado).

**Lo que no se puede dejar así** es que el ADR diga una cosa y el programa haga
otra. Una de las dos tiene que cambiar.

## 8. Verificación independiente

- **Verificado por:** pendiente.
- **Evidencia:** el `grep` de la sección 5 y la cita literal de ADR-002.
- **Registrado en Kiwi el 2026-09-27** (Bug `pk=11`), con su caso de regresión
  `TOK-009-C13` (id 388) cargado como `PROPOSED` antes de arreglar nada.
- **Pendiente:** que el test lo escriba TDD y no Desarrollo, que QA lo corra
  independiente, y linkear este Bug a la Test Execution con `Bug.add_execution`
  cuando exista el Test Run.
