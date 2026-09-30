---
title: "Tokenizadores offline por modelo: qué existe hoy para Gemini, DeepSeek, Kimi, GLM, Nemotron, Qwen, Llama, Mistral y OpenAI"
aliases:
  - "Relevamiento tokenizadores offline 20260930"
project: tokmd
document_type: research
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
  - "[[20260924-tokenizadores-por-plataforma]]"
  - "[[ADR-008-registro-de-tokenizadores-por-configuracion]]"
  - "[[PBI-010-registro-de-tokenizadores-multi-modelo]]"
---

# Tokenizadores offline por modelo: qué existe hoy

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. Datos traídos por un agente Sonnet consultando PyPI, la API de Hugging Face y código fuente en GitHub el 30/09/2026. Base del ADR-008 y del PBI-010. |

## Método y límites

Consultas directas a `pypi.org/pypi/<paquete>/json`, `huggingface.co/api/models/<id>`
y código fuente en `raw.githubusercontent.com`. **Ninguna carga real de
tokenizador se ejecutó** (`pip` no estaba disponible en el Bash del agente):
todo sale de metadatos y código leído. Lo que dice «no verificado» es eso.

## Tabla resumen

| Modelo | Offline | Motor Python | Id en Hugging Face (verificado 200) | `tokenizer.json` | Gated | Endpoint de conteo por API | Gratis |
|---|---|---|---|---|---|---|---|
| Claude (todos) | sí, reconstrucción | `ctok` | — | — | — | `POST /v1/messages/count_tokens` | **sí** (verificado 27/09) |
| OpenAI gpt-5.x / codex | sí, exacto texto plano | `tiktoken` 0.14.0 | — | — | — | `POST /v1/responses/input_tokens` | según foro sí; doc oficial no lo dice |
| Gemini 3.x | sí, **aproximado** (SentencePiece de Gemma, «text only») | `sentencepiece` + `.spiece.model` de Google | no aplica: `.spiece.model` de 4,7 MB en GitHub (`google/gemma_pytorch`), sha256 fijado | no | no | `models.countTokens` | no verificado |
| DeepSeek V4 Pro / Flash | sí | `tokenizers` | `deepseek-ai/DeepSeek-V4-Pro`, `deepseek-ai/DeepSeek-V4-Flash` | sí, 6,37 MB | no (MIT) | no hay; sólo un zip de demo | — |
| Kimi K3 | sí, pero formato `tiktoken.model` | `tiktoken` (`load_tiktoken_bpe`) | `moonshotai/Kimi-K3` | **no**: `tiktoken.model` de 2,8 MB + `tokenization_kimi.py` (requiere `transformers` si se usa su clase) | no («other») | `POST /v1/tokenizers/estimate-token-count` (api.moonshot.ai), con key | no verificado |
| GLM 5.3 | sí | `tokenizers` | `zai-org/GLM-5.3` (también `GLM-5`, `GLM-4.7`, MIT) | sí | no («other») | no investigado | — |
| Nemotron 3 Super | sí | `tokenizers` | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8` (y `-Base-BF16`) | sí, 17 MB | no («other») | no investigado | — |
| Qwen 3.5 / Qwen3-Coder | sí | `tokenizers` | `Qwen/Qwen3.5-9B`, `Qwen/Qwen3-Coder-480B-A35B-Instruct` | sí | no (Apache-2.0) | no investigado | — |
| Llama 4 Scout | sí, con licencia aceptada | `tokenizers` | `meta-llama/Llama-4-Scout-17B-16E-Instruct` | sí | **sí, `gated: manual`** (token de HF + aprobación) | no investigado | — |
| Mistral Large 3 | sí | `tokenizers` (o `mistral-common` para `tekken.json`) | `mistralai/Mistral-Large-3-675B-Instruct-2512-NVFP4` | sí (+ `tekken.json`) | no (Apache-2.0) | no investigado | — |

## Los tres hechos que deciden la arquitectura

1. **Un solo motor cubre a la mayoría.** DeepSeek, GLM, Nemotron, Qwen,
   Llama y Mistral publican `tokenizer.json` en formato de la librería
   `tokenizers` de Hugging Face. Esa librería (0.23.2) **no depende de
   torch**: el wheel de Windows pesa 2,9 MB y su única dependencia es
   `huggingface_hub`. Se descarga sólo el archivo con
   `huggingface_hub.hf_hub_download(id, "tokenizer.json")` y se carga con
   `tokenizers.Tokenizer.from_file(path)`. Un motor genérico «hf» con el id
   del repo como parámetro cubre seis familias de modelos.
2. **Gemini no se puede resolver con el paquete oficial sin arrastrar
   torch.** El extra `google-genai[local-tokenizer]` exige `torch`,
   `torchvision` y `transformers` — inaceptable para un CLI de 3 MB. Pero el
   código fuente de Google (`_local_tokenizer_loader.py`) muestra qué usa
   por dentro: para `gemini-3-pro-preview` / `gemini-3-flash-preview`, un
   SentencePiece `gemma3_cleaned_262144_v2.spiece.model` público en GitHub
   (4,7 MB, sha256 fijado); para `gemini-3.5-flash` / `gemini-3.1-*`, el
   tokenizador de `google/gemma-4-E4B-it` en Hugging Face. Se puede cargar
   el `.spiece.model` directamente con el paquete `sentencepiece` (chico,
   sin torch). Google lo llama explícitamente «local tokenizer for text
   only token counting»: **es una aproximación**, no el conteo facturado.
   Para el número exacto está `countTokens` por API.
3. **Kimi es el caso raro.** No publica `tokenizer.json` sino
   `tiktoken.model` (formato BPE de OpenAI) más una clase Python que
   depende de `transformers`. Contarlo sin `transformers` exige reconstruir
   un `tiktoken.Encoding` a mano (patrón de regex + tokens especiales
   sacados de `tokenization_kimi.py`). Es factible pero no está probado, y
   el oracle para verificarlo (`estimate-token-count`) exige key de
   Moonshot. **Queda fuera del primer corte**; entra cuando haya un
   testigo contra el que medirlo.

## Cosas que quedaron sin verificar (para el spike del PBI)

- Que `Tokenizer.from_file` sobre el `tokenizer.json` de cada modelo dé el
  mismo conteo que la clase oficial de `transformers` (debería, es el mismo
  archivo; hay que probarlo con un texto con acentos, código y emoji).
- Si `glm-5.3-flash` comparte tokenizador con `zai-org/GLM-5.3`.
- Si las variantes FP8/NVFP4/Base de Nemotron usan el mismo vocabulario.
- Si `google/gemma-4-E4B-it` es gated en Hugging Face (los Gemma suelen
  pedir aceptar licencia).
- Si `countTokens` de Gemini y `estimate-token-count` de Kimi son gratis.
- `gpt-6` / `gpt-6-astra` **no figuran** en `tiktoken/model.py`; el mapeo
  por prefijo `gpt-5` → `o200k_base` existe. Para gpt-6 hay que fijar el
  encoding en configuración hasta que tiktoken lo agregue.

## Lo que ninguna de estas familias tiene y Claude sí

Un **marco de mensaje medido** (los 5 tokens por trozo de ADR-007). Para
los modelos de Hugging Face el conteo es de **contenido**: lo que cuesta la
plantilla de chat de cada proveedor no está en `tokenizer.json`. tokmd tiene
que decirlo en la salida en vez de fingir que el número es lo facturado.
