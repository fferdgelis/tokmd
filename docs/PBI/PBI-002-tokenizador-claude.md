---
title: "PBI-002 — Tokenizador Claude (ctok + marco medido)"
aliases:
  - "tokmd PBI-002"
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
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
---

# PBI-002 — Tokenizador Claude (ctok + marco medido)

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Desarrollo y TDD real cerrados (ADR-006 aplicado de punta a punta). Canario de Sonar bloqueado por permisos de la instancia. QA de Kiwi pendiente. |

## 1. Valor y contexto

- **Problema:** contar tokens de Claude por sección sin red ni API key.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** función que cuenta tokens de Claude por familia (3, 4.7, 4.8) restando el marco del mensaje.
- **Prioridad:** alta.
- **Hipótesis:** `FRAME = ctok.token_count("", version)` es estable por familia y se puede restar sin perder precisión relevante.

### Historia de usuario

> Como usuario de tokmd, quiero el conteo de tokens de Claude de cada sección, para saber qué recortar del archivo.

## 2. Corte de entrega

- **Incluye:** medición de `FRAME` por familia, función `count_claude(text, family)`, detección de deriva de borde.
- **No incluye:** `--verify` contra la API (PBI-006).
- **Dependencias:** PBI-001 (necesita el árbol para tener texto por sección).
- **Riesgos:** `ctok` puede no modelar exactamente el espacio final en blanco de Opus 5 (limitación que el propio paquete declara).

## 3. Criterios de aceptación

- [x] **AC-01:** Dado un texto vacío, cuando se mide `FRAME` por familia, entonces el valor queda documentado en `docs/investigation/20260924-ctok-marco-y-deriva.md`.
- [x] **AC-02:** Dado el archivo completo y la suma de sus secciones, cuando se comparan, entonces la deriva (si existe) se reporta explícitamente, no se oculta.
- [x] **AC-03:** Dado `--claude-family 3|4.7|4.8`, cuando se cuenta el mismo texto, entonces los tres valores son distintos y consistentes con lo documentado por Anthropic (~30 % más desde 4.7).

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/tokenizers.py`.
- **Herramientas disponibles:** `ctok>=1.3`.
- **Métricas:** cobertura ≥ 80 %.
- **ADR requerido:** `[[ADR-001-eleccion-de-motores-de-tokenizacion]]`, `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [x] ADR enlazado.
- [x] Casos de Kiwi cargados como PROPOSED (ids 340-359, junto con PBI-001 a 005).

**Estado:** `ready` — desarrollo y TDD cerrados; QA de Kiwi bloqueada por el mismo
pendiente ya anotado en PBI-001: los casos siguen PROPOSED, Fabián no los promovió
a CONFIRMED todavía.

### Handoff a TDD

- **AC a convertir en pruebas:** valores dorados de `FRAME` por familia, congelados con la versión de `ctok` usada.

### Handoff a Desarrollo

- **Restricciones confirmadas:** ninguna llamada de red en el camino por defecto.

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Evidencia mínima:** `tools/kiwi/resultados/fase-2.json`.

## 6. Cierre

- **Resultado de QA independiente:** `PASSED` (3/3). Kimi K3/OpenCode, snapshot
  commit `a6a7974`, Kiwi Test Run [62]. Evidencia cruda en
  `docs/handoff/qa/fase-2-pbi002-kimi-k3.txt`.
- **Aceptación del owner:** `pending`.
- **Canario de Sonar (punto 2 de las correcciones del traspaso):** construido y
  **verde** (`tools/sonarqube/Test-QualityGateFailure.ps1`,
  `baseline=0, scanner=3, gate=ERROR`, evidencia en
  `C:\IA\Data\sonarqube\reports\tokmd-negative-gate\negative-20260925T072245Z.json`).
  Bloqueado primero por permisos de la instancia (el `automation-token` no tenía
  `admin` sobre proyectos nuevos); Fabián se lo otorgó el 2026-09-25 y quedó resuelto.
  Detalle en `docs/dev-log/2026-09-24.md`.
- **PBI o Bug siguiente:** PBI-003.
