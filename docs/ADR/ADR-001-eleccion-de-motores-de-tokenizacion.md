---
title: "ADR-001 — Elección de motores de tokenización por plataforma"
aliases:
  - "tokmd ADR-001"
project: tokmd
document_type: architecture-decision-record
adr_id: ADR-001
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
  - "[[20260924-tokenizadores-por-plataforma]]"
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
---

# ADR-001 — Elección de motores de tokenización por plataforma

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Propuesta inicial, pendiente de aceptación de Fabián. |

## Estado

`proposed`. Pendiente de aceptación de Fabián Ferdgelis.

## Contexto

tokmd necesita contar tokens por sección de un archivo Markdown con el tokenizador
correcto de la plataforma que va a leer ese archivo. No existe tokenizador oficial local
de Anthropic para Claude 3 en adelante (`@anthropic-ai/tokenizer` archivado el
01/09/2026, inexacto desde Claude 3). El detalle completo del relevamiento está en
`[[20260924-tokenizadores-por-plataforma]]`.

## Opciones

1. Sólo la API `count_tokens`. Exacta y gratis, pero requiere `ANTHROPIC_API_KEY` y red
   en cada invocación: barrera para una herramienta de línea de comandos de difusión
   pública.
2. Sólo `ctok` (offline). Cero fricción, pero depende de que un tercero mantenga la
   reconstrucción cuando Anthropic cambie de tokenizador, y ya declara no modelar el
   espacio final en blanco de Opus 5.
3. `ctok` por defecto + `--verify` opcional contra la API. Sin fricción para el uso
   normal; quien quiera exactitud garantizada o sospeche una divergencia puede pedirla.

## Decisión propuesta

Opción 3. Motor por defecto: `ctok` (MIT, Sander Land), acreditado en `NOTICE`. Flag
`--verify`: manda cada sección a `POST /v1/messages/count_tokens` (gratis, sin caché) y
agrega columnas `API` y `Δ`. Para OpenAI/Codex: `tiktoken`, encoding `o200k_base` para
GPT-5/GPT-4o (verificado), `cl100k_base` disponible por `--encoding` para compatibilidad
con mediciones anteriores.

## Consecuencias

tokmd queda dependiente de un paquete de terceros (`ctok`) para su función central en
Claude. Si `ctok` deja de mantenerse o Anthropic vuelve a cambiar de tokenizador sin que
`ctok` lo siga, el motor por defecto queda desactualizado hasta que se actualice la
dependencia; `--verify` sigue siendo exacto porque llama a la API real. Se documenta esta
dependencia en el README, no se oculta.

## Verificación y reversibilidad

Se verifica midiendo `--verify` sobre una muestra y comparando Δ con `ctok` solo (ver
PBI-002 y PBI-006). Cambiar el motor por defecto requiere reemplazar este ADR.
