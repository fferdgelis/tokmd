---
title: "ADR-004 — Empaquetado y publicación: nombre, licencia y canal"
aliases:
  - "tokmd ADR-004"
project: tokmd
document_type: architecture-decision-record
adr_id: ADR-004
status: accepted
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
related_documents: []
---

# ADR-004 — Empaquetado y publicación: nombre, licencia y canal

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Propuesta inicial, decisiones de Fabián del 24/09/2026. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Aceptado por Fabián. |

## Estado

`accepted`. Aceptado por Fabián Ferdgelis el 2026-09-25, tal cual estaba escrito.

## Contexto

Se busca publicar una primera herramienta terminada, no seguir iterando sin sacar nada
(pedido explícito de Fabián). Se necesita nombre libre en PyPI, licencia, e idioma para
maximizar difusión, más un canal de publicación que no dependa de que Fabián guarde un
token en esta máquina (regla de secretos del CLAUDE.md global).

## Decisiones

- **Nombre:** `tokmd`, verificado libre en PyPI el 24/09/2026 (404 en `pypi.org/pypi/tokmd/json`).
- **Licencia:** Apache License 2.0, igual que `ttok`, cuyo patrón de CLI inspiró esta
  herramienta. Titular: Fabián Ferdgelis, 2026.
- **Idioma:** inglés para código, CLI, docstrings y `README.md`; `README.es.md` en
  español para difusión local. El resto de la documentación de proceso (ADR, PBI, dev-log)
  queda en español, como en el resto de los proyectos de Fabián.
- **Repositorio:** `github.com/fferdgelis/tokmd`, público. Se confirma con Fabián antes
  del primer push (regla de acciones de cara al exterior).
- **Publicación en PyPI:** Trusted Publishing (OIDC de GitHub Actions), sin token de
  larga vida guardado en ningún lado. Fabián crea la cuenta de PyPI y el «pending
  publisher»; el repo sólo aporta el workflow `publish.yml`.

## Consecuencias

El primer publish requiere que Fabián haga dos pasos manuales (crear cuenta PyPI,
configurar el pending publisher) antes de que el tag dispare la publicación automática.

## Verificación y reversibilidad

Se verifica con `uvx tokmd --version` desde una consola limpia después de publicar.
Cambiar nombre o licencia después de publicar requiere deprecar el paquete existente.
