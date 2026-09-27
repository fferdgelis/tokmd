---
title: "Traspaso TTOK-05 → TTOK-06: el CLAUDE.md global medido contra la API (17.381), catorce respuestas sobre tokenización, BUG-011 y merge de PBI-009 a main"
aliases:
  - "Handoff tokmd 20260927 TTOK-05"
project: tokmd
document_type: work-plan
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
  - handoff
related_documents:
  - "[[HANDOFF-fase-4-pbi008-cierre-pbi009-consulta-20260927]]"
  - "[[20260927-count-tokens-api-vs-tokmd-ctok-ttok]]"
  - "[[20260927-respuestas-14-preguntas-tokenizacion]]"
  - "[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
  - "[[BUG-011-salida-unicodeencodeerror-cp1252-windows]]"
---

# Traspaso TTOK-05 → TTOK-06: el CLAUDE.md global medido contra la API (17.381), catorce respuestas, BUG-011 y merge de PBI-009 a main

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación, a pedido de Fabián, para abrir TTOK-06. TTOK-05 corrió en paralelo con TTOK-04 (Opus 5, rama `worktree-ttok04-pbi009-ronda2`); las dos sesiones se coordinaron por mensaje y acordaron un protocolo. |

## En una línea

Fabián pidió el número oficial de Anthropic para su `CLAUDE.md` global, sin
pasar por tokmd: **17.381 tokens** (`count_tokens`, Sonnet 5 / Opus 5 /
Opus 4.8). ctok crudo da exactamente lo mismo; tokmd daba 15.903 porque no
cuenta los encabezados (BUG-008, ya registrado por TTOK-04 y en el alcance de
PBI-009). De ahí salieron catorce preguntas suyas, respondidas con fuentes;
un bug nuevo (BUG-011, salida cp1252 en Windows); y el merge de toda la rama
de TTOK-04 a `main`. **Lo primero para TTOK-06: la inconsistencia de datos
dorados de PBI-009 (17.375 vs 17.381), abajo.**

## Repositorio y commit actual

`C:\IA\Projects\Claude-Tokenizer`, rama `main`, remoto
`https://github.com/fferdgelis/tokmd`. `main` == `origin/main` en `cb11142`
(merge `--no-ff` de `worktree-ttok04-pbi009-ronda2`) más el commit de este
traspaso. La rama de TTOK-04 sigue viva en
`.claude/worktrees/ttok04-pbi009-ronda2`; TTOK-04 sigue trabajando ahí y avisa
antes de pedir otro merge.

## Primer paso concreto: los datos dorados de PBI-009 dicen 17.375 y tienen que decir 17.381

ADR-007 v0.3.0 (corregido hoy por TTOK-04 con el dato de la API) dice que el
**total que muestra tokmd es 17.381, marco incluido** (`Own 17.376 + marco 5`).
Pero quedaron tres lugares con el número viejo:

| Archivo | Línea | Dice | Tiene que decir |
|---|---|---|---|
| `docs/PBI/PBI-009-defaults-del-cli-y-total.md` | 228 («Métricas», dato dorado de AC-02) | 17.375 | **17.381** |
| `docs/PBI/PBI-009-casos-de-prueba.md` | 81 (tabla de datos dorados) | 17.375 | **17.381** |
| `docs/PBI/PBI-009-casos-de-prueba.md` | 115 (**TOK-009-C05**, resultado esperado) | 17.375 exacto | **17.381 exacto** |

Si un desarrollador implementa contra 17.375, C05 falla contra el ADR y
contra la API. Las secciones «no-aditividad medida» de PBI-009 llevan un
cartel de «superado» y pueden quedar, pero el dato dorado y el caso no. **Se le
avisó a TTOK-04 por mensaje al cerrar TTOK-05**; TTOK-06 verifica que esté
corregido (en `main` o en la rama) antes de que PBI-009 pase a Desarrollo. Y el
caso de Kiwi correspondiente a C05 (ids 376–391) también.

## El número, y de dónde sale

Medido con `POST https://api.anthropic.com/v1/messages/count_tokens`, el
archivo entero como único mensaje `user`, key de la bóveda DPAPI
(`multi-modelos-ai` / `anthropic.api-key`). **El endpoint es gratis y funcionó
con la cuenta en saldo cero.** JSON crudo en
`local/count_tokens-claude-md-global-2026-09-27.json` y `-b.json`.

| Modelo | Tokens | Familia |
|---|---|---|
| claude-sonnet-5, claude-opus-5, claude-opus-4-8 | **17.381** | tokenizador «Opus 4.7» (ctok `4.8`) |
| claude-fable-5-1 | 17.383 | misma, +2 de marco |
| claude-sonnet-4-6, claude-haiku-4-5 | 13.076 | tokenizador anterior (ctok `3.0`) |

ctok crudo sobre el archivo entero: `4.8` = 17.381, `3.0` = 13.076 —
**exacto**. Sonda corta: `## Motores de IA…` = 25; sección sin heading 38, con
heading 58 → `58 = 38 + 25 − 5`: **el costo por trozo es 5**, confirmado desde
la API, independiente de la medición de TTOK-04 (ADR-007 lo cita).

Detalle y comparación con tokmd/ctok/ttok:
`docs/investigation/20260927-count-tokens-api-vs-tokmd-ctok-ttok.md`.

## Las catorce respuestas (para no rehacer la investigación)

`docs/investigation/20260927-respuestas-14-preguntas-tokenizacion.md`. Lo que
TTOK-06 necesita saber sin abrirlo:

- **Baseline por familia, no universal:** 17.381 (Sonnet 5/Opus 5/4.8),
  13.076 (Sonnet 4.6/Haiku 4.5), 17.383 (Fable 5.1). Siempre con modelo y
  fecha al lado.
- **ctok** (`github.com/sanderland/ctok`, Sander Land, MIT, 1 contribuidor,
  2 meses de vida) es 100 % offline: vocabulario reconstruido por ingeniería
  inversa sondeando `count_tokens`, teselado de costo mínimo. No hay
  tokenizador oficial de Anthropic (`@anthropic-ai/tokenizer` archivado).
- **Riesgo de ctok:** no es que desaparezca (MIT, lo tenemos en disco) sino
  que quede atrás: su README ya dice que el +2 de Opus 5.5 «is not yet
  modeled». Propuesta A+B+C: vendorizar, gate periódico gratis contra
  `count_tokens` sobre un corpus dorado, `--verify` de documento entero.
  Un ctok propio no se justifica.
- **Los encabezados pesan siempre**, en toda plataforma: los tokenizadores
  no saben qué es Markdown; Claude Code, Codex (tope 32 KB) y OpenCode mandan
  el archivo crudo.
- **cl100k/o200k** son vocabularios de OpenAI; `ttok` mide OpenAI, no
  Claude. Comparar conteos entre proveedores sin el precio no dice nada.
- **Modelos viejos no ahorran:** Sonnet 4.6 = 13.076 × $3 = $0,039;
  Sonnet 5 = 17.381 × $2 = $0,035. Y en Claude Code por suscripción ni
  aplica. La palanca es achicar el `CLAUDE.md` (Anthropic: < 200 líneas).

## Qué pasó en TTOK-05, en orden

1. Medición contra la API con un script PowerShell propio (scratchpad, no
   versionado): `count-tokens.ps1`, key desde DPAPI, un modelo por llamada.
2. Comparación con tokmd (15.903, −8,5 %), ctok (exacto) y ttok (OpenAI).
   Informe en `docs/investigation/`.
3. Fabián pidió catorce respuestas con fuentes y sin memoria: cuatro agentes
   Sonnet en paralelo (docs Anthropic; repo y código de ctok; tiktoken, Codex,
   Antigravity, OpenCode, Kimi; historia del repo tokmd). Informe en
   `docs/investigation/`.
4. Al ir a registrar «BUG-008» (UTF-8) y «el PBI de los encabezados», se
   descubrió que TTOK-04 ya tenía BUG-008 (encabezados), BUG-009, BUG-010,
   ADR-007 y PBI-009 en su rama. El bug de UTF-8 pasó a **BUG-011**; el PBI no
   se duplicó.
5. Coordinación con TTOK-04 por `send_message`: acordado que el total es
   17.381 con marco (TTOK-04 corrigió su ADR-007 v0.2.0, que decía 17.376);
   BUG-011 entró en PBI-009 (AC-18/19, casos C16/C17, Kiwi pk=13).
6. Fabián pidió commitear los informes en `main` (`dad57fa`), pushear y
   mezclar la rama de TTOK-04 (`cb11142`, sin conflictos).
7. Protocolo entre sesiones acordado y guardado en memoria del proyecto.

## Protocolo entre sesiones (vigente)

1. Cada sesión commitea en su rama. TTOK-05 trabajó directo en `main`, pero
   commitea y pushea **sólo cuando Fabián lo pide**.
2. Los merges a `main` los pide Fabián y los ejecuta quien él diga.
3. Antes de tocar `main`, una sesión avisa a la otra por
   `mcp__ccd_session_mgmt__send_message` (confirmar el id con
   `list_sessions`; TTOK-04 hoy es `local_ce58477c-5ea2-4ef0-8fe7-ddb107b0eda8`).
4. **Antes de numerar un BUG/PBI/ADR, mirar todas las ramas y los
   worktrees** (`git ls-tree -r --name-only <rama> -- docs/bugs`), no sólo
   `main`. Hoy dos sesiones tomaron el mismo número.

## Pendientes que sólo decide Fabián

1. **ADR-007, opción D:** aceptarla. Bloquea PBI-009.
2. **PBI-009:** pasar a `ready` una vez corregidos los datos dorados (primer
   paso de arriba).
3. **Propuesta A+B+C sobre ctok** (vendorizar + gate de deriva contra la API +
   `--verify` de documento entero): ¿un PBI o tres?
4. **Baseline versionado:** tabla `(archivo, sha256, modelo, fecha, tokens)`
   en el repo, con las tres filas de hoy.
5. **Qué recortar del `CLAUDE.md` global** (17.381 tokens en cada llamada de
   cada sesión). Ya venía del handoff anterior; ahora con el número real.
6. Arrastrados del handoff anterior, sin novedad: aceptación formal de los 8
   PBI; `framework-multi-ai` (`codex/dpapi-central-v2` vs `master`); nombre de
   la categoría «Error» en Kiwi; dónde está la key de NVIDIA para OpenCode.

## Kiwi, ids

- Plan 30 (PBI-009). Casos **376–379 y 381–391** (el 380 se dio de baja por
  duplicado); C16/C17 cargados por TTOK-04 en `1c8d148`.
- Bugs: pk 9 = BUG-008, 10 = BUG-009, 11 = BUG-010, **13 = BUG-011** (el 12
  fue un duplicado borrado). Ids 2–8 = BUG-001 a 007.
- Test Runs anteriores: 67 (PBI-007), 68 y 69 (PBI-008).

## Trampas pagadas en TTOK-05

- **`count_tokens` rechaza texto vacío o sólo espacios** (400; es BUG-001).
  Para medir el marco no sirve mandar `""`: se mide por diferencia entre dos
  textos (`58 − 38 − 25 = −5`).
- **Windows + salida redirigida = cp1252.** tokmd revienta (BUG-011);
  `ttok < archivo` **no revienta y miente** (13.075 en vez de 11.660).
  Para cualquier medición: `PYTHONUTF8=1` en el entorno, o `-i archivo`.
- **`pwsh -File script.ps1 -Models a,b,c`** pasa la lista como un solo
  string; invocar con `& script.ps1 -Models @('a','b')` desde PowerShell.
- **`Clear-Host` sin consola** (script corrido desde el arnés) tira
  «The handle is invalid»; envolverlo en `try {} catch {}`.
- **El hook `guardia-bash.ps1` bloquea `> archivo` en el repo** aunque sea
  salida de un comando. Procesar en memoria (script Python con `subprocess`)
  o escribir al scratchpad.
- **Hook de gobernanza Markdown:** todo `.md` de `docs/` exige `tags`,
  `related_documents` y la sección `## Historial de modificaciones` con su
  tabla; si falta, el Write se rechaza y hay que rehacerlo.
- **`--format json` de tokmd sobrevive a cp1252 por casualidad**
  (`ensure_ascii`); no tomarlo como evidencia de que el bug no existe.
- **Los agentes Sonnet de investigación cuestan ~100–200k tokens cada uno**
  y tardan 3–11 min; el de Codex/Antigravity/OpenCode hizo 87 llamadas. Vale
  para «leer manuales y traer citas», no para preguntas de una línea.

## Archivos que Fabián tiene que leer para decidir

1. `docs/investigation/20260927-respuestas-14-preguntas-tokenizacion.md` —
   la sección final «Qué queda para decidir».
2. `docs/ADR/ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol.md` —
   «Opción D» y «Corrección del 27/09/2026».
3. `docs/PBI/PBI-009-defaults-del-cli-y-total.md` — sección 3 (AC-01 a
   AC-19), después de la corrección de datos dorados.
