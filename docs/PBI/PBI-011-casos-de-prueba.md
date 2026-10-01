---
title: "PBI-011 — casos de prueba para Kiwi (--live, engines/, pregunta, banner, tabla legible)"
aliases:
  - "PBI-011 casos de prueba"
project: tokmd
document_type: test-plan
status: active
version: 0.3.0
created: 2026-09-30
updated: 2026-09-30
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-opus-5-5"
llm_harness: "Claude Code Desktop"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription"
modified_by: "Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription"
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
| 2026-09-30 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | 17 casos. |
| 2026-09-30 | 0.3.0 | Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription | Reescrito sobre la decisión de configuración aceptada: 22 casos, uno por AC. Sin `keyring`. |

**Estado:** `PROPOSED`. Plan de Kiwi nuevo: `PBI-011 — live, engines y legibilidad`.
Identidad de cada caso por el prefijo `TOK-011-Cnn -`.

## Dato dorado

| Dato | Valor | Origen |
|---|---|---|
| `CLAUDE.md` global (copia del 27/09), `--live` con key real | **17.381** | API `count_tokens`, invariante desde PBI-009 |

## Casos

| Id | AC | Qué se prueba | Resultado esperado | Qué falla caza |
|---|---|---|---|---|
| TOK-011-C01 | AC-01 | Carpeta de usuario por SO y por `TOKMD_CONFIG_DIR` | Ruta correcta en los tres SO (simulados) y con la variable | Ruta fija de un solo SO |
| TOK-011-C02 | AC-02 | Carpeta de sistema por SO y por `TOKMD_SYSTEM_CONFIG_DIR` | ídem | ídem |
| TOK-011-C03 | AC-03 | `tokmd --init` | Crea los 3 archivos, no pisa uno existente, exit 0 sin `FILE` | `--init` que pisa configuración del usuario |
| TOK-011-C04 | AC-04 | Fusión sistema + usuario | Usuario gana clave por clave; sin archivos, valores por defecto | Usuario pisa el archivo entero |
| TOK-011-C05 | AC-05 | Guardar un valor | Otras claves intactas; `0600` en POSIX | Guardado que borra claves; permisos abiertos |
| TOK-011-C06 | AC-06 | Orden de resolución | env > usuario > sistema > `None`; `""` = ausente | Prioridad invertida |
| TOK-011-C07 | AC-07 | Referencia `op://` | Usa la salida de `op read`; si `op` falla, error claro sin traceback | Referencia usada literal como key |
| TOK-011-C08 | AC-08 | Keys por motor | La de Anthropic no se usa para Codex ni al revés | Providers mezclados |
| TOK-011-C09 | AC-09 | `--help` | `--live` presente; `--verify` y `--api-key` ausentes | Rename incompleto |
| TOK-011-C10 | AC-10 | `--live` con key | Cuenta por la API del motor; stdout sólo el número | Banner o texto en stdout |
| TOK-011-C11 | AC-11 | Sin key, TTY, preguntar | Banner + 3 opciones exactas por stderr | Pregunta en stdout o con otras opciones |
| TOK-011-C12 | AC-12 | Opción 1 | Key oculta, guardada en el archivo del motor, cuenta live | Key no guardada o mostrada |
| TOK-011-C13 | AC-13 | Opción 2 | Offline, aviso, exit 0, nada guardado | Guardado accidental |
| TOK-011-C14 | AC-14 | Opción 3 | Guarda `ask_for_key=false`; la siguiente no pregunta | Vuelve a preguntar |
| TOK-011-C15 | AC-15 | Sin TTY (subprocess real, `stdin=DEVNULL`) | Error inmediato con el nombre de la variable, exit ≠ 0, sin colgarse | Prompt que cuelga un CI |
| TOK-011-C16 | AC-16 | Texto de costo | Anthropic «gratis»; Codex «costo no confirmado por OpenAI» | Promesa de gratis sin verificar |
| TOK-011-C17 | AC-17 | `--forget-key` | Vacía keys, `ask_for_key=true`, exit 0 aunque no haya archivos | Borra la mitad; falla sin archivos |
| TOK-011-C18 | AC-18 | `--about` y ausencia del banner | Banner completo con email; nunca en corrida normal | Banner en stdout de una corrida normal |
| TOK-011-C19 | AC-19 | Sin regresión, key real | **17.381**; suite anterior en verde | Cambio de resolución que altera el conteo |
| TOK-011-C20 | AC-20 | Codex real (lo corre Fabián) | Número > 0; costo registrado | Endpoint mal llamado |
| TOK-011-C21 | AC-21 | `render(width=N)` | Ninguna línea > N; `…`; conectores en la misma línea | Fila que envuelve |
| TOK-011-C22 | AC-22 | Ancho sólo en terminal | Redirigido a archivo no trunca | Archivo truncado al ancho de quien lo generó |
