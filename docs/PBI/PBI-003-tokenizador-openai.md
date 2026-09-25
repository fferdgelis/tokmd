---
title: "PBI-003 — Tokenizador OpenAI (tiktoken)"
aliases:
  - "tokmd PBI-003"
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
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
---

# PBI-003 — Tokenizador OpenAI (tiktoken)

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |

## 1. Valor y contexto

- **Problema:** contar tokens para Codex/OpenAI con el encoding correcto (`o200k_base`, no `cl100k_base` por defecto).
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** función `count_openai(text, encoding)` aditiva y exacta.
- **Prioridad:** media (más simple que Claude, sirve de control).
- **Hipótesis:** `tiktoken` es exacto y aditivo sin marco que restar.

### Historia de usuario

> Como usuario de Codex, quiero contar tokens con el mismo encoding que usa mi modelo, para no repetir el error del 20/09 (medir con `cl100k_base` en vez de `o200k_base`).

## 2. Corte de entrega

- **Incluye:** `count_openai`, mapeo de modelo a encoding (`o200k_base` para gpt-5/gpt-4o, `cl100k_base` disponible por override).
- **No incluye:** detección automática de todos los modelos de OpenAI existentes.
- **Dependencias:** PBI-001.
- **Riesgos:** ninguno relevante; es la vía más simple del proyecto.

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado un texto, cuando se cuenta con `o200k_base`, entonces el resultado es exacto y determinista.
- [ ] **AC-02:** Dado el mismo texto partido en secciones, cuando se suman los conteos, entonces la suma es exactamente igual al conteo del texto completo (sin deriva, a diferencia de Claude).
- [ ] **AC-03:** Dado `--encoding cl100k_base`, cuando se cuenta, entonces el resultado reproduce lo que hubiera dado `ttok -m gpt-4` el 20/09.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/tokenizers.py` (mismo módulo que PBI-002).
- **Herramientas disponibles:** `tiktoken>=0.14`.
- **Métricas:** cobertura ≥ 80 %.
- **ADR requerido:** `[[ADR-001-eleccion-de-motores-de-tokenizacion]]`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [x] ADR enlazado.
- [ ] Casos de Kiwi cargados como PROPOSED.

**Estado:** `not ready`

### Handoff a TDD

- **AC a convertir en pruebas:** valores dorados exactos (deterministas, sin necesidad de congelar versión).

### Handoff a Desarrollo

- **Restricciones confirmadas:** ninguna.

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** `tools/kiwi/resultados/fase-2.json` (comparte fase con PBI-002).

## 6. Cierre

- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** PBI-004.
