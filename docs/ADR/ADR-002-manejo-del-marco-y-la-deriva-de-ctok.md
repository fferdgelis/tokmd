---
title: "ADR-002 — Manejo del marco de mensaje y la deriva de borde de ctok"
aliases:
  - "tokmd ADR-002"
project: tokmd
document_type: architecture-decision-record
adr_id: ADR-002
status: accepted
decision_date: 2026-09-24
created: 2026-09-24
updated: 2026-09-24
version: 0.1.0
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
tags:
  - project/tokmd
  - adr
related_documents:
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
---

# ADR-002 — Manejo del marco de mensaje y la deriva de borde de ctok

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Propuesta inicial, pendiente de medición en PBI-002. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Aceptado por Fabián. Medición real de PBI-002 cerrada. |

## Estado

`accepted`. Aceptado por Fabián Ferdgelis el 2026-09-25. Cerrado con la medición real
de PBI-002 en `docs/investigation/20260924-ctok-marco-y-deriva.md`: la deriva medida
es mayor a la esperada por bordes de palabra (confirmada estructural, escala con
`(N-1) × FRAME` para un documento de N filas), pero la opción 2 sigue siendo la
decisión — se reporta, como ya preveía este ADR, no se oculta.

## Contexto

`ctok.token_count(text, version)` incluye el marco del mensaje (roles y delimitadores del
formato de Anthropic) y no ofrece una función para contar sólo el contenido. tokmd
necesita tokens de secciones individuales de texto plano, sumables entre sí.

## Opciones

1. Reportar el número crudo de `ctok`, marco incluido, por cada sección. Rompe la
   aditividad: la suma de secciones no se acerca al total del archivo.
2. Medir `FRAME = token_count("", version)` una vez por familia y restarlo de cada
   sección. Aditividad aproximada, con posible deriva de borde de tokenización en los
   límites entre secciones.
3. Concatenar todo el archivo antes de tokenizar y repartir proporcionalmente. Pierde
   precisión por sección, que es el propósito central de la herramienta.

## Decisión propuesta

Opción 2. `FRAME` se mide una vez al importar `tokenizers.py`, por familia (`3`, `4.7`,
`4.8`), y se resta de cada `token_count(section, version)`. Se expone la constante y su
valor medido en el propio módulo con un comentario de la versión de `ctok` usada.

**Deriva de borde:** si `sum(Own de todas las filas) != token_count(archivo completo) −
FRAME`, tokmd imprime una línea `boundary drift: ±N` en vez de esconder la diferencia.
Se documenta como limitación conocida, no como bug, salvo que la medición real (PBI-002)
muestre una deriva mayor a la esperable por marcadores de palabra en los bordes.

## Consecuencias

El número que ve el usuario por sección es una aproximación aditiva, no una partición
exacta certificada por Anthropic. Se dice explícitamente en el README.

## Verificación y reversibilidad

PBI-002 mide `FRAME` real por familia y la deriva sobre los fixtures de prueba; los
valores quedan congelados como datos dorados en `tests/test_tokenizers.py`. Cambiar el
tratamiento del marco requiere actualizar este ADR y los datos dorados.
