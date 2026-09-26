---
title: "BUG-002 — QA de PBI-006 dio un FAILED falso por git status dentro de un snapshot sin .git"
aliases:
  - "tokmd BUG-002"
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

# BUG-002 — QA de PBI-006 dio un FAILED falso por `git status` dentro de un snapshot sin `.git`

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-26 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación retroactiva — el incidente ocurrió el 2026-09-25 durante el cierre de PBI-006, documentado sólo en prosa (dev-log/PBI) hasta ahora. Registrado a pedido explícito de Fabián: todo bug real tiene que quedar en Kiwi, no sólo narrado. |

## 1. Clasificación

- **Título:** el brief de QA le pedía a Kimi K3 correr `git status` como parte de la
  verificación de AC-04, dentro de un snapshot armado con `git archive` — que no
  tiene `.git`. El comando falló, y ese fallo se interpretó como FAILED del caso.
- **Estado:** `fixed` (brief corregido y QA re-corrida el mismo día, con el
  resultado que se registró como definitivo).
- **Tipo:** `test-defect` — no era un defecto de `tokmd`, era un defecto del
  instrumento de verificación (el brief que QA ejecuta).
- **Severidad:** `3-medium` — no bloqueó el cierre, pero costó una vuelta completa
  de QA repetida.
- **PBI relacionado:** [[PBI-006-verificacion-contra-api]].
- **Caso de Kiwi relacionado:** TOK-006-C04 (el caso de AC-04, mutante del parser
  de front matter), Test Execution 244, Run 66.
- **Reportado por:** Kimi K3/OpenCode (QA), primera vuelta; diagnosticado por
  Desarrollo el mismo día.
- **Fecha de detección:** 2026-09-25.

## 2. Contexto reproducible

- **Build/commit:** `65c6844` (PBI-006).
- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, sobre un snapshot de
  `git archive` (sin `.git`).
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Precondiciones:** el brief original de QA (versión 1) incluía un paso que le
  pedía a QA correr `git status` para comparar el estado del snapshot contra algo,
  sin considerar que un export de `git archive` no tiene directorio `.git`.

## 3. Reproducción

Correr `git status` (o cualquier comando `git`) dentro de un directorio creado con
`git archive <commit> | tar -x -C <dir>` (o el equivalente por zip) falla siempre,
porque no hay repositorio ahí — es un export de archivos, no un checkout.

## 4. Impacto

Una vuelta completa de QA de PBI-006 (Kimi K3, tiempo y costo real de la llamada)
se perdió por un chequeo mal diseñado, no por un defecto de `verify.py`/`sections.py`.
El caso quedó registrado como FAILED en la corrida real, antes de corregirse.

## 5. Evidencia

- `docs/PBI/PBI-006-verificacion-contra-api.md`, sección 6: "Primera vuelta dio un
  FAILED falso en AC-04 por un chequeo mal diseñado en el brief (`git status`
  dentro de un snapshot sin `.git`) — corregido y re-corrido, no era un defecto
  del código."
- La lección se aplicó explícitamente al revés en PBI-007 (AC-01, CI): ver
  `docs/dev-log/2026-09-25.md`, sección "AC-01: verificado en dos mitades, a
  propósito".

## 6. Causa

El brief de QA (`tools/qa/brief-qa-pbi006.md.prompt`, versión original) no
distinguía entre "verificar algo dentro del snapshot" y "verificar algo que
depende de tener un repositorio git real" — un snapshot de `git archive` es
deliberadamente un export sin historial, por diseño (ADR-005, aislamiento
read-only de QA), así que cualquier paso del brief que asuma `.git` está mal
diseñado desde el origen.

## 7. Corrección

Brief corregido para no pedir comandos `git` dentro del snapshot. QA re-corrida
el mismo día contra el mismo commit: 4/4 PASSED, veredicto final registrado en
Kiwi Run 66. La lección quedó como principio de diseño explícito para los
briefs siguientes (PBI-007 AC-01 la aplicó al revés: lo que necesita red/git
real lo verifica Desarrollo, no QA).

## 8. Verificación independiente

- **Verificado por:** Kimi K3/OpenCode, segunda corrida, mismo día.
- **Evidencia:** `docs/handoff/qa/fase-4-pbi006-kimi-k3.txt` (veredicto final,
  4/4 PASSED).
