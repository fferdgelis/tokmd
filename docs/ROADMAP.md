---
title: "Roadmap — fuera del alcance de la v1.0.0"
aliases:
  - "tokmd Roadmap"
project: tokmd
document_type: roadmap
status: active
version: 0.1.0
created: 2026-09-24
updated: 2026-09-24
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-fable-5-1"
llm_harness: "Claude Code Desktop"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription"
modified_by: "Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - roadmap
related_documents:
  - "[[20260924-tokenizadores-por-plataforma]]"
---

# Roadmap — fuera del alcance de la v1.0.0

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |

## v1.1 — Gemini / Antigravity

Tokenizador local de Google (`vertexai.preview.tokenization`) o `countTokens` por API.
Requiere `google-cloud-aiplatform[tokenization]` (pesado) o una key de AI Studio, que hoy
no existe en esta máquina. Ver `docs/investigation/20260924-tokenizadores-por-plataforma.md`.

## Sin fecha

- Truncado a N tokens, estilo `ttok -t N`.
- Ranking de varios archivos por consumo total.
- Diff de tokens entre dos versiones (dos commits) del mismo archivo.
- Filtro de secciones por nombre, más allá de `--depth`.
