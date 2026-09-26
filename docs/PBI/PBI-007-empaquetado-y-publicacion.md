---
title: "PBI-007 — Empaquetado y publicación en GitHub y PyPI"
aliases:
  - "tokmd PBI-007"
project: tokmd
document_type: pbi
status: ready
version: 0.3.0
created: 2026-09-24
updated: 2026-09-25
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-opus-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-opus-5 / Claude Code / subscription"
reviewed_by: "opencode-kimi-k3"
review_status: "passed"
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
| 2026-09-25 | 0.3.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Cierre de QA independiente: Kiwi Test Run 67, 4/4 PASSED (Kimi K3 sobre snapshot de `d90fb73`). Corregida la evidencia mínima del handoff a QA, que apuntaba a un archivo inexistente. |

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

- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only sobre un snapshot de
  `git archive` del commit gateado (no sobre el repo vivo).
- **Evidencia mínima:** `docs/handoff/qa/fase-4-pbi007-kimi-k3.txt` (salida cruda de
  QA) y `docs/handoff/qa/fase-4-pbi007-ci-github-actions.txt` (AC-01, verificado por
  Desarrollo porque el snapshot no tiene red). El brief usado es
  `tools/qa/brief-qa-pbi007.md.prompt`.

## 6. Cierre

- **Resultado de QA independiente:** `PASSED` (4/4). Kimi K3/OpenCode, snapshot
  commit `d90fb73`, Kiwi Test Run [67] (ejecuciones 245-248). Evidencia cruda en
  `docs/handoff/qa/fase-4-pbi007-kimi-k3.txt`.
  - **AC-01 se verificó en dos mitades, a propósito.** El snapshot de QA es un
    export de `git archive`: no tiene `.git` ni acceso a la API de GitHub, así
    que no puede consultar el run real. Desarrollo verificó el run
    (`36143105506`, SHA `d90fb73`, 4/4 jobs `success`) y se lo pasó a QA como
    dato ya verificado, con el número de run y el SHA para que sea auditable —
    evidencia en `docs/handoff/qa/fase-4-pbi007-ci-github-actions.txt`. QA
    verificó por su cuenta que `ci.yml` declara realmente esa matriz. Es la
    lección de PBI-006 aplicada al revés: ahí el brief le pidió a QA correr
    `git status` dentro de un snapshot sin `.git` y salió un FAILED falso.
  - AC-04 no se dio por bueno leyendo el README: QA re-corrió el comando del
    ejemplo contra `docs/ADR/ADR-004-empaquetado-y-publicacion.md` y comparó la
    salida real contra el bloque publicado. Diff vacío.
- **Aceptación del owner:** `pending`.
- **Tag `v1.0.0` y publicación en PyPI:** al cierre de este PBI, deliberadamente
  NO hechos (publicar es irreversible). Se hicieron después, a pedido explícito
  de Fabián — ver `docs/dev-log/2026-09-25.md`.
- **Bug de herramienta, encontrado cerrando el gate de Sonar de este PBI
  (registrado formalmente el 2026-09-26):** [[BUG-007-sonargate-git-archive-tar-path]].
- **PBI o Bug siguiente:** PBI-008 (bloqueado: falta decisión sobre `--verify` y
  una `ANTHROPIC_API_KEY` con facturación).
