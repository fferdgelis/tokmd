---
title: "PBI-011 — --live (Claude y Codex) con key guardada en engines/, pregunta interactiva, banner, y tabla de --sections legible"
aliases:
  - "PBI-011 live, engines y legibilidad"
project: tokmd
document_type: pbi
status: ready
version: 0.3.0
created: 2026-09-30
updated: 2026-09-30
language: es
owners:
  - project-founder
author_human: "none"
created_by: "llm"
llm_provider: "Anthropic"
llm_model: "claude-opus-5-5"
llm_harness: "Claude Code Desktop"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription"
modified_by: "Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription"
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
  - "[[20260930-configuracion-de-motores-y-api-keys]]"
  - "[[20260930-lectura-del-arbol-de-secciones]]"
  - "[[PBI-011-casos-de-prueba]]"
---

# PBI-011 — `--live` (Claude y Codex), key en `engines/`, pregunta, banner y tabla legible

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación tras aceptar ADR-009. |
| 2026-09-30 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | `--verify`→`--live`, banner, Codex, legibilidad (opción A). |
| 2026-09-30 | 0.3.0 | Anthropic / claude-opus-5-5 / Claude Code Desktop / subscription | Aplicada la decisión `20260930-configuracion-de-motores-y-api-keys` (aceptada por Fabián): sin `keyring`; key en texto plano dentro de `engines/<motor>.toml` con permisos; 1Password por `op://`; carpetas por sistema operativo con capa de usuario y de sistema; pregunta de 3 opciones (guardar / offline / no volver a preguntar). Contrato público fijado para TDD. Pasa a `ready`. |

## Roles (ROL-02)

`TDD: DeepSeek (deepseek-v4-pro) · Desarrollo: Claude (Claude Code) · QA: Kimi K3 (OpenCode + OpenRouter, read-only)` — ADR-006.

## 1. Valor y contexto

- **Problema.** Fabián probó tokmd como un usuario nuevo: `--verify` corta
  en seco sin key, la tabla de `--sections` es ilegible en una consola
  angosta, y nada orienta sobre qué es la herramienta.
- **Stakeholder:** Fabián Ferdgelis.
- **Resultado esperado.** `--live` (Claude y Codex) pregunta en vez de
  cortar, guarda la key en un archivo de motor que un sysadmin entiende y
  edita, nunca cuelga un CI, y `--sections` se lee en cualquier ancho.
- **Prioridad:** la más alta abierta (pedido explícito, antes que PBI-010).

## 2. Corte de entrega

- **Incluye:** todo lo de la sección 4 (contrato público), README EN/ES,
  `CHANGELOG.md` `[2.1.0]`.
- **No incluye:** `keyring` ni cifrado propio; que los archivos de motor
  definan cómo se cuenta (eso es PBI-010 — acá sólo guardan `live`,
  `api_key` y `ask_for_key`); `--live` para Gemini/Kimi/DeepSeek; treemap
  `--html`.
- **Riesgos:** ver ADR-009 enmienda 0.4.0. El nuevo: la llamada real de
  Codex necesita una `OPENAI_API_KEY` que **hoy no está en la bóveda**
  (`multi-modelos-ai` tiene anthropic, deepseek, nvidia y openrouter). La
  verificación real de AC-20 la hace Fabián con su key.

## 3. Criterios de aceptación

### Carpetas y archivos de motor

- [ ] **AC-01:** `user_config_dir()` devuelve `TOKMD_CONFIG_DIR` si está
      definida; si no, `%APPDATA%\tokmd` en Windows,
      `~/Library/Application Support/tokmd` en macOS, y
      `$XDG_CONFIG_HOME/tokmd` (o `~/.config/tokmd`) en Linux.
- [ ] **AC-02:** `system_config_dir()` devuelve `TOKMD_SYSTEM_CONFIG_DIR`
      si está definida; si no, `%ProgramData%\tokmd`,
      `/Library/Application Support/tokmd` o `/etc/tokmd`.
- [ ] **AC-03:** `tokmd --init` copia `engines/claude-code.toml`,
      `engines/codex.toml` y `engines/README.md` a la carpeta de usuario,
      **sin pisar** archivos existentes, imprime la ruta y sale con 0, sin
      pedir `FILE`.
- [ ] **AC-04:** `load_engine(nombre)` combina sistema y usuario: el valor
      del usuario gana clave por clave; sin archivos, devuelve los valores
      por defecto empaquetados.
- [ ] **AC-05:** `save_engine_value(nombre, clave, valor)` escribe en el
      archivo del usuario (crea carpetas si faltan) y conserva las demás
      claves; en Linux/macOS el archivo queda con permisos `0600`.

### Resolución de la key

- [ ] **AC-06:** Orden: variable de entorno (`ANTHROPIC_API_KEY` para
      `claude-code`, `OPENAI_API_KEY` para `codex`) → `api_key` del archivo
      del usuario → del sistema → `None`. Una `api_key` vacía cuenta como
      ausente.
- [ ] **AC-07:** Si el valor empieza con `op://`, se resuelve ejecutando
      `op read <valor>` y se usa su salida sin espacios finales; si `op` no
      está instalado o falla, error claro (`OpReferenceError`), sin
      traceback en el CLI.
- [ ] **AC-08:** La key de Anthropic nunca se usa para Codex ni al revés.

### `--live` y la pregunta

- [ ] **AC-09:** `--live` existe; `--verify` y `--api-key` no existen.
- [ ] **AC-10:** Con key disponible, `--live` cuenta contra la API del
      motor resuelto (Anthropic para `claude-code`, OpenAI para `codex`) y
      **stdout es sólo el número**, sin banner.
- [ ] **AC-11:** Sin key, con `ask_for_key = true` y terminal interactiva:
      se muestra el banner y la pregunta **por stderr** con exactamente
      tres opciones: `[1]` ingresar y guardar, `[2]` seguir offline,
      `[3]` no volver a preguntar.
- [ ] **AC-12:** Opción 1: pide la key sin mostrarla, la guarda con
      `save_engine_value(..., "api_key", key)` y cuenta en modo live.
- [ ] **AC-13:** Opción 2: cuenta offline, aviso por stderr, exit 0, no
      guarda nada.
- [ ] **AC-14:** Opción 3: guarda `ask_for_key = false`, cuenta offline,
      exit 0; la corrida siguiente **no** pregunta: aviso de una línea por
      stderr y offline.
- [ ] **AC-15 (protege CI):** Sin key y sin terminal interactiva (stdin
      no es TTY): **nunca** pregunta ni cuelga; error con el nombre de la
      variable de entorno, exit ≠ 0. Probado con `subprocess` real y
      `stdin=DEVNULL`.
- [ ] **AC-16:** El texto de la pregunta dice que el conteo de Anthropic
      es gratis; el de Codex dice que **el costo no está confirmado por
      OpenAI**.
- [ ] **AC-17:** `tokmd --forget-key` vacía `api_key` y vuelve
      `ask_for_key = true` en los archivos de motor del usuario; exit 0
      aunque no exista ninguno; no pide `FILE`.

### Banner

- [ ] **AC-18:** `tokmd --about` imprime el banner (nombre, versión,
      fecha de último release, modelos soportados, autor, email) y sale con
      0 sin pedir `FILE`. Una corrida sin `--about` y sin pregunta **nunca**
      muestra el banner.

### Sin regresión y llamada real

- [ ] **AC-19:** Con `ANTHROPIC_API_KEY` real, `tokmd CLAUDE.md --live`
      sobre el `CLAUDE.md` global del 27/09 da **17.381**. Suite anterior en
      verde (retrofit de los tests de `--verify` a `--live`).
- [ ] **AC-20:** Con una `OPENAI_API_KEY` real, `tokmd f.md --platform
      codex --live` devuelve un número > 0 y queda registrado si la llamada
      se cobró (saldo antes/después). Lo corre Fabián.

### Legibilidad de `--sections`

- [ ] **AC-21:** `render(..., width=N)` en formato `table`: ninguna línea
      supera `N` caracteres; las truncadas terminan en `…`; los conectores
      del árbol quedan en la misma línea que su texto. `width=None`: sin
      truncar.
- [ ] **AC-22:** El CLI pasa el ancho de la terminal sólo si stdout es una
      terminal; redirigido a archivo, no trunca.

## 4. Contrato público (lo que ve TDD)

**`tokmd.config`**
- `user_config_dir() -> Path`, `system_config_dir() -> Path` (AC-01/02).
- `ENGINE_ENV_VARS = {"claude-code": "ANTHROPIC_API_KEY", "codex": "OPENAI_API_KEY"}`.
- `load_engine(name: str) -> dict` (AC-04): claves `engine`, `live`,
  `api_key` (str, `""` por defecto), `ask_for_key` (bool, `True` por
  defecto), más las que cada plantilla traiga.
- `save_engine_value(name: str, key: str, value) -> Path` (AC-05).
- `resolve_api_key(name: str) -> str | None` (AC-06/07).
- `forget_api_keys() -> None` (AC-17).
- `init_config() -> Path` (AC-03), devuelve la carpeta de usuario.
- `class OpReferenceError(Exception)`.
- `op read` se invoca con `subprocess.run(["op", "read", ref], ...)`
  (los tests lo reemplazan con `monkeypatch` sobre `tokmd.config.subprocess.run`).

**`tokmd.banner`**
- `banner_text() -> str`: contiene `tokmd`, la versión instalada, la fecha
  de último release, `Modelos soportados`, `Fabián Ferdgelis` y
  `fferdgelis@gmail.com`.

**`tokmd.render.render(...)`** gana `width: int | None = None` (AC-21).

**CLI (`tokmd.cli.main`)**
- Flags nuevos: `--live`, `--about`, `--forget-key`, `--init`. Se va
  `--verify`.
- Motor de la corrida: tokenizador `claude` → `claude-code`; `openai` →
  `codex`.
- Funciones que los tests pueden reemplazar con `monkeypatch` en
  `tokmd.cli`: `get_client` (Anthropic, ahora recibe la key:
  `get_client(api_key)`), `measure_frame`, `count_verified`,
  `get_openai_client(api_key)`, `count_openai_live(client, text, model)`,
  `resolve_api_key`, `stdin_is_interactive()` (envuelve
  `sys.stdin.isatty()` para que el test la controle).
- Las pruebas usan `TOKMD_CONFIG_DIR` y `TOKMD_SYSTEM_CONFIG_DIR` apuntando
  a `tmp_path`: **ningún test toca la carpeta real de quien corre la
  suite, ni la red, ni `op` real.**

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables (contrato público en la sección 4).
- [x] ADR-009 `accepted` con enmienda 0.4.0; decisión de configuración
      `accepted`.
- [ ] Casos de Kiwi cargados como PROPOSED.

**Estado:** `ready` para TDD. La carga en Kiwi se hace en paralelo.

### Handoff a TDD (DeepSeek)

Specs en `tools/deepseek/specs/PBI-011-*.md.prompt`: `config`, `cli-live`
(incluye el retrofit de `test_cli_verify*.py`), `banner`, `render-width`.
Rojo real contra el código de hoy antes de pasar a Desarrollo.

### Handoff a Desarrollo

No modificar tests; defecto en un test → a TDD con evidencia (ROL-05).
Decisiones menores en el dev-log.

### Handoff a QA (Kimi K3)

Casos `TOK-011-C01` a `C22`, read-only, sobre snapshot. AC-19 con key
real; AC-20 lo corre Fabián.

## 6. Cierre

- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
