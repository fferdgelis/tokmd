---
title: "PBI-004 — CLI y flag de plataforma"
aliases:
  - "tokmd PBI-004"
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

# PBI-004 — CLI y flag de plataforma

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |

## 1. Valor y contexto

- **Problema:** el usuario no debe tener que saber qué tokenizador usa cada plataforma; sólo elige la plataforma.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** `tokmd FILE --platform <p>` resuelve automáticamente el tokenizador.
- **Prioridad:** alta, es la interfaz pública.
- **Hipótesis:** un mapeo fijo de plataforma a tokenizador (con excepción de OpenCode, que depende de `--model`) cubre los casos reales de uso.

### Historia de usuario

> Como usuario de Claude Code, quiero correr `tokmd CLAUDE.md` sin flags y obtener el conteo correcto de Claude, para no tener que saber qué encoding usar.

## 2. Corte de entrega

- **Incluye:** flags `--platform`, `--model`, `--tokenizer`, `--claude-family`, `--encoding`, `--depth`, `--sort`; mapeo de plataforma; validación de errores (opencode sin `--model`, antigravity no soportado).
- **No incluye:** `--verify` (PBI-006), formatos de salida (PBI-005, mismo módulo CLI pero criterios separados).
- **Dependencias:** PBI-001, PBI-002, PBI-003.
- **Riesgos:** ambigüedad si `--platform` y `--tokenizer` se contradicen (se resuelve documentando que `--tokenizer` gana).

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado `--platform claude-code` sin más flags, cuando se corre, entonces usa Claude familia 4.8.
- [ ] **AC-02:** Dado `--platform codex`, cuando se corre, entonces usa OpenAI `o200k_base`.
- [ ] **AC-03:** Dado `--platform opencode` sin `--model`, cuando se corre, entonces falla con un mensaje de error claro (no una excepción cruda).
- [ ] **AC-04:** Dado `--platform opencode --model claude-opus-5`, cuando se corre, entonces usa el tokenizador de Claude.
- [ ] **AC-05:** Dado `--platform antigravity`, cuando se corre, entonces sale con código 2 y el mensaje «Gemini tokenizer: planned for 1.1».

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/cli.py`.
- **Herramientas disponibles:** `click`.
- **Métricas:** cobertura ≥ 80 %, tests con `click.testing.CliRunner`.
- **ADR requerido:** `[[ADR-001-eleccion-de-motores-de-tokenizacion]]`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [x] ADR enlazado.
- [ ] Casos de Kiwi cargados como PROPOSED.

**Estado:** `not ready`

### Handoff a TDD

- **AC a convertir en pruebas:** AC-01 a AC-05 con `CliRunner`.

### Handoff a Desarrollo

- **Restricciones confirmadas:** mensajes de error en inglés (CLI pública).

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** `tools/kiwi/resultados/fase-3.json`.

## 6. Cierre

- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** PBI-005.
