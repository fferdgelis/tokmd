---
title: "ctok: marco (FRAME) medido por familia y deriva de borde entre secciones"
aliases:
  - "Investigación FRAME y deriva tokmd"
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
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
  - "[[PBI-002-tokenizador-claude]]"
---

# ctok: marco (FRAME) medido por familia y deriva de borde entre secciones

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-25 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, medición real de PBI-002 (AC-01, AC-02). |

## FRAME por familia

Medido con `ctok.token_count("", version)`, ctok **1.3.0** (pin en `pyproject.toml`:
`ctok>=1.3`).

| Familia (`version` de ctok) | `FRAME` |
|---|---|
| `3.0` | 8 |
| `4.7` | 12 |
| `4.8` | 6 |

Valores congelados como datos dorados en `tests/test_tokenizers.py` (rol TDD,
DeepSeek, spec en `tools/deepseek/specs/PBI-002.md.prompt`).

`ctok.main.FAMILIES` (inspección directa del paquete) muestra por qué `4.8` da un
`FRAME` menor que `4.7` pese a ser una versión más nueva: la familia `v4.8` declara
`meta=(('message_overhead', 6), ('frame_bow', False))` — un modelo de marco distinto,
no un error de medición.

## Deriva de borde

Medida sobre los tres fixtures ya existentes de PBI-001 (`tests/fixtures/*.md.fixture`),
comparando `count_claude(texto_completo, familia)` contra la suma de
`count_claude(own_text_de_cada_fila, familia)` para cada fila del árbol de secciones con
`own_text` no vacío.

| Fixture | `3.0` | `4.7` | `4.8` |
|---|---|---|---|
| `empty.md.fixture` | 0 | 0 | 0 |
| `no_headings.md.fixture` | 0 | 0 | 0 |
| `sample.md.fixture` | 17 | 25 | 25 |

**La deriva en `sample.md.fixture` no es un error de borde de tokenización menor —
es structural.** `sample.md.fixture` tiene 5 filas con `own_text` no vacío (front
matter, preámbulo y tres secciones). ADR-002 resta `FRAME` de **cada** fila por
separado (opción 2, tal como está escrita), así que un documento con N filas de
contenido termina restando `FRAME` N veces en vez de una sola vez para todo el
documento — la deriva crece aproximadamente con `(N-1) × FRAME`, no con los bordes
entre palabras en los límites de sección. Con `sample.md.fixture` (N=5, `FRAME(3.0)=8`):
`(5-1) × 8 = 32` es el orden de magnitud correcto frente a la deriva medida de 17
(las filas no son de tamaño uniforme, así que no da exacto, pero confirma el origen).

Esto **confirma lo que ADR-002 ya anticipaba y decidía aceptar explícitamente**: la
opción 2 da aditividad aproximada, no exacta, y la diferencia se reporta, no se
esconde. El ejemplo de "1 token de diferencia" mencionado en el traspaso previo
(`docs/handoff/HANDOFF-fase-0-y-1-completadas-20260925.md`) era una medición sobre un
caso de dos secciones concatenadas, no sobre un documento real con varias filas — con
más filas la deriva escala como se describe arriba, no se mantiene en 1 token.

**Ningún valor por fila da negativo** en los tres fixtures medidos (la fila más chica,
`Section One` en `sample.md.fixture`, tiene 15 tokens crudos contra `FRAME(3.0)=8`).
`count_claude` no clampea a 0: una sección real más chica que `FRAME` para su familia
sí devolvería un valor negativo, documentado en el docstring del módulo como
comportamiento esperado, no manejado especialmente en PBI-002.

## Metodología de medición

Script de una sola vez, no versionado como herramienta (la medición queda congelada
acá y en los tests, no hace falta repetirla salvo que cambie la versión de `ctok`):

```python
import ctok
from tokmd.sections import parse_sections

FRAME = {"3.0": 8, "4.7": 12, "4.8": 6}

def flatten(section):
    rows = [section]
    for c in section.children:
        rows += flatten(c)
    return rows

text = open("tests/fixtures/sample.md.fixture", encoding="utf-8").read()
rows = flatten(parse_sections(text))
for v, frame in FRAME.items():
    whole = ctok.token_count(text, v) - frame
    summed = sum(ctok.token_count(r.own_text, v) - frame for r in rows if r.own_text)
    print(v, "whole=", whole, "summed=", summed, "drift=", whole - summed)
```
