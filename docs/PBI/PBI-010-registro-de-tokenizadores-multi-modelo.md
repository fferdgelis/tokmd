---
title: "PBI-010 — Registro de tokenizadores por configuración: DeepSeek, GLM, Nemotron, Qwen, Mistral, Llama y Gemini sin tocar código"
aliases:
  - "PBI-010 multi-modelo"
project: tokmd
document_type: pbi
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
  - delivery/pbi
related_documents:
  - "[[ADR-008-registro-de-tokenizadores-por-configuracion]]"
  - "[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]"
  - "[[20260930-tokenizadores-offline-por-modelo]]"
  - "[[PBI-010-casos-de-prueba]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
---

# PBI-010 — Registro de tokenizadores por configuración

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación, a pedido de Fabián («preparemos todo lo necesario para que lo ejecute Sonnet»). Borrador para su revisión; no está `ready` hasta que acepte ADR-008 y este PBI. |

## Roles (ROL-02)

`TDD: DeepSeek (deepseek-v4-pro, vía Invoke-DeepSeekCodeTask) · Desarrollo: Claude Sonnet 5 (Claude Code) · QA: Kimi K3 (OpenCode + OpenRouter, read-only)` — según ADR-006.

## 1. Valor y contexto

- **Problema.** tokmd cuenta bien para Claude y OpenAI, y para nadie más. Un
  equipo que usa Claude Code, Codex, Antigravity y DeepSeek a la vez (el
  caso real de este mismo proyecto: seis motores en las consultas de
  PBI-009) no tiene un número para la mitad de ellos, y `--platform
  antigravity` lleva desde la 1.0 devolviendo «planned for 1.1». Agregar un
  modelo hoy es tocar `cli.py` y publicar.
- **Stakeholder:** Fabián Ferdgelis, owner del proyecto.
- **Resultado esperado.** Un archivo de configuración (`tokenizers.toml`)
  donde cada modelo está dado de alta con su motor. tokmd trae uno
  empaquetado con los modelos relevados; el usuario extiende o pisa con el
  suyo. Seis familias abiertas entran con un solo motor genérico de Hugging
  Face; Gemini entra marcado como aproximado; `claude-code` sigue dando
  exactamente lo de hoy.
- **Prioridad:** la más alta después del cierre de 2.0.0. Es la apuesta de
  producto decidida el 30/09 («el foso es fino; lo multi-plataforma es lo
  que ningún proveedor va a hacer»).
- **Hipótesis.** El valor no está en un modelo más sino en que **agregar
  uno cueste una entrada de TOML**. Si al terminar este PBI un usuario
  puede dar de alta un modelo privado de su empresa sin tocar Python, el
  PBI cumplió.

### Historia de usuario

> Como **desarrollador de un equipo que trabaja con varios modelos**, quiero
> **`tokmd AGENTS.md --model deepseek-v4-pro` (o glm-5.3, o gemini-3-flash)
> y que dé el número con el tokenizador correcto de ese modelo**, para
> **saber cuánto pesa mi harness en cada plataforma sin instalar el SDK de
> cada proveedor ni escribir código**.

> Como **usuario con un modelo que tokmd no conoce**, quiero **agregar tres
> líneas a `~/.config/tokmd/tokenizers.toml`** para **contarlo sin esperar
> un release**.

## 2. Corte de entrega

- **Incluye:**
  - `src/tokmd/registry.py`: carga y validación del registro (TOML
    empaquetado + TOML del usuario + `--registry`), con la prioridad y las
    reglas de ADR-008.
  - `src/tokmd/engines/`: un módulo por motor con la misma firma
    `count(text: str) -> int`: `ctok_engine.py` y `tiktoken_engine.py`
    (envuelven lo que ya hay en `tokenizers.py`, sin cambiar su
    comportamiento), `hf_engine.py` (nuevo), `sentencepiece_engine.py`
    (nuevo). Importación perezosa de `tokenizers`, `huggingface_hub` y
    `sentencepiece`.
  - `src/tokmd/data/tokenizers.toml`, el registro empaquetado, con estas
    entradas iniciales (todas con id verificado en Hugging Face el 30/09;
    ver relevamiento): `claude-sonnet-5` (alias de la familia 4.8, frame 5),
    `claude-sonnet-4-6` (familia 3.0, frame por medir — ver AC-13),
    `gpt-5`, `gpt-6` (o200k fijado), `deepseek-v4-pro`, `deepseek-v4-flash`,
    `glm-5.3`, `nemotron-3-super`, `qwen3.5`, `mistral-large-3`,
    `llama-4-scout` (gated: documentado que exige token de HF),
    `gemini-3-flash` (sentencepiece, `approx = true`). Sección `[platforms]`
    con `claude-code`, `codex`, `antigravity`, `opencode`.
  - CLI: `--model <nombre-del-registro>` para cualquier plataforma;
    `--platform` pasa a resolverse por `[platforms]`; `--registry <ruta>`;
    `--offline`; subcomando o flag `tokmd --list-models` que imprime el
    registro efectivo (nombre, motor, origen: empaquetado/usuario, approx).
  - Salida: en `table`/`md` una línea de cabecera `model=<n> engine=<e>
    [approx] [content-only]`; en `json`/`csv` los mismos campos.
  - Extras en `pyproject.toml`: `hf = ["tokenizers>=0.23", "huggingface_hub>=0.16"]`,
    `gemini = ["sentencepiece>=0.2"]`, `all = [hf + gemini + verify]`.
  - `--claude-family`, `--encoding`, `--tokenizer` siguen funcionando como
    sobreescritura de la entrada resuelta (sin regresión de PBI-004).
  - README (EN/ES): sección «Adding a model» con el TOML mínimo, la lista
    de modelos empaquetados y la nota de qué es exacto y qué aproximado.
  - `CHANGELOG.md` `[2.1.0]`.
- **No incluye:**
  - Kimi K3 (formato `tiktoken.model`, sin testigo; comentado en el TOML
    como pendiente).
  - `--verify` para otros proveedores (ADR aparte).
  - Escaneo recursivo (`tokmd .`), PBI propio.
  - Medir el marco (`frame`) de ningún modelo nuevo: va `0` explícito y
    etiquetado `content-only`.
- **Dependencias:** ADR-008 aceptado. Red disponible en la máquina de
  Desarrollo y de QA para bajar los `tokenizer.json` la primera vez (una
  vez; después caché de `huggingface_hub`).
- **Riesgos:**
  - Que `Tokenizer.from_file` sobre algún `tokenizer.json` no cargue o dé
    un conteo distinto al de la clase oficial de `transformers`. Mitigación:
    el spike de AC-14 se hace **primero**, antes de escribir el resto.
  - Que `google/gemma-4-E4B-it` sea gated: por eso el registro inicial usa
    el `.spiece.model` de gemma3 (público, sha256 fijado), no el de gemma4.
  - Tamaño de descargas (6–17 MB por modelo): se avisa en stderr y hay
    `--offline`. Nunca se baja un modelo completo.
  - Tests que necesiten red: **la suite no toca la red** (regla de
    PBI-006/009). Los tests de `hf` usan un `tokenizer.json` chico en
    `tests/fixtures/` y `monkeypatch` sobre `hf_hub_download`.

## 3. Criterios de aceptación

### Registro

- [ ] **AC-01:** Dado el registro empaquetado, cuando se corre
      `tokmd --list-models`, entonces lista cada entrada con nombre, motor,
      origen (`bundled`) y marca `approx` donde corresponda, y sale con 0.
- [ ] **AC-02:** Dado un `tokenizers.toml` de usuario con una entrada
      `[models.mi-modelo]` de motor `hf` y `repo` válido, cuando se corre
      `tokmd archivo.md --model mi-modelo`, entonces cuenta con ese
      tokenizador y `--list-models` lo muestra con origen `user`.
- [ ] **AC-03:** Dado un TOML de usuario que redefine `claude-sonnet-5`
      con `family = "4.7"`, cuando se corre con `--model claude-sonnet-5`,
      entonces gana la entrada del usuario y **sólo** esa (las demás
      entradas empaquetadas siguen intactas en `--list-models`).
- [ ] **AC-04:** Dado un TOML con una entrada de motor desconocido, o sin
      un parámetro obligatorio (`repo` para `hf`, `encoding` para
      `tiktoken`, `family` para `ctok`, `url`/`sha256` para
      `sentencepiece`), cuando se carga, entonces falla **antes de contar**
      con un mensaje que nombra la entrada, el campo y el archivo de origen,
      exit code 2.
- [ ] **AC-05:** Dado `--registry <ruta>` a un archivo inexistente, cuando
      se corre, entonces error legible y exit code ≠ 0; dado `--registry`
      válido, esa ruta reemplaza al TOML de usuario por defecto (no al
      empaquetado).

### Motores

- [ ] **AC-06 (sin regresión):** Dado `C:\Users\fferdgelis\.claude\CLAUDE.md`
      sin cambios desde la medición del 27/09, cuando se corre
      `tokmd CLAUDE.md` (sin flags) y `tokmd CLAUDE.md --platform codex`,
      entonces da **17381** y **10742** respectivamente — idéntico a 2.0.0.
      La suite completa de 2.0.0 (77 tests) sigue en verde.
- [ ] **AC-07:** Dado el fixture `tests/fixtures/tiny_tokenizer.json`
      (un `tokenizer.json` mínimo válido incluido en el repo) y una entrada
      `hf` que apunta a él vía `monkeypatch` de `hf_hub_download`, cuando
      se cuenta un texto conocido, entonces el resultado es **igual** a
      `tokenizers.Tokenizer.from_file(fixture).encode(texto).ids` de largo
      — sin red.
- [ ] **AC-08:** Dado un motor `hf` cuyo `tokenizer.json` no está en caché
      y `--offline`, cuando se corre, entonces falla con mensaje que dice
      qué archivo falta y de qué repo, exit code ≠ 0, **sin intentar red**
      (verificable con `monkeypatch` que hace fallar cualquier llamada a
      `hf_hub_download`).
- [ ] **AC-09:** Dado un motor `hf` sin `--offline` y sin caché, cuando se
      corre, entonces antes de descargar escribe en **stderr** (no stdout)
      una línea con el repo y el archivo que va a bajar; stdout sigue
      siendo sólo el número (compatibilidad con `tokmd f.md | algo`).
- [ ] **AC-10:** Dado un motor `sentencepiece` con `sha256` declarado y un
      archivo cuyo hash no coincide, cuando se carga, entonces falla con
      exit code ≠ 0 nombrando la entrada; con hash correcto, cuenta.
- [ ] **AC-11:** Dado que `tokenizers` (o `sentencepiece`) **no está
      instalado** y una entrada lo requiere, cuando se corre, entonces el
      error dice exactamente qué extra instalar (`pip install "tokmd[hf]"`)
      y exit code ≠ 0; y `tokmd archivo.md` con `claude-code` sigue
      funcionando sin ese extra.

### Salida

- [ ] **AC-12:** Dado cualquier corrida, cuando se pide `--format json`,
      entonces el JSON incluye `model`, `engine`, `approx` (bool) y
      `content_only` (bool); en `table`/`md` aparece una línea de cabecera
      con lo mismo. Para `claude-code`: `approx=false, content_only=false`;
      para `hf`: `content_only=true`; para `sentencepiece`: `approx=true`.
- [ ] **AC-13:** Dado `--model claude-sonnet-4-6`, cuando se corre sobre el
      `CLAUDE.md` global, entonces da **13076** (medido contra la API el
      27/09 para Sonnet 4.6 / Haiku 4.5) — con el `frame` de la familia 3.0
      que haya que medir con el mismo método de ADR-007 (dos textos y su
      diferencia), **no** con `token_count("")`.

### Spike previo (bloquea el resto)

- [ ] **AC-14 (spike, primero):** Dado el `tokenizer.json` real de
      `deepseek-ai/DeepSeek-V4-Pro`, `zai-org/GLM-5.3`, `Qwen/Qwen3.5-9B` y
      `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8` bajados una vez con
      `hf_hub_download`, cuando se cuenta con `Tokenizer.from_file` un
      texto de control (castellano con acentos, un bloque de código, un
      emoji, 2 KB), entonces carga sin error en los cuatro y el conteo queda
      registrado como **dato dorado** en `docs/PBI/PBI-010-casos-de-prueba.md`
      (con sha256 de cada `tokenizer.json`). Si alguno no carga, se saca
      del registro empaquetado y se anota por qué. Este AC es el que
      convierte «no verificado» en verificado.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/registry.py` (nuevo),
  `src/tokmd/engines/` (nuevo), `src/tokmd/data/tokenizers.toml` (nuevo),
  `src/tokmd/cli.py` (resolutor reemplazado por el registro).
- **Herramientas disponibles:** `tomllib` (stdlib, Python ≥ 3.11 — el
  proyecto exige 3.12), `click`, `ctok`, `tiktoken`; extras `tokenizers`,
  `huggingface_hub`, `sentencepiece`.
- **Versión de tests y configuración:** `pytest`; los 77 tests de 2.0.0 no
  se tocan salvo para reemplazar `resolve_tokenizer` por su equivalente por
  registro **manteniendo cada aserción**; tests nuevos por AC; **cero red
  en la suite** (fixtures + `monkeypatch`).
- **Métricas:** AC-06 (17381 / 10742) y AC-13 (13076) son datos dorados
  contra la API real; AC-14 produce los dorados de autoconsistencia para
  los motores nuevos.
- **ADR requerido:** `[[ADR-008-registro-de-tokenizadores-por-configuracion]]`
  — bloqueante.
- **Versión:** `2.1.0` (agrega; no rompe `tokmd archivo.md`).

## 5. Handoffs

### Definition of Ready

- [ ] Valor, alcance y fuera de alcance claros.
- [ ] Criterios observables y testeables.
- [x] ADR enlazado (ADR-008, `proposed`; pasa a `accepted` con la decisión
      de Fabián).
- [ ] Casos de Kiwi cargados como PROPOSED (`PBI-010-casos-de-prueba.md`,
      plan nuevo).

**Estado:** `not ready` — falta la aceptación de Fabián de ADR-008 y de
este corte.

### Handoff a TDD (DeepSeek)

- **Orden:** AC-14 (spike) lo corre **Desarrollo** primero y deja los
  dorados; recién entonces TDD escribe. Sin dorados no hay tests honestos.
- **AC a convertir en pruebas:** AC-01 a AC-13, uno o más tests por AC, en
  `tests/test_registry.py`, `tests/test_engines_hf.py`,
  `tests/test_engines_sentencepiece.py`, `tests/test_cli_models.py`.
- **Fixtures y contratos:** `tests/fixtures/tiny_tokenizer.json` (un
  `tokenizer.json` BPE mínimo de ~20 tokens, escrito a mano, para que la
  suite no toque la red); `tests/fixtures/registry_user.toml` con los
  casos de AC-02/03/04; firma de motor `count(text: str) -> int`;
  `hf_hub_download` y `sentencepiece.SentencePieceProcessor` siempre
  parcheados en tests.
- **Rojo real:** cada test tiene que fallar contra 2.0.0 por la razón
  esperada (módulo inexistente, flag desconocido) antes de entregar.

### Handoff a Desarrollo (Claude Sonnet 5)

- **Restricciones confirmadas:** las seis reglas de ADR-008 (etiqueta en la
  salida, frame explícito, sin red por defecto, validación al cargar,
  prioridad fija, `--verify` sin cambios). No modificar tests para que
  pasen; defecto en un test → reportar a TDD con evidencia (ROL-05).
- **Preguntas abiertas:** ninguna bloqueante. Dos decisiones menores que
  Desarrollo toma y documenta en el dev-log: ruta exacta del TOML de
  usuario en Windows (`%APPDATA%\tokmd\` propuesto) y si `--list-models` es
  flag o subcomando (flag propuesto, para no cambiar la forma del CLI).

### Handoff a QA (Kimi K3)

- **Candidato identificable:** commit corto del snapshot.
- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Casos independientes:** `TOK-010-C01` a `C16` de
  `[[PBI-010-casos-de-prueba]]`.
- **Evidencia mínima:** log crudo + resultado por caso en
  `tools/kiwi/resultados/`; para C06 y C13 (números contra la API real) QA
  corre `tokmd` a mano sobre la copia del `CLAUDE.md` global del snapshot,
  como en PBI-009.

## 6. Cierre

- **Artefactos y enlaces:** pendiente.
- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** escaneo recursivo (`tokmd .`) y `--verify`
  multi-proveedor, ambos ya identificados en
  `[[20260930-de-cli-a-producto-para-equipos]]`.
