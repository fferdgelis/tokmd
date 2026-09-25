---
title: "PBI-XXX — Título orientado a resultado"
aliases:
  - "tokmd PBI Template"
project: tokmd
document_type: pbi-template
status: template
version: 1.0.0
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
  - template
related_documents:
  - "[[BUG_TEMPLATE]]"
---

# PBI-XXX — Título orientado a resultado

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| YYYY-MM-DD | x.y.z | Persona, proveedor, modelo/harness, canal y modo | Cambio realizado en no más de dos líneas. |

## 1. Valor y contexto

- **Problema:**
- **Stakeholder:** Fabián Ferdgelis, owner del proyecto.
- **Resultado esperado:**
- **Prioridad:**
- **Hipótesis:**

### Historia de usuario

> Como **[tipo de usuario]**, quiero **[resultado]** para **[beneficio verificable]**.

## 2. Corte de entrega

- **Incluye:**
- **No incluye:**
- **Dependencias:**
- **Riesgos:**

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado **[contexto]**, cuando **[acción]**, entonces **[resultado observable]**.
- [ ] **AC-02:** Dado **[caso límite]**, cuando **[acción]**, entonces **[resultado esperado]**.
- [ ] **AC-03:** Dado **[fallo o entrada inválida]**, cuando **[acción]**, entonces **[comportamiento]**.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:**
- **Herramientas disponibles:**
- **Versión de tests y configuración:**
- **Métricas:**
- **ADR requerido:** `none | [[ADR-XXX]] | to investigate`

## 5. Handoffs

### Definition of Ready

- [ ] Valor, alcance y fuera de alcance claros.
- [ ] Criterios observables y testeables.
- [ ] ADR enlazado si cambia una decisión arquitectónica.
- [ ] Casos de Kiwi cargados como PROPOSED.

**Estado:** `ready | not ready | blocked`

### Handoff a TDD

- **AC a convertir en pruebas:**
- **Fixtures y contratos:**

### Handoff a Desarrollo

- **Restricciones confirmadas:**
- **Preguntas abiertas:**

### Handoff a QA

- **Candidato identificable:** commit corto del snapshot.
- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Casos independientes:**
- **Evidencia mínima:** log crudo de la ejecución + resultado por caso en `tools/kiwi/resultados/`.

## 6. Cierre

- **Artefactos y enlaces:**
- **Resultado de QA independiente:** `pending | accepted | rejected | blocked`
- **Aceptación del owner:** `pending | accepted | rejected`
- **PBI o Bug siguiente:**
