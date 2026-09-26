---
title: "BUG-001 — measure_frame usaba un espacio en blanco, rechazado por la API real"
aliases:
  - "tokmd BUG-001"
project: tokmd
document_type: bug
status: verified
version: 1.0.0
created: 2026-09-25
updated: 2026-09-25
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-sonnet-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-sonnet-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-sonnet-5 / Claude Code / subscription"
reviewed_by: "pending"
review_status: "pending"
tags:
  - project/tokmd
  - bug
related_documents:
  - "[[PBI-006-verificacion-contra-api]]"
  - "[[PBI-008-medicion-claude-md-global]]"
---

# BUG-001 — measure_frame usaba un espacio en blanco, rechazado por la API real

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-25 | 1.0.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Creación, corrección y verificación en la misma sesión: detectado al cablear `--verify` en `cli.py` (PBI-008) y probarlo contra la API real por primera vez. |

## 1. Clasificación

- **Título:** `measure_frame` llama a `count_tokens` con contenido de un solo espacio (`" "`), que la API real rechaza.
- **Estado:** `fixed` (corregido y verificado con una llamada real en esta misma sesión).
- **Tipo:** `product-defect`.
- **Severidad:** `2-high` — bloqueaba por completo cualquier uso real de `--verify`, la funcionalidad central de PBI-006/PBI-008.
- **PBI relacionado:** [[PBI-006-verificacion-contra-api]] (donde se escribió `measure_frame`), descubierto durante [[PBI-008-medicion-claude-md-global]] (donde se usó por primera vez contra la API real).
- **Caso de Kiwi relacionado:** TOK-006-C02 (`count_verified` resta el marco medido) — su veredicto PASSED sigue siendo correcto para lo que probaba (la aritmética de resta), no para el contenido literal usado en la llamada real, que nunca se ejerció con red real.
- **Reportado por:** Desarrollo (Claude Code, Opus 5), en esta sesión.
- **Fecha de detección:** 2026-09-25.

## 2. Contexto reproducible

- **Build/commit:** `f55a0c4` (antes del fix), rama `worktree-pbi008-verify`.
- **Canal de QA:** el que detectó el bug NO fue QA — fue Desarrollo, haciendo una prueba de humo manual contra la API real con `ANTHROPIC_API_KEY` de la bóveda DPAPI, algo que el flujo de QA de este proyecto nunca hace (ADR-006 prohíbe red real en los tests).
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Precondiciones:** `ANTHROPIC_API_KEY` real, válida y con facturación habilitada (confirmado antes, ver dev-log 2026-09-25).

## 3. Reproducción

```
uv run tokmd smoke.md --platform claude-code --verify
```

con `ANTHROPIC_API_KEY` real en el entorno, produce:

```
anthropic.BadRequestError: Error code: 400 - {'type': 'error', 'error':
{'type': 'invalid_request_error', 'message': 'messages: text content
blocks must contain non-whitespace text'}, 'request_id': '...'}
```

## 4. Impacto

`--verify` (y por lo tanto `count_verified`/`measure_frame`, y por lo tanto
PBI-008 entero, cuyo único propósito es correr `--verify` sobre el
`CLAUDE.md` global) fallaba al primer intento, siempre, contra cualquier key
real. Nunca se había ejecutado contra la API real desde que se escribió
`verify.py` en PBI-006 — los 4/4 PASSED de esa QA usaron exclusivamente un
cliente falso que no valida contenido (`FakeMessages.count_tokens`
respondía por longitud de diccionario, no por si la API real aceptaría ese
`content`).

## 5. Evidencia

- Traceback completo de la reproducción (arriba).
- Confirmado independientemente: probar el mismo endpoint a mano con
  PowerShell (`Invoke-RestMethod` directo a
  `https://api.anthropic.com/v1/messages/count_tokens`) con
  `content = " "` da el mismo error `400`; con `content = "hola"` funciona.
- Post-fix: la misma prueba de humo con `content = "."` responde
  `input_tokens` correctamente, y `tokmd smoke.md --platform claude-code
  --verify` completo imprime una tabla con números reales (52 y 28 tokens
  para las dos secciones de prueba).

## 6. Causa

El diseño original de `measure_frame` (spec de TDD para PBI-006,
`tools/deepseek/specs/PBI-006.md.prompt`) especificó explícitamente
`content: " "` como "contenido mínimo". La API de Anthropic rechaza
cualquier bloque de texto que sea sólo espacio en blanco
(`text content blocks must contain non-whitespace text`) — una restricción
no documentada en la spec ni verificada contra la API real al momento de
escribirla. El test suite de PBI-006 (por diseño, ADR-006: nunca red real)
usa un cliente falso (`FakeMessages`) que no reproduce esa validación, así
que el defecto pasó los 4/4 de QA sin que nadie lo notara.

## 7. Corrección

- `src/tokmd/verify.py`: `measure_frame` ahora llama con `content="."` en
  vez de `content=" "` (un carácter no-espacio, sigue siendo "contenido
  mínimo").
- `tests/test_verify.py`: el fake `FakeMessages.count_tokens` actualizado
  para reconocer `"."` como el contenido mínimo (antes reconocía `" "`).
  Esta es una corrección de Desarrollo sobre un test ya escrito por TDD, no
  una reescritura para forzar que pase: el contrato real cambió (`" "` no es
  válido), así que el fake que lo simula tiene que cambiar con él. Ambos
  cambios están comentados en el código citando este bug.

### Segunda ocurrencia, mismo día: `count_verified` con texto de sección en blanco

Corriendo `--verify` contra el `CLAUDE.md` global de verdad (PBI-008, no un
archivo de prueba pequeño), el mismo `400` volvió a aparecer — esta vez desde
`count_verified`, no `measure_frame`. Causa: una sección cuyo encabezado está
seguido inmediatamente por otro encabezado (sin texto entre medio) tiene
`own_text` igual a la línea en blanco que los separa — una cadena no vacía
pero sólo espacio en blanco, que `render.py`'s guardia `if section.own_text
else 0` no atrapa (mira si es *falsy*, no si es *sólo blanco*).

**Corrección, en `cli.py`** (no en `render.py`, para no tocar el contrato de
un módulo ya cerrado en PBI-005 que nunca tuvo este problema con los
tokenizadores offline): el `count_fn` que arma `--verify` ahora devuelve `0`
directamente para cualquier texto de sección que sea sólo espacio en blanco,
sin llamar a la API.

**Corrección de proceso, 2026-09-26:** el test de regresión de esta segunda
ocurrencia lo había escrito Desarrollo mismo (`test_claude_code_verify_skips_count_verified_for_whitespace_only_section`
en `tests/test_cli_verify.py`) — violando ADR-006 (TDD escribe los tests,
Desarrollo no). Fabián lo señaló. Removido de `test_cli_verify.py` y
reemplazado por uno escrito de punta a punta por DeepSeek (rol TDD) desde
una spec de contrato puro, sin narrar el bug
(`tools/deepseek/specs/PBI-008-verify-gap-01.md.prompt`), en un archivo nuevo
(`tests/test_cli_verify_gap01.py`) — el script de TDD hizo el `Set-Content`,
no Desarrollo. Ningún cambio en la implementación. Cargado en Kiwi como
`TOK-008-C06`, Test Run 69 (commit `59553dd`), QA independiente (Kimi K3)
re-corrida: 6/6 PASSED.

**Re-verificado con la API real** contra el `CLAUDE.md` global completo
(677 líneas, sección con encabezados consecutivos incluida): corre de punta a
punta, total real 15877 tokens. Ver `docs/dev-log/2026-09-25.md` para la
medición completa (PBI-008).

## 8. Verificación independiente

- **Verificado por:** Desarrollo mismo, con una llamada real a la API (no
  QA — QA de este proyecto nunca toca la red real, por diseño de ADR-006).
  El veredicto de QA independiente sobre el flag `--verify` en sí (mockeado,
  sin red real) se registra aparte en Kiwi como parte del cierre normal de
  esta pieza de trabajo.
- **Evidencia:** salida real de `tokmd smoke.md --platform claude-code
  --verify` pegada en la sección 5, más la corrida completa de PBI-008
  sobre el `CLAUDE.md` global (ver `docs/dev-log/2026-09-25.md`).
