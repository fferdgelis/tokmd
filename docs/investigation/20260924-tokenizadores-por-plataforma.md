---
title: "Tokenizadores por plataforma: qué existe hoy para Claude, OpenAI, Gemini y OpenCode"
aliases:
  - "Investigación tokenizadores tokmd"
project: tokmd
document_type: research
status: active
version: 0.1.0
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
source_of_truth: true
tags:
  - project/tokmd
  - reference/tokens
related_documents:
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
---

# Tokenizadores por plataforma: qué existe hoy para Claude, OpenAI, Gemini y OpenCode

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación, relevamiento previo a escribir tokmd. |

## Propósito

Determinar, antes de escribir una línea de código, si existe una herramienta que cuente
tokens por sección de un archivo Markdown con el tokenizador correcto de cada plataforma
de destino (Claude Code, Codex/OpenAI, OpenCode, Antigravity/Gemini). Ninguna encontrada
lo hace; este documento es la base de ADR-001.

## 1. Claude (Anthropic)

**No existe tokenizador oficial local para Claude 3 en adelante.** El paquete
`@anthropic-ai/tokenizer` (TypeScript, MIT) fue archivado el 01/09/2026. Su propio README
dice: «this package can be used to count tokens for Anthropic's older models. As of the
Claude 3 models, this algorithm is no longer accurate». Fuente:
github.com/anthropics/anthropic-tokenizer-typescript.

**Vía oficial exacta:** `POST /v1/messages/count_tokens`. Gratis (no consume cuota de
mensajes), límite propio de 5.000 req/min en tier Start (independiente del límite de
`messages.create`), y el conteo **depende del modelo** pasado en el request. Desde Opus
4.7 el tokenizador cambia y da aproximadamente 30 % más tokens que en modelos anteriores
para el mismo texto; Claude Fable 5.1, Claude Mythos 5.1, Claude Fable 5 y Claude Opus 5
comparten ese tokenizador. Fuente: platform.claude.com/docs/en/build-with-claude/token-counting
(fetched 24/09/2026).

**Vía offline: `ctok`.** Paquete de terceros (no de Anthropic), autor Sander Land, licencia
MIT, PyPI 1.3.0 publicado 01/09/2026, requiere Python ≥3.12, única dependencia `regex`.
Reconstruye el tokenizador por «minimum-cost tiling» sobre el vocabulario medido, en tres
familias por rango de versión:

| Familia | Rango de versión | Modelos |
|---|---|---|
| v3 | `"3.0" ≤ v < "4.7"` | Claude 3 a Opus 4.6 |
| v4.7 | `"4.7" ≤ v < "4.8"` | Opus 4.7 |
| v4.8+ | `v ≥ "4.8"` | Opus 4.8, Sonnet 5, Fable 5 |

Precisión medida por el autor: 962.053 de 962.054 textos exactos en el corpus «Goldfish»
para v3, exactitud perfecta en MultiPL-E, Rosetta Code y UDHR; cero subconteos en
2.276.929 textos v3 y 2.328.425 textos v4.7. `tokenize()` devuelve **una** tesela de costo
mínimo válida, no una afirmación sobre la segmentación real de Anthropic. `token_count()`
incluye el marco del mensaje (roles, delimitadores); no hay función para contar sólo el
contenido. Fuente: pypi.org/project/ctok, github.com/sanderland/ctok (fetched 24/09/2026).

**Decisión para tokmd:** usar `ctok` como motor por defecto (offline, sin key, instantáneo)
y ofrecer `--verify` contra `count_tokens` (gratis, exacto) para que el usuario compruebe la
diferencia en su propio archivo. Ver ADR-001.

## 2. OpenAI (Codex, ChatGPT)

`tiktoken` (Apache 2.0-compatible, MIT en realidad — verificar en el paquete) es el
tokenizador oficial. Codex usa modelos GPT-5 y GPT-4o, que mapean al encoding
`o200k_base` (verificado ejecutando `tiktoken.encoding_for_model('gpt-5')` y
`tiktoken.encoding_for_model('gpt-4o')` con tiktoken 0.14.0 el 24/09/2026 — ambos
devuelven `o200k_base`, no `cl100k_base` como asumió la medición del 20/09 con `ttok`
usando `-m gpt-4`, que sí es `cl100k_base`).

## 3. OpenCode

No tiene tokenizador propio. Reenvía `AGENTS.md`, instrucciones y esquemas de herramientas
al modelo que el usuario configuró; el conteo correcto es el de ese proveedor. Herramientas
de terceros como `opencode-tokenscope` resuelven el tokenizador por modelo (tiktoken para
familia OpenAI, tokenizadores de Hugging Face para algunos Claude/Llama/DeepSeek/Mistral,
con fallback aproximado declarado). Fuente: github.com/ramtinJ95/opencode-tokenscope,
opencode.ai/docs (fetched 24/09/2026).

## 4. Google Gemini / Antigravity

Gemini sí tiene tokenizador local oficial: `vertexai.preview.tokenization`
(`get_tokenizer_for_model`), descarga el vocabulario una vez y cachea. También hay
`countTokens` gratis por API. Antigravity 1.2.9 corre modelos Gemini 3.x y lee
`~/.gemini/GEMINI.md`. Queda fuera de la v1 de tokmd (ver `docs/ROADMAP.md`) porque
requiere `google-cloud-aiplatform[tokenization]` (pesado) o una key de AI Studio que hoy
no existe en esta máquina.

## Conclusión

No existe, en ningún lado, una herramienta que combine (a) desglose por sección de un
archivo Markdown y (b) el tokenizador correcto según la plataforma que va a leer ese
archivo. `ttok` hace (parcialmente, sin secciones) sólo la mitad equivocada para Claude.
`ctok` resuelve el tokenizador de Claude pero no conoce secciones ni otras plataformas.
Ese cruce es lo que construye tokmd.
