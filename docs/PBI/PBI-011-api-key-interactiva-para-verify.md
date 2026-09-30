---
title: "PBI-011 — --live pregunta por la API key en modo interactivo (Claude y Codex), banner de bienvenida, y tabla de --sections legible"
aliases:
  - "PBI-011 API key interactiva y legibilidad"
project: tokmd
document_type: pbi
status: proposed
version: 0.2.0
created: 2026-09-30
updated: 2026-09-30
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
  - delivery/pbi
related_documents:
  - "[[ADR-009-manejo-de-api-key-para-verify]]"
  - "[[ADR-008-registro-de-tokenizadores-por-configuracion]]"
  - "[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]"
  - "[[20260930-lectura-del-arbol-de-secciones]]"
  - "[[PBI-006-verificacion-contra-api]]"
  - "[[PBI-011-casos-de-prueba]]"
---

# PBI-011 — `--live` interactivo (Claude y Codex), banner, y tabla de `--sections` legible

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, a pedido de Fabián («Priorizá B, empezá el PBI»), tras aceptar ADR-009. |
| 2026-09-30 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Fabián confirmó el rename `--verify` → `--live` y pidió arrancar con la opción A de legibilidad. Además amplió el alcance: carpeta de config por usuario (no `ProgramData`, ver ADR-009 enmienda 0.3.0), banner de bienvenida sólo en el prompt/`--about`, y Codex/OpenAI en esta misma versión con aviso de costo no confirmado. Título y alcance actualizados. |

## Roles (ROL-02)

`TDD: DeepSeek (deepseek-v4-pro) · Desarrollo: Claude Sonnet 5 (Claude Code) · QA: Kimi K3 (OpenCode + OpenRouter, read-only)` — mismo reparto que PBI-009/010, según ADR-006.

## 1. Valor y contexto

- **Problema.** Tres cosas separadas que Fabián encontró probando tokmd
  como lo probaría cualquier persona nueva: (1) `--verify` (ahora `--live`)
  corta en seco si falta la key, sin ofrecer nada; (2) la tabla de
  `--sections` es ilegible con archivos grandes en una consola angosta
  (títulos que envuelven, árbol que se rompe); (3) la primera experiencia
  de uso no orienta — no hay ningún lugar donde se vea qué es tokmd, qué
  versión, qué motores soporta.
- **Stakeholder:** Fabián Ferdgelis, owner del proyecto.
- **Resultado esperado.** `--live` pregunta en vez de cortar (Claude y
  Codex), guarda la key donde el usuario elija, y la tabla de `--sections`
  se lee sin romperse en cualquier ancho de terminal.
- **Prioridad:** la más alta abierta, por pedido explícito.
- **Hipótesis.** La fricción de hoy —no la falta de interés— es lo que
  hace que nadie use el modo de verificación real. Bajarla sube el uso.

### Historias de usuario

> Como **desarrollador que instala tokmd por primera vez**, quiero **que
> `tokmd archivo.md --live` me pregunte por mi key si no la tiene, en vez
> de sólo decirme que falta**, para **poder probar la verificación real
> sin ir a buscar documentación de variables de entorno**.

> Como **ese mismo desarrollador, la segunda vez**, quiero **que si guardé
> mi key no me la vuelva a pedir**, para **no repetir el trámite**.

> Como **quien corre tokmd en CI**, quiero **que si no hay key nunca quede
> colgado esperando un input que no va a llegar**, para **que el pipeline
> falle rápido y claro, como hoy**.

> Como **alguien que mira `tokmd archivo.md --sections` sobre un archivo
> grande**, quiero **que cada fila entre en una sola línea sin romperse**,
> para **poder leer el árbol de verdad**.

## 2. Corte de entrega

- **Incluye:**
  - Rename `--verify` → `--live` en todo el código, tests y README (sin
    alias de compatibilidad).
  - `src/tokmd/keystore.py` (nuevo): `resolve_api_key(provider: str) ->
    str | None` con la cadena **env var → `keyring` → archivo de la
    carpeta de config → `None`**; `save_api_key(provider, key)`,
    `forget_api_key(provider)`. `provider` es `"anthropic"` u `"openai"`.
  - Carpeta de config de tokmd, **por usuario**, ya prevista en ADR-008:
    `%APPDATA%\tokmd\` (Windows) / `~/.config/tokmd/` (Linux/Mac),
    override por `TOKMD_CONFIG_DIR`. El archivo de key vive ahí
    (`anthropic.key`, `openai.key` — sólo el valor, sin TOML).
  - `verify.py` (se puede renombrar a `live.py` o mantener el nombre de
    archivo — decisión menor de Desarrollo, no cambia el contrato):
    `get_client()` usa `keystore.resolve_api_key("anthropic")`.
  - **Módulo Codex/OpenAI nuevo** (`src/tokmd/live_openai.py` o similar):
    mismo patrón que `verify.py` pero contra `POST
    /v1/responses/input_tokens`; usa `OPENAI_API_KEY` vía
    `keystore.resolve_api_key("openai")`.
  - `cli.py`: prompt de 4 opciones (ADR-009) cuando `--live` se pide sin
    key **y** `sys.stdin.isatty()`; el texto dice «gratis» para Anthropic
    y «costo no confirmado por OpenAI» para Codex; opción 1 sólo en
    memoria, 2 guarda con `keystore.save_api_key`, 3 cae a offline con
    aviso, 4 cancela. Fuera de TTY, error inmediato como hoy.
  - Flags nuevos: `--forget-key` (borra la key del proveedor resuelto por
    la plataforma activa), `--about` (muestra el banner y sale con 0, sin
    tocar ningún archivo).
  - **Banner** (`src/tokmd/banner.py`, nuevo): texto fijo con nombre,
    versión (de `importlib.metadata`), fecha del último release (constante
    a actualizar por release, o derivada de `importlib.metadata` si hay un
    campo disponible — decisión de Desarrollo), cantidad de motores
    soportados (constante), autor. Se invoca **sólo** desde el prompt de
    key faltante y desde `--about`; nunca en una corrida normal.
  - **Legibilidad de `--sections`** (opción A de
    `[[20260930-lectura-del-arbol-de-secciones]]`): cada fila truncada al
    ancho real de la terminal (`shutil.get_terminal_size()`, con fallback
    fijo si no hay terminal — p.ej. al redirigir a archivo) con `…` al
    final, nunca envuelve; los conectores del árbol nunca quedan en una
    línea separada del texto.
  - Extras en `pyproject.toml`: `verify` pasa a incluir `keyring>=25`
    además de `anthropic>=0.40`; nombre del extra se mantiene (menos
    rotura) aunque ahora cubra también Codex — evaluar en Desarrollo si
    conviene renombrarlo a `live` (`pip install tokmd[live]`) y dejar
    `verify` como alias del extra por compatibilidad de instalación (esto
    sí es gratis mantenerlo, a diferencia del flag del CLI).
  - README (EN/ES) y `CHANGELOG.md` con todo lo anterior.
- **No incluye:**
  - Nada de ADR-008 más allá de reusar su carpeta de config (el registro
    multi-modelo en sí es PBI-010, sin tocar acá).
  - Backend de 1Password (ADR-009, enmienda: no en esta versión).
  - El treemap/`--html` (`[[20260930-lectura-del-arbol-de-secciones]]`,
    opción B): PBI propio, después de este.
  - `--live` para Gemini/Kimi/otros: sigue fuera de alcance (ADR-009).
- **Dependencias:** ADR-009 aceptado, con su enmienda 0.3.0 (✅). `keyring`
  disponible para Desarrollo/QA.
- **Riesgos:**
  - Confundir la resolución de key entre proveedores (usar la de
    Anthropic para Codex o viceversa). Mitigación: `provider` explícito en
    toda la API de `keystore.py`, nunca un booleano genérico.
  - El banner filtrándose a una corrida normal por un bug de invocación.
    Mitigación: AC-12 lo prueba explícitamente.
  - Prometer «gratis» para OpenAI sin haberlo verificado. Mitigación: el
    texto lo dice tal cual está (no confirmado), AC-13 lo fija como
    contrato de texto, no sólo de comportamiento.
  - Tests que tocan `keyring` real o archivos reales de la carpeta de
    config de quien corre la suite. **No negociable:** todo mockeado.

## 3. Criterios de aceptación

### `--live`: rename y resolución de key (Claude)

- [ ] **AC-01:** Dado `tokmd --help`, cuando se revisa, entonces existe
      `--live` y **no** existe `--verify` ni `--api-key`.
- [ ] **AC-02:** Dado `--live` sin key en ninguna capa y `stdin` TTY
      simulado, cuando se corre, entonces aparece el prompt con las 4
      opciones, precedido del banner.
- [ ] **AC-03:** Opción 1 → key en memoria, `keyring.set_password` y el
      archivo de config **no** se tocan.
- [ ] **AC-04:** Opción 2 → se llama `keyring.set_password`; una segunda
      corrida sin env var **no** pregunta.
- [ ] **AC-05:** Opción 3 → sigue en offline (`ctok`), aviso de que no se
      verificó, exit 0.
- [ ] **AC-06:** Opción 4 → exit ≠ 0, no imprime número.
- [ ] **AC-07 (protege CI):** `stdin` no-TTY (subprocess real con
      `stdin=DEVNULL`) y sin key → error inmediato, mismo mensaje de hoy,
      **sin prompt, sin colgarse**.
- [ ] **AC-08:** Prioridad de resolución: env var > `keyring` > archivo
      de la carpeta de config > `None`. Verificable con las cuatro
      combinaciones presentes a la vez, sólo gana la de mayor prioridad.
- [ ] **AC-09:** Si el archivo de la carpeta de config tiene la key (sin
      env var ni `keyring`), `--live` la usa sin preguntar nada.
- [ ] **AC-10:** `--forget-key` borra de `keyring` **y** del archivo de
      config; exit 0 siempre (exista o no algo que borrar).
- [ ] **AC-11 (sin regresión):** `ANTHROPIC_API_KEY` seteada, sobre el
      `CLAUDE.md` global del snapshot del 27/09 → **17.381**, igual que
      PBI-009. Suite completa de 2.1.0 en verde.

### Banner

- [ ] **AC-12:** Una corrida normal sin `--about` y con key ya resuelta
      (por cualquier capa) **no** imprime el banner en ningún flujo —
      `stdout` es sólo el número.
- [ ] **AC-13:** `tokmd --about` imprime el banner (nombre, versión, fecha
      de release, cantidad de motores, autor) y sale con 0 sin leer ningún
      archivo `FILE`.

### Codex/OpenAI

- [ ] **AC-14:** Dado `--platform codex --live` sin `OPENAI_API_KEY` en
      ninguna capa y TTY, cuando se corre, entonces el prompt dice
      explícitamente que el costo de este endpoint **no está confirmado
      por OpenAI** (texto exacto, no aproximado) — a diferencia del de
      Anthropic, que dice que es gratis.
- [ ] **AC-15:** Las mismas 4 opciones y la misma cadena de resolución
      (env → keyring → archivo → prompt) aplican a Codex, con
      `provider="openai"`, sin mezclarse con la key de Anthropic.

### Legibilidad de `--sections`

- [ ] **AC-16:** Dado un título más largo que el ancho de la terminal
      (`shutil.get_terminal_size()` mockeado a un valor chico, p. ej. 60
      columnas), cuando se corre `--sections`, entonces esa fila se trunca
      con `…` y ocupa **una sola línea** — no envuelve.
- [ ] **AC-17:** Dado que la salida **no** es una terminal (redirigida a
      archivo), cuando se corre `--sections`, entonces no trunca (usa el
      ancho completo o un fallback razonable — decisión de Desarrollo,
      documentada) para que el archivo resultante sea útil sin depender
      del ancho de quien lo generó.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/keystore.py` (nuevo),
  `src/tokmd/banner.py` (nuevo), `src/tokmd/verify.py` (o `live.py`),
  módulo nuevo para Codex/OpenAI, `src/tokmd/cli.py`, `src/tokmd/render.py`
  (truncado de filas).
- **Herramientas disponibles:** `keyring>=25` (nuevo), `click`, `shutil`
  (stdlib, para el ancho de terminal).
- **Versión de tests y configuración:** `pytest`; cero contacto con
  `keyring` real, con la red, o con la carpeta de config real de quien
  corre la suite (usar `tmp_path`/`monkeypatch` de `TOKMD_CONFIG_DIR`).
- **Métricas:** AC-11 (17.381) es el dato dorado de no regresión.
- **ADR requerido:** `[[ADR-009-manejo-de-api-key-para-verify]]` —
  `accepted` con enmienda 0.3.0.

## 5. Handoffs

### Definition of Ready

- [ ] Valor, alcance y fuera de alcance claros.
- [ ] Criterios observables y testeables.
- [x] ADR enlazado y `accepted`.
- [ ] Casos de Kiwi cargados como PROPOSED
      (`[[PBI-011-casos-de-prueba]]`).

**Estado:** `not ready` — falta la confirmación final de Fabián sobre este
corte ampliado (0.2.0) antes de que TDD escriba los tests; el corte 0.1.0
ya tenía su OK pero cambió sustancialmente.

### Handoff a TDD (DeepSeek)

- **AC a convertir en pruebas:** AC-01 a AC-17, en
  `tests/test_keystore.py`, `tests/test_banner.py`,
  `tests/test_cli_live.py` (reemplaza `test_cli_verify.py`/
  `test_cli_verify_gap01.py`), `tests/test_render.py` (ampliado con
  AC-16/17).
- **Fixtures y contratos:** `keyring` falso en memoria con modo
  `NoKeyringError`; `TOKMD_CONFIG_DIR` apuntado a `tmp_path` en cada test;
  `monkeypatch` de `sys.stdin.isatty` y de `shutil.get_terminal_size`;
  para AC-07 real, `subprocess.run(..., stdin=subprocess.DEVNULL)`.
- **Rojo real:** cada test falla contra el código de hoy (sin
  `keystore.py`, sin `--live`, sin banner, sin truncado) antes de
  entregar.

### Handoff a Desarrollo (Claude Sonnet 5)

- **Restricciones confirmadas:** las 5 reglas de la enmienda 0.3.0 de
  ADR-009. No modificar tests para que pasen; defecto en un test →
  reportar a TDD con evidencia (ROL-05).
- **Preguntas abiertas (decisión menor de Desarrollo, documentar en
  dev-log):** nombre exacto del archivo de `verify.py`
  (mantener o pasar a `live.py`); si el extra de `pyproject.toml` se
  renombra a `live` con `verify` como alias.

### Handoff a QA (Kimi K3)

- **Candidato identificable:** commit corto del snapshot.
- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Casos independientes:** `TOK-011-C01` a `C17` de
  `[[PBI-011-casos-de-prueba]]`.
- **Evidencia mínima:** log crudo + resultado por caso en
  `tools/kiwi/resultados/`. Para AC-11, QA corre `--live` a mano con su
  propia `ANTHROPIC_API_KEY` sobre la copia del `CLAUDE.md` global del
  snapshot, como en PBI-009.

## 6. Cierre

- **Artefactos y enlaces:** pendiente.
- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** treemap/`--html`
  (`[[20260930-lectura-del-arbol-de-secciones]]`, opción B); escaneo
  recursivo (`-r`).
