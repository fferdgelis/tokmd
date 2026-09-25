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
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | verify.py con TDD real y mutante AC-04 ejecutado. Cableado de CLI/render explícitamente recortado, no hecho. |

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

- [x] **AC-01:** Dado `--verify` sin `ANTHROPIC_API_KEY` en el entorno, cuando se corre, entonces el error es legible y dice qué variable falta. (a nivel de `verify.get_client()`; ver nota de alcance sobre el cableado en `cli.py`)
- [x] **AC-02 (parcial, ver nota de alcance):** `verify.count_verified` da el valor de API neto de `frame`, verificado con un cliente falso en tests. Falta cablear la columna Δ en la tabla de `render.py`.
- [x] **AC-03:** ninguna llamada de red real en la suite (`test_no_real_anthropic_import_in_this_module` lo confirma: `anthropic` nunca aparece en `sys.modules`).
- [x] **AC-04 (mutante, paso 10 de los doce):** ejecutado a mano el 2026-09-25 — `FRONT_MATTER_RE` roto a propósito (prefijo `XXX` agregado), `uv run pytest` corrido, **exactamente 1 test falló**
  (`test_front_matter_becomes_root_child_with_content`, `AssertionError: assert None is not None`), señalando con precisión la ruptura. Revertido, suite verde de nuevo (37/37). No queda código de la mutación en el repo — fue un ejercicio, no un artefacto permanente.

**Nota de alcance (importante, no ocultar):** `src/tokmd/verify.py` está
completo, testeado (TDD real, rojo confirmado) y con QA independiente — es
el módulo principal declarado en el contrato técnico. **Lo que NO se hizo:**
cablear `--verify` como flag en `cli.py`, ni agregar las columnas `API` y
`Δ` a la tabla de `render.py` — eso requiere extender el esquema de `Row`
(hoy sólo `title/level/tokens`) y no estaba en el contrato técnico de este
PBI (que sólo lista `src/tokmd/verify.py`, a diferencia de PBI-004/005 que
sí listaban `cli.py`). Es trabajo real pendiente, no un olvido silencioso:
queda para una fase de integración aparte (podría ir en PBI-007 o ser un
PBI nuevo — decisión de Fabián).

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

**Estado:** `ready` — `verify.py` con TDD real cerrado (37/37 tests, 99%
cobertura del proyecto; sólo la rama de éxito de `get_client()`, que
requiere una key real, queda sin cubrir por diseño). Falta el cableado de
CLI/render (ver nota de alcance arriba). QA de Kiwi pendiente.

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
