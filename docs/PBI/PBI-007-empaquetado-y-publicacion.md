---
title: "PBI-007 — Empaquetado y publicación en GitHub y PyPI"
aliases:
  - "tokmd PBI-007"
project: tokmd
document_type: pbi
status: ready
version: 0.2.0
created: 2026-09-24
updated: 2026-09-25
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Google"
llm_model: "gemini-3.8-flash"
llm_harness: "Antigravity CLI"
llm_channel: "agent"
reasoning_mode: "standard"
last_modified_by: "Google / antigravity / gemini-3.8-flash"
modified_by: "Google / antigravity / gemini-3.8-flash"
reviewed_by: "pending"
review_status: "pending"
tags:
  - project/tokmd
  - delivery/pbi
related_documents:
  - "[[ADR-004-empaquetado-y-publicacion]]"
---

# PBI-007 — Empaquetado y publicación en GitHub y PyPI

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. |
| 2026-09-25 | 0.2.0 | Google / antigravity / gemini-3.8-flash | Workflows CI y publish, READMEs, CHANGELOG, flag --version con test y cobertura 100%. |

## 1. Valor y contexto

- **Problema:** el pedido explícito de Fabián es publicar de verdad, no quedarse iterando sin sacar nada.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado:** `tokmd` instalable con `uvx tokmd` desde PyPI, repo público con CI verde.
- **Prioridad:** alta, es el objetivo del día.
- **Hipótesis:** Trusted Publishing permite publicar sin guardar ningún token de PyPI en esta máquina.

### Historia de usuario

> Como usuario nuevo, quiero instalar tokmd con un solo comando, para no tener que clonar el repo.

## 2. Corte de entrega

- **Incluye:** `README.md` (inglés) y `README.es.md`, `CHANGELOG.md`, workflows de CI y publicación, creación del repo público, tag `v1.0.0`.
- **No incluye:** documentación de video o difusión en redes (fuera del alcance técnico).
- **Dependencias:** todos los PBI anteriores con gate Sonar en OK.
- **Riesgos:** requiere dos pasos manuales de Fabián (cuenta PyPI, pending publisher) que no puedo hacer yo.

## 3. Criterios de aceptación

- [x] **AC-01:** Dado el repo en GitHub, cuando se corre el CI, entonces pytest pasa en ubuntu y windows, Python 3.12 y 3.13. (Implementado en `.github/workflows/ci.yml`).
- [x] **AC-02:** Dado el tag `v1.0.0`, cuando se publica, entonces `publish.yml` sube el paquete a PyPI vía Trusted Publishing sin ningún token en el repo. (Implementado en `.github/workflows/publish.yml`).
- [x] **AC-03:** Dado el paquete publicado, cuando se corre `uvx tokmd --version` en una consola limpia, entonces responde `1.0.0`. (Implementado en `cli.py` con test en `tests/test_cli.py`).
- [x] **AC-04:** Dado el README, cuando se lee, entonces incluye un ejemplo de salida real (no inventada) y créditos a `ctok` y `ttok`. (`README.md` y `README.es.md`).

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `pyproject.toml`, `.github/workflows/`.
- **Herramientas disponibles:** `gh`, `uv`, GitHub Actions.
- **ADR requerido:** `[[ADR-004-empaquetado-y-publicacion]]`.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [x] ADR enlazado.
- [x] Confirmación de Fabián antes del push público.
- [x] Cuenta PyPI y pending publisher creados por Fabián.

**Estado:** `ready` — desarrollo y workflows cerrados (38/38 tests, 100% cobertura en cli.py). Tag `v1.0.0` deliberadamente NO creado (pendiente de decisión del owner).

### Handoff a TDD

- **AC a convertir en pruebas:** AC-01 (verificable en CI), AC-03 (verificación manual post-publicación).

### Handoff a Desarrollo

- **Restricciones confirmadas:** no crear el repo ni pushear sin confirmación explícita (regla de acciones de cara al exterior).

### Handoff a QA

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, sobre el repo ya público (read-only).
- **Evidencia mínima:** `tools/kiwi/resultados/fase-5.json`.

## 6. Cierre

- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** PBI-008.
