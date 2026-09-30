---
title: "PBI-011 — --verify pregunta por la API key en modo interactivo y la guarda con keyring"
aliases:
  - "PBI-011 API key interactiva"
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
  - "[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]"
  - "[[PBI-006-verificacion-contra-api]]"
  - "[[PBI-011-casos-de-prueba]]"
---

# PBI-011 — `--verify` pregunta por la API key en modo interactivo y la guarda con `keyring`

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, a pedido de Fabián («Priorizá B, empezá el PBI»), inmediatamente después de aceptar ADR-009. Borrador para su revisión; pasa a `ready` cuando acepte el corte. |

## Roles (ROL-02)

`TDD: DeepSeek (deepseek-v4-pro) · Desarrollo: Claude Sonnet 5 (Claude Code) · QA: Kimi K3 (OpenCode + OpenRouter, read-only)` — mismo reparto que PBI-009/010, según ADR-006.

## 1. Valor y contexto

- **Problema.** Fabián probó `--verify` en una terminal limpia (la que
  usaría cualquier persona que instale tokmd por primera vez) y se
  encontró con un error seco: falta la key, cortá. Es correcto y seguro,
  pero es la razón por la que nadie prueba el feature que demuestra que
  tokmd es confiable. Y lo que Fabián maneja para sus propias keys —la
  bóveda DPAPI— es infraestructura de su máquina, no algo que tokmd pueda
  asumir que existe (ADR-009).
- **Stakeholder:** Fabián Ferdgelis, owner del proyecto.
- **Resultado esperado.** En una terminal interactiva, sin key en el
  entorno ni guardada, `--verify` pregunta qué hacer en vez de cortar en
  seco. En un script o CI, sigue cortando en seco exactamente como hoy.
- **Prioridad:** la más alta abierta, por pedido explícito («priorizá
  B»), por delante de PBI-010 y PBI-011 recursivo (que pasa a ser
  PBI-012 cuando se escriba).
- **Hipótesis.** La fricción de hoy, no la falta de interés, es lo que
  hace que `--verify` casi no se use. Si preguntar en el momento cuesta
  tres segundos y guardarla es opcional, el uso sube.

### Historia de usuario

> Como **desarrollador que instala tokmd por primera vez**, quiero
> **que `tokmd archivo.md --verify` me pregunte por mi key si no la
> tiene, en vez de sólo decirme que falta**, para **poder probar la
> verificación real sin tener que ir a buscar documentación sobre
> variables de entorno**.

> Como **ese mismo desarrollador, la segunda vez**, quiero **que si
> guardé mi key no me la vuelva a pedir**, para **no repetir el trámite
> en cada corrida**.

> Como **quien corre tokmd en un pipeline de CI**, quiero **que si no hay
> key nunca me quede colgado esperando un input que no va a llegar**,
> para **que el pipeline falle rápido y claro, como hoy**.

## 2. Corte de entrega

- **Incluye:**
  - `src/tokmd/keystore.py` (nuevo): `resolve_api_key() -> str | None`
    (env var → `keyring` → `None`, en ese orden), `save_api_key(key)`,
    `forget_api_key()`, todas envolviendo `keyring` con manejo de
    `keyring.errors.NoKeyringError`/`PasswordDeleteError` sin que se
    propague un traceback crudo.
  - `verify.py`: `get_client()` deja de mirar sólo `os.environ` — usa
    `keystore.resolve_api_key()`. Si sigue sin haber key **y**
    `sys.stdin.isatty()`, `cli.py` dispara el prompt (la decisión de
    UI vive en `cli.py`, no en `verify.py`, que sigue siendo lógica pura
    sin `click`).
  - `cli.py`: el prompt de 4 opciones de ADR-009, con `click.prompt`/
    `click.confirm`; opción 1 sólo en memoria; opción 2 llama a
    `save_api_key`; opción 3 cae al camino offline (`ctok`) con un aviso
    de una línea; opción 4 sale con exit code ≠ 0 sin ejecutar nada.
  - Flag nuevo `--forget-key`: borra lo guardado en `keyring` bajo el
    servicio `tokmd`, sale con 0 (exista o no algo guardado — idempotente).
  - Extra `verify` en `pyproject.toml`: agrega `keyring>=25`.
  - README (EN/ES): sección sobre el prompt, qué guarda y dónde
    (Credential Manager / Keychain / Secret Service), y `--forget-key`.
  - `CHANGELOG.md` `[2.2.0]` (o la que corresponda según lo que esté
    publicado cuando este PBI cierre).
- **No incluye:**
  - Nada de ADR-008 (registro multi-modelo): este PBI es ortogonal, sólo
    toca la resolución de la key de Anthropic.
  - `--verify` para otros oráculos (Gemini, Kimi): fuera de alcance,
    como ya dice ADR-009.
  - Rotar o expirar keys guardadas: `keyring` las guarda hasta que el
    usuario las borra a mano o con `--forget-key`; no hay TTL.
- **Dependencias:** ADR-009 aceptado (✅). `keyring` disponible para
  Desarrollo y QA en sus entornos (Windows con Credential Manager; el
  entorno de QA puede necesitar `keyrings.alt` o backend de archivo
  cifrado si no tiene sesión de escritorio — se decide en el handoff a
  QA, no bloquea Desarrollo).
- **Riesgos:**
  - Un test que llama a `keyring` real y ensucia el almacén de secretos
    de quien corre la suite. **Mitigación, no negociable:** todo test
    mockea `keyring.set_password`/`get_password`/`delete_password`;
    ninguno toca el almacén real de la máquina que corre `pytest`.
  - Detectar mal `isatty()` y que el prompt aparezca en CI, colgando un
    pipeline. Mitigación: AC-05 es justamente ese caso, con evidencia.
  - `keyring` sin backend en Linux headless: falla con mensaje, no con
    traceback (AC-07).

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado `--verify`, sin `ANTHROPIC_API_KEY` en el entorno,
      sin nada guardado en `keyring`, y `stdin` simulado como TTY, cuando
      se corre, entonces se muestra el prompt con las 4 opciones exactas
      de ADR-009 (texto verificable, no aproximado).
- [ ] **AC-02:** Dado ese prompt, cuando se elige **[1]**, entonces se
      pide la key con entrada oculta (`hide_input=True` o equivalente),
      se usa para esa corrida, y **no** se llama a `keyring.set_password`
      en ningún momento (verificable con mock que falla si se invoca).
- [ ] **AC-03:** Dado ese prompt, cuando se elige **[2]** con una key
      válida, entonces se llama a `keyring.set_password` con esa key, se
      usa para esa corrida, y una **segunda** corrida del mismo comando
      (mismo entorno, sin `ANTHROPIC_API_KEY`) **no** vuelve a preguntar:
      resuelve la key desde `keyring` directamente.
- [ ] **AC-04:** Dado ese prompt, cuando se elige **[3]**, entonces
      continúa en modo offline (`ctok`), imprime el total igual que sin
      `--verify`, y el mensaje deja explícito que no se contrastó contra
      la API.
- [ ] **AC-05 (el que protege CI):** Dado `--verify` sin key disponible y
      `sys.stdin.isatty()` devolviendo `False` (pipe, redirección, CI),
      cuando se corre, entonces **no aparece ningún prompt**, termina
      inmediato con el mismo `MissingApiKeyError`/mensaje de hoy, exit
      code ≠ 0. Verificable con `subprocess` real con stdin redirigido
      desde `/dev/null` o `NUL`, no sólo mockeado.
- [ ] **AC-06:** Dado `ANTHROPIC_API_KEY` seteada en el entorno, cuando se
      corre `--verify` (con o sin algo guardado en `keyring`), entonces
      se usa la del entorno y **no** se consulta `keyring` — prioridad
      env var > keyring, sin excepción (AC-06 de ADR-009).
- [ ] **AC-07:** Dado que `keyring.get_password`/`set_password` lanza
      `keyring.errors.NoKeyringError` (sin backend disponible), cuando se
      elige **[2]**, entonces el mensaje explica que no hay backend
      disponible y sugiere `ANTHROPIC_API_KEY` como alternativa — nunca
      un traceback crudo, exit code ≠ 0.
- [ ] **AC-08:** Dado algo guardado en `keyring` bajo el servicio de
      tokmd, cuando se corre `tokmd --forget-key`, entonces se borra,
      sale con 0, y la siguiente corrida de `--verify` (sin env var)
      vuelve a preguntar (AC-01).
- [ ] **AC-09:** Dado que **no** hay nada guardado, cuando se corre
      `tokmd --forget-key`, entonces sale con 0 igual (idempotente, no
      es error borrar lo que no existe).
- [ ] **AC-10 (sin regresión):** Dado `ANTHROPIC_API_KEY` seteada como
      hoy, cuando se corre `tokmd CLAUDE.md --verify` sobre el
      `CLAUDE.md` global del snapshot, entonces el número sigue
      coincidiendo con el de PBI-009 (17.381 sobre el archivo del
      27/09 — el dato dorado no cambia, sólo cambia cómo se consiguió
      la key). La suite completa de 2.1.0 (la que deje PBI-010) sigue en
      verde.
- [ ] **AC-11:** Dado que la key nunca se pasa como flag, cuando se
      revisa el `--help`, entonces no existe ningún flag `--api-key` ni
      equivalente (regresión de la regla ya escrita en el código).

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/keystore.py` (nuevo),
  `src/tokmd/verify.py` (cambia `get_client`), `src/tokmd/cli.py` (prompt
  y `--forget-key`).
- **Herramientas disponibles:** `keyring>=25` (nuevo, extra `verify`),
  `click` (ya está, para el prompt).
- **Versión de tests y configuración:** `pytest`; **cero contacto con el
  almacén real de secretos de la máquina que corre la suite** — regla
  dura, no negociable, análoga a «la suite no toca la red» de PBI-006/009.
  `monkeypatch` sobre las tres funciones de `keyring` en todos los tests.
- **Métricas:** AC-10 es el dato dorado de no regresión (17.381).
- **ADR requerido:** `[[ADR-009-manejo-de-api-key-para-verify]]` —
  `accepted`, ya no bloquea.

## 5. Handoffs

### Definition of Ready

- [ ] Valor, alcance y fuera de alcance claros.
- [ ] Criterios observables y testeables.
- [x] ADR enlazado y `accepted`.
- [ ] Casos de Kiwi cargados como PROPOSED
      (`[[PBI-011-casos-de-prueba]]`).

**Estado:** `not ready` — falta que Fabián confirme el corte (sección 2) y
que TDD escriba los casos de Kiwi antes de que Desarrollo empiece.

### Handoff a TDD (DeepSeek)

- **AC a convertir en pruebas:** AC-01 a AC-11, en
  `tests/test_keystore.py` (nuevo) y `tests/test_cli_verify.py`
  (ampliado).
- **Fixtures y contratos:** un `keyring` falso en memoria (dict) que se
  inyecta por `monkeypatch.setattr("tokmd.keystore.keyring", fake)`, con
  los tres métodos (`get_password`, `set_password`, `delete_password`) y
  un modo que simula `NoKeyringError` para AC-07; `monkeypatch` de
  `sys.stdin.isatty` para AC-01 y AC-05; para AC-05 real (no mockeada),
  un test con `subprocess.run(..., stdin=subprocess.DEVNULL)`.
- **Rojo real:** cada test falla contra el código de hoy (sin
  `keystore.py`, sin prompt, sin `--forget-key`) antes de entregar.

### Handoff a Desarrollo (Claude Sonnet 5)

- **Restricciones confirmadas:** las reglas 1 a 5 de la «Decisión
  propuesta» de ADR-009 (orden env→keyring→prompt; nunca flag de CLI;
  nunca se imprime/loguea la key; `--forget-key` explícito; texto del
  prompt informa que el endpoint es gratis). No modificar tests para que
  pasen; defecto en un test → reportar a TDD con evidencia (ROL-05).
- **Preguntas abiertas:** ninguna bloqueante.

### Handoff a QA (Kimi K3)

- **Candidato identificable:** commit corto del snapshot.
- **Canal de QA:** OpenCode + OpenRouter + Kimi K3, read-only.
- **Casos independientes:** `TOK-011-C01` a `C11` de
  `[[PBI-011-casos-de-prueba]]`.
- **Evidencia mínima:** log crudo + resultado por caso en
  `tools/kiwi/resultados/`. Para AC-10, QA corre `--verify` a mano con
  una `ANTHROPIC_API_KEY` propia sobre la copia del `CLAUDE.md` global
  del snapshot, como en PBI-009.

## 6. Cierre

- **Artefactos y enlaces:** pendiente.
- **Resultado de QA independiente:** `pending`.
- **Aceptación del owner:** `pending`.
- **PBI o Bug siguiente:** el escaneo recursivo (`-r` + `--html`,
  mencionado en `[[20260930-de-cli-a-producto-para-equipos]]`) queda
  como próximo número libre cuando se escriba.
