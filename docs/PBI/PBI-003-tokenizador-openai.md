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
  - "[[20260925-tiktoken-deriva]]"
---

# PBI-003 — Tokenizador OpenAI (tiktoken)

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Desarrollo y TDD cerrados. Hallazgo: la hipótesis de aditividad exacta era falsa (deriva de borde por fusión de BPE, medida y documentada); AC-02 corregido con confirmación de Fabián. |

## 1. Valor y contexto

- **Problema:** contar tokens para Codex/OpenAI con el encoding correcto (`o200k_base`, no `cl100k_base` por defecto).
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** función `count_openai(text, encoding)` aditiva y exacta.
- **Prioridad:** media (más simple que Claude, sirve de control).
- **Hipótesis:** `tiktoken` es exacto y sin marco que restar. **Corregido
  2026-09-25:** exacto sí, aditivo entre secciones NO — tiene su propia deriva de
  borde por fusión de BPE, medida en
  `docs/investigation/20260925-tiktoken-deriva.md`. La hipótesis original de
  aditividad perfecta era falsa.

### Historia de usuario

> Como usuario de Codex, quiero contar tokens con el mismo encoding que usa mi modelo, para no repetir el error del 20/09 (medir con `cl100k_base` en vez de `o200k_base`).

## 2. Corte de entrega

- **Incluye:** `count_openai`, mapeo de modelo a encoding (`o200k_base` para gpt-5/gpt-4o, `cl100k_base` disponible por override).
- **No incluye:** detección automática de todos los modelos de OpenAI existentes.
- **Dependencias:** PBI-001.
- **Riesgos:** ninguno relevante; es la vía más simple del proyecto.

## 3. Criterios de aceptación

- [x] **AC-01:** Dado un texto, cuando se cuenta con `o200k_base`, entonces el resultado es exacto y determinista.
- [x] **AC-02 (corregido 2026-09-25, ver `docs/investigation/20260925-tiktoken-deriva.md`):**
  Dado el mismo texto partido en secciones, cuando se suman los conteos, entonces
  la deriva contra el conteo del texto completo (si existe) se mide y se puede
  reportar — no se asume aditividad exacta. Medido: `tiktoken` también tiene
  deriva de borde (fusión de BPE), no es "sin deriva, a diferencia de Claude"
  como decía la hipótesis original.
- [x] **AC-03:** Dado `--encoding cl100k_base`, cuando se cuenta, entonces el resultado reproduce lo que hubiera dado `ttok -m gpt-4` el 20/09 (verificado: ambos rutean al mismo encoding `cl100k_base`).

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

**Estado:** `ready` — desarrollo y TDD cerrados (incluido el gap de AC-02). QA de
Kiwi pendiente de cargar los casos y de que Fabián los confirme (mismo bloqueo de
PBI-001/002).

### Handoff a TDD

- **AC a convertir en pruebas:** valores dorados exactos (deterministas, sin necesidad de congelar versión).

### Handoff a Desarrollo

- **Restricciones confirmadas:** ninguna.

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** `tools/kiwi/resultados/fase-2.json` (comparte fase con PBI-002).

## 6. Cierre

- **Resultado de QA independiente:** `PASSED` (3/3). Kimi K3/OpenCode, snapshot
  commit `185b269`, Kiwi Test Run [63]. Evidencia cruda en
  `docs/handoff/qa/fase-2-pbi003-kimi-k3.txt`. Caso `TOK-003-C02` corregido en
  Kiwi antes de correr QA (tenía la redacción vieja "sin deriva").
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** PBI-004.
