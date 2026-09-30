---
title: "ADR-008 — Registro de tokenizadores por configuración: un motor genérico de Hugging Face y modelos dados de alta en un archivo, no en el código"
aliases:
  - "ADR-008 registro de tokenizadores"
project: tokmd
document_type: adr
status: proposed
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
  - adr
related_documents:
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
  - "[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]"
  - "[[20260930-tokenizadores-offline-por-modelo]]"
  - "[[20260930-de-cli-a-producto-para-equipos]]"
  - "[[PBI-010-registro-de-tokenizadores-multi-modelo]]"
---

# ADR-008 — Registro de tokenizadores por configuración

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Borrador a pedido de Fabián: «dar de alta más LLMs a través del archivo de configuración» como la apuesta multi-plataforma que ningún proveedor va a hacer. Pendiente de su decisión. |

## Estado

`proposed`. Pendiente de la decisión de Fabián Ferdgelis. **Bloquea
`[[PBI-010-registro-de-tokenizadores-multi-modelo]]`.**

## Contexto

tokmd 2.0.0 conoce dos motores, cableados en `src/tokmd/cli.py`
(`resolve_tokenizer`): `ctok` para Claude y `tiktoken` para OpenAI. Agregar
un modelo hoy es tocar código: un `if` más en el resolutor, un diccionario
más en `tokenizers.py`, un release. La plataforma `antigravity` figura en
el CLI desde la 1.0 y sigue devolviendo «planned for 1.1».

El 30/09/2026 Fabián decidió que la apuesta del producto es lo que
`[[20260930-de-cli-a-producto-para-equipos]]` identificó como el único foso
que un proveedor no va a cubrir: **contar bien para todos los modelos que un
equipo usa, no sólo para el del proveedor**. Y pidió que la forma sea un
archivo de configuración donde se dan de alta los modelos.

El relevamiento `[[20260930-tokenizadores-offline-por-modelo]]` cambia el
costo de esa apuesta: **seis familias de modelos abiertos (DeepSeek, GLM,
Nemotron, Qwen, Llama, Mistral) publican su tokenizador en el mismo
formato**, el `tokenizer.json` de la librería `tokenizers` de Hugging Face,
que pesa 2,9 MB y no arrastra torch. Un solo motor genérico, parametrizado
con el id del repo, los cubre a todos. Gemini se cubre con `sentencepiece`
y el modelo público de Gemma que Google usa por dentro (aproximado, y Google
lo dice). Kimi queda para después: publica en formato `tiktoken.model` y
exige reconstrucción manual sin testigo contra el que medir.

## Opciones

### Opción A — Seguir agregando motores en el código, uno por proveedor

Un módulo `count_gemini`, un `count_deepseek`, etc., cada uno con su `if`
en el resolutor.

- **Pros:** es lo que hay; no cambia la arquitectura.
- **Contras:** cada modelo nuevo es un PR y un release; el usuario no puede
  agregar el suyo; seis familias que usan el mismo formato terminarían en
  seis funciones iguales. Es exactamente lo contrario de lo que Fabián
  pidió.

### Opción B — Registro de tokenizadores en un archivo TOML, con motores genéricos

Un archivo `tokenizers.toml` **empaquetado con tokmd** (el registro base) y
uno **del usuario** (`~/.config/tokmd/tokenizers.toml` en Linux/macOS,
`%APPDATA%\tokmd\tokenizers.toml` en Windows, o `--registry <ruta>`) que lo
extiende o lo pisa entrada por entrada. Cada entrada declara **qué motor**
y **con qué parámetros**:

```toml
[models.claude-sonnet-5]
engine = "ctok"
family = "4.8"
frame  = 5                    # ADR-007: costo fijo por trozo, medido
verify = "anthropic"          # qué API puede confirmar el número

[models.gpt-5]
engine   = "tiktoken"
encoding = "o200k_base"

[models.gpt-6]                # tiktoken todavía no lo lista: se fija acá
engine   = "tiktoken"
encoding = "o200k_base"

[models.deepseek-v4-pro]
engine = "hf"
repo   = "deepseek-ai/DeepSeek-V4-Pro"   # baja sólo tokenizer.json (6,4 MB)

[models.glm-5.3]
engine = "hf"
repo   = "zai-org/GLM-5.3"

[models.gemini-3-flash]
engine  = "sentencepiece"
url     = "https://raw.githubusercontent.com/google/gemma_pytorch/014acb7.../tokenizer/gemma3_cleaned_262144_v2.spiece.model"
sha256  = "..."
approx  = true                # Google: «text only token counting»

[platforms]
claude-code = "claude-sonnet-5"
codex       = "gpt-5"
antigravity = "gemini-3-flash"
opencode    = ""              # exige --model
```

Motores (cada uno un módulo chico con una sola función `count(text) -> int`):

| Motor | Librería | Parámetros | Exactitud |
|---|---|---|---|
| `ctok` | `ctok` (ya está) | `family` | exacto contra la API (verificado 27/09) |
| `tiktoken` | `tiktoken` (ya está) | `encoding` | exacto para texto plano |
| `hf` | `tokenizers` + `huggingface_hub` (nuevo, extra opcional) | `repo`, opcional `file` (default `tokenizer.json`), opcional `revision` | exacto para contenido; sin plantilla de chat |
| `sentencepiece` | `sentencepiece` (nuevo, extra opcional) | `url` o `repo`+`file`, `sha256` | aproximado (lo dice Google) |

Las librerías nuevas son **extras** de `pyproject.toml` (`tokmd[hf]`,
`tokmd[gemini]`, `tokmd[all]`) y se importan sólo cuando una entrada las
pide. Sin extras, tokmd sigue pesando lo que pesa hoy y `tokmd archivo.md`
sigue sin red. La descarga de un `tokenizer.json` pasa por el caché de
`huggingface_hub` (una vez por máquina); si no hay red y no está en caché,
error claro, no cuelgue.

- **Pros:** un modelo nuevo es una entrada de TOML, sin release; el usuario
  agrega los suyos (incluidos privados o gated, con su propio token de HF);
  seis familias con un motor; `--platform` pasa a ser un alias del registro
  en vez de un `if`; `tokmd models` lista lo que hay. Es lo que Fabián
  pidió, y es el foso.
- **Contras:** hay que decidir la política de caché y de red (abajo); un
  registro que el usuario puede pisar es un registro que el usuario puede
  romper (se valida al cargar y se dice qué entrada está mal); dos
  dependencias opcionales más que mantener.

### Opción C — Plugins Python (entry points) en vez de TOML

Cada motor es un paquete instalable que se registra por `entry_points`.

- **Pros:** máxima extensibilidad.
- **Contras:** para dar de alta un modelo hay que escribir y publicar un
  paquete; es lo contrario de «un archivo de configuración». Sobredimensionado
  para seis familias que comparten formato. Los motores de la opción B son
  módulos internos; si algún día hace falta un motor de terceros, se agrega
  entry points **encima** del registro, no en vez de.

## Decisión propuesta

**Opción B.** Con estas reglas fijas, para que el registro no convierta la
herramienta en algo que miente con más modelos:

1. **La salida dice qué contó.** Toda salida (tabla, JSON) lleva el nombre
   del modelo del registro, el motor, y una marca `approx` cuando el motor
   es aproximado (Gemini) o cuando el conteo es de contenido sin marco
   (todos los `hf`). El número sin su etiqueta no se muestra.
2. **El marco se declara por entrada o es cero explícito.** `frame` sólo se
   pone donde está medido (Claude: 5, ADR-007). Para `hf` y `sentencepiece`
   es `0` y la salida lo dice: «content tokens, chat template not
   included». Nada de inventar un marco por analogía.
3. **Sin red por defecto.** `tokmd archivo.md` con `claude-code` sigue
   100 % offline. Un motor `hf` descarga su `tokenizer.json` la primera vez
   que se usa **y avisa en stderr qué baja y de dónde**; `--offline` prohíbe
   toda descarga y falla si falta el archivo. Nunca se descarga un modelo
   entero: sólo el archivo del tokenizador (`hf_hub_download` de un archivo,
   no `snapshot_download`).
4. **El registro se valida al cargar.** Entrada con motor desconocido,
   parámetro faltante o `sha256` que no coincide → error con el nombre de la
   entrada y el archivo de donde vino, antes de contar nada.
5. **La prioridad es fija:** `--model` explícito > `--platform` (alias del
   registro) > default (`claude-code`). El registro del usuario pisa el
   empaquetado entrada por entrada, nunca entero.
6. **`--verify` no se extiende en este ADR.** Sigue siendo sólo Anthropic.
   Extenderlo a otros oráculos (Gemini `countTokens`, Kimi
   `estimate-token-count`, OpenAI `input_tokens`) es un ADR aparte cuando se
   sepa cuáles son gratis.

## Consecuencias

- `resolve_tokenizer` y `PLATFORMS` en `cli.py` se reemplazan por la carga
  del registro; `--claude-family`, `--encoding` y `--tokenizer` quedan como
  atajos que sobreescriben parámetros de la entrada elegida, para no romper
  a quien los usa hoy. Es cambio de contrato interno, no de CLI: `tokmd
  archivo.md` sigue dando `17381`. Versión **2.1.0** (agrega, no rompe).
- Kimi K3 no entra hasta tener testigo. Se deja documentado en el registro
  como comentario, no como entrada.
- Los datos dorados de tests para los motores nuevos son de
  **autoconsistencia** (el conteo de tokmd = el de la librería sobre el
  mismo archivo) más un fixture pinneado por modelo. No hay oráculo externo
  gratis verificado para ninguno; el ADR lo dice en vez de fingirlo.
- Un usuario de Antigravity obtiene por fin un número, marcado `approx`.
  Es mejor que «planned for 1.1» y peor que exacto; las dos cosas se dicen.

## Verificación y reversibilidad

- **Se verifica** con PBI-010: el mismo archivo contado con `--model
  deepseek-v4-pro` da lo mismo que `tokenizers.Tokenizer.from_file(...)
  .encode(texto)` directo; el registro del usuario pisa una entrada y se ve
  en `tokmd models`; `--offline` sin caché falla con mensaje y exit code;
  `claude-code` sigue dando 17.381 sobre el `CLAUDE.md` global.
- **Se revierte** quitando el registro y volviendo al resolutor cableado:
  los motores `ctok` y `tiktoken` no cambian, así que la marcha atrás es
  borrar `registry.py` y los dos motores nuevos. Nada de datos de usuario
  se pierde (el archivo TOML del usuario queda inerte).

## Lo que este ADR NO decide

- Qué modelos van en el registro **empaquetado** más allá de los del
  relevamiento (eso es una lista en el PBI, no arquitectura).
- Nada de `--verify` para otros proveedores.
- Nada del escaneo recursivo (`tokmd .`), que es otro PBI y no depende de
  este.
