---
title: "Consulta PBI-009, ronda 2 — los seis motores sobre el planteo v2 de Fabián"
aliases:
  - "Consulta PBI-009 ronda 2"
project: tokmd
document_type: consultation
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
  - consulta
  - ronda-2
related_documents:
  - "[[CONSULTA-PBI-009-api-key-opcional-20260926]]"
  - "[[HANDOFF-fase-4-pbi008-cierre-pbi009-consulta-20260927]]"
---

# Consulta PBI-009, ronda 2 — los seis motores sobre el planteo v2 de Fabián

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación. Ronda 2 de la consulta: los seis motores sobre el planteo v2 (`docs/handoff/consulta-pbi009/planteo-v2-fabian-20260927.txt`), con comparación contra la ronda 1 y verificación contra el código y la documentación oficial. Archivo nuevo al lado del consolidado de la ronda 1, a elección de Fabián. |

## 0. Cómo leer esto

**Si vas a leer una sola sección, leé la 2.** Es un hallazgo de método que cambia
lo que significa el resultado de la votación, y no estaba visto en la ronda 1.

Después, en orden de utilidad para decidir: la **3** (qué votó cada uno y qué se
movió), la **5** (los datos oficiales que quedaron cerrados hoy, que cambian la
redacción del README) y la **8** (las tres opciones con lo que implica cada una
y mi recomendación).

Las secciones 4, 6 y 7 son para cuando quieras el detalle. La 9 dice dónde está
cada opinión completa.

## 1. Qué se consultó y cómo

**El texto.** El planteo v2 tuyo, literal, sin reescribir ni resumir, desde
`C:\IA\Projects\Claude-Tokenizer\docs\handoff\consulta-pbi009\planteo-v2-fabian-20260927.txt`.
Copia exacta de lo enviado en
`C:\IA\Projects\Claude-Tokenizer\docs\handoff\consulta-pbi009\ronda2-mensaje-enviado-literal.txt`.

A los tres de OpenCode se les antepuso la única línea autorizada en la ronda 1
(*«Respondé con tu opinión sobre lo siguiente. El proyecto está en esta
carpeta.»*), que está en
`C:\IA\Projects\Claude-Tokenizer\docs\handoff\consulta-pbi009\ronda2-mensaje-enviado-opencode.txt`.
Sin ella, Kimi sale a buscar el proyecto fuera de su carpeta y la corrida muere.

**Las copias.** Una copia limpia por motor, desde `git archive HEAD` del commit
`808b009`, en `C:\IA\tmp-ronda2\<motor>` — cinco copias, ninguna reusada. Esa
fue la lección más cara de la ronda 1: Antigravity escribe archivos en su
carpeta y Kimi los leyó.

**Los seis, lo que tardaron y cómo salieron:**

| Motor | Vía | Tiempo | Resultado |
|---|---|---|---|
| Codex (OpenAI) | `mcp__panel__ask_codex_web`, sandbox de sólo lectura | — | Completo, con 3 búsquedas web reales |
| Antigravity (Google) | `mcp__panel__ask_antigravity`, `effort=high` | — | Completo |
| Kimi K3 | `opencode run -m nvidia/moonshotai/kimi-k3` | ~3 min | Completo; escribió además su propio archivo |
| GLM-5.3 | `opencode run -m nvidia/z-ai/glm-5.3` | **950,8 s (15,8 min)** | Completo; el más sustancioso de los seis |
| Nemotron 3 Super | `opencode run -m nvidia/nvidia/nemotron-3-super-120b-a12b` | 24,3 s | Completo pero **no leyó el proyecto** |
| Claude (yo) | Sobre el worktree | — | Escrita antes de leer a cuatro de los cinco (ver 2.3) |

**La clave de NVIDIA ya estaba cargada en OpenCode.** `opencode auth list`
mostró `OpenRouter api` y `Nvidia api`, y los tres modelos aparecieron en
`opencode models`. No hizo falta pasarle `NVIDIA_API_KEY` al proceso como en la
ronda 1 — queda cerrado el pendiente 6 del traspaso.

**Las salidas crudas**, byte a byte como las devolvió cada motor, están todas en
`C:\IA\Projects\Claude-Tokenizer\docs\handoff\consulta-pbi009\` con el prefijo
`ronda2-`. La lista completa está en la sección 9.

## 2. El hallazgo que cambia cómo se lee el voto

Esto es lo que encontré, dónde, y por qué importa.

### 2.1 Las seis opiniones de la ronda 1 estaban adentro de las copias

El consolidado de la ronda 1 —`docs/CONSULTA-PBI-009-api-key-opcional-20260926.md`,
con las seis opiniones, la tabla de votos y el «4 a 2»— **está commiteado en el
repositorio**. `git archive HEAD` lo incluye. O sea que **las cinco copias
limpias traían adentro el resultado de la ronda 1**, y el traspaso de la fase 4
también, que nombra quién votó qué.

No es una sospecha: **dos motores dicen explícitamente que lo leyeron.** Kimi
K3 lo abrió (`→ Read docs/CONSULTA-PBI-009-api-key-opcional-20260926.md` en su
salida cruda) y GLM-5.3 escribió una aclaración de honestidad propia: *«esta
copia incluye el consolidado de la ronda 1 con las opiniones de los seis
motores, y lo leí durante el relevamiento. No puedo desleerlo.»* GLM leyó además
el traspaso completo.

**Por qué importa.** La ronda 2 **no es una segunda opinión independiente: es
una revisión de la ronda 1.** Que los seis vuelvan a decir lo mismo no es
confirmación por seis caminos distintos; en buena medida es el mismo camino
recorrido dos veces. Un motor que ve «4 a 2 a favor del archivo de config»
antes de opinar tiene un ancla que no tenía en la ronda 1.

Eso **no invalida la ronda 2** —los argumentos técnicos se pueden verificar uno
por uno, y abajo están verificados— pero sí invalida contar votos como si
fueran independientes.

### 2.2 Y además: cuatro de los seis tenían tu propia regla de secretos

`C:\Users\fferdgelis\.codex\AGENTS.md`, línea 27, dice textual:

> *Está prohibido persistir secretos en `.env`, variables de entorno
> User/Machine, archivos sin cifrar, argumentos o logs.*

OpenCode le carga ese archivo a **los tres** de su lado (Kimi, GLM, Nemotron) y
Codex lo lee nativamente porque es su propia configuración. Son **cuatro de los
seis**. Yo tengo la misma regla en
`C:\Users\fferdgelis\.claude\CLAUDE.md`: **cinco de seis.** El único cuyo «no»
a la variable de entorno es independiente de tu propia regla escrita es
**Antigravity**.

Se nota en la superficie, además: Codex y Kimi te llaman «Fabi», que es lo que
pide ese mismo archivo, y GLM cita *«tu propio CLAUDE.md global»*, al que no
tiene acceso desde su copia limpia.

**La consecuencia incómoda, y es la parte que te toca decidir:** esa regla tuya
prohíbe las dos cosas — la variable de entorno **y** el archivo sin cifrar.
Cuatro motores que la tenían en contexto recomiendan igual un archivo sin
cifrar. O sea que **la recomendación mayoritaria contradice tu propia política
de secretos**, y ninguno lo dijo.

Se puede defender: tu política gobierna **tu máquina**, no una herramienta
pública que usa otra gente. Pero es una decisión que conviene tomar a ojos
abiertos y no por omisión, porque `tokmd` es tuyo y lleva tu nombre en el
`pyproject.toml`.

### 2.3 Mi propia opinión: el orden se cumplió con cuatro de cinco

El traspaso pedía que mi opinión se escribiera antes de leer las de los demás.
Cuando la escribí **no había leído** a Kimi, GLM, Nemotron ni Codex. **Sí había
leído la de Antigravity**, porque su consulta va por una herramienta que
devuelve la respuesta en la misma llamada y no hay forma de lanzarla sin verla.
Lo digo porque en la ronda 2 me aparté de mi voto de la ronda 1, y hay que poder
juzgar si eso es razonamiento propio o eco (el argumento que me movió está en la
sección 8 y es verificable: lo medí).

**Para una ronda 3, si la hubiera:** la copia de cada motor tiene que salir de
un `HEAD` **sin** el consolidado ni el traspaso, o la consulta sigue siendo un
eco. Y a los de OpenCode conviene pasarles un `AGENTS.md` neutro mientras opinan
sobre secretos. No lo cambié: no lo pediste, y el traspaso dice explícitamente
no tocar esa configuración sin que lo pidas.

## 3. Dónde coinciden y dónde no, y qué se movió desde la ronda 1

| Tema | Codex | Antigravity | Kimi K3 | GLM-5.3 | Nemotron 3 | Claude |
|---|---|---|---|---|---|---|
| El diagnóstico del planteo v2 es correcto | Sí | Sí | Sí | Sí | Sí | Sí |
| `--verify` opcional, offline es el producto | Sí | Sí | Sí | Sí | Sí | Sí |
| Guardar en una **variable de estado del sistema** (tu planteo literal) | **No** | **No** | **No** | **No** | **No** | **No** |
| Dónde guardarla | Almacén del SO (`keyring`) | Archivo de config | Archivo de config | Archivo de config | **Almacén nativo del SO** | Archivo de config **+ guardar un comando** |
| `keyring` como escalón futuro | (es su opción) | No lo trata | Sí, no en v1 | Sí, v1.2 | (es su opción) | **No** |
| Orden de búsqueda | No lo detalla | Variable → archivo → mensaje | Variable → archivo | Variable → archivo → mensaje | No lo detalla | Variable → comando → archivo |
| Forma del comando | `--config` con menú | Flag `--config` estilo `--version` | **Subcomando** `tokmd config` | Flag `--config` estilo `--version` | `--config` | **Subcomando** `tokmd config` |
| Avisar que `--verify` manda el texto a Anthropic | **Sí** | **Sí** | No | **Sí** | No | **Sí** |
| Validar la key al guardarla | **Sí**, con texto fijo | No | No | Formato `sk-ant-` | No | No |
| Cuánto prometer | No prometer exactitud (cita fuente) | "la referencia del proveedor" | No prometer "muy superior" | No prometer exactitud (cita fuente) | "precisión crítica" | No prometer exactitud |
| Medir el Δ offline-vs-API antes de redactar | **Sí** (documento entero) | No | No | **Sí**, como criterio del PBI | No | **Sí** |
| Dónde registrar | — | PBI-009 | PBI-009 **+ ADR-007** | PBI-009 **+ ADR-007** | — | — |

**Lo que se movió desde la ronda 1 — dos motores, en direcciones opuestas:**

- **Nemotron 3** pasó de archivo de config a **almacén nativo del SO**
  (`cmdkey` en Windows, `security add-generic-password` en macOS,
  `secret-tool` en Linux), con archivo cifrado como respaldo. Su voto pesa poco
  igual: en las dos rondas **no leyó el proyecto** (cero herramientas usadas) y
  volvió a inventar datos (ver 4.2).
- **Yo** pasé de `keyring` a **archivo de config**, y agregué una opción que
  nadie planteó en ninguna de las dos rondas: que el config pueda guardar **el
  comando que produce la key** en vez de la key. El motivo del cambio está en
  la 8.1 y lo verifiqué midiendo, no razonando.

**El recuento queda 4 a 2 otra vez** (archivo: Antigravity, Kimi, GLM, Claude ·
almacén del SO: Codex, Nemotron), pero **con distinta composición** y —por lo
de la sección 2— **sin valor como votación independiente**.

**La coincidencia que sí es sólida, y no porque sean seis:** ninguno acepta la
variable de estado del sistema, y el argumento no depende de quién lo diga
porque es verificable y ya está verificado en tu propia máquina —
**una variable de entorno nueva no la ven los procesos que ya estaban
corriendo**, o sea que quien corra `tokmd --config` y después `tokmd --verify`
en la misma terminal va a ver "falta la key". En Linux y macOS es peor: no
existe esa variable sin editarle al usuario los archivos de arranque del shell.

## 4. Afirmaciones verificadas y afirmaciones falsas

### 4.1 Lo que verifiqué contra el código (commit `808b009`) y da cierto

- `src/tokmd/verify.py`, `get_client()`: la key sale **sólo** de
  `os.environ["ANTHROPIC_API_KEY"]`. No hay otra fuente. **Cierto**, lo dicen
  Codex, Kimi, GLM y yo.
- `src/tokmd/cli.py`: `file` es un `@click.argument` **obligatorio** y
  `--platform` es `required=True`; `--version` ya corre sin archivo. O sea que
  **las dos formas son posibles** (flag de acción o subcomando): cierto lo que
  dicen GLM y Antigravity, y cierto lo que dice Kimi.
- `import anthropic` es lazy dentro de `get_client()`, y el `try/except` del CLI
  atrapa `MissingApiKeyError` pero **no `ImportError`**. **Cierto:** sin el
  extra instalado, `--verify` termina con `ModuleNotFoundError` crudo.
- `README.md`: **cero apariciones de `--verify`** (grep). **Cierto.**
- `--verify` hace **una llamada por sección más una** (`measure_frame`). Un
  archivo de 60 secciones son 61 pedidos en una corrida.

### 4.2 Lo que es falso o no está medido

- **Antigravity: «discrepancias típicas entre 0,5 % y 1 %»** del modo offline.
  **No medido en este proyecto**, igual que en la ronda 1. Sigue sin fuente.
  GLM lo marcó por su cuenta y pidió no citarlo. No citarlo.
- **Nemotron: «estimador local (ej. tiktoken) con posible variación ±15 %».**
  **Doblemente falso.** Para el camino de Claude `tokmd` usa `ctok`, no
  `tiktoken` (`src/tokmd/tokenizers.py`); y el ±15 % es inventado. Además su
  respuesta trae caracteres chinos sueltos («la价值 claro»), señal de que no
  releyó lo que escribió.
- **Kimi: «la deriva del modo offline es acotada, está medida y se reporta al
  usuario en vez de ocultarse».** La parte de «se reporta» es **falsa** y es el
  mismo error de la ronda 1: ADR-002 dice que `tokmd` tiene que imprimir una
  línea `boundary drift: ±N`, y **eso no existe en el código** (grep de
  "boundary drift" en `src/`: cero). Y «acotada» es engañoso — ver 4.3.
- **Antigravity, ronda 1: «`keyring` exige librerías nativas compiladas en
  C/Rust».** Era el argumento principal para descartar `keyring` y quedó sin
  verificar. **Lo verifiqué hoy** resolviendo el árbol de dependencias con `uv`
  (gestor de paquetes de Python) en un proyecto vacío:
  - **Windows:** `keyring` → `pywin32-ctypes` + `jaraco-*` + `more-itertools`.
    **Todo Python puro. Nada compilado.**
  - **macOS:** nada específico de plataforma. **Nada compilado.**
  - **Linux:** `keyring` → `jeepney` (Python puro) + `secretstorage` →
    `cryptography` → `cffi` → `pycparser`. `cryptography` y `cffi` **sí** son
    compilados (Rust y C), pero publican ruedas precompiladas para
    manylinux.

  O sea: **la afirmación es falsa en Windows y macOS, cierta sólo en Linux, y
  aun ahí la mitigan las ruedas precompiladas.** El argumento real contra
  `keyring` es otro y es el de GLM: en Linux sin escritorio, en WSL y en
  contenedores **no hay servicio de secretos corriendo**, así que `keyring`
  falla al usarlo y necesitás el respaldo al archivo de todos modos. Ese
  argumento sí se sostiene solo.
- **GLM no pudo reverificar lo de `keyring`** (su `WebFetch` a PyPI no cargó) y
  lo dijo. Queda cerrado con la medición de arriba.
- **GLM, ronda 1: «PBI-008 midió el Δ real entre offline y API».** Falso, y
  **GLM se corrigió solo en la ronda 2**: PBI-008 midió `--verify` (15877) y
  OpenAI `o200k_base` (9852), nunca `ctok` sobre ese mismo archivo. **El Δ no
  existe todavía.**

### 4.3 Lo que nadie dijo y cambia la redacción del README

Esto lo encontré leyendo `docs/investigation/20260924-ctok-marco-y-deriva.md` y
el código, y ninguno de los seis lo trató:

**La deriva del modo offline no es un error de borde chico: es estructural, y
`--verify` la tiene igual.** ADR-002 resta `FRAME` de **cada** fila, así que un
documento de N secciones resta `FRAME` N veces en vez de una — la deriva escala
como `(N-1) × FRAME`, no con los bordes entre palabras. Está medido en ese
documento (`sample.md.fixture`, N=5, `FRAME(3.0)=8`: 17 tokens de deriva contra
32 del orden de magnitud previsto).

**Y `count_verified` hace exactamente lo mismo:** resta `frame` por sección, y
`render.py` suma. O sea que **activar `--verify` no arregla la aditividad**;
cambia de dónde sale el número de cada sección. Es el punto 6 de Codex, y es
correcto.

Consecuencia práctica para la comunicación: **no se puede prometer «el total
exacto que te va a costar el archivo»** por dos razones a la vez — Anthropic
describe su propio conteo como estimación (ver 5) y la suma de secciones de
`tokmd` no es el conteo del archivo completo, ni offline ni con `--verify`.

## 5. Los datos oficiales, cerrados hoy

GLM y Codex trajeron esto con búsqueda web real. **Lo reverifiqué contra la
documentación oficial de Anthropic** (`platform.claude.com`, consultada el
27/09/2026) y **los cinco puntos dan exactos**:

1. **Es gratis.** Textual: *«Token counting is free to use but subject to
   requests per minute rate limits based on your usage tier.»*
2. **Los límites, por tier:** Start **5.000** pedidos por minuto, Build
   **10.000**, Scale **20.000**. Los números de GLM son correctos.
3. **Los límites son independientes de los de mensajes.** Textual: *«Token
   counting and message creation have separate and independent rate limits.
   Usage of one does not count against the limits of the other.»* Contar no le
   come cuota a nada. Con 61 pedidos por corrida, rozar 5.000 por minuto es
   materialmente imposible en uso manual.
4. **Es una estimación, dicho por Anthropic.** Textual: *«The token count is an
   **estimate**. In some cases, the actual number of input tokens used when
   creating a message might differ by a small amount.»* Confirma a Codex y GLM,
   y confirma que mi redacción de la ronda 1 y la de Antigravity
   sobreprometían.
5. **El tokenizador cambió en 4.7, y el número de GLM es exacto.** Textual:
   *«Claude 4.7 and later models and Claude Mythos Preview use a newer
   tokenizer. The same input text produces approximately **30 percent more
   tokens** than on earlier models.»* Y: *«Recount prompts against the model
   you plan to use rather than reusing counts measured against earlier
   models.»*

**El punto 5 es el mejor argumento a favor de `--verify` que salió de las dos
rondas, y es de GLM.** `ctok` es una reconstrucción de terceros (ADR-001 lo
dice). Cuando el proveedor cambia el tokenizador —y acaba de cambiarlo, con un
salto del 30 %— toda reconstrucción queda vieja hasta que alguien la actualice.
`--verify` no puede quedar viejo, porque le pregunta al que fabrica el número.
Eso es una ventaja real y no amedrenta a nadie.

**Un dato de regalo que valida PBI-008.** La documentación de Anthropic dice
además que `tiktoken` (el tokenizador de OpenAI) **subestima** los tokens de
Claude en un 15-20 % en texto típico y **mucho más en código o texto que no es
inglés**. Eso explica el 15877 contra 9852 del `CLAUDE.md` global —un 61 % de
diferencia— que es español con bloques de código: no era un error de medición,
es el comportamiento esperado.

## 6. Los huecos del producto, verificados hoy

Valen **independientemente** de lo que decidas sobre la key:

1. **`README.md` no menciona `--verify`.** La función existe, está testeada,
   tiene su PBI cerrado, está publicada en PyPI, y **ningún usuario tiene forma
   de enterarse**. Es el hueco más grande.
2. **Sin `tokmd[verify]` instalado, `--verify` explota con
   `ModuleNotFoundError`** en vez de decir "instalá `pip install tokmd[verify]`".
3. **`ADR-002` promete una línea `boundary drift: ±N` que el código no
   imprime.** O se implementa o se corrige el ADR; hoy el documento dice una
   cosa y el programa hace otra, y eso ya hizo que dos motores afirmaran algo
   falso creyendo que leían documentación válida.
4. **`README.md` dice «### From PyPI (once published)»** y `v1.0.0` ya está
   publicado. Línea vieja.

## 7. Lo que aporté yo, y que no salió en ninguna de las dos rondas

**Que `tokmd config` pueda guardar «cómo obtener la key» en vez de la key.**
Dos opciones a elección del usuario:

| Opción | Qué guarda | Para quién |
|---|---|---|
| **(a)** | la key, en el archivo de config del usuario con permisos restringidos | el usuario común |
| **(b)** | la **línea de comando** que devuelve la key por salida estándar | el que ya tiene bóveda: vos, y cualquiera con 1Password, `pass` o Vault |

`tokmd` corre el comando, toma la salida, la usa en memoria y **nunca la
escribe a disco**. Es el patrón de `git` con `credential.helper` y de `docker`
con `credsStore`: la herramienta no guarda secretos, guarda **quién se los da**.

**Por qué importa acá y no es una idea suelta.** Es lo que resuelve la
contradicción de la sección 2.2: con la opción (b), **tu regla de secretos se
puede cumplir usando `tokmd` tal como viene**, sin excepciones y sin parches. En
tu caso la línea sería
`pwsh -c "Unprotect-IADpapiSecret -Application multi-modelos-ai -Name anthropic.api-key"`.
Hoy eso no se puede: la única vía es la variable de entorno, que tu propia regla
permite sólo en memoria y nunca persistida.

**El riesgo, dicho de frente:** un archivo de config que contiene un comando que
se ejecuta es superficie de ataque nueva. Quien pueda escribir ese archivo
ejecuta código como ese usuario. Dos mitigaciones honestas: el archivo vive en
el perfil del usuario, con los mismos permisos que su `.bashrc` —quien puede
escribirlo ya podía ejecutar código suyo— y `tokmd config show` tiene que
**mostrar el comando en claro**, para que nadie tenga un comando corriendo a sus
espaldas sin saberlo.

## 8. Lo que queda por decidir, y es tuyo

### 8.1 La decisión de fondo: dónde se guarda la key

| Opción | Qué implica | Quién la vota (ronda 2) |
|---|---|---|
| **A — variable de estado del sistema** (tu planteo literal) | Tres caminos de código, uno por SO. En Windows la terminal abierta no la ve, así que el primer uso después de configurar **falla**. En Linux/macOS hay que editarle al usuario el `.bashrc`/`.zshrc`. No gana nada de seguridad: sigue siendo texto plano legible por cualquier proceso del usuario. | **Ninguno de los seis** |
| **B — archivo de config en la carpeta del usuario** (`%APPDATA%\tokmd\config.json`, `~/.config/tokmd/config.json` con `chmod 0600`) | Un solo camino de código, biblioteca estándar, cero dependencias nuevas, funciona en el acto en la terminal abierta. Nivel de protección: el de `~/.aws/credentials`. La key queda en texto plano protegida sólo por permisos de archivo, y el README lo tiene que decir sin eufemismos. | Antigravity, Kimi, GLM, Claude |
| **C — almacén de credenciales del SO** (`keyring`) | La key no queda en texto plano. Pero en Linux sin escritorio, en WSL y en contenedores no hay servicio de secretos, así que falla al usarla y necesitás el respaldo al archivo igual: dos caminos de código y una dependencia nueva, para un "mecanismo mínimo". La objeción de "librerías compiladas" quedó **desmentida** (4.2): en Windows y macOS no compila nada. | Codex, Nemotron |

**Mi recomendación: B, con la extensión de la sección 7** — que el config pueda
guardar la key (opción a) **o** el comando que la produce (opción b), y que
`ANTHROPIC_API_KEY` del entorno gane siempre sobre las dos, para que CI y tu
flujo actual con DPAPI no cambien ni una línea.

**Por qué cambié de C a B desde la ronda 1, con el argumento medido:** en la
ronda 1 voté `keyring` para que la key no quedara en texto plano. Lo revisé y no
se sostiene — en Windows **cualquier proceso corriendo como ese usuario lee el
Credential Manager sin pedir permiso**, igual que leería un archivo con permisos
de usuario: el modelo de amenaza es idéntico. La ganancia real existe sólo en
macOS, donde el Llavero pide autorización por aplicación. Pagar una dependencia
que se rompe en Linux headless, WSL y contenedores para comprar seguridad que
existe en una sola de las tres plataformas es un mal negocio.

**Y la tensión que tenés que resolver vos** (sección 2.2): B guarda un secreto
en un archivo sin cifrar, que es exactamente lo que tu regla de secretos
prohíbe. Para `tokmd` como producto público es el estándar aceptado (`aws`,
`gcloud`, `gh`, `npm` hacen eso). La opción (b) de la sección 7 es la que te
deja cumplir tu regla sin imponérsela a nadie.

### 8.2 Las decisiones chicas que vienen con la grande

1. **Forma del comando.** `tokmd --config` como flag de acción (Antigravity,
   GLM, Codex, Nemotron) o `tokmd config` como subcomando (Kimi, yo). Las dos
   son posibles: `--version` ya prueba que un flag puede correr sin archivo. El
   flag es menos trabajo; el subcomando aguanta mejor `show` y `unset` cuando
   los necesites. **Es tu preferencia, no hay argumento técnico decisivo.**
2. **Medir el Δ offline-vs-API antes de escribir el README**, o escribir el
   README diciendo que todavía no se midió. Codex, GLM y yo pedimos medirlo;
   yo me niego a afirmar un porcentaje sin medirlo. **Una corrida de `--verify`
   más una offline sobre el `CLAUDE.md` global alcanza, y es gratis** (sección
   5). Si querés que lo mida, decilo: necesita la key de la bóveda y eso te lo
   pido aparte.
3. **Si va ADR-007 además del PBI-009.** Kimi y GLM dicen que sí, y el motivo es
   bueno: hay dos alternativas rechazadas con argumentos (A y C) y un
   trade-off de seguridad que conviene dejar escrito. Vos decidís.
4. **Qué hacer con los cuatro huecos de la sección 6.** El del README es el que
   más duele y no depende de nada de esto.

**No escribí el PBI-009, no creé el ADR-007 y no toqué una línea de código**,
como pide el traspaso. Espero tu decisión.

## 9. Dónde está cada opinión completa

Todo en `C:\IA\Projects\Claude-Tokenizer\docs\handoff\consulta-pbi009\`:

| Archivo | Qué es |
|---|---|
| `ronda2-glm53-archivo-propio.md.txt` | **GLM-5.3, la más completa de las seis.** Si leés una sola, leé esta. |
| `ronda2-glm53-crudo.txt` | Salida cruda de GLM, con las herramientas que usó y su resumen en consola |
| `ronda2-codex.txt` | Codex (OpenAI), con sus tres búsquedas web |
| `ronda2-antigravity.txt` | Antigravity (Google) |
| `ronda2-kimi-k3-archivo-propio.txt` | Kimi K3, versión larga que escribió él |
| `ronda2-kimi-k3-crudo.txt` | Salida cruda de Kimi, incluido el `Read` del consolidado de la ronda 1 (la evidencia de la sección 2.1) |
| `ronda2-nemotron3-crudo.txt` | Nemotron 3 Super. Corta, sin leer el proyecto, con datos inventados |
| `ronda2-claude.txt` | La mía, con la advertencia de orden de la sección 2.3 |
| `ronda2-mensaje-enviado-literal.txt` | Lo que recibieron Codex y Antigravity |
| `ronda2-mensaje-enviado-opencode.txt` | Lo que recibieron los tres de OpenCode (tu texto + la línea autorizada) |

El consolidado de la **ronda 1** queda intacto en
`C:\IA\Projects\Claude-Tokenizer\docs\CONSULTA-PBI-009-api-key-opcional-20260926.md`.
