---
title: "PBI-005 — Render de salida (table/md/json/csv)"
aliases:
  - "tokmd PBI-005"
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
  - "[[ADR-003-parseo-de-secciones]]"
---

# PBI-005 — Render de salida (table/md/json/csv)

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Desarrollo y TDD cerrados, cableado en cli.py. |

## 1. Valor y contexto

- **Problema:** el árbol de secciones con tokens necesita presentarse en distintos formatos según el uso (lectura humana, pegar en Markdown, procesar con otra herramienta).
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** `--format table|md|json|csv` con la misma información en cada uno.
- **Prioridad:** media.
- **Hipótesis:** una sola estructura de datos intermedia (lista de filas con indentación) alcanza para los cuatro formatos.

### Historia de usuario

> Como usuario, quiero exportar el resultado a JSON para procesarlo con otro script, o a Markdown para pegarlo en un handoff.

## 2. Corte de entrega

- **Incluye:** los cuatro formatos, `--depth N` para limitar niveles mostrados, `--sort document|tokens`.
- **No incluye:** gráficos o visualizaciones.
- **Dependencias:** PBI-001, PBI-002, PBI-003.
- **Riesgos:** ninguno relevante.

## 3. Criterios de aceptación

- [x] **AC-01:** Dado `--format json`, cuando se corre, entonces la salida es JSON válido y parseable.
- [x] **AC-02:** Dado `--format table` (default), cuando se corre, entonces la indentación refleja el nivel de anidamiento.
- [x] **AC-03:** Dado `--depth 2`, cuando se corre, entonces sólo se muestran secciones hasta nivel 2, con sus totales acumulados intactos.
- [x] **AC-04:** Dado `--sort tokens`, cuando se corre, entonces las filas del mismo nivel se ordenan de mayor a menor token count.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/render.py`.
- **Herramientas disponibles:** biblioteca estándar (`json`, `csv`).
- **Métricas:** cobertura ≥ 80 %.
- **ADR requerido:** `[[ADR-003-parseo-de-secciones]]`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [x] ADR enlazado.
- [ ] Casos de Kiwi cargados como PROPOSED.

**Estado:** `ready` — desarrollo y TDD cerrados (33/33 tests, 100% cobertura).
Cableado en `cli.py`: `--format/--depth/--sort` ya funcionan de punta a punta.
QA de Kiwi pendiente.

### Handoff a TDD

- **AC a convertir en pruebas:** AC-01 a AC-04 sobre un árbol fijo de prueba.

### Handoff a Desarrollo

- **Restricciones confirmadas:** ninguna.

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** `tools/kiwi/resultados/fase-3.json` (comparte fase con PBI-004).

## 6. Cierre

- **Resultado de QA independiente:** `PASSED` (4/4). Kimi K3/OpenCode, snapshot
  commit `e80afc1`, Kiwi Test Run [65]. Evidencia cruda en
  `docs/handoff/qa/fase-3-pbi005-kimi-k3.txt`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** PBI-006.
