---
title: "PBI-011 — casos de prueba para Kiwi (--live interactivo, Claude y Codex, banner, legibilidad de --sections)"
aliases:
  - "PBI-011 casos de prueba"
project: tokmd
document_type: test-plan
status: active
version: 0.2.0
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
  - qa
related_documents:
  - "[[PBI-011-api-key-interactiva-para-verify]]"
  - "[[ADR-009-manejo-de-api-key-para-verify]]"
---

# PBI-011 — casos de prueba

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, once casos. |
| 2026-09-30 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Ampliado a 17 casos: `--verify`→`--live`, carpeta de config como capa de resolución, banner, Codex, legibilidad de `--sections`. |

## Para qué sirve este documento

Fuente de la que se cargan los casos a Kiwi, escrita **antes** de tocar el
código (ROL-03).

**Estado:** `PROPOSED`, sin cargar. Plan de Kiwi: nuevo, para PBI-011.

## Datos dorados

| Dato | Valor | Origen |
|---|---|---|
| `CLAUDE.md` global (snapshot del 27/09), `--live` con key real | **17.381** | invariante desde PBI-009 |

## Casos

| Id | Nombre | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-011-C01** | `--live` existe, `--verify` no | build de este PBI | `tokmd --help` | `--live` en la lista; `--verify` y `--api-key` ausentes | Rename incompleto |
| **TOK-011-C02** | Prompt con banner, TTY sin key | `isatty` mockeado `True`; sin key en ninguna capa | `tokmd f.md --live` | Banner primero, después las 4 opciones exactas | Prompt sin banner, o banner en corrida normal |
| **TOK-011-C03** | Opción 1: sólo memoria | ídem, elige `1` | corre y cuenta | Usa la key para esta corrida; ni `keyring` ni el archivo de config se tocan | Guardado accidental |
| **TOK-011-C04** | Opción 2: guarda en keyring, persiste | ídem, elige `2` | 1ª corrida guarda; 2ª corrida sin env var | 2ª **no** pregunta | Key no persistida |
| **TOK-011-C05** | Opción 3: sigue offline | ídem, elige `3` | corre | Total offline (ctok), aviso explícito, exit 0 | Falla en vez de degradar |
| **TOK-011-C06** | Opción 4: cancela | ídem, elige `4` | corre | Exit ≠ 0, sin número | Cancelación que igual imprime |
| **TOK-011-C07 (protege CI)** | Sin TTY, nunca prompt | `subprocess` real, `stdin=DEVNULL`, sin key | `tokmd f.md --live` | Error inmediato igual que hoy, exit ≠ 0, sin colgarse | Prompt en pipe/CI |
| **TOK-011-C08** | Prioridad: env > keyring > archivo | las tres presentes a la vez, con valores distintos | `tokmd f.md --live` | Usa la del entorno | Prioridad invertida |
| **TOK-011-C09** | Archivo de config resuelve sin preguntar | sólo el archivo tiene key (sin env, sin keyring) | `tokmd f.md --live` | Cuenta sin prompt | Capa de archivo no implementada |
| **TOK-011-C10** | `--forget-key` borra las dos capas | key en `keyring` y en archivo | `tokmd --forget-key`, después `--live` sin nada más | Primero exit 0; segundo vuelve a preguntar (C02) | Borra sólo una capa |
| **TOK-011-C11** | `--forget-key` idempotente | nada guardado en ninguna capa | `tokmd --forget-key` | Exit 0, sin error | Tratar "no había nada" como fallo |
| **TOK-011-C12** | Banner nunca en corrida normal | key ya resuelta por cualquier capa, sin `--about` | `tokmd f.md --live` | `stdout` es sólo el número; sin banner | Banner filtrado a un flujo normal |
| **TOK-011-C13** | `--about` | cualquier estado | `tokmd --about` | Banner completo, exit 0, no exige `FILE` | `--about` exige argumento o falla |
| **TOK-011-C14** | Codex: aviso de costo no confirmado | `--platform codex --live`, sin `OPENAI_API_KEY` en ninguna capa, TTY | corre | El prompt dice explícitamente "costo no confirmado por OpenAI" (texto exacto) | Texto que dice "gratis" sin haberlo verificado |
| **TOK-011-C15** | Codex: resolución de key no se mezcla con Anthropic | `ANTHROPIC_API_KEY` seteada, sin `OPENAI_API_KEY` en ninguna capa | `tokmd f.md --platform codex --live` | Pregunta igual (no usa la key de Anthropic para Codex) | Providers mezclados |
| **TOK-011-C16** | `--sections` trunca sin envolver | terminal simulada a 60 columnas, título largo | `tokmd f.md --sections` | Esa fila en una sola línea, con `…` | Fila que envuelve en 2+ líneas |
| **TOK-011-C17 (sin regresión)** | Con env var, mismo número de siempre | `CLAUDE.md` global del snapshot, `ANTHROPIC_API_KEY` real | `tokmd CLAUDE.md --live` | **17.381**, igual que PBI-009 | Cambio en la resolución de key que afecta el conteo |

## Registro en Kiwi

Mismo procedimiento verificado en PBI-009/010. Identidad de cada caso por
el prefijo `TOK-011-Cnn -`. Plan nuevo, nombre `PBI-011 — live interactivo`.
