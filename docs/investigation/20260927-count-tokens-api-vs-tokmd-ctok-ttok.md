---
title: "count_tokens (API oficial) vs tokmd, ctok y ttok sobre el mismo archivo"
aliases:
  - "Comparación oráculo Anthropic vs tokmd"
project: tokmd
document_type: research
status: active
version: 0.1.0
created: 2026-09-27
updated: 2026-09-27
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
source_of_truth: true
tags:
  - project/tokmd
  - reference/tokens
related_documents:
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
  - "[[ADR-003-parseo-de-secciones]]"
  - "[[20260924-ctok-marco-y-deriva]]"
  - "[[20260925-tiktoken-deriva]]"
---

# count_tokens (API oficial) vs tokmd, ctok y ttok sobre el mismo archivo

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. Medición del CLAUDE.md global contra el endpoint count_tokens y comparación con tokmd, ctok y ttok. |

**Sesión:** TTOK-05, 27/09/2026. **Pedido de Fabián:** medir cuánto pesa
`C:\Users\fferdgelis\.claude\claude.md` según Anthropic (sin usar tokmd) y
después comparar en las mismas condiciones con tokmd, ctok y ttok.

## Archivo medido

`C:\Users\fferdgelis\.claude\claude.md` — 38.185 bytes, 37.405 caracteres,
UTF-8, 44 líneas que empiezan con `#` (15 de ellas son los «comentarios» de la
REGLA CERO, que Markdown lee como H1 vacíos).

## 1. Oráculo: `POST /v1/messages/count_tokens`

Un mensaje `user` con el archivo entero como `content`. Key de la bóveda DPAPI
(`multi-modelos-ai / anthropic.api-key`). Script:
`scratchpad/count-tokens.ps1` de la sesión; JSON crudo en
`C:\IA\Projects\Claude-Tokenizer\local\count_tokens-claude-md-global-2026-09-27.json`
y `...-b.json`.

| Modelo | input_tokens |
|---|---|
| claude-fable-5-1 | 17.383 |
| claude-opus-5 | 17.381 |
| claude-opus-4-8 | 17.381 |
| claude-sonnet-5 | 17.381 |
| claude-sonnet-4-6 | 13.076 |
| claude-haiku-4-5 | 13.076 |

Dos familias de tokenizador y nada más: la nueva (desde Opus 4.7) y la
anterior. El nivel Opus/Sonnet/Haiku no cambia el conteo. El número incluye
el marco del mensaje (rol y delimitadores), del orden de un dígito.

## 2. ctok (motor offline de tokmd), archivo entero

`ctok.token_count(texto, version)`; `FRAME` es el marco que tokmd resta
(ADR-002).

| Familia ctok | crudo | FRAME | neto | Oráculo | Desvío neto |
|---|---|---|---|---|---|
| 4.8 | 17.381 | 6 | 17.375 | 17.381 (Sonnet 5 / Opus 5 / 4.8) | −6 |
| 4.7 | 17.386 | 12 | 17.374 | 17.381 | −7 |
| 3.0 | 13.076 | 8 | 13.068 | 13.076 (Sonnet 4.6 / Haiku 4.5) | −8 |

**ctok crudo sobre el archivo entero coincide con la API al token exacto**
en 4.8 y 3.0 (17.381 y 13.076); en 4.7 se pasa por 5. El «neto» queda abajo
por el FRAME que resta, que es justo lo que la API sí cuenta.

## 3. tokmd (misma familia, archivo entero, `--depth 1` con roll-up)

| tokmd | total | Oráculo | Desvío |
|---|---|---|---|
| `--platform claude-code` (4.8, default) | 15.903 | 17.381 | **−1.478 (−8,5 %)** |
| `--claude-family 4.7` | 15.903 | 17.381 | −1.478 |
| `--claude-family 3.0` | 11.945 | 13.076 | −1.131 (−8,6 %) |
| `--platform codex` (o200k) | 9.852 | tiktoken o200k 10.742 | −890 (−8,3 %) |

**Causa del desvío, verificada:** tokmd no cuenta la línea del encabezado
(`sections.py`: `own_text = lines[content_start:end_line]`, y
`content_start` es la línea siguiente al heading). Las 44 líneas `#` de este
archivo pesan por sí solas 1.429 tokens en ctok 4.8 y 917 en o200k; eso
explica 1.429 de los 1.478 y 917 de los 890 (el resto es el borde BPE ya
documentado en `20260925-tiktoken-deriva.md` y el FRAME por sección).

Este archivo es un caso extremo: 44 encabezados, 15 de ellos líneas de
«comentario» con `#`. En un Markdown normal el desvío será menor, pero el
signo es siempre el mismo: **tokmd reporta menos de lo que la API cobra.**

Que 4.7 y 4.8 den idéntico nodo a nodo no es un bug: ctok 4.7 y 4.8 difieren
en 1 token neto sobre 37 KB.

## 4. ttok (Simon Willison, v0.3) — no es un contador de Claude

ttok usa `tiktoken` (OpenAI). Sirve como control de tiktoken, no como medida
de Claude.

| ttok | tokens | tiktoken directo |
|---|---|---|
| `ttok -i archivo` (default = cl100k_base) | 11.660 | 11.660 |
| `ttok -i archivo -m gpt-4o` (o200k_base) | 10.742 | 10.742 |

Contra la API de Anthropic (17.381) ttok **subestima un 33–38 %**, que es lo
que dice `shared/token-counting.md` de Anthropic: «no usar tiktoken para
Claude».

**Trampa de Windows:** `ttok < archivo` desde Git Bash sin `PYTHONUTF8=1`
dio 13.075 en vez de 11.660 — lee stdin en cp1252 y rompe los acentos en
más tokens. Con `-i archivo` o con `PYTHONUTF8=1` da el número correcto.

## 5. Bug encontrado en tokmd (no arreglado, registrado como BUG-011)

`tokmd <archivo> --platform claude-code` **revienta en Windows** con
`UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'`
(`cli.py:163`, `click.echo`) cuando algún título tiene caracteres fuera de
cp1252 (→, «, », —) y la salida va a un archivo o pipe. Falla en `table`,
`md` y `csv`; `json` no (escapa a ASCII). Workaround: `PYTHONUTF8=1`.
Registrado como `BUG-011-salida-unicodeencodeerror-cp1252-windows.md` en la
rama `worktree-ttok04-pbi009-ronda2` (008, 009 y 010 ya estaban tomados ahí).

**Nota del mismo día:** el desvío por encabezados de la sección 3 ya estaba
registrado por la sesión TTOK-04 como **BUG-008** y entra en el alcance de
**PBI-009** (AC-10 y AC-11), en esa misma rama. El ADR-007 de esa rama midió
además que el costo por trozo es 5 y no 6: coincide con la sonda de esta
sesión (`58 = 38 + 25 − 5`).

## Conclusión

- El número que cobra Anthropic por este archivo hoy: **17.381** (Sonnet 5,
  Opus 5, Opus 4.8; Fable 5.1 = 17.383).
- **ctok crudo es exacto** contra la API en el archivo entero.
- **tokmd queda 8,5 % abajo** porque omite las líneas de encabezado; es una
  decisión de `sections.py`, no de ctok. Si el total de tokmd tiene que
  coincidir con lo que la API cobra, el heading tiene que entrar en el
  `own_text` de su sección.
- ttok mide OpenAI, no Claude: −33 % a −38 %.
