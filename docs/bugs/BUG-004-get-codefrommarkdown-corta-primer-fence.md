---
title: "BUG-004 — Get-CodeFromMarkdown corta en el primer fence de cierre"
aliases:
  - "tokmd BUG-004"
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
  - "[[PBI-001-parser-de-secciones]]"
  - "[[BUG-003-deepseek-thinking-trunca-respuesta-tdd]]"
---

# BUG-004 — `Get-CodeFromMarkdown` corta en el primer fence de cierre

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-26 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación retroactiva — incidente del 2026-09-24/25 (retrofit de PBI-001), documentado sólo en el dev-log hasta ahora. |

## 1. Clasificación

- **Título:** `Get-CodeFromMarkdown` (módulo compartido
  `C:\IA\modulo-conexion-deepseek`) usa una regex no-greedy (`(.*?)`) que corta
  en el **primer** ` ``` ` que encuentra, en vez del último.
- **Estado:** `fixed` (evitado en el wrapper propio de este proyecto, sin tocar
  el módulo compartido).
- **Tipo:** `harness-defect`.
- **Severidad:** `3-medium` — rompe cualquier test generado que necesite un
  bloque de código de ejemplo embebido dentro de sí mismo.
- **PBI relacionado:** [[PBI-001-parser-de-secciones]].
- **Caso de Kiwi relacionado:** ninguno directo — defecto de tooling, no de
  `tokmd`.
- **Reportado por:** Desarrollo, retrofit de PBI-001.
- **Fecha de detección:** 2026-09-24/25.

## 2. Contexto reproducible

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Precondiciones:** el test de AC-04 de PBI-001 necesita, por definición, un
  bloque de código de ejemplo embebido (para probar que un `#` dentro de un
  fence no se detecta como encabezado) — ese fence de apertura interno es
  justo lo que la regex no-greedy toma como el cierre del bloque completo.

## 3. Reproducción

Pasar por `Get-CodeFromMarkdown` una respuesta de LLM que contiene un bloque de
código externo (el test completo) con un fence embebido adentro (el fixture de
ejemplo) corta el resultado en el primer ` ``` ` interno, no en el real cierre
al final de la respuesta.

## 4. Impacto

El test de AC-04 generado por DeepSeek se hubiera truncado silenciosamente al
extraerlo, aunque la respuesta completa del modelo fuera correcta.

## 5. Evidencia

`docs/dev-log/2026-09-24.md`, sección "Retrofit de PBI-001: dos bugs de
instrumento encontrados y corregidos", punto 2.

## 6. Causa

`(.*?)` no-greedy en el módulo compartido toma la coincidencia más corta
posible — el primer ` ``` ` de cierre que encuentra, sin considerar que el
contenido entre medio pueda tener sus propios fences.

## 7. Corrección

No se tocó el módulo compartido (evitar romper otros proyectos que lo usan).
Extracción propia en `tools/deepseek/Invoke-TddDeepSeek.ps1`: desde el primer
fence de apertura hasta el **último** ` ``` ` de toda la respuesta.

## 8. Verificación independiente

- **Verificado por:** Desarrollo — confirmado corriendo el test de AC-04
  generado completo, sin truncar, contra la implementación real.
- **Evidencia:** `docs/dev-log/2026-09-24.md`, sección citada arriba; 8/8 tests
  verdes tras el fix (`tools/deepseek/specs/PBI-001-gap-01.md.prompt`).
