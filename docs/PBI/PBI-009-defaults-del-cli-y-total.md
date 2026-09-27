---
title: "PBI-009 — `tokmd archivo.md` funciona solo y da el total: plataforma Claude por defecto, desglose opt-in"
aliases:
  - "PBI-009 defaults del CLI"
project: tokmd
document_type: pbi
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
llm_model: "claude-opus-5"
llm_harness: "Claude Code"
llm_channel: "subscription"
reasoning_mode: "no expuesto"
last_modified_by: "Anthropic / claude-opus-5 / Claude Code / subscription"
modified_by: "Anthropic / claude-opus-5 / Claude Code / subscription"
reviewed_by: "pending"
review_status: "pending"
source_of_truth: true
tags:
  - project/tokmd
  - delivery/pbi
related_documents:
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
  - "[[PBI-004-cli-y-plataformas]]"
  - "[[PBI-005-render-de-salida]]"
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
---

# PBI-009 — `tokmd archivo.md` funciona solo y da el total

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación, a pedido de Fabián. **El número PBI-009 se reasignó**: antes designaba la configuración de la API key del `--verify`, que quedó diferida en `docs/diferido/verify-api-key/`. Borrador para revisión del owner; no está `ready`. |

## 1. Valor y contexto

- **Problema.** Fabián intentó usar `tokmd` como lo usaría cualquier
  desarrollador —abrir una terminal y preguntar cuánto mide su `CLAUDE.md`— y la
  herramienta no funcionó. Tres fallas de producto, en el orden en que las
  encontró:

  1. **No arranca sin parámetros.** `uvx tokmd "claude.md"` termina en error:

     ```
     Error: Missing option '--platform'. Choose from:
             claude-code,
             codex,
             opencode,
     ```

     Es la primera pantalla que ve un usuario nuevo, y es un error.
  2. **La plataforma no tiene default, y debería tenerlo.** El proyecto existe
     para gente que trabaja con Claude Code: que `--platform` sea obligatorio le
     hace elegir algo que ya está decidido por el propósito de la herramienta.
  3. **No existe el total.** La única salida es el desglose sección por sección.
     Lo primero que quiere saber cualquiera es **cuánto mide el archivo**, y
     `tokmd` no lo dice en ninguna parte — ni con el desglose.

- **Stakeholder:** Fabián Ferdgelis, owner del proyecto.
- **Resultado esperado:** `tokmd archivo.md` responde con el total, sin
  parámetros, asumiendo Claude Code. El desglose sigue existiendo y se pide.
- **Prioridad:** **la más alta abierta.** Afecta a `v1.0.0`, que ya está en PyPI,
  y toca el primer minuto de uso de cualquier usuario nuevo.
- **Hipótesis:** el default correcto es «el total, para Claude», y el desglose es
  la función avanzada. Hoy están al revés.

### Historia de usuario

> Como **desarrollador que trabaja con Claude Code**, quiero **escribir
> `tokmd CLAUDE.md` y ver cuánto me cuesta el archivo**, para **decidir si tengo
> que recortarlo, sin leer la ayuda ni elegir opciones que ya están decididas por
> el propósito de la herramienta**.

## 2. Corte de entrega

- **Incluye:**
  - `--platform` deja de ser obligatorio; su default es `claude-code`.
  - La salida por defecto es **una línea con el total del archivo**.
  - El desglose por secciones pasa a ser opt-in, con un flag nuevo.
  - El total se cuenta **de una sola pasada sobre el archivo completo**, no
    sumando filas (ver 4, «la decisión técnica»).
  - `README.md` y `README.es.md` actualizados: el ejemplo de portada pasa a ser
    `tokmd CLAUDE.md`.
  - `CHANGELOG.md` con el cambio incompatible declarado.

- **No incluye:**
  - **Arreglar `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`.** Va aparte,
    como bug, con su propio test de regresión. **Pero lo bloquea** — ver
    Dependencias.
  - Documentar `--verify` en el README (hueco conocido, va aparte).
  - Cualquier cosa de la API key: diferido en `docs/diferido/verify-api-key/`.
  - La línea `boundary drift: ±N` que `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]`
    promete y el código no imprime.

- **Dependencias:**
  - **`[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` es bloqueante para el
    desglose, no para el total.** El total contado de una pasada es correcto
    aunque el bug siga vivo; las filas del desglose seguirían 8,5 % abajo y no
    sumarían al total. **No se publica una versión donde el total y el desglose
    no cierren.**

- **Riesgos:**
  - **Rompe compatibilidad.** Quien hoy corra
    `tokmd x.md --platform claude-code` y espere la tabla va a recibir una línea.
    Decisión de versión en la sección 4.
  - Cambiar el default de salida toca `render.py`, que tiene datos dorados en
    `tests/test_render.py`.

## 3. Criterios de aceptación

- [ ] **AC-01:** Dado un archivo Markdown válido, cuando se corre
      `tokmd archivo.md` **sin ninguna opción**, entonces sale con código 0 y
      escribe el total de tokens del archivo para el tokenizador de Claude.
- [ ] **AC-02:** Dado ese mismo archivo, cuando se corre `tokmd archivo.md`,
      entonces el número informado es **igual** al de contar el archivo completo
      de una sola pasada con el tokenizador resuelto, **no** la suma de las filas
      del desglose.
- [ ] **AC-03:** Dado que no se pasa `--platform`, cuando se corre el comando,
      entonces la plataforma resuelta es `claude-code` y el tokenizador resuelto
      es el de Claude, con la misma familia por defecto que hoy (`4.8`).
- [ ] **AC-04:** Dado `--platform codex` explícito, cuando se corre el comando,
      entonces el default de `claude-code` **no** se aplica y el comportamiento
      de selección de tokenizador es el de hoy (sin regresión en
      `[[PBI-004-cli-y-plataformas]]`).
- [ ] **AC-05:** Dado el flag de desglose, cuando se corre
      `tokmd archivo.md <flag-de-desglose>`, entonces se imprime la tabla
      sección por sección como hoy, **y** el total.
- [ ] **AC-06:** Dado un archivo con encabezados y con `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`
      corregido, cuando se pide el desglose, entonces la suma de las filas de
      primer nivel coincide con el total informado (tolerancia: 0).
- [ ] **AC-07:** Dado `--format json`, cuando se corre sin el flag de desglose,
      entonces el JSON tiene el total como campo propio y es parseable.
- [ ] **AC-08:** Dado un archivo que no existe o una ruta que es un directorio,
      cuando se corre el comando, entonces el mensaje de error es legible y el
      código de salida no es 0 (sin regresión).
- [ ] **AC-09:** Dado un archivo Markdown **sin ningún encabezado**, cuando se
      corre el comando, entonces informa el total sin fallar.
- [ ] **AC-10:** Dado un archivo vacío, cuando se corre el comando, entonces
      informa `0` sin fallar ni tirar traceback.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/cli.py` (opciones y defaults),
  `src/tokmd/render.py` (salida y total).
- **Herramientas disponibles:** `click`, `markdown-it-py`, `ctok`, `tiktoken`.
  Sin dependencias nuevas.
- **Versión de tests y configuración:** `pytest`, con datos dorados a remedir en
  `tests/test_render.py` y `tests/test_cli.py`.
- **Métricas:** el total de `C:\Users\fferdgelis\.claude\CLAUDE.md` con
  tokenizador de Claude `4.8` tiene que dar **17.375** (medido el 27/09/2026
  contando el archivo de una pasada). Es el dato dorado del AC-02.
- **ADR requerido:** `to investigate`. Cambiar el default de salida de una
  herramienta ya publicada es una decisión con marcha atrás costosa; si Fabián
  quiere dejarla escrita, sería ADR-007.

### La decisión técnica que hay que tomar acá

**El total NO se calcula sumando las filas.** Se cuenta el archivo completo de
una pasada. Dos razones:

1. Es correcto por construcción, incluso con
   `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` sin arreglar.
2. La suma de filas **resta el marco (`FRAME`) una vez por sección en vez de una
   vez por documento**, que es la deriva estructural que
   `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` ya midió y aceptó para el
   desglose. Para un número que se presenta como «el total», esa deriva no es
   aceptable.

**Dato útil para quien lo implemente:** el total acumulado **ya se calcula y se
descarta**. En `render.py`, `_build_rows` hace
`_, rows = _accumulate_and_flatten(...)` y devuelve `rows[1:]` — tanto el primer
valor de la tupla como `rows[0]` (la fila `(document)`) llevan el acumulado.
**No reusar ese número**: arrastra las dos deformaciones de arriba. Sirve para
comparar contra el total real y detectar la deriva.

### Tres decisiones que son de Fabián

1. **Cómo se llama el flag del desglose.** Recomiendo **`--sections`**: dice qué
   hace y no se confunde con `--format`. Alternativas: `--detail`, `--by-section`,
   `--tree`.
2. **Qué número de versión.** Cambiar la salida por defecto rompe a cualquiera
   que parsee la tabla, así que por semver estricto es **`2.0.0`**. Es lo que
   recomiendo: cuesta lo mismo y no deja a nadie pisado en silencio.
   `1.1.0` con el cambio bien documentado en el `CHANGELOG` es defendible —
   `v1.0.0` tiene un día y es improbable que alguien ya dependa de la tabla—,
   pero es tu llamada, no mía.
3. **Si además querés la fila de total en el desglose** o sólo el total arriba.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables.
- [ ] ADR enlazado si cambia una decisión arquitectónica — **pendiente de que
      Fabián decida si quiere ADR-007.**
- [ ] Casos de Kiwi cargados como PROPOSED — **pendiente.**
- [ ] **Las tres decisiones de la sección 4 tomadas por el owner.**

**Estado:** `not ready` — es un borrador para que Fabián lo revise. Falta el
nombre del flag, el número de versión, y los casos en Kiwi.

### Handoff a TDD

- **AC a convertir en pruebas:** los diez. El AC-02 y el AC-06 son los que
  cazan el defecto de fondo: uno fija que el total se cuenta de una pasada, el
  otro que la tabla cierra contra el total.
- **Fixtures y contratos:** hacen falta dos fixtures nuevos —
  un archivo con encabezados sin cuerpo (el caso que destapó
  `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`, con `#` usado como
  comentario) y uno vacío (`tests/fixtures/empty.md.fixture` ya existe).
  Los datos dorados se remiden contra el tokenizador, no se escriben a mano.

### Handoff a Desarrollo

- **Restricciones confirmadas:** sin dependencias nuevas. `--verify` tiene que
  seguir funcionando igual. No romper `--platform codex` ni `opencode`
  explícitos (AC-04).
- **Preguntas abiertas:** las tres decisiones de la sección 4.

### Handoff a QA

- **Candidato identificable:** commit corto del snapshot, a definir.
- **Canal de QA:** OpenCode + Kimi K3, read-only.
- **Casos independientes:** uno por AC.
- **Evidencia mínima:** log crudo de la ejecución más el resultado por caso en
  `tools/kiwi/resultados/`.

## 6. Cierre

- **Artefactos y enlaces:** pendiente.
- **Resultado de QA independiente:** `pending`
- **Aceptación del owner:** `pending`
- **PBI o Bug siguiente:** `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`
  tiene que cerrarse para poder publicar esto con el desglose cuadrado.
