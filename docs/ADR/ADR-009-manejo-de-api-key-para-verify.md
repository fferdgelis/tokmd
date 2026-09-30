---
title: "ADR-009 — Cómo maneja tokmd la ANTHROPIC_API_KEY de --verify para usuarios que no son Fabián"
aliases:
  - "ADR-009 API key de verify"
project: tokmd
document_type: adr
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
  - adr
related_documents:
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
  - "[[ADR-008-registro-de-tokenizadores-por-configuracion]]"
  - "[[PBI-006-verificacion-contra-api]]"
---

# ADR-009 — Cómo maneja tokmd la `ANTHROPIC_API_KEY` de `--verify` para usuarios que no son Fabián

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Borrador. Fabián probó `--verify` sin key en su máquina, propuso que el sistema pregunte si dar de alta la key o seguir en modo aproximado, y pidió explícitamente definir esto **como si tokmd lo instalara otra persona**, no él. |

## Estado

`proposed`. Pendiente de la decisión de Fabián Ferdgelis.

## Contexto

Fabián corrió `tokmd CLAUDE.md --verify` sin `ANTHROPIC_API_KEY` seteada y
vio el error actual: mensaje claro, no cuelga, no pide nada. Preguntó cómo
debería comportarse para **«un montón de gente»** usando tokmd, y dio la
forma: si falta la key, preguntar si quiere darla de alta ahora o seguir en
modo offline.

**El hallazgo que cambia la pregunta:** la forma en que Fabián maneja sus
propias keys —la bóveda DPAPI central, `C:\ProgramData\IA\Secrets\DPAPI\`,
con el módulo `IA.DpapiSecrets`— es infraestructura personal de **esta
máquina Windows**, no algo que un usuario de `pip install tokmd` tiene. Y
tokmd ya no es sólo de esta máquina: su propio CI corre en **Ubuntu y
Windows** (`docs/PBI/PBI-007-empaquetado-y-publicacion.md`, workflow
`ci.yml`). DPAPI no existe en Linux ni en macOS. **La bóveda de Fabián no
es una opción para el producto, aunque siga siendo la forma correcta de
manejar sus propias keys en sus propios proyectos internos** (la regla
crítica de secretos del `CLAUDE.md` global sigue aplicando ahí, sin
cambios).

Estado actual del código (`src/tokmd/verify.py`, `get_client`): lee
**sólo** `os.environ["ANTHROPIC_API_KEY"]`; si falta, levanta
`MissingApiKeyError` con mensaje legible; nunca acepta la key como flag de
CLI («terminaría en el historial de la shell», dice el propio código).
`cli.py` la atrapa y termina con `click.UsageError`. No hay prompt, no hay
almacenamiento, no hay dependencia de secretos más allá de `anthropic` (el
extra `verify`).

## Dos problemas distintos, que conviene no mezclar

1. **¿Qué pasa en el momento** que falta la key y el usuario está mirando
   la terminal? (interactivo)
2. **¿Cómo se guarda** la key entre una corrida y la siguiente, para no
   pedirla cada vez? (persistencia)

Un CLI público con un feature secundario (`--verify` es el oráculo de
verificación, no el camino principal — el offline es exacto para Claude,
ADR-001) no debería resolver el problema 2 con algo pesado. Pero tampoco
puede ignorarlo: pedir la key a mano en cada corrida es fricción real, y es
la fricción que hace que nadie use `--verify` nunca.

## Opciones

### Opción A — Statu quo: sólo variable de entorno, sin prompt

Lo que hay hoy. El usuario exporta `ANTHROPIC_API_KEY` él mismo, cada vez o
en su perfil de shell.

- **Pros:** cero código nuevo, cero dependencias, cero superficie de
  ataque nueva. Es lo que hacen `git`, `docker`, casi cualquier CLI que
  delega a una env var estándar.
- **Contras:** fricción alta → `--verify` casi no se usa, que es
  exactamente lo que pasó hoy en la prueba de Fabián. El feature que
  demuestra que tokmd es confiable (contrastar contra la API real) queda
  escondido.
- **Riesgo:** bajo (~5 %). Es no hacer nada.

### Opción B — Prompt interactivo + guardado en el almacén de secretos del sistema operativo (`keyring`)

Cuando `--verify` se corre **en una terminal interactiva** (`sys.stdin.isatty()`)
y no hay `ANTHROPIC_API_KEY` en el entorno ni en el almacén, preguntar:

```
No se encontró ANTHROPIC_API_KEY.
  [1] Ingresarla ahora, sólo para esta corrida
  [2] Ingresarla y guardarla de forma segura para la próxima vez
  [3] Seguir en modo offline (ctok, sin contrastar contra la API)
  [4] Cancelar
>
```

- **[1]** la pide con `click.prompt(hide_input=True)` (no aparece en
  pantalla, no queda en el historial de la shell — a diferencia de un
  flag `--api-key`, que si quedaría en el historial), la usa en memoria
  para esta corrida y no la guarda en ningún lado.
- **[2]** la guarda con la librería **`keyring`** (PyPI, dependencia
  chica, sin transitivas pesadas), que delega al almacén nativo de cada
  sistema: **Windows Credential Manager**, **macOS Keychain**, **Secret
  Service de Linux** (GNOME Keyring / KWallet). Es el mismo patrón que usan
  `twine`, `poetry` y otros CLIs de PyPI para credenciales — no un archivo
  de texto plano como el de AWS CLI (`~/.aws/credentials`), que es un
  vector de filtración conocido.
- **[3]** sigue con `ctok`, exacto para Claude sin necesitar nada — no
  cambia nada del flujo normal.
- **Si `sys.stdin` no es una terminal** (CI, un pipe, un script): **nunca
  prompt**. Se mantiene el comportamiento de hoy, error inmediato y claro.
  Colgarse esperando input en un `GitHub Action` sería un bug, no una
  mejora.
- **Si `keyring` no tiene backend disponible** (Linux headless sin Secret
  Service, contenedor sin sesión de usuario): la opción [2] falla con un
  mensaje que explica por qué y sugiere la variable de entorno como
  alternativa; nunca cae a guardar en texto plano en silencio.
- **Pros:** resuelve los dos problemas (fricción en el momento y
  persistencia) con el estándar de la industria para esto, cruza
  plataformas de verdad (a diferencia de DPAPI), y nunca compromete la
  regla de «la key nunca aparece en pantalla ni en logs» que ya tiene el
  código.
- **Contras:** una dependencia nueva (`keyring`) en el extra `verify`;
  código nuevo con superficie de prueba (detectar TTY, simular los cuatro
  caminos, simular ausencia de backend de `keyring`).
- **Riesgo:** medio-bajo (~20 %). El riesgo principal es de UX (un prompt
  mal hecho es peor que un error claro), mitigable con AC explícitos y
  QA independiente.

### Opción C — Archivo de configuración propio (tipo `~/.aws/credentials`)

Guardar la key en `~/.config/tokmd/credentials` (o
`%APPDATA%\tokmd\credentials` en Windows), texto plano o con una ofuscación
simple.

- **Pros:** no depende de que el sistema tenga un almacén de secretos
  nativo disponible; funciona siempre.
- **Contras:** texto plano en disco es exactamente el patrón que la regla
  crítica de secretos de Fabián prohíbe para sus propios proyectos (bóveda
  DPAPI en vez de `.env`), y por el mismo motivo: cualquier proceso o
  backup que lea ese archivo tiene la key. Es peor práctica que la opción B,
  no mejor.
- **Riesgo:** medio-alto (~35 %), no por complejidad sino por seguridad —
  es el tipo de decisión que después hay que deshacer cuando alguien
  reporta la filtración.

## Decisión propuesta

**Opción B**, con `keyring` como dependencia del extra `verify` (pasa de
`["anthropic>=0.40"]` a `["anthropic>=0.40", "keyring>=25"]`), y estas
reglas fijas:

1. El prompt **sólo** aparece si: `--verify` fue pedido, no hay
   `ANTHROPIC_API_KEY` en el entorno, no hay nada guardado en `keyring`
   bajo el servicio `tokmd`/`ANTHROPIC_API_KEY`, **y** `sys.stdin.isatty()`
   es verdadero. Cualquier otra combinación mantiene el error actual.
2. Orden de resolución de la key, de mayor a menor prioridad: **env var**
   (lo que ya hay, sin cambios — permite CI y el patrón de Fabián con
   `$env:ANTHROPIC_API_KEY` en una sola consola) → **`keyring`** → prompt
   interactivo.
3. La key **nunca** se acepta como flag de CLI (eso no cambia) ni se
   imprime, loguea o devuelve por ninguna función (eso tampoco cambia).
4. Guardar y borrar son acciones explícitas del usuario: `tokmd --verify`
   pregunta; existe además `tokmd --forget-key` para borrar lo guardado en
   `keyring` sin tener que ir al Credential Manager / Keychain a mano.
5. El texto del prompt deja claro que el endpoint es **gratis** (ya
   verificado, sección 3 del README) y qué se guarda dónde, para que la
   decisión del usuario sea informada.

## Consecuencias

- Nueva dependencia opcional (`keyring`), sólo en el extra `verify`; el
  camino offline (el default) no la arrastra.
- `verify.py` gana una función de resolución de key (env → keyring →
  `None`) y `cli.py` gana el prompt, con `click.confirm`/`click.prompt`.
- Documentar en el README la opción [2] y el nuevo flag `--forget-key`.
- **Esto es un PBI de desarrollo real** (toca `verify.py` y `cli.py`,
  necesita tests para los cuatro caminos del prompt y para la detección de
  TTY), así que cuando se acepte entra con
  `TDD: <agente> · Desarrollo: <agente> · QA: <agente>` declarado, como
  PBI-009 y PBI-010.

## Lo que este ADR NO decide

- Nada de PBI-008/ADR-008 (registro multi-modelo): la resolución de key
  de este ADR es específica del motor `ctok`/Anthropic vía `--verify`; el
  día que haya `--verify` para otros oráculos (Gemini, Kimi), cada uno
  define su propia variable de entorno y entra al mismo mecanismo de
  `keyring` por su propio nombre de servicio.
- No cambia nada de cómo Fabián maneja sus propias keys en sus proyectos
  internos (DPAPI sigue siendo la regla ahí, sin excepción).

## Verificación y reversibilidad

- **Se verifica** con AC del PBI correspondiente: TTY simulado con key
  ausente → aparecen las 4 opciones; no-TTY → error actual sin prompt;
  `keyring` guardado → segunda corrida no pregunta; `--forget-key` borra y
  la tercera corrida vuelve a preguntar; ninguna ruta de test real llama a
  `keyring` sin mockear (regla de «la suite no toca red ni el almacén real
  del sistema que la corre»).
- **Se revierte** sacando `keyring` de las dependencias y el prompt de
  `cli.py`: vuelve a la opción A tal cual está hoy, sin que ningún dato
  guardado por un usuario quede huérfano de forma insegura (`keyring` sigue
  siendo legible manualmente por el usuario con su Credential
  Manager/Keychain, no es propietario de tokmd).
