---
title: "BUG-006 — cargar_casos.py creó un caso duplicado por una edición directa no reflejada"
aliases:
  - "tokmd BUG-006"
project: tokmd
document_type: bug
status: fixed
version: 1.0.0
created: 2026-09-26
updated: 2026-09-26
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-sonnet-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-sonnet-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-sonnet-5 / Claude Code / subscription"
reviewed_by: "pending"
review_status: "pending"
tags:
  - project/tokmd
  - bug
related_documents:
  - "[[PBI-006-verificacion-contra-api]]"
---

# BUG-006 — `cargar_casos.py` creó un caso duplicado por una edición directa no reflejada

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-26 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación retroactiva — incidente del 2026-09-25, documentado sólo en el dev-log hasta ahora. |

## 1. Clasificación

- **Título:** al recargar `cargar_casos.py` para agregar los 4 casos nuevos de
  PBI-006, se creó sin querer un caso duplicado (id 360) de `TOK-003-C02` con
  el texto viejo ("sin deriva").
- **Estado:** `fixed`.
- **Tipo:** `data-defect` — dato duplicado en Kiwi, no un defecto de `tokmd`.
- **Severidad:** `4-low` — detectado y corregido en la misma sesión, sin
  impacto fuera de Kiwi.
- **PBI relacionado:** [[PBI-006-verificacion-contra-api]] (aparece durante la
  carga de sus casos), pero el caso duplicado pertenecía a PBI-003.
- **Caso de Kiwi relacionado:** TOK-003-C02 (el caso real, no el duplicado, ya
  borrado).
- **Reportado por:** Desarrollo, mismo día.
- **Fecha de detección:** 2026-09-25.

## 2. Contexto reproducible

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`, script
  `tools/kiwi/cargar_casos.py` — idempotente por diseño, filtra por `summary`
  antes de crear.

## 3. Reproducción

1. Se corrige el texto de `TOK-003-C02` directamente en Kiwi vía
   `actualizar_caso.py` (edición puntual, sin tocar `cargar_casos.py`).
2. `CASOS` en `cargar_casos.py` sigue con el texto viejo.
3. Al recargar `cargar_casos.py` (para agregar los casos de PBI-006), el
   filtro por `summary` no encuentra coincidencia con el texto viejo que
   sigue en `CASOS` (porque en Kiwi el summary real ya cambió), y crea un
   caso nuevo en vez de actualizar el existente.

## 4. Impacto

Un caso duplicado (id 360) quedó en Kiwi, PROPOSED, sin ninguna Test Execution
asociada — detectado antes de que entrara a ningún Test Run.

## 5. Evidencia

`docs/dev-log/2026-09-24.md`, sección "Duplicado propio en Kiwi, corregido".

## 6. Causa

Cualquier edición directa a un caso vía `actualizar_caso.py` (fuera del flujo
normal de `cargar_casos.py`) rompe la idempotencia del filtro por `summary` de
`cargar_casos.py`, porque éste compara contra el texto que él mismo tiene
hardcodeado en `CASOS`, no contra el estado real en Kiwi.

## 7. Corrección

`CASOS` actualizado con el texto correcto de `TOK-003-C02`. Caso 360 verificado
como PROPOSED, sin ninguna Test Execution, antes de borrarlo
(`tools/kiwi/borrar_caso_duplicado.py`). Confirmado que PBI-003 vuelve a tener
exactamente 3 casos. Lección aplicada desde entonces: cualquier edición
directa a un caso tiene que reflejarse también en `cargar_casos.py`, o la
próxima carga idempotente lo duplica.

## 8. Verificación independiente

- **Verificado por:** Desarrollo, contando los casos de PBI-003 después del
  borrado (exactamente 3, sin duplicados).
- **Evidencia:** `docs/dev-log/2026-09-24.md`, sección citada arriba.
