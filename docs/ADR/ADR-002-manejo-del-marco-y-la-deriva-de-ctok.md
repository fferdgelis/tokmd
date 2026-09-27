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
updated: 2026-09-27
version: 0.3.0
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
  - "[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]"
---

# ADR-002 — Manejo del marco de mensaje y la deriva de borde de ctok

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-24 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Propuesta inicial, pendiente de medición en PBI-002. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Aceptado por Fabián. Medición real de PBI-002 cerrada. |
| 2026-09-27 | 0.3.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | **Corrección por `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]` (aceptado el mismo día).** Lo que esta versión llamaba «deriva de borde de tokenización» no era deriva: era `FRAME` mal medido. `FRAME = token_count("", version)` mide **6** para la familia `4.8`, pero el costo marginal real de un trozo adicional es **5** — medido en 17 archivos reales, residuo 0 sin excepciones cuando se corta en saltos de línea. Y el total **no** se resta el marco: es igual al conteo crudo de una pasada, porque el marco es parte de lo que Anthropic factura. Sección «Decisión propuesta» y «Consecuencias» reescritas; el resto del documento queda como registro histórico de lo que se creía el 2026-09-24/25. |

## Estado

`accepted`, **con la corrección de la v0.3.0**. Aceptado originalmente por Fabián
Ferdgelis el 2026-09-25; la corrección del 2026-09-27 no reabre la decisión (opción
2 sigue siendo la correcta: restar un costo fijo del `content` de cada sección),
corrige el **valor** de ese costo fijo y **retira** la afirmación de que hay
deriva de borde entre secciones — no la hay, cuando el corte cae en un salto de
línea, que es como corta el parser de `tokmd`.

### Lo que se creía el 2026-09-24/25 (superado, se deja como historial)

Cerrado con la medición real de PBI-002 en
`docs/investigation/20260924-ctok-marco-y-deriva.md`: la deriva medida era mayor a
la esperada por bordes de palabra (se creía «confirmada estructural», escalando
con `(N-1) × FRAME` para un documento de N filas), pero la opción 2 seguía siendo
la decisión — se reportaba, como preveía este ADR, no se ocultaba.

**Verificado el 2026-09-27, en `ADR-007`:** esa «deriva estructural» era
aritméticamente exacta en su forma —`(N-1) × K`— pero con el número equivocado:
no es `FRAME` (6), es el costo marginal real (5). Con el número correcto, el
residuo es **0** en los 17 archivos medidos, no una deriva irreducible.

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

## Decisión propuesta (corregida 2026-09-27, ver ADR-007)

Opción 2, con el número corregido. El costo fijo por trozo (llamado `FRAME` en la
v0.1.0/0.2.0) **no** se mide como `token_count("", version)` — eso da 6 para la
familia `4.8`, un token más de lo real. Se mide como el costo marginal de un
corte adicional (medido y verificado: **5** para `4.8`), y se resta **una vez por
cada sección**, tal como decidía esta opción.

**El total del archivo NO resta este costo fijo.** Se cuenta de una sola pasada
sobre el texto completo (`token_count(archivo, version)`, crudo), porque el
costo fijo es parte de lo que Anthropic factura, no un overhead a descontar del
total. Restarlo del total —lo que hacía la implementación hasta el 2026-09-27—
daba un número por debajo de lo que la API cobra.

**Línea de deriva, redefinida como control:** `tokmd` imprime siempre una línea
`boundary drift: ±N` con `N = token_count(archivo) − Σ Own`. Con el costo fijo
correcto y cortando en saltos de línea (que es como corta el parser), **`N` es
siempre `0`.** Ya no es una limitación conocida que se documenta: es un chequeo
de sanidad — si algún día no da `0`, hay un defecto nuevo que investigar, no una
propiedad esperada de la herramienta.

## Consecuencias

El número que ve el usuario por sección **es** aditivo: la suma de las filas
coincide, token a token, con lo que Anthropic cobra por el archivo completo. Se
dice explícitamente en el README — ya no hace falta la reserva de «aproximación,
no partición exacta» de la versión anterior de este ADR.

## Verificación y reversibilidad

El costo fijo por familia (`3`: por medir, `4.7`: por medir, `4.8`: **5**,
verificado sobre 17 archivos reales con residuo 0 en todos —
`[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]`, sección
«Verificación y reversibilidad») y la deriva quedan como datos dorados en
`tests/test_tokenizers.py` y `tests/test_render.py`. Cambiar el tratamiento del
marco requiere actualizar este ADR (y el ADR-007, que lo corrigió) y los datos
dorados.
