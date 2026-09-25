---
title: "PBI-008 — Medición final del CLAUDE.md global con tokmd"
aliases:
  - "tokmd PBI-008"
project: tokmd
document_type: pbi
status: proposed
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
tags:
  - project/tokmd
  - delivery/pbi
related_documents:
  - "[[20260924-tokenizadores-por-plataforma]]"
---

# PBI-008 — Medición final del CLAUDE.md global con tokmd

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |

## 1. Valor y contexto

- **Problema:** la medición del 20/09 midió tokens de OpenAI (`cl100k_base`) para un archivo que sólo lee Claude.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** medición corregida en tokens de Claude, publicada como cierre visible de todo el proyecto.
- **Prioridad:** alta, es la razón original del pedido de esta sesión.
- **Hipótesis:** el ranking relativo de secciones (qué pesa más) se mantiene parecido, pero el número absoluto cambia sustancialmente.

### Historia de usuario

> Como Fabián, quiero saber cuántos tokens de Claude cuesta realmente mi CLAUDE.md global, para decidir qué recortar con el número correcto.

## 2. Corte de entrega

- **Incluye:** correr `tokmd ~/.claude/CLAUDE.md --platform claude-code --verify` y `--platform codex`; actualizar `framework-multi-ai/docs/reference/MEDICION-CLAUDE-MD-GLOBAL.md` a v0.2.0.
- **No incluye:** decidir qué recortar (eso es de Fabián, con el dato correcto en mano).
- **Dependencias:** tokmd publicado y funcionando (PBI-007).
- **Riesgos:** ninguno técnico; el resultado puede ser incómodo si el archivo pesa más de lo esperado en tokens de Claude.

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado el CLAUDE.md global, cuando se mide con `--platform claude-code --verify`, entonces la tabla resultante reemplaza la de `MEDICION-CLAUDE-MD-GLOBAL.md` con nota explícita de que la anterior (9.359) era `cl100k_base`, no Claude.
- [ ] **AC-02:** Dado el mismo archivo, cuando se mide con `--platform codex`, entonces el número queda registrado como referencia de comparación, no como el dato principal.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer` (ejecuta) y `C:\IA\Projects\framework-multi-ai` (actualiza el doc de destino).
- **Módulo/archivo principal:** ninguno nuevo; uso de la CLI ya publicada.
- **ADR requerido:** `none`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [ ] tokmd publicado y verificado (depende de PBI-007).

**Estado:** `blocked` (depende de PBI-007)

### Handoff a TDD

- No aplica: es medición, no desarrollo de tokmd.

### Handoff a Desarrollo

- No aplica.

### Handoff a QA

- **Canal de QA:** revisión manual de Fabián sobre el documento actualizado.

## 6. Cierre

- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** ninguno; cierra el alcance de hoy.
