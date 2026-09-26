---
title: "PBI-001 — Parser de secciones en árbol"
aliases:
  - "tokmd PBI-001"
project: tokmd
document_type: pbi
status: proposed
version: 0.2.0
created: 2026-09-24
updated: 2026-09-25
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
  - "[[PBI_TEMPLATE]]"
---

# PBI-001 — Parser de secciones en árbol

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Cerrado: código+tests (ADR-006)+gate Sonar+QA en Kiwi, los cinco casos PASSED. |

## 1. Valor y contexto

- **Problema:** tokmd necesita partir un archivo Markdown en un árbol de secciones antes de poder contar tokens por sección.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** módulo `sections.py` que devuelve un árbol con front matter, preámbulo y encabezados anidados.
- **Prioridad:** alta, es la base de todo lo demás.
- **Hipótesis:** `markdown-it-py` alcanza para detectar encabezados por nivel e ignorar los que están dentro de bloques de código.

### Historia de usuario

> Como usuario de tokmd, quiero ver mi archivo partido en secciones anidadas, para saber qué parte pesa más en tokens.

## 2. Corte de entrega

- **Incluye:** parseo de front matter YAML, preámbulo, árbol de encabezados con niveles arbitrarios y saltos de nivel tolerados.
- **No incluye:** cálculo de tokens (PBI-002/003), CLI (PBI-004).
- **Dependencias:** ninguna.
- **Riesgos:** archivos con encabezados dentro de bloques de código o HTML embebido.

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado un archivo con front matter YAML, cuando se parsea, entonces aparece una fila `(front matter)` con su texto completo.
- [ ] **AC-02:** Dado texto antes del primer encabezado, cuando se parsea, entonces aparece una fila `(preamble)`.
- [ ] **AC-03:** Dado un salto de nivel (`##` seguido de `####`), cuando se parsea, entonces el nodo hijo cuelga del ancestro de nivel inmediatamente menor sin error.
- [ ] **AC-04:** Dado un `#` dentro de un bloque ```` ``` ````, cuando se parsea, entonces no se trata como encabezado.
- [ ] **AC-05:** Dado un archivo sin encabezados o vacío, cuando se parsea, entonces se devuelve un árbol válido sin excepción.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/sections.py`.
- **Herramientas disponibles:** `markdown-it-py`, `pytest`.
- **Métricas:** cobertura del módulo ≥ 80 % (gate Sonar).
- **ADR requerido:** `[[ADR-003-parseo-de-secciones]]`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [x] ADR enlazado.
- [ ] Casos de Kiwi cargados como PROPOSED.

**Estado:** `not ready` (falta carga en Kiwi, Fase 0)

### Handoff a TDD

- **AC a convertir en pruebas:** AC-01 a AC-05, más fixtures en `tests/fixtures/`.

### Handoff a Desarrollo

- **Restricciones confirmadas:** árbol completo, no corte plano.

### Handoff a QA

- **Candidato identificable:** commit corto del snapshot al cerrar la fase.
- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** log crudo + resultado por caso `TOK-001-C*` en `tools/kiwi/resultados/fase-1.json`.

## 6. Cierre

- **Artefactos y enlaces:** `src/tokmd/sections.py`, `tests/test_sections.py` (autoría DeepSeek, ADR-006), Test Run Kiwi id=61, gate Sonar OK (`C:\IA\Data\sonarqube\reports\tokmd\20260925-024139\`), respuesta cruda de QA en `docs/handoff/qa/fase-1-kimi-k3.txt`.
- **Resultado de QA independiente:** `accepted` — 5/5 casos PASSED (Kimi K3/OpenCode, read-only sobre snapshot del commit `6be061d`, 25/09/2026).
- **Aceptación del owner:** `pending`.
- **Bugs de instrumento encontrados durante el retrofit de TDD/Sonar, sin
  registro formal hasta el 2026-09-26:** [[BUG-003-deepseek-thinking-trunca-respuesta-tdd]],
  [[BUG-004-get-codefrommarkdown-corta-primer-fence]],
  [[BUG-005-sonargate-ps7-getresponsestream]] — ninguno era un defecto de
  `tokmd`, los tres eran de tooling (DeepSeek, Sonar), corregidos el mismo día.
- **PBI o Bug siguiente:** PBI-002.
