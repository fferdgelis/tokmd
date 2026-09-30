---
title: "PBI-010 — casos de prueba para Kiwi (registro de tokenizadores, motores hf y sentencepiece, sin regresión)"
aliases:
  - "PBI-010 casos de prueba"
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
  - qa
related_documents:
  - "[[PBI-010-registro-de-tokenizadores-multi-modelo]]"
  - "[[ADR-008-registro-de-tokenizadores-por-configuracion]]"
  - "[[PBI-009-casos-de-prueba]]"
---

# PBI-010 — casos de prueba

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación, junto con el PBI. Dieciséis casos. Pendiente de cargar a Kiwi como PROPOSED cuando Fabián acepte el PBI. Los datos dorados de los motores nuevos quedan **vacíos a propósito** hasta el spike AC-14. |

## Para qué sirve este documento

Es la fuente de la que se cargan los casos a Kiwi, escrita **antes** de
tocar el código (ROL-03). Cada caso lleva la columna «qué falla caza»: la
modificación concreta que tiene que hacerlo fallar. Es lo que faltó en
PBI-001/005 y dejó pasar tres bugs (ver PBI-009).

**Estado:** `PROPOSED`, sin cargar. Plan de Kiwi: nuevo, para PBI-010.

## Datos dorados

| Dato | Valor | Origen |
|---|---|---|
| `CLAUDE.md` global, `claude-code` (Sonnet 5 / Opus 5 / 4.8) | **17.381** | API `count_tokens`, 27/09/2026; igual en tokmd 2.0.0 |
| `CLAUDE.md` global, `codex` (o200k_base) | **10.742** | tiktoken, 27/09/2026; igual en tokmd 2.0.0 |
| `CLAUDE.md` global, `claude-sonnet-4-6` (familia 3.0) | **13.076** | API `count_tokens`, 27/09/2026 (Sonnet 4.6 y Haiku 4.5) |
| Texto de control (`control_2kb.md.fixture`, 1.189 chars, sha256 `6cbac76c2fdb7e7f…`), `deepseek-v4-pro` | **395** | spike AC-14, 30/09/2026, `tokenizers` 0.23 |
| ídem, `deepseek-v4-flash` | **395** (mismo `tokenizer.json` que Pro, sha256 idéntico) | ídem |
| ídem, `glm-5.3` | **386** | ídem |
| ídem, `qwen3.5` | **411** | ídem |
| ídem, `nemotron-3-super` | **399** | ídem |
| ídem, `mistral-large-3` | **399** sin tokens especiales; 400 con (`add_special_tokens=True` agrega BOS) | ídem — **el motor `hf` cuenta siempre con `add_special_tokens=False`**; es el único de los seis donde importa |
| ídem, `gemini-3-flash` (spiece gemma3) | **411** | spike AC-14, `sentencepiece` 0.2 |

sha256 de los archivos de tokenizador (para el campo `sha256` opcional del
registro y para detectar cambios silenciosos en Hugging Face):

| Archivo | Tamaño | sha256 |
|---|---|---|
| `deepseek-ai/DeepSeek-V4-Pro` y `-Flash` · `tokenizer.json` | 6.367.146 | `8f9f37ca37fdc4f5fd36d5cf4d3b0e8392edb4e894fd10cc0d70b4957c8633cf` |
| `zai-org/GLM-5.3` · `tokenizer.json` | 20.217.442 | `19e773648cb4e65de8660ea6365e10acca112d42a854923df93db4a6f333a82d` |
| `Qwen/Qwen3.5-9B` · `tokenizer.json` | 12.807.982 | `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42` |
| `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8` · `tokenizer.json` | 17.077.484 | `623c34567aebb18582765289fbe23d901c62704d6518d71866e0e58db892b5b7` |
| `mistralai/Mistral-Large-3-675B-Instruct-2512-NVFP4` · `tokenizer.json` | 17.078.110 | `577575622324b2e099e2648be26bdeb5e5815ffe66d7004e9e3ddbf421db6bf1` |
| gemma3 `gemma3_cleaned_262144_v2.spiece.model` (commit `014acb7…` de `google/gemma_pytorch`) | 4.689.074 | `1299c11d7cf632ef3b4e11937501358ada021bbdf7c47638d13c0ee982f2e79c` |

**Resultado del spike: 7 de 7 cargan** con `Tokenizer.from_file` /
`SentencePieceProcessor`, sin `transformers` ni torch. Salida cruda del
script en el dev-log del 30/09. Descarga total: ~78 MB (GLM es el más
pesado, 20 MB); una vez por máquina, en el caché de `huggingface_hub`.

El texto de control es `tests/fixtures/control_2kb.md.fixture` (extensión
`.fixture` como los demás fixtures del repo, para que el hook de gobernanza
Markdown no le exija front matter): castellano con acentos y «comillas», un
bloque de código Python, una tabla Markdown, un emoji y una URL. Se escribe
una vez y no se vuelve a tocar.

## Casos

| Id | Nombre | Precondición | Pasos | Resultado esperado | Qué falla caza |
|---|---|---|---|---|---|
| **TOK-010-C01** | El registro empaquetado se lista | tokmd 2.1.0 instalado sin extras | `tokmd --list-models` | Sale con 0; una línea por entrada con nombre, motor, `bundled`; `gemini-3-flash` marcado `approx`; incluye `claude-sonnet-5`, `gpt-5`, `deepseek-v4-pro`, `glm-5.3` | Registro que no carga o `--list-models` inexistente |
| **TOK-010-C02** | Entrada de usuario se agrega | `tests/fixtures/registry_user.toml` con `[models.mi-modelo]` `engine="hf"` `repo="x/y"`; `hf_hub_download` parcheado al fixture | `tokmd control_2kb.md --model mi-modelo --registry registry_user.toml` | Cuenta con el tokenizador del fixture; `--list-models` muestra `mi-modelo` con origen `user` | Registro de usuario ignorado |
| **TOK-010-C03** | Entrada de usuario pisa una empaquetada, y sólo esa | TOML de usuario redefine `claude-sonnet-5` con `family="4.7"` | `tokmd CLAUDE.md --model claude-sonnet-5 --registry ...` y `--list-models` | Cuenta con familia 4.7 (número distinto a 17.381 en ≥1 token); `--list-models` muestra `claude-sonnet-5` como `user` y **todas las demás** como `bundled` | Fusión que pisa el registro entero en vez de entrada por entrada |
| **TOK-010-C04** | Motor desconocido falla antes de contar | TOML con `engine="magia"` | `tokmd control_2kb.md --model malo --registry ...` | Exit 2; mensaje con el nombre `malo`, el campo `engine` y la ruta del TOML; **stdout vacío** | Validación perezosa que revienta a mitad de conteo |
| **TOK-010-C05** | Parámetro obligatorio faltante | TOML con `engine="hf"` sin `repo` | ídem | Exit 2; mensaje nombra `repo` | Defaults silenciosos para parámetros obligatorios |
| **TOK-010-C06** | Sin regresión: Claude | `CLAUDE.md` global del snapshot (copia como fixture, como en PBI-009) | `tokmd CLAUDE.md` | **17381** | Cualquier cambio en el camino `ctok` al meter el registro |
| **TOK-010-C07** | Sin regresión: OpenAI | ídem | `tokmd CLAUDE.md --platform codex` | **10742** | ídem para `tiktoken` |
| **TOK-010-C08** | Sin regresión: suite de 2.0.0 | snapshot | `uv run pytest` | Los 77 tests de 2.0.0 en verde, más los nuevos | Reemplazo del resolutor que cambia una aserción vieja |
| **TOK-010-C09** | Motor `hf` = librería `tokenizers` | fixture `tiny_tokenizer.json`; `hf_hub_download` parcheado | Contar `control_2kb.md` con una entrada `hf` que apunte al fixture; comparar con `len(Tokenizer.from_file(fixture).encode(texto).ids)` | Iguales | Motor que agrega/quita tokens especiales o BOS por su cuenta |
| **TOK-010-C10** | `--offline` sin caché falla sin red | `hf_hub_download` parcheado para lanzar si se llama; caché vacío | `tokmd control_2kb.md --model deepseek-v4-pro --offline` | Exit ≠ 0; mensaje con repo y archivo; **el parche no fue invocado** | Descarga aunque se pidió offline |
| **TOK-010-C11** | Aviso de descarga va a stderr, no a stdout | `hf_hub_download` parcheado que «descarga» al fixture y registra la llamada | `tokmd control_2kb.md --model deepseek-v4-pro 2>err.txt >out.txt` | `out.txt` = sólo el número; `err.txt` contiene el repo y `tokenizer.json` | Mensaje mezclado en stdout que rompe `tokmd f.md \| algo` |
| **TOK-010-C12** | `sha256` incorrecto en `sentencepiece` falla | Entrada `sentencepiece` con `sha256` que no coincide con el archivo local (parcheado) | `tokmd control_2kb.md --model gemini-3-flash --registry ...` | Exit ≠ 0; mensaje nombra la entrada y «sha256» | Hash declarado pero no verificado |
| **TOK-010-C13** | Extra no instalado, mensaje útil | Entorno sin `tokenizers` (parchear `importlib` o `sys.modules["tokenizers"] = None`) | `tokmd control_2kb.md --model deepseek-v4-pro` | Exit ≠ 0; mensaje contiene `pip install "tokmd[hf]"`; **y** `tokmd control_2kb.md` (Claude) sigue funcionando en el mismo entorno | `import tokenizers` a nivel de módulo que rompe todo el CLI |
| **TOK-010-C14** | La salida dice qué contó | cualquier archivo | `--format json` con `claude-code`, con una entrada `hf` y con `gemini-3-flash` | JSON con `model`, `engine`, `approx`, `content_only`: `(false,false)`, `(false,true)`, `(true,true)` respectivamente; en `table` una cabecera con lo mismo | Número sin etiqueta |
| **TOK-010-C15** | Familia 3.0 contra la API | `CLAUDE.md` global | `tokmd CLAUDE.md --model claude-sonnet-4-6` | **13076** | `frame` de 3.0 medido con `token_count("")` en vez de por diferencia (ADR-007) |
| **TOK-010-C16** | Los `tokenizer.json` reales cargan (spike AC-14) | red disponible **una vez**; fuera de la suite de pytest | Script `tools/spike/pbi010_hf_load.py`: baja los `tokenizer.json` + el `.spiece.model`, cuenta `control_2kb.md.fixture`, imprime conteo y sha256 | Los cinco cargan; los conteos y hashes quedan copiados en la tabla de datos dorados de este documento | Un `tokenizer.json` que la librería `tokenizers` no lee (formato viejo, `tekken.json`, etc.) |

## Registro en Kiwi

Mismo procedimiento verificado en PBI-009 (`tools/kiwi/cargar_casos.py`,
credencial `kiwi-tcms / qa-bot-password` de la bóveda DPAPI, puerto 443
desde Windows). Identidad de cada caso por el prefijo `TOK-010-Cnn -`, no
por el `summary` completo (lección de BUG-006 y del loader de PBI-009).
Plan nuevo, nombre `PBI-010 — Registro de tokenizadores`.
