---
title: "PBI-006 — Verificación contra la API (--verify)"
aliases:
  - "tokmd PBI-006"
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

# PBI-006 — Verificación contra la API (--verify)

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |

## 1. Valor y contexto

- **Problema:** el usuario debe poder confirmar que el conteo offline de `ctok` es confiable para su archivo, sin tener que confiar ciegamente.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** `--verify` agrega columnas `API` y `Δ` llamando a `count_tokens` real.
- **Prioridad:** media, es la garantía de exactitud del proyecto.
- **Hipótesis:** el Δ entre `ctok` y la API es pequeño (≤ 1 %) para texto en español/inglés típico de archivos de instrucciones.

### Historia de usuario

> Como usuario que no confía en un conteo offline, quiero verificarlo contra la API real de Anthropic, para decidir con datos exactos qué recortar.

## 2. Corte de entrega

- **Incluye:** `verify.py` con `client.messages.count_tokens`, resta del marco medido con contenido mínimo, columna Δ por fila.
- **No incluye:** caché de resultados de verificación entre corridas.
- **Dependencias:** PBI-002, PBI-004, PBI-005.
- **Riesgos:** requiere `ANTHROPIC_API_KEY`; sin ella, error claro, no traceback.

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado `--verify` sin `ANTHROPIC_API_KEY` en el entorno, cuando se corre, entonces el error es legible y dice qué variable falta.
- [ ] **AC-02:** Dado `--verify` con key válida, cuando se corre sobre un archivo pequeño, entonces cada fila tiene su valor de API y su Δ.
- [ ] **AC-03:** Dado un cliente mockeado en tests, cuando se simula una respuesta, entonces `verify.py` no hace ninguna llamada de red real en la suite de tests.
- [ ] **AC-04 (mutante, paso 10 de los doce):** dado el parser de front matter roto a propósito, cuando corren los tests, entonces al menos un test falla y señala exactamente esa ruptura.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/verify.py`.
- **Herramientas disponibles:** `anthropic` (extra `tokmd[verify]`).
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

- **AC a convertir en pruebas:** AC-01 a AC-04, cliente Anthropic mockeado.

### Handoff a Desarrollo

- **Restricciones confirmadas:** nunca imprimir la API key.

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** `tools/kiwi/resultados/fase-4.json`, incluyendo la corrida real con `local/tokmd-verify.ps1` sobre el CLAUDE.md global.

## 6. Cierre

- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** PBI-007.
