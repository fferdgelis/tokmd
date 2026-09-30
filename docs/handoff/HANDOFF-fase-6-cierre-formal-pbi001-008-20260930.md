---
title: "Cierre formal: aceptación del owner en PBI-001 a 008, ADR-007 sincronizado"
aliases:
  - "Cierre administrativo tokmd 20260930"
project: tokmd
document_type: work-plan
status: active
version: 0.1.0
created: 2026-09-30
updated: 2026-09-30
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-sonnet-5"
llm_harness: "Claude Code Desktop"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription"
modified_by: "Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - handoff
related_documents:
  - "[[HANDOFF-fase-5-ttok05-medicion-api-y-merge-pbi009-20260927]]"
  - "[[PBI-001-parser-de-secciones]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
---

# Cierre formal: aceptación del owner en PBI-001 a 008, ADR-007 sincronizado

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, a pedido de Fabián («avanzá con el A» sobre la consulta «qué falta para terminar el proyecto»). |

## Qué se hizo

`tokmd` está terminado y en producción desde el 27/09 (v2.0.0 en PyPI,
verificado contra `count_tokens` real: `tokmd` sobre `~/.claude/CLAUDE.md`
da `17381`, exacto). Lo único que quedaba era administrativo: **ocho PBI
tenían el código en producción desde hace días pero la sección 6, «Aceptación
del owner», seguía en `pending`.**

Cerrados hoy, con la misma fórmula (`status` a `closed`, fila nueva en el
historial, «Aceptación del owner: `approved` — Fabián Ferdgelis,
2026-09-30»):

| PBI | Nota puntual |
|---|---|
| PBI-001 — Parser de secciones | sin novedad |
| PBI-002 — Tokenizador Claude | sin novedad |
| PBI-003 — Tokenizador OpenAI | sin novedad |
| PBI-004 — CLI y plataformas | el default de `--platform` que este PBI dejó obligatorio después lo cambió PBI-009 |
| PBI-005 — Render de salida | ese render lo reescribió PBI-009 (BUG-009: `own`/`total`, fila raíz, `boundary drift`) |
| PBI-006 — Verificación contra la API | el cableado de `--verify` en `cli.py` que este PBI dejó explícitamente sin hacer **ya está hecho** — verificado ahora en el código (`cli.py` tiene el flag y usa `verify.py`), documentado en el README |
| PBI-007 — Empaquetado y publicación | el pipeline de este PBI es el que publicó la 2.0.0 el 27/09 |
| PBI-008 — Medición del CLAUDE.md global | **aviso:** el número que dejó este PBI (`15.877`, en `framework-multi-ai/docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md`) estaba subestimado por BUG-008, que no existía el 25/09. El correcto es `17.381`. Ese archivo de `framework-multi-ai` no se tocó desde acá — es de otro proyecto. |

También corregido: `docs/ADR/ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol.md`
tenía el frontmatter en `status: proposed` mientras el cuerpo decía
`accepted` desde el 27/09 (aceptaste la opción D ese día). Sincronizado a
`accepted`.

PBI-009 no se tocó: ya estaba `closed` con su propia aceptación explícita
del 27/09.

## Qué no se tocó (fuera del alcance de «el A»)

Los tres grupos B y C de la consulta anterior siguen exactamente como
estaban, sin decisión: ctok (propuesta B/C del informe
`20260927-ctok-propio-o-dependencia-pros-y-contras.md`), baseline
versionado, recorte del `CLAUDE.md` global, y el ruido de otros proyectos
(`framework-multi-ai`, categoría «Error» en Kiwi, key de NVIDIA).

## Estado del proyecto después de este cierre

Los nueve PBI (001 a 009) están `closed` con aceptación formal del owner.
Los siete ADR están `accepted`. Los once bugs registrados están `fixed` o
`verified`. `tokmd 2.0.0` en PyPI. **No queda ningún PBI, ADR ni bug
abierto en este repositorio.**
