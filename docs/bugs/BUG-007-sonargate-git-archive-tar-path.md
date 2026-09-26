---
title: "BUG-007 — Invoke-SonarGate.ps1: git archive | tar dependía de cuál tar ganaba en el PATH"
aliases:
  - "tokmd BUG-007"
project: tokmd
document_type: bug
status: fixed
version: 1.0.0
created: 2026-09-26
updated: 2026-09-26
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
reviewed_by: "pending"
review_status: "pending"
tags:
  - project/tokmd
  - bug
related_documents:
  - "[[PBI-007-empaquetado-y-publicacion]]"
  - "[[BUG-005-sonargate-ps7-getresponsestream]]"
---

# BUG-007 — `Invoke-SonarGate.ps1`: `git archive | tar` dependía de cuál `tar` ganaba en el PATH

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-26 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación retroactiva — incidente del 2026-09-25, documentado sólo en el dev-log hasta ahora. |

## 1. Clasificación

- **Título:** `Invoke-SonarGate.ps1` armaba su snapshot con
  `git archive HEAD | & tar -x -C $snapshotDir`. En esta máquina hay dos `tar`
  en el PATH (`C:\Program Files\Git\usr\bin\tar.exe`, MSYS, traduce rutas
  absolutas de Windows; `C:\WINDOWS\system32\tar.exe`, bsdtar, no traduce) —
  cuál gana depende del orden del PATH de la consola que lo invoque.
- **Estado:** `fixed`.
- **Tipo:** `harness-defect`.
- **Severidad:** `3-medium` — bloqueaba por completo la corrida del gate
  cuando el `tar` de Git ganaba en el PATH.
- **PBI relacionado:** [[PBI-007-empaquetado-y-publicacion]] (donde se
  encontró; el mismo patrón lo tenía también el snapshot de QA, corregido en
  paralelo).
- **Caso de Kiwi relacionado:** ninguno directo — infraestructura de Sonar, no
  un caso funcional de `tokmd`.
- **Reportado por:** Desarrollo.
- **Fecha de detección:** 2026-09-25.

## 2. Contexto reproducible

- **Build/commit:** `d90fb73` (cierre de QA de PBI-007).
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`, script
  `tools/sonarqube/Invoke-SonarGate.ps1`.

## 3. Reproducción

`git archive HEAD | & tar -x -C <ruta absoluta de Windows>` desde PowerShell,
con el `tar` de MSYS ganando en el PATH:

```
/usr/bin/tar: C\:\\Users\...\\: Cannot open: No such file or directory
```

El `tar` de MSYS traduce la ruta absoluta de Windows como si fuera una ruta de
Linux, rompiéndola.

## 4. Impacto

El gate de Sonar de PBI-007 falló al primer intento. **Los 12 análisis previos
habían funcionado por casualidad**: en esa consola ganaba el `tar` de
System32. Una herramienta que anda o no según de dónde se la llame no es
confiable aunque tenga corridas verdes previas.

## 5. Evidencia

`docs/dev-log/2026-09-25.md`, sección "Trampa nueva y pagada: `git archive |
tar` no sirve desde PowerShell con rutas de Windows".

## 6. Causa

Dos binarios `tar` distintos conviven en el PATH de esta máquina, con
comportamiento distinto frente a rutas absolutas de Windows, y cuál se
resuelve primero depende del orden del PATH de la consola invocada, no de
nada que el script controle.

## 7. Corrección

Reemplazado `git archive HEAD | & tar -x -C $snapshotDir` por
`git archive --format=zip -o <zip> HEAD` + `Expand-Archive`, que no depende de
ningún `tar`. Mismo arreglo aplicado en paralelo al snapshot de QA
(`Invoke-QA-Kimi.ps1`'s flujo de armado de snapshot).

## 8. Verificación independiente

- **Verificado por:** Desarrollo, gate re-corrido sobre el commit `e685e1e`
  tras el fix.
- **Evidencia:** `C:\IA\Data\sonarqube\reports\tokmd\20260925-110449\`, Quality
  Gate OK, 38/38 tests.
