---
title: "PBI-008 — Medición final del CLAUDE.md global con tokmd"
aliases:
  - "tokmd PBI-008"
project: tokmd
document_type: pbi
status: done
version: 0.2.0
created: 2026-09-24
updated: 2026-09-25
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-sonnet-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-sonnet-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-sonnet-5 / Claude Code / subscription"
reviewed_by: "opencode-kimi-k3"
review_status: "passed"
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
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Cierre: `--verify` cableado en `cli.py` (no existía, ver sección 4), BUG-001 encontrado y corregido en el camino, medición real corrida y `MEDICION-CLAUDE-MD-GLOBAL.md` actualizado a v0.2.0. |

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

- [x] **AC-01:** Dado el CLAUDE.md global, cuando se mide con `--platform claude-code --verify`, entonces la tabla resultante reemplaza la de `MEDICION-CLAUDE-MD-GLOBAL.md` con nota explícita de que la anterior (9.359) era `cl100k_base`, no Claude. **Resultado: 15877 tokens de Claude** (`claude-sonnet-5`), contra 677 líneas actuales del archivo (creció de 547 desde la medición vieja).
- [x] **AC-02:** Dado el mismo archivo, cuando se mide con `--platform codex`, entonces el número queda registrado como referencia de comparación, no como el dato principal. **Resultado: 9852 tokens** (`o200k_base`), anotado como referencia, no como dato principal.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer` (ejecuta) y `C:\IA\Projects\framework-multi-ai` (actualiza el doc de destino,
  ruta real `docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md` —
  la ruta de esta sección, `docs/reference/...`, estaba mal desde la creación
  de este PBI).
- **Módulo/archivo principal:** `src/tokmd/cli.py` — a diferencia de lo que decía esta sección, **`--verify` no existía todavía** en la CLI publicada (PBI-006 escribió `verify.py` pero nunca lo cableó, PBI-007 lo dejó pendiente). Cableado en esta sesión, con TDD real (ADR-006): firma vacía → spec para DeepSeek → `tests/test_cli_verify.py` (rojo confirmado) → implementado → verde. Detalle en `docs/dev-log/2026-09-25.md`.
- **BUG-001** ([[BUG-001-espacio-en-blanco-rechazado-por-count-tokens]]): encontrado corriendo `--verify` contra la API real por primera vez — `measure_frame` y `count_verified` podían mandar contenido de puro espacio en blanco, que la API rechaza con `400`. Corregido en dos puntos (el marco interno, y las secciones con texto en blanco de un documento real). Los tests con cliente falso de PBI-006 nunca lo hubieran detectado, por diseño (ADR-006 prohíbe red real en tests).
- **ADR requerido:** `none`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] tokmd publicado y verificado (PBI-007, `v1.0.0` en PyPI).

**Estado:** `done`.

### Handoff a TDD

- Sí aplica, a diferencia de lo que decía esta sección: el cableado de
  `--verify` sí necesitó desarrollo nuevo (ver sección 4). TDD por DeepSeek,
  spec en `tools/deepseek/specs/PBI-008-verify.md.prompt`.

### Handoff a Desarrollo

- Cableado de `--verify` en `cli.py`, corrección de BUG-001, medición real.

### Handoff a QA

- **Canal de QA:** Kimi K3 / OpenCode, sobre un snapshot sin red (5 casos
  nuevos del cableado de `--verify`, TOK-008-C01..C05). La medición real
  contra el `CLAUDE.md` global en sí — el objetivo del PBI — la corrió
  Desarrollo con la API real (no es algo que QA pueda repetir sin red, mismo
  criterio que AC-01 de PBI-007); revisión manual de Fabián sobre el
  documento actualizado sigue siendo el paso final.

## 6. Cierre

- **Resultado de QA independiente:** `PASSED` (5/5). Kimi K3/OpenCode,
  snapshot commit `bfed82b`, Kiwi Test Run [68] (ejecuciones 249-253).
  Evidencia cruda en `docs/handoff/qa/fase-5-pbi008-verify-kimi-k3.txt`.
- **Medición real, corrida por Desarrollo:** `docs/dev-log/2026-09-25.md` y
  `framework-multi-ai/docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md`
  v0.2.0 (**sin commitear** — esa rama de `framework-multi-ai` tiene otra
  sesión trabajando en vivo, ver el dev-log).
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** ninguno formal; PBI-008 sigue como el último de la
  lista original. [[BUG-001-espacio-en-blanco-rechazado-por-count-tokens]] es
  el único hallazgo abierto que quedó de este cierre, y ya está corregido.
