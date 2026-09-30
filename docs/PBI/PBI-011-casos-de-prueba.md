---
title: "PBI-011 — casos de prueba para Kiwi (prompt interactivo de API key, keyring, --forget-key)"
aliases:
  - "PBI-011 casos de prueba"
project: tokmd
document_type: test-plan
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
  - qa
related_documents:
  - "[[PBI-011-api-key-interactiva-para-verify]]"
  - "[[ADR-009-manejo-de-api-key-para-verify]]"
---

# PBI-011 — casos de prueba

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, junto con el PBI. Once casos. Pendiente de cargar a Kiwi como PROPOSED cuando Fabián acepte el corte. |

## Para qué sirve este documento

Fuente de la que se cargan los casos a Kiwi, escrita **antes** de tocar el
código (ROL-03). Columna «qué falla caza»: la modificación concreta que
tiene que hacerlo fallar.

**Estado:** `PROPOSED`, sin cargar. Plan de Kiwi: nuevo, para PBI-011.

## Dato dorado

| Dato | Valor | Origen |
|---|---|---|
| `CLAUDE.md` global (snapshot del 27/09), `--verify` con key real | **17.381** | invariante: la key ya no se busca igual, pero el número que devuelve la API es el mismo de PBI-009 |

## Casos

| Id | Nombre | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-011-C01** | Prompt aparece en TTY sin key | `isatty` mockeado `True`; sin env var; `keyring` falso vacío | `tokmd f.md --verify` | Aparecen las 4 opciones exactas de ADR-009 | Prompt ausente o con texto distinto |
| **TOK-011-C02** | Opción 1: sólo memoria | ídem, se elige `1` e ingresa una key | corre y cuenta | Usa la key para esta corrida; `keyring.set_password` **no** se llamó | Guardado accidental en modo "sólo esta vez" |
| **TOK-011-C03** | Opción 2: guarda y persiste | ídem, se elige `2` | primera corrida cuenta y guarda; segunda corrida sin env var | Segunda corrida **no** pregunta, resuelve desde `keyring` | Key no persistida o prompt repetido |
| **TOK-011-C04** | Opción 3: sigue offline | ídem, se elige `3` | corre | Imprime el total offline (ctok), aviso de que no se verificó contra la API, exit 0 | Falla en vez de degradar a offline |
| **TOK-011-C05** | Opción 4: cancela | ídem, se elige `4` | corre | Exit ≠ 0, no imprime número | Cancelación que igual imprime algo |
| **TOK-011-C06** | Sin TTY, nunca prompt (el que protege CI) | `subprocess.run` real con `stdin=DEVNULL`, sin env var, sin `keyring` | `tokmd f.md --verify` | Termina inmediato, mismo mensaje de error de hoy, exit ≠ 0, **sin colgarse** | Prompt que cuelga esperando input en un pipe |
| **TOK-011-C07** | Prioridad: env var gana siempre | `ANTHROPIC_API_KEY` seteada **y** algo guardado en `keyring` (distinto) | `tokmd f.md --verify` | Usa la del entorno; `keyring.get_password` no se consulta | Prioridad invertida |
| **TOK-011-C08** | Sin backend de `keyring` | `keyring` falso que lanza `NoKeyringError` en `set_password` | elegir opción `2` | Mensaje explica que no hay backend, sugiere la variable de entorno, exit ≠ 0, **sin traceback crudo** | Excepción no atrapada |
| **TOK-011-C09** | `--forget-key` borra | algo guardado en `keyring` falso | `tokmd --forget-key`, después `tokmd f.md --verify` sin env var | Primer comando exit 0; segundo vuelve a preguntar (C01) | Borrado que no borra, o que no re-dispara el prompt |
| **TOK-011-C10** | `--forget-key` idempotente | nada guardado | `tokmd --forget-key` | Exit 0, sin error | Tratar "no había nada" como fallo |
| **TOK-011-C11 (sin regresión)** | Con env var, mismo número de siempre | `CLAUDE.md` global del snapshot, `ANTHROPIC_API_KEY` real | `tokmd CLAUDE.md --verify` | **17.381**, igual que PBI-009 | Cambio en la resolución de key que afecta el conteo (no debería tocarlo) |

## Registro en Kiwi

Mismo procedimiento verificado en PBI-009/010. Identidad de cada caso por
el prefijo `TOK-011-Cnn -`. Plan nuevo, nombre `PBI-011 — API key
interactiva`.
