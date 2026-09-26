---
title: "BUG-003 — Invoke-DeepSeekChat sin -DisableThinking trunca la respuesta de TDD"
aliases:
  - "tokmd BUG-003"
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
---

# BUG-003 — `Invoke-DeepSeekChat` sin `-DisableThinking` trunca la respuesta de TDD

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-26 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación retroactiva — incidente del 2026-09-24/25 (retrofit de PBI-001), documentado sólo en el dev-log hasta ahora. |

## 1. Clasificación

- **Título:** `Invoke-DeepSeekChat` (módulo compartido `C:\IA\modulo-conexion-deepseek`)
  sin `-DisableThinking` gasta el presupuesto de `max_tokens` en
  `reasoning_content` (razonamiento visible) antes de terminar la respuesta —
  el test que TDD tenía que escribir (AC-04 de PBI-001) quedó cortado a mitad.
- **Estado:** `fixed`.
- **Tipo:** `harness-defect` — no es un bug de `tokmd`, es un patrón de uso del
  conector compartido de DeepSeek que rompe con specs largas.
- **Severidad:** `3-medium` — no bloqueó el proyecto, pero costó dos llamadas
  pagas repetidas antes de identificar la causa real.
- **PBI relacionado:** [[PBI-001-parser-de-secciones]] (retrofit de TDD real,
  ADR-006).
- **Caso de Kiwi relacionado:** ninguno directo — es un defecto de la
  herramienta de invocación de TDD (`tools/deepseek/Invoke-TddDeepSeek.ps1`),
  no de un caso funcional de `tokmd`.
- **Reportado por:** Desarrollo, en esta sesión de retrofit.
- **Fecha de detección:** 2026-09-24/25.

## 2. Contexto reproducible

- **Build/commit:** retrofit de PBI-001, previo a `6be061d`.
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Precondiciones:** llamada a `Invoke-DeepSeekChat` con una spec que pide un
  test de AC-04 (bloque de código embebido), sin `-DisableThinking`.

## 3. Reproducción

Con `MaxTokens=8192` la respuesta cortó a mitad de AC-04. Subir a `16000` sin
tocar el razonamiento cortó exactamente en el mismo punto — el `reasoning_content`
crecía para llenar el presupuesto disponible, no importa cuánto se suba el techo.

## 4. Impacto

Dos llamadas pagas (aunque de costo bajo, centavos) se perdieron antes de dar
con la causa real. Es la segunda vez que aparece el mismo síntoma en la sesión
(regla del 23/09 del CLAUDE.md global: parar y verificar con datos antes de un
tercer intento a ciegas) — se verificó la causa real con los propios campos de
`Invoke-DeepSeekChat` (`reasoning_length`, `completion_tokens`) antes de aplicar
el fix, no se adivinó.

## 5. Evidencia

`docs/dev-log/2026-09-24.md`, sección "Retrofit de PBI-001: dos bugs de
instrumento encontrados y corregidos", punto 1: con `-DisableThinking`,
`reasoning_length=0` y la respuesta completa en 718-871 tokens.

## 6. Causa

El modelo subyacente (DeepSeek) con `thinking` habilitado escribe su
razonamiento visible dentro del mismo presupuesto de `max_tokens` que la
respuesta final — con specs largas (como la de AC-04, que pide un bloque de
código de ejemplo embebido), el razonamiento solo puede consumir todo el
presupuesto antes de llegar al bloque de código.

## 7. Corrección

Usar `-DisableThinking` en `Invoke-DeepSeekChat` para tareas mecánicas de
generación desde una spec precisa — ya documentado como regla general en el
CLAUDE.md global ("`Invoke-DeepSeekChat` con `thinking` habilitado puede
truncar la respuesta..."). Aplicado en
`tools/deepseek/Invoke-TddDeepSeek.ps1` desde el principio del proyecto.

## 8. Verificación independiente

- **Verificado por:** Desarrollo, con los campos de diagnóstico propios de la
  llamada (no una corrida de QA — es un defecto de tooling, no de producto).
- **Evidencia:** `docs/dev-log/2026-09-24.md`, sección citada arriba.
