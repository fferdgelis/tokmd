---
title: "tiktoken: deriva de borde por fusión BPE entre secciones"
aliases:
  - "Investigación deriva tiktoken tokmd"
project: tokmd
document_type: research
status: active
version: 0.1.0
created: 2026-09-25
updated: 2026-09-25
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
  - reference/tokens
related_documents:
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
  - "[[PBI-003-tokenizador-openai]]"
  - "[[20260924-ctok-marco-y-deriva]]"
---

# tiktoken: deriva de borde por fusión BPE entre secciones

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-25 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación. Hallazgo durante PBI-003: la hipótesis de aditividad exacta era falsa, medido con el rol TDD (DeepSeek). |

## El hallazgo, contra la hipótesis original de PBI-003

PBI-003 asumía (AC-02 original, corregido más abajo): "dado el mismo texto partido
en secciones, cuando se suman los conteos, entonces la suma es exactamente igual
al conteo del texto completo (sin deriva, a diferencia de Claude)". **Es falso.**
`tiktoken` también tiene deriva de borde entre secciones — no por un marco de
mensaje que restar (OpenAI no tiene eso; a diferencia de Claude, `count_openai`
no resta nada), sino por cómo el algoritmo BPE decide dónde cortar un token.

## Por qué pasa: fusión de BPE en el borde

BPE (Byte Pair Encoding, el algoritmo detrás de `tiktoken`) no tokeniza carácter
por carácter ni palabra por palabra: agrupa según qué combinaciones son más
frecuentes en el corpus de entrenamiento, y esa decisión depende del contexto
inmediato — qué hay *después* del texto que se está tokenizando, no sólo el texto
en sí. Cuando una sección termina con un espacio y esa misma sección se tokeniza
sola (sin nada después), el espacio queda como su propio token, aislado. Cuando
esa sección forma parte de un documento más largo, ese mismo espacio se funde con
la primera palabra de lo que sigue, y los dos ocupan menos tokens juntos que por
separado. El resultado: la suma de los conteos por sección da **más** tokens que
el conteo del documento completo — al revés que en Claude, donde ADR-002 resta
`FRAME` por fila y la suma termina dando **más**, no menos, por otra razón
distinta (ahí es overhead de mensaje restado de más veces, acá es fusión de BPE
que ocurre menos veces cuando se corta el texto).

## Medición de control (texto sintético)

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
parts = [
    "The quick brown fox jumps over the lazy dog. ",
    "Pack my box with five dozen liquor jugs. ",
    "How vexingly quick daft zebras jump! ",
    "Sphinx of black quartz, judge my vow.",
]
joined = "".join(parts)
sum(len(enc.encode(p)) for p in parts)  # == 43
len(enc.encode(joined))                  # == 40, 3 tokens menos
```

Congelado como dato dorado en `tests/test_tokenizers_openai.py`
(`test_count_openai_additivity_is_not_guaranteed`, generado por el rol TDD tras
el gap encontrado — `tools/deepseek/specs/PBI-003-gap-01.md.prompt`).

## Medición sobre los fixtures reales del proyecto

Mismo método que `docs/investigation/20260924-ctok-marco-y-deriva.md`: parsear
con `parse_sections`, sumar `count_openai` sobre el `own_text` de cada fila no
vacía, comparar contra `count_openai` del archivo completo.

| Fixture | Encoding | Archivo completo | Suma de secciones | Deriva |
|---|---|---|---|---|
| `empty.md.fixture` | `o200k_base` | 0 | 0 | 0 |
| `no_headings.md.fixture` | `o200k_base` | 17 | 17 | 0 |
| `sample.md.fixture` | `o200k_base` | 91 | 80 | 11 (≈12 %) |

`sample.md.fixture` tiene 5 filas con `own_text` no vacío (front matter,
preámbulo, tres secciones) — 4 bordes entre filas, cada uno una oportunidad de
fusión de BPE. 11 tokens de deriva sobre 4 bordes es consistente con el orden de
magnitud del ejemplo sintético (3 tokens sobre 3 bordes).

## Decisión: mismo criterio que ADR-002, sin ADR nuevo

Confirmado por Fabián Ferdgelis el 2026-09-25: se trata igual que la deriva de
Claude — **se reporta, no se oculta**, sin intentar neutralizarla con trucos de
tokenización (separadores especiales, no unir con espacio, etc.). No se abre un
ADR nuevo para esto: es la misma decisión de ADR-002 (opción 2: aditividad
aproximada, deriva visible), aplicada también a OpenAI porque la medición muestra
que la premisa de "OpenAI no la necesita" era falsa. Queda para una fase de CLI
(PBI-004/005) implementar el mensaje `boundary drift: ±N` para ambas plataformas,
no sólo Claude — `count_openai` en sí no cambia: sigue siendo una llamada directa
a `tiktoken`, exacta para cualquier texto individual, sin nada que restar.

## AC-02 de PBI-003, corregido

El texto original de AC-02 ("la suma es exactamente igual al conteo del texto
completo, sin deriva") queda reemplazado por: "dado el mismo texto partido en
secciones, cuando se suman los conteos, entonces la deriva contra el conteo del
texto completo (si existe) se mide y se puede reportar — no se asume aditividad
exacta". Ver `docs/PBI/PBI-003-tokenizador-openai.md`, sección 3, para el texto
vigente.
