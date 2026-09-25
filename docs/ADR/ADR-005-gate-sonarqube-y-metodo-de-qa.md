---
title: "ADR-005 — Quality Gate de SonarQube y método de QA con Kiwi"
aliases:
  - "tokmd ADR-005"
project: tokmd
document_type: architecture-decision-record
adr_id: ADR-005
status: proposed
decision_date: 2026-09-24
created: 2026-09-24
updated: 2026-09-24
version: 0.1.0
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
  - adr
  - qa/kiwi
  - qa/sonarqube
related_documents: []
---

# ADR-005 — Quality Gate de SonarQube y método de QA con Kiwi

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Propuesta inicial, decisiones de Fabián del 24-25/09/2026 sobre Kiwi y canal de QA. |

## Estado

`proposed`.

## Contexto

Fabián pidió expresamente que SonarQube sea el gate obligatorio de cada fase, y que se
arme la estructura completa de Kiwi TCMS (catálogo, planes, casos, runs, ejecuciones)
para correr los Test Runs de QA de este proyecto, reusando la infraestructura y el
método ya verificados en `framework-multi-ai`, `whatsapp-mcp` e `ia-evaluator`.

## Decisiones

### 1. Gate de SonarQube

Cada fase de desarrollo cierra sólo si: `pytest` verde, y el Quality Gate de SonarQube en
`OK` según la política común (`Framework-QA/policies/QUALITY-GATE.md`: 0 blocker/critical,
ratings A, 100 % de hotspots revisados, cobertura ≥ 80 %, duplicación < 3 %). El análisis
corre sobre un snapshot de `git archive HEAD` (nunca el checkout con temporales), en la
red `local-sonarqube-network`, con `sonar.scm.disabled=true` porque el snapshot no lleva
`.git`. El proyecto Sonar es `tokmd`, creado idempotente con el `automation-token`
(bóveda DPAPI `sonarqube`), nunca con el `scanner-token` (atado a `whatsapp-mcp`). El
período de código nuevo lo fija Fabián una vez en la UI tras el análisis baseline; el
script lo exige con `&branch=main` y aborta si no está fijado, replicando la lección
pagada por `whatsapp-mcp` el 27/08/2026 (un período no fijado deja un gate verde que no
mide nada).

### 2. Catálogo de Kiwi (se crea una vez)

Clasificación **Herramientas de desarrollo** → producto **tokmd** → versión **1.0.0**.
Categorías: las cinco del método (Functional, Error, Edge case, Performance, Security)
más `--default--` de fábrica. Componentes: Sections parser, Tokenizers, CLI, Render,
Verify, Packaging, SonarQube gate.

### 3. Eje de trabajo en Kiwi (se repite por fase)

Un Test Plan tipo `Unit` por PBI (8 planes) más un plan `Acceptance` «Release 1.0.0» con
los casos de extremo a extremo. Los Test Case se cargan como `PROPOSED` antes de escribir
el código de esa fase, con id `TOK-<PBI>-C<nn>`. El Build es el commit corto del snapshot
evaluado. Un Test Run por (plan × build), creado con todas las Test Execution en `IDLE`.

### 4. Quién ejecuta y marca

Sólo QA marca `PASSED`/`FAILED`, nunca el rol de desarrollo. El canal de QA de este
proyecto es **OpenCode + OpenRouter + Kimi K3** (`opencode run -m
openrouter/moonshotai/kimi-k3 --dir <snapshot>`), verificado en `framework-multi-ai` los
días 18 al 21 de septiembre de 2026. QA corre en modo read-only sobre el snapshot, nunca
sobre el checkout real, y deja evidencia cruda en `docs/handoff/qa/`. Lo que QA no
ejecutó queda `IDLE`, nunca `PASSED`.

## Consecuencias

El desarrollo no puede autocalificarse: toda fase espera un ciclo de QA con otro motor
antes de cerrar. Kimi K3 tiene una trampa documentada (Reels R-40: puede negar que puede
hacer algo citando una fuente ajena) que el brief de QA neutraliza pidiendo ejecución y
evidencia, no opinión. El gate de Sonar puede bloquear una fase por cobertura o
duplicación aunque los tests pasen; eso es la política, no un error del script.

## Verificación y reversibilidad

Se verifica con la evidencia JSON de cada análisis Sonar (`C:\IA\Data\sonarqube\reports\tokmd\`)
y con las Test Execution de Kiwi con fecha y comentario de evidencia. Cambiar el canal de
QA o la política de gate requiere reemplazar este ADR.
