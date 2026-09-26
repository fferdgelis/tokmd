---
title: "BUG-005 — Invoke-SonarGate.ps1: GetResponseStream no existe en PS7"
aliases:
  - "tokmd BUG-005"
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
  - "[[PBI-001-parser-de-secciones]]"
  - "[[BUG-007-sonargate-git-archive-tar-path]]"
---

# BUG-005 — `Invoke-SonarGate.ps1`: `GetResponseStream` no existe en PS7

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-26 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación retroactiva — incidente del 2026-09-25 (primer gate de Sonar), documentado sólo en el dev-log hasta ahora. |

## 1. Clasificación

- **Título:** el manejo de errores de `Invoke-SonarGate.ps1` usaba
  `$_.Exception.Response.GetResponseStream()` (patrón de .NET Framework /
  PowerShell 5.1) para leer el cuerpo de un error de `Invoke-RestMethod` —
  en PowerShell 7, ese método no existe en `HttpResponseMessage`, y la
  detección de "el proyecto ya existe" (un 400 esperado e inofensivo) se
  rompía en silencio.
- **Estado:** `fixed`.
- **Tipo:** `harness-defect`.
- **Severidad:** `3-medium` — rompía silenciosamente una detección de
  idempotencia, no el resultado del gate en sí.
- **PBI relacionado:** [[PBI-001-parser-de-secciones]] (primer análisis de
  Sonar del proyecto).
- **Caso de Kiwi relacionado:** ninguno directo — infraestructura de Sonar, no
  un caso funcional de `tokmd`.
- **Reportado por:** Desarrollo.
- **Fecha de detección:** 2026-09-25.

## 2. Contexto reproducible

- **Build/commit:** `6be061d` (primer análisis de Sonar).
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`, script
  `tools/sonarqube/Invoke-SonarGate.ps1`.

## 3. Reproducción

Llamar `Invoke-RestMethod` contra un endpoint de Sonar que responde 400 (por
ejemplo, "el proyecto ya existe"), y en el bloque `catch` intentar leer
`$_.Exception.Response.GetResponseStream()` en PowerShell 7: el método no
existe en el tipo real de la respuesta (`HttpResponseMessage`, no
`HttpWebResponse`), así que el manejo de error falla silenciosamente en vez de
interpretar el 400 como "ya existe".

## 4. Impacto

La detección de "el proyecto ya existe" (paso idempotente del script) se rompía
sin avisar. No bloqueó el primer análisis en sí, pero un código 3 en el primer
intento no se pudo diagnosticar con la evidencia correcta hasta corregir esto.

## 5. Evidencia

`docs/dev-log/2026-09-24.md`, sección "Gate de Sonar: OK en el primer análisis
(25/09)".

## 6. Causa

PowerShell 7 usa `System.Net.Http.HttpClient` internamente para
`Invoke-RestMethod`, no `System.Net.HttpWebRequest` — el cuerpo de un error va
en `$_.ErrorDetails.Message`, no en un stream que haya que leer a mano. Ya
está documentado como regla general en el CLAUDE.md global.

## 7. Corrección

Cambiado a `$_.ErrorDetails.Message` en `Invoke-SonarGate.ps1`. Con el fix:
snapshot del commit `6be061d`, pytest 8/8 verde, escáner Docker OK, **Quality
Gate: OK** en el primer análisis real.

## 8. Verificación independiente

- **Verificado por:** Desarrollo, corriendo el gate completo tras el fix.
- **Evidencia:** `C:\IA\Data\sonarqube\reports\tokmd\20260925-024139\`.
