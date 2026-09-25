---
title: "ADR-003 — Parseo de secciones: árbol completo, front matter y preámbulo"
aliases:
  - "tokmd ADR-003"
project: tokmd
document_type: architecture-decision-record
adr_id: ADR-003
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
related_documents:
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
---

# ADR-003 — Parseo de secciones: árbol completo, front matter y preámbulo

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Propuesta inicial, decisión de Fabián sobre árbol completo (24/09/2026). |

## Estado

`proposed`.

## Contexto

La medición del 20/09 del CLAUDE.md global cortó a mano por `##` (nivel 2 fijo). tokmd
necesita un parser general y reutilizable. Fabián pidió expresamente **árbol completo con
subtotales**, no un corte plano de un solo nivel.

## Opciones

1. Corte plano por un nivel fijo (`--level N`), como la medición manual del 20/09.
2. Árbol completo: todos los niveles de encabezado, anidados, cada nodo con su propio
   texto (`Own`) y el acumulado con sus hijos (`Total`).

## Decisión propuesta

Opción 2, con `markdown-it-py` (CommonMark) para detectar encabezados por línea y nivel,
ignorando los que aparecen dentro de bloques de código (```` ``` ````). Filas especiales:
`(front matter)` para el YAML inicial delimitado por `---`, y `(preamble)` para el texto
entre el fin del front matter (o el inicio del archivo) y el primer encabezado. Saltos de
nivel (`##` seguido de `####` sin `###` intermedio) se toleran sin error, el hijo cuelga
del ancestro de nivel inmediatamente menor. `--depth N` filtra la vista sin cambiar el
cálculo.

## Consecuencias

Un árbol completo es más código que un corte plano, y en archivos con muchos niveles
puede ser ruidoso; `--depth` mitiga eso en la presentación sin perder el dato subyacente.

## Verificación y reversibilidad

PBI-001 prueba: front matter, preámbulo, salto de nivel, encabezado dentro de bloque de
código ignorado, archivo sin encabezados, archivo vacío. Cambiar la estrategia de corte
requiere reemplazar este ADR.
