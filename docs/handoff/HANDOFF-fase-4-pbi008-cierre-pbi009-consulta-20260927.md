---
title: "Traspaso TTOK-03 → TTOK-04: PBI-007/008 cerrados, v1.0.0 publicado, PBI-009 abierto por el owner"
aliases:
  - "Handoff tokmd 20260927"
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
llm_model: "claude-opus-5-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-opus-5-5 / Claude Code / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - handoff
related_documents:
  - "[[HANDOFF-fase-3-pbi006-007-20260925-1016]]"
  - "[[CONSULTA-PBI-009-api-key-opcional-20260926]]"
---

# Traspaso TTOK-03 → TTOK-04: PBI-007/008 cerrados, v1.0.0 publicado, PBI-009 abierto por el owner

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5-5 / Claude Code / subscription | Creación, a pedido de Fabián, para abrir la sesión TTOK-04. La sesión TTOK-03 corrió con Opus 5, Sonnet 5 y Opus 5.5 (Fabián cambió el modelo dos veces). |

## En una línea

Creíamos el proyecto cerrado —PBI-001 a 008 verdes y `v1.0.0` en PyPI— hasta
que Fabián, como owner, preguntó **cómo hace cualquier usuario para usar la
verificación con la API de Anthropic** (`--verify`): hoy sólo funciona si uno
sabe setear `ANTHROPIC_API_KEY` en su shell. Eso es el **PBI-009**, todavía sin
decidir. **Lo primero que tiene que hacer TTOK-04 es reconsultar a los seis
motores con el planteo nuevo de Fabián** (ver "Primer paso concreto").

## Repositorio y commit actual

`C:\IA\Projects\Claude-Tokenizer`, rama `main`, remoto
`https://github.com/fferdgelis/tokmd` (público). El commit de este traspaso es
el último de `main`; verificar con `git log --oneline -15`. Tag `v1.0.0` sobre
`f55a0c4`. Paquete publicado: https://pypi.org/project/tokmd/ (1.0.0).

## Primer paso concreto: reconsultar a los seis con el planteo v2

**Contexto.** En TTOK-03 se consultó a seis motores con el planteo de Fabián
sobre PBI-009. Después de la consulta, Fabián **amplió su planteo**
(`docs/handoff/consulta-pbi009/planteo-v2-fabian-20260927.txt`): agrega qué es
`tokmd` y qué es exactamente la funcionalidad opcional. Pidió explícitamente
que TTOK-04 vuelva a consultar a los seis con ese texto antes de que él decida.

**Los seis:**

| Motor | Cómo se consulta |
|---|---|
| Codex (OpenAI) | `mcp__panel__ask_codex_web`, con `cwd` = su copia limpia |
| Antigravity (Google) | `mcp__panel__ask_antigravity`, con `cwd` = su copia limpia |
| Kimi K3 | `opencode run -m openrouter/moonshotai/kimi-k3 --dir <copia> <mensaje>` |
| GLM-5.3 | `opencode run -m nvidia/z-ai/glm-5.3 --dir <copia> <mensaje>` |
| Nemotron 3 Super | `opencode run -m nvidia/nvidia/nemotron-3-super-120b-a12b --dir <copia> <mensaje>` |
| Claude (vos) | Tu opinión, **escrita antes de leer la de los demás** |

**Cómo hacerlo bien (todo esto se aprendió pagando en TTOK-03):**

1. **El texto de Fabián va literal.** No se reescribe, no se resume, no se le
   agrega tu propia propuesta. En TTOK-03 se reescribió en el primer intento y
   Fabián lo frenó: condiciona a los demás motores.
2. **Única excepción autorizada por Fabián (opción A), sólo para los tres de
   OpenCode:** anteponer esta línea: *"Respondé con tu opinión sobre lo
   siguiente. El proyecto está en esta carpeta."* Sin ella, Kimi sale a buscar
   el proyecto fuera de su carpeta, OpenCode se lo rechaza y la corrida
   termina sin respuesta (pasó tres veces seguidas).
3. **Cada motor, su propia copia limpia** del repo (`git archive --format=zip
   -o <zip> HEAD` + `Expand-Archive`). Nunca reusar una copia: Antigravity
   escribe archivos en su carpeta, y en TTOK-03 Kimi leyó el borrador que había
   dejado Antigravity y su primera opinión no sirvió.
4. **OpenCode se corre desde dentro de la copia** (`Set-Location` a la copia,
   además de `--dir`).
5. **Nombres de archivo de salida únicos** (con la hora). En TTOK-03 la salida
   de GLM se perdió porque otro proceso tenía tomado el archivo.
6. **GLM-5.3 por NVIDIA es lento: tardó 726 s (12 min).** Correr en segundo
   plano (`run_in_background`) y con timeout largo.
7. **Key de NVIDIA:** Fabián dice que OpenCode ya la tiene cargada. En TTOK-03,
   desde el proceso de la sesión, `opencode auth list` mostraba sólo
   OpenRouter y `opencode models nvidia` no listaba nada hasta pasarle
   `NVIDIA_API_KEY` al proceso (leída de la bóveda DPAPI,
   `multi-modelos-ai` / `nvidia.api-key`, sin guardarla en ningún lado).
   **Verificar primero** con `opencode models nvidia`; pasar la key al proceso
   sólo si hace falta.
8. **OpenCode les carga a todos sus modelos `~/.codex/AGENTS.md`** como
   instrucciones. Nemotron terminó imitando las reglas de formato de Fabián
   ("OK, seguimos", "ERROR en…") en vez de opinar. Anotarlo si vuelve a pasar;
   no tocar esa config sin que Fabián lo pida.
9. **Verificar contra el código real** toda afirmación factual de los motores
   antes de consolidar. En la ronda 1 hubo afirmaciones falsas (ver sección 3
   del consolidado).

**Entregable del paso:** una versión nueva del consolidado
(`docs/CONSULTA-PBI-009-api-key-opcional-20260926.md`, o un archivo nuevo al
lado si Fabián lo prefiere — preguntarle), con la ronda 2 y la comparación
contra la ronda 1. Los crudos van a `docs/handoff/consulta-pbi009/`.

**Después: Fabián decide.** No se escribe el PBI-009, no se crea un ADR-007 y
no se implementa nada hasta que él decida el mecanismo.

## PBI-009: qué se sabe hoy (ronda 1, sobre el planteo v1)

Detalle completo en `docs/CONSULTA-PBI-009-api-key-opcional-20260926.md`.

- **Los seis desaconsejan** guardar la key en una variable de entorno
  permanente del sistema (lo que planteó Fabián literal): la terminal abierta
  no la ve, en Linux/macOS no existe sin tocar los archivos del shell.
- **Discrepancia de fondo: dónde guardarla. 4 a 2** a favor de un archivo de
  configuración en la carpeta del usuario con permisos restringidos
  (Antigravity, Kimi, GLM, Nemotron) contra el almacén de credenciales del
  sistema vía `keyring` (Codex, Claude). Nemotron no leyó el proyecto; su voto
  pesa poco.
- **Coinciden:** `--verify` es opcional y el modo offline es el principal;
  primero la variable de entorno (CI, el flujo DPAPI de Fabián) y después lo
  guardado; `--config` pide la key oculta, nunca como argumento.
- **Huecos reales encontrados (verificados):** el README no documenta
  `--verify`; sin `tokmd[verify]` instalado, `--verify` termina con un error
  técnico de Python (`ModuleNotFoundError`) en vez de un mensaje.
- **Afirmaciones falsas detectadas:** que la herramienta ya muestra la deriva
  en pantalla; que PBI-008 midió la diferencia offline vs API (nunca se midió).
- **Codex (con fuente oficial):** el conteo de tokens de la API es gratis con
  límite de pedidos por minuto, y Anthropic lo describe como estimación — no
  prometer "número exacto".

## Qué pasó en TTOK-03, en orden

1. **PBI-007 QA cerrado.** Kiwi Test Run 67, 4/4 PASSED (Kimi K3 sobre
   snapshot `d90fb73`). AC-01 (CI verde) lo verificó Desarrollo porque el
   snapshot no tiene red (run `36136759090` y `36143105506`). Commit `e685e1e`.
2. **Sonar: snapshot por zip** en vez de `git archive | tar`, que dependía de
   qué `tar` ganaba en el PATH (BUG-007). Commit `f55a0c4`.
3. **`v1.0.0` publicado en PyPI**, a pedido explícito de Fabián: merge a
   `main`, tag, `publish.yml` en verde, verificado con
   `uvx --from tokmd==1.0.0 tokmd --version` → `1.0.0`.
4. **`.gitignore` ignora `.claude/`** (worktrees). Commit `1784fe6`.
5. **PBI-008.** La key de Anthropic está en la bóveda DPAPI
   (`multi-modelos-ai` / `anthropic.api-key`); se validó que autentica y tiene
   facturación (`count_tokens` con `claude-sonnet-5` respondió). `--verify` no
   existía en la CLI: se cableó con TDD (DeepSeek escribió los tests, rojo
   confirmado). Kiwi Run 68, 5/5 PASSED.
6. **BUG-001, dos veces.** Corriendo `--verify` contra la API real apareció
   que la API rechaza texto de sólo espacios (400): primero en `measure_frame`,
   después en `count_verified` con secciones en blanco del `CLAUDE.md` real.
   Corregido (`bfed82b`, `e4e2fbb`).
7. **Medición real:** el `CLAUDE.md` global cuesta **15877 tokens de Claude**
   (no 9359, que era una medición con tokenizador de OpenAI). Con OpenAI
   `o200k_base`: 9852. Documento actualizado en `framework-multi-ai`
   (`docs/mejoras Claude-MD-General/MEDICION-CLAUDE-MD-GLOBAL.md` v0.2.0,
   commit `5a3d94e` en `codex/dpapi-central-v2`, pusheado).
8. **Violación de separación de roles, señalada por Fabián.** En el punto 6,
   Desarrollo encontró el bug con una prueba propia, lo arregló y escribió el
   test de regresión — trabajo de QA y de TDD. **PBI-008 se rehízo:** el test
   lo reescribió DeepSeek desde una spec de contrato (`59553dd`), caso nuevo
   `TOK-008-C06` (id 375), Run 69, 6/6 PASSED (`1652d13`).
9. **Los 7 bugs reales del proyecto registrados en Kiwi** como registros Bug
   (ids 2 a 8), linkeados a la Test Execution que corresponde cuando existe.
   Docs `docs/bugs/BUG-001` a `BUG-007`. Commit `ff9c776`.
10. **Auditoría de TE-249 a pedido de Fabián:** el "Error" que se ve en la fila
    es la **categoría** del caso, no el resultado (que es PASSED, verificado
    en Postgres). Mala elección de nombre, anotada; sin cambiar.
11. **PBI-009 abierto por Fabián** y consulta a seis motores (ver arriba).

## Reglas que TTOK-03 violó y TTOK-04 no puede repetir

- **Separación de roles (ADR-006 + CLAUDE.md global):** el que escribe TDD no
  programa ni hace QA; el que programa no hace TDD ni QA; el que hace QA no
  hace TDD ni programa. Desarrollo no sale a buscar bugs por su cuenta ni
  escribe tests.
- **Todo bug se registra en Kiwi**, en la Test Execution que corresponda, con
  su doc en `docs/bugs/`. Si aparece un bug y se corrige, se ve el FAILED y
  después el PASSED; no se tapa.
- **No hacer nada que Fabián no pidió.** Ni implementar, ni proponer de más,
  ni reescribir sus textos. Ante la duda, preguntar antes.
- **Commitear antes de correr el gate de Sonar** (analiza `git archive HEAD`,
  no el working tree). En TTOK-03 se corrió una vez sobre el commit viejo.
- **Worktree aislado antes de editar**, siempre.

**Mecanismo para la separación de roles:** se propuso un hook que bloquee que
la sesión edite archivos de test. Fabián lo rechazó por ahora. **No volver a
proponerlo salvo que él lo pida.**

## Pendientes que sólo decide Fabián

1. **PBI-009:** el mecanismo (después de la ronda 2).
2. **Aceptación de los 8 PBI:** los ocho dicen `Aceptación del owner: pending`
   en la sección 6 de cada `docs/PBI/PBI-00X-*.md`. Los ADR ya están aceptados.
3. **Qué recortar del `CLAUDE.md` global**, con la medición real en mano.
4. **`framework-multi-ai`:** la rama `codex/dpapi-central-v2` es la rama por
   defecto en GitHub y tiene 90 commits de todo tipo, no sólo DPAPI; `master`
   (igual a `skills/centralizacion`) tiene 3 commits de skills que esa rama no
   tiene. Nadie los mergeó. Fabián no decidió nada todavía.
5. **Nombre de la categoría "Error" en Kiwi** (se confunde con el estado
   `ERROR`): se ofreció renombrarla, sin respuesta.
6. **Dónde está cargada la key de NVIDIA para OpenCode** (Fabián dice que ya
   está; desde TTOK-03 no se veía): se ofreció buscarlo, sin respuesta.

## Estado de los repositorios al cierre de TTOK-03

- **tokmd (`main`):** limpio después del commit de este traspaso.
- **framework-multi-ai (`codex/dpapi-central-v2`):** en `5da6fa3`, pusheado.
  Hay un archivo sin trackear que **no es de TTOK-03**:
  `docs/reference/SECRETOS-EN-WINDOWS-Y-CLAUDE-CODE-DESDE-CERO.md` (de otra
  sesión). No tocarlo.

## Kiwi, ids para no tener que buscarlos

- Test Runs: 67 (PBI-007), 68 (PBI-008), 69 (PBI-008 rehecho).
- Casos de PBI-008: 370 a 375 (`TOK-008-C01` a `C06`).
- Bugs: ids 2 a 8 = BUG-001 a BUG-007 (el id 1 no es de tokmd).

## Trampas pagadas en TTOK-03

- **Kiwi, bugs:** `Bug.status` `True` = abierto, `False` = cerrado. No existe
  `Bug.update` por API: el estado se pasa al crearlo. Un Bug se linkea a una
  **Test Execution** (`Bug.add_execution`), no a un caso.
- **Kiwi, scripts:** `cargar_casos.py` lee la contraseña **cruda** por stdin;
  los demás (`crear_run.py`, `registrar_resultados.py`, `confirmar_casos.py`)
  esperan **JSON**.
- **Postgres de Kiwi, sólo lectura:** `docker exec ia-postgres psql -U
  kiwi_prod_reader -d kiwi_prod` con la contraseña de la bóveda
  (`postgresql-general` / `kiwi-prod-reader`). No hay `psql` en Windows. El
  historial real de una ejecución está en `testruns_historicaltestexecution`,
  no en `django_admin_log`.
- **Sonar:** si tarda en publicar el análisis ("no se publicó a tiempo"), es
  transitorio: reintentar una vez.
- **`--verify` necesita el extra:** `uv sync --extra verify` (instala
  `anthropic`); sin eso, error de Python.
- **Credenciales:** el clasificador del modo automático bloquea leer secretos
  de la bóveda desde Bash; por PowerShell funcionó con autorización de Fabián.
- **Hook de tope:** 300 llamadas a herramientas por sesión; al llegar, se para
  y se resume.

## Archivos que Fabián tiene que leer para decidir PBI-009

1. `docs/CONSULTA-PBI-009-api-key-opcional-20260926.md` — el consolidado de
   la ronda 1. Alcanza con las secciones 2 (dónde coinciden y dónde no) y 3
   (qué es cierto y qué no).
2. `docs/handoff/consulta-pbi009/planteo-v2-fabian-20260927.txt` — su propio
   texto ampliado, para confirmar que es lo que quiere que reciban los seis
   en la ronda 2.
3. Este traspaso, sección "PBI-009: qué se sabe hoy".

Opcionales, si quiere el contexto técnico: `docs/ADR/ADR-001-eleccion-de-motores-de-tokenizacion.md`
(por qué el modo offline es el principal y `--verify` es opcional) y
`README.md` (hoy no menciona `--verify`).
