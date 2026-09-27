---
title: "PBI-009 — `tokmd archivo.md` funciona solo y da el total: plataforma Claude por defecto, desglose opt-in"
aliases:
  - "PBI-009 defaults del CLI"
project: tokmd
document_type: pbi
status: closed
version: 0.3.0
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
reviewed_by: "Fabián Ferdgelis, owner"
review_status: "approved"
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
| 2026-09-27 | 0.2.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Fabián decidió las tres: flag `--sections`, versión `2.0.0`, y que el parser y el total den el mismo valor real. Entran al alcance BUG-009 y BUG-010 (ADR-003 y ADR-002 incumplidos, los levantó él). Se agrega la sección «la no-aditividad medida»: su requisito de igualdad exacta no es alcanzable, y está medido por qué. |
| 2026-09-27 | 0.3.0 | Anthropic / claude-sonnet-5 / Claude Code / subscription | Cierre: bump de versión a `2.0.0` (commit `657386e`), README actualizado (commit `8106bd1`), y Fabián aprobó el PBI («apruebo PBI-009, dalo por cerrado»). `status` → `closed`. |

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
  - El desglose por secciones pasa a ser opt-in, con el flag **`--sections`**
    (decidido por Fabián el 27/09).
  - El total se cuenta **de una sola pasada sobre el archivo completo**, no
    sumando filas (ver 4, «la decisión técnica»).
  - **Los cuatro bugs de esta zona, juntos**, porque arreglar uno sin los otros
    deja números que no cierran (BUG-011 es independiente en su causa, pero
    toca los mismos archivos y la misma versión, así que entra con el resto por
    decisión de Fabián):
    - `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]` — el título del
      encabezado pasa a contarse en su propia sección.
    - `[[BUG-009-adr-003-arbol-sin-own-ni-total]]` — `Own` **y** `Total` por
      fila, más la fila raíz con el total, como decidió ADR-003.
    - `[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]` — la línea de
      deriva que ADR-002 promete.
    - `[[BUG-011-salida-unicodeencodeerror-cp1252-windows]]` — la salida se fija
      a UTF-8 sin depender de la consola, para que un título con `→`, `«`, `»`
      o `—` no reviente al redirigir la salida en Windows.
  - `README.md` y `README.es.md` actualizados: el ejemplo de portada pasa a ser
    `tokmd CLAUDE.md`.
  - `CHANGELOG.md` con el cambio incompatible declarado.

  - **El dibujo del árbol con conectores** (`├─`, `└─`, `│`) — **variante B,
    aprobada por Fabián el 27/09/2026** sobre la indentación por espacios.
  - **`FRONT_MATTER_RE` corregida** para que absorba las líneas en blanco que
    siguen al `---` de cierre. Es el cambio de una línea que cierra el residuo de
    1 token del `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]` y, de
    paso, el segundo texto sin contar de
    `[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]`.

- **No incluye:**
  - Documentar `--verify` en el README (hueco conocido, va aparte).
  - Cualquier cosa de la API key: diferido en `docs/diferido/verify-api-key/`.

- **Dependencias:**
  - **Una decisión de ADR que todavía no está tomada**, y es la de la sección 4:
    qué se hace con los 215 tokens de deriva de borde que quedan cuando el total
    y la suma de filas no coinciden. Sin eso, el caso de prueba que verifica la
    igualdad no se puede escribir, porque no se sabe contra qué comparar.

- **Riesgos:**
  - **Rompe compatibilidad**, por eso va como **`2.0.0`** (decidido por Fabián).
    Quien hoy corra `tokmd x.md --platform claude-code` y espere la tabla va a
    recibir una línea.
  - Toca `sections.py`, `render.py` y `tokenizers.py` a la vez, y hay que
    **remedir todos los datos dorados** de `tests/test_sections.py`,
    `tests/test_render.py` y `tests/test_tokenizers.py`.
  - **Si además se cambia dónde se resta el marco** (ver sección 4), cambia el
    número que informa la herramienta para todo archivo, no sólo el total.

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
- [ ] **AC-05:** Dado `--sections`, cuando se corre `tokmd archivo.md --sections`,
      entonces se imprime el desglose sección por sección **y** el total.
- [ ] **AC-06:** Dado `--format json`, cuando se corre sin `--sections`, entonces
      el JSON tiene el total como campo propio y es parseable.
- [ ] **AC-07:** Dado un archivo que no existe o una ruta que es un directorio,
      cuando se corre el comando, entonces el mensaje de error es legible y el
      código de salida no es 0 (sin regresión).
- [ ] **AC-08:** Dado un archivo Markdown **sin ningún encabezado**, cuando se
      corre el comando, entonces informa el total sin fallar.
- [ ] **AC-09:** Dado un archivo vacío, cuando se corre el comando, entonces
      informa `0` sin fallar ni tirar traceback.

### Regresión de BUG-008 — el encabezado se cuenta

- [ ] **AC-10:** Dado un archivo con encabezados **sin cuerpo** (`#` usado como
      comentario, el caso real del `CLAUDE.md` de Fabián), cuando se pide
      `--sections`, entonces **ninguna** fila con encabezado no vacío informa
      `Own = 0`.
- [ ] **AC-11:** Dado un archivo con un único encabezado de texto conocido,
      cuando se pide `--sections`, entonces el `Own` de esa fila **incluye** los
      tokens del título.

### Regresión de BUG-009 — el árbol que decidió ADR-003

- [ ] **AC-12:** Dado `--sections`, cuando se corre, entonces cada fila muestra
      **`Own` y `Total` como dos números distinguibles**.
- [ ] **AC-13:** Dado `--sections`, cuando se corre, entonces existe una **fila
      raíz** cuyo `Total` es el total del archivo.
- [ ] **AC-14:** Dado un archivo con un padre de cuerpo corto y un hijo de cuerpo
      largo, cuando se pide `--sections`, entonces en la fila del padre
      `Own` < `Total`.

### Regresión de BUG-010 — la deriva se declara

- [ ] **AC-15:** Dado un archivo donde la suma de los `Own` no coincide con el
      total contado de una pasada, cuando se pide `--sections`, entonces se
      informa la deriva con su signo en vez de esconderla.
- [ ] **AC-16:** Dado un archivo donde la deriva es 0, cuando se pide
      `--sections`, entonces la salida **no** miente informando una deriva que no
      existe.

> **AC que falta y no se puede escribir todavía:** el que verificaría que la suma
> de filas es **igual** al total. Está medido que no se alcanza (215 tokens,
> 1,24 %, por la no-aditividad del tokenizador — ver sección 4). Hasta que Fabián
> decida qué se hace con esa deriva, no hay contra qué comparar. AC-15 es la
> versión verificable hoy.

### Regresión de BUG-011 — la salida no revienta por encoding en Windows

Bug encontrado por la sesión **TTOK-05** (Claude Fable 5.1), en paralelo sobre
este mismo worktree, midiendo el `CLAUDE.md` global contra la API real. Fabián
decidió que entra en este PBI, porque ya toca `cli.py`/`render.py` y sube a
`2.0.0`. Ver `[[BUG-011-salida-unicodeencodeerror-cp1252-windows]]`.

- [ ] **AC-18:** Dado un título de sección con un carácter fuera de cp1252
      (`→`, `«`, `»`, `—`) y la salida estándar redirigida a un archivo o pipe
      (no una consola interactiva), cuando se corre en Windows con cualquier
      `--format` (`table`, `md`, `csv`, `json`), entonces el programa **no**
      revienta con `UnicodeEncodeError` y produce la salida completa.
- [ ] **AC-19:** Dado ese mismo caso, cuando se corre, entonces el carácter
      aparece **tal cual** en la salida (UTF-8) — no se reemplaza por `?` ni por
      ningún carácter de repuesto. Una herramienta de medición que mutila
      silenciosamente el texto miente peor que si revienta.

### Presentación — variante B (conectores de árbol)

Aprobada por Fabián el 27/09/2026. La sección 2 ya la lista como incluida; el
párrafo de «Lo que Fabián preguntó sobre `--tree`» decía «queda fuera de este
PBI» porque se escribió **antes** de esa aprobación — corregido, esta sección
manda.

- [ ] **AC-20:** Dado `--sections` sobre un archivo con al menos dos niveles de
      anidamiento, cuando se corre, entonces las filas anidadas se dibujan con
      conectores de árbol (`├─`, `└─`, `│` para continuar la rama de un ancestro
      que todavía tiene más hermanos) en vez de indentación por espacios.

## 4. Contrato técnico

- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`.
- **Módulo/archivo principal:** `src/tokmd/cli.py` (opciones y defaults),
  `src/tokmd/render.py` (salida y total).
- **Herramientas disponibles:** `click`, `markdown-it-py`, `ctok`, `tiktoken`.
  Sin dependencias nuevas.
- **Versión de tests y configuración:** `pytest`, con datos dorados a remedir en
  `tests/test_render.py` y `tests/test_cli.py`.
- **Métricas:** el total de `C:\Users\fferdgelis\.claude\CLAUDE.md` con
  tokenizador de Claude `4.8` tiene que dar **17.381** — es lo que cobra la API
  de Anthropic (medido por TTOK-05 contra `count_tokens` el 27/09/2026) y
  coincide exacto con `ctok` crudo de una pasada. Es el dato dorado del AC-02;
  **no** 17.375/17.376, que era el total sin el marco, corregido por
  `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]` v0.3.0.
- **ADR requerido:** `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]`,
  **aceptado por Fabián el 2026-09-27** (opción D). Corrigió en consecuencia
  `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` (v0.3.0): el costo fijo por
  trozo es **5**, no los 6 de `token_count("")`; se resta una vez por sección
  pero **no** del total, que se cuenta crudo de una pasada; y la línea de deriva
  pasa de «limitación conocida» a control de sanidad (`+0` siempre esperado).

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

### Las tres decisiones, tomadas por Fabián el 27/09/2026

1. **Flag del desglose: `--sections`.**
2. **Versión: `2.0.0`** — «con el cambio rotundo de funcionamiento tiene que ser
   la versión 2.0.0».
3. **El arreglo de BUG-008:** *«tanto el parser como el total tienen que dar el
   mismo valor y ese valor tiene que ser el valor real, no un invento»*. O sea
   las dos cosas, con convergencia. Ver abajo: la primera mitad se cumple, la
   segunda tiene un límite medido.

### La no-aditividad medida: por qué la igualdad exacta no se alcanza

> **⚠ SUPERADO POR MEDICIÓN, 27/09/2026 — leer
> `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]` en su lugar.**
> Todo lo que sigue en esta sección parte de un supuesto que resultó falso: que
> los 215 tokens eran deriva de borde del tokenizador, y por lo tanto
> irreducibles. **No lo son.** Son el marco contado una vez por sección en vez de
> una por documento, y el marco vale **5**, no los 6 que mide `FRAME`. Medido en
> once archivos: **−5,00 tokens por corte**, constante. Corrigiéndolo, la suma de
> `Own` más el marco da **17.381**, exactamente lo que cobra la API de
> Anthropic (medido por TTOK-05 contra `count_tokens`; ver
> `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]`, corrección
> v0.3.0). El archivo contado de una pasada da **17.381**: deriva
> `+0`. **El requisito de Fabián se cumple exactamente.**
>
> Se deja el análisis viejo abajo porque explica de dónde salían las tres
> opciones descartadas, y porque el «dato incómodo» del final sigue siendo
> cierto y es importante.

**Medido el 27/09/2026** sobre `C:\Users\fferdgelis\.claude\CLAUDE.md`, con la
partición del archivo verificada byte a byte (ningún carácter perdido ni
duplicado), tokenizador de Claude `4.8`:

| | Tokens |
|---|---|
| **A) El archivo contado de una sola pasada** — el valor real | **17.375** |
| **B) Suma de las 44 filas con el título incluido, marco restado una vez** | **17.590** |
| C) Suma de las 44 filas, marco restado una vez por sección (lo de hoy) | 17.332 |
| **Deriva de borde real (A − B)** | **−215, o 1,24 %** |

**El problema no es un bug: es una propiedad del tokenizador.** Los tokenizadores
BPE fusionan caracteres vecinos. Cuando se corta el archivo en 44 trozos, las
fusiones que cruzaban un límite de sección se pierden, y cada trozo por separado
necesita **más** tokens que el mismo texto contado junto. Por eso B > A, y por eso
**ninguna forma de sumar filas puede dar exactamente el total del archivo.**

**Un dato incómodo que sale de la misma medición:** C (17.332) está más cerca de
A (17.375) que B (17.590). O sea que restar el marco 44 veces —que es
aritméticamente incorrecto— estaba **compensando por casualidad** la deriva de
borde: 44 × 6 = 264 de sobrerresta contra 215 de deriva. Se cancelan casi. **El
número de hoy parecía razonable por una coincidencia, no por diseño.**

**Consecuencia para el requisito.** «El mismo valor, y que sea el real» se puede
cumplir en su parte sustantiva —que no haya dos números distintos presentándose
los dos como «el total», y que el que se presenta sea el real— pero no como
igualdad aritmética exacta. Las tres salidas posibles:

| Opción | Qué implica |
|---|---|
| **1. El total es A, y la deriva se declara** | El total es el valor real. Las filas son el desglose, y una línea dice `boundary drift: −215`. Es exactamente lo que `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` ya decidió y nunca se implementó (`[[BUG-010-boundary-drift-prometido-por-adr-002-no-existe]]`). **Es la que recomiendo:** cumple «el valor real» y no esconde nada. |
| **2. El total es B (la suma de filas)** | Las filas cierran perfecto con el total, pero **el total deja de ser el valor real**: informaría 17.590 cuando el archivo cuesta 17.375. Contradice tu requisito de frente. |
| **3. Repartir la deriva entre las filas** | Los dos números cierran y el total es real, pero **las filas pasan a ser un invento**: a cada sección se le asigna una parte de una diferencia que no le pertenece. Contradice el «no un invento». |

**Recomiendo la 1**, y es lo que asumen los casos de prueba
`TOK-009-C05` y `TOK-009-C13` de `docs/PBI/PBI-009-casos-de-prueba.md`. **Pero la
decisión es tuya y necesita ADR**, porque cambia lo que la herramienta promete y
porque toca ADR-002.

### Dónde se resta el marco: decisión abierta, del mismo ADR

Hoy `count_claude` resta `FRAME` **en cada llamada**, o sea una vez por sección.
Eso es aritméticamente incorrecto: el marco es un costo fijo del mensaje, no de
cada sección. Corregirlo (restarlo una sola vez) **cambia el número que informa
la herramienta para todo archivo**, así que va en el mismo ADR que la decisión de
arriba. No se puede arreglar uno sin el otro: el `FRAME` mal restado y la deriva
de borde son los dos términos de la misma resta.

### Dato útil para quien lo implemente

El total acumulado **ya se calcula y se descarta**. En `render.py`, `_build_rows`
hace `_, rows = _accumulate_and_flatten(...)` y devuelve `rows[1:]` — tanto el
primer valor de la tupla como `rows[0]` (la fila `(document)`) llevan el
acumulado. **No reusar ese número como total**: arrastra las dos deformaciones.
Sirve para compararlo contra el total real y calcular la deriva de C13.

### Lo que Fabián preguntó sobre `--tree`

Preguntó si `--tree` podría dibujar el árbol real con los títulos, el texto de
cada sección, el total por sección, y la raíz con el total del archivo.

**Eso no es un flag aparte: es el desglose bien hecho.** Todo lo que describió es
literalmente lo que `[[ADR-003-parseo-de-secciones]]` ya decidió y el código no
cumple (`[[BUG-009-adr-003-arbol-sin-own-ni-total]]`). Así que no hacen falta dos
flags: `--sections` tiene que devolver **eso**. Los conectores de dibujo
(`├─`, `└─`) en vez de la indentación por espacios eran, al escribir este
párrafo, un agregado opcional fuera de alcance — **Fabián los aprobó el mismo
día** (variante B) y pasaron a **AC-20**, adentro del PBI. Ver la sección de
Criterios de aceptación.

## 5. Handoffs

### Definition of Ready

- [x] Valor, alcance y fuera de alcance claros.
- [x] Criterios observables y testeables — veinte, en la sección 3.
- [x] **Las tres decisiones del owner tomadas** (27/09/2026): `--sections`,
      `2.0.0`, y parser + total convergentes al valor real.
- [x] **ADR-007 aceptado por Fabián el 2026-09-27**, opción D: costo fijo 5
      restado por trozo, total contado de una pasada sin restar el marco, línea
      de deriva como control. `[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]`
      pasa a `accepted`; se corrigió en consecuencia
      `[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]` (v0.3.0).
- [x] **AC-17:** dado **cualquier** archivo, con front matter o sin él, cuando se
      pide `--sections`, entonces la deriva informada es exactamente **`+0`**.
      Reemplaza al AC que «no se podía escribir», y ya está verificado en 17
      archivos antes de escribir una línea de código.
- [x] **Presentación decidida:** variante B, con conectores de árbol.
- [x] **BUG-011 sumado al alcance** (AC-18, AC-19), decidido por Fabián el mismo
      día.
- [x] Casos de Kiwi cargados como `PROPOSED` — plan 30, ids 376–379 y 381–393
      (diecisiete casos; el 380 se dio de baja, ver
      `docs/PBI/PBI-009-casos-de-prueba.md`). Bugs `pk=9`, `10`, `11`, `13`
      registrados.

**Estado:** `ready`. Las cuatro condiciones de la Definition of Ready están
cumplidas. Queda para el handoff a TDD (abajo).

### Handoff a TDD

**Las cuatro specs para DeepSeek ya están escritas**, siguiendo el patrón de
`[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]` (contrato público, nunca
la implementación; AC en Dado/cuando/entonces; un solo bloque de código
`pytest` de vuelta):

| Spec | Módulo destino | AC que cubre |
|---|---|---|
| `tools/deepseek/specs/PBI-009-sections.md.prompt` | `tests/test_sections.py` | AC-10, AC-11 (más una regresión general vía el invariante de reconstrucción byte a byte) |
| `tools/deepseek/specs/PBI-009-tokenizers.md.prompt` | `tests/test_tokenizers.py` | El `FRAME["4.8"]=5` y la función nueva `count_claude_total` (sostienen AC-01, AC-02, AC-08, AC-09 desde abajo) |
| `tools/deepseek/specs/PBI-009-render.md.prompt` | `tests/test_render.py` | AC-05, AC-06, AC-12, AC-13, AC-14, AC-15, AC-16, AC-20 |
| `tools/deepseek/specs/PBI-009-cli.md.prompt` | `tests/test_cli.py` | AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-18, AC-19 |

**Tres decisiones de contrato que quedaron fijadas al escribir las specs**, y
que Desarrollo tiene que implementar exactamente así (no son negociables sin
volver a tocar las cuatro specs a la vez, porque se referencian entre sí):

1. **`tokenizers.py` gana una función nueva: `count_claude_total(text, family)`**
   — el conteo crudo, sin restar `FRAME`, para el total del documento completo.
   `count_claude` (la que ya existe) se sigue usando para el `Own` de cada
   sección, con `FRAME["4.8"]` corregido a `5`. Consecuencia directa y buscada:
   `count_claude("", "4.8")` pasa a dar **`1`**, no `0` — es la fórmula
   funcionando, no una regresión.
2. **`render.py`: `Row` gana dos campos (`own`, `total`) en vez de uno**, y
   `render()` gana un parámetro nuevo y obligatorio, `total: int` — el valor
   real que el llamador (la CLI) calculó con `count_claude_total` sobre el
   archivo entero. La fila raíz usa ese valor directo, **nunca** la suma de
   sus hijos (sumar da exactamente un `FRAME` menos — es la causa de fondo de
   BUG-009). La fórmula de la deriva, verificada antes de escribir la spec
   porque la primera versión que anoté en `ADR-002` estaba mal:
   **`drift = total − Σ Own − FRAME`** (restar el costo fijo **una sola vez**;
   sin ese término da `FRAME`, no `0`, en el caso sano).
3. **`--format json` cambia de forma:** de un array plano a un objeto
   `{"total": ..., "drift": ..., "rows": [...]}`. Es un cambio incompatible
   más, justificado por venir en la misma versión `2.0.0`.

- **Fixtures que faltan crear:** `tests/fixtures/headings_sin_cuerpo.md.fixture`
  (varios `#` seguidos sin texto entre ellos, el caso real del `CLAUDE.md` de
  Fabián). `empty`, `no_headings` y `sample` ya existen; **los datos dorados de
  `sample` hay que remedirlos** contra el `FRAME` nuevo.
- **Los datos dorados se remiden contra el tokenizador, nunca se escriben a
  mano.** Los del `CLAUDE.md` global están en la sección «Datos dorados» del
  documento de casos, y valen sólo para ese archivo sin editar.

### Handoff a Desarrollo — hecho el 2026-09-27

- **Restricciones confirmadas:** sin dependencias nuevas. `--verify` sigue
  funcionando igual (`test_cli_verify.py`/`test_cli_verify_gap01.py` en
  verde, sin tocarlos). `--platform codex`/`opencode` explícitos no se
  rompieron (AC-04, verificado).
- **Las tres decisiones de la sección 4 ya estaban resueltas** al momento de
  implementar (opción D del ADR-007, aceptada).
- **Suite completa: 77 passed, 0 failed.** Verificado además a mano contra
  `C:\Users\fferdgelis\.claude\CLAUDE.md`: total **17.381** (coincide con la
  API real), `--sections` da `boundary drift: +0`, `--platform codex` da
  **10.742** (coincide con `tiktoken o200k_base` directo).
- **Dos fallos reales encontrados implementando, arreglados en `src/tokmd/`,
  nunca en los tests:** el choque entre indentación por espacios (AC-02) y
  conectores de árbol (AC-20) — resuelto con una capa de indentación real
  además del conector; y `--sections` sin ninguna línea de dígito puro
  (pedido por mi propia spec, AC-05) — resuelto imprimiendo el total desnudo
  después del desglose. Detalle en el dev-log, tramo «Noveno tramo».
- **Pendiente, no decidido por Desarrollo:** el bump de versión a `2.0.0` —
  `test_version_flag_succeeds` sigue esperando `"1.0.0"` y sigue pasando
  porque no se tocó `pyproject.toml`. Tocar ese test es una decisión de
  release, no de contrato; queda para cuando Fabián confirme el corte.

### Handoff a QA

- **Candidato identificable:** pendiente de fijar el commit del snapshot.
- **Canal de QA:** OpenCode + Kimi K3, read-only.
- **Casos independientes:** los diecisiete de Kiwi (plan 30, ids 376–379 y
  381–393), más los tres de `--verify` (PBI-008) que no se tocaron.
- **Evidencia mínima:** log crudo de la ejecución más el resultado por caso en
  `tools/kiwi/resultados/`.

## 6. Cierre

- **Artefactos y enlaces:** Kiwi Test Run **70** (build `421b8cb`), 17
  Test Execution, todas `PASSED`. Log crudo de QA en
  `docs/handoff/qa/fase-6-pbi009-kimi-k3.txt`. Brief:
  `tools/qa/brief-qa-pbi009.md.prompt`. Los cuatro bugs (`pk=9,10,11,13`)
  quedaron linkeados a su Test Execution correspondiente vía
  `Bug.add_execution` — el estado del registro Bug en sí no se pudo pisar
  por API (`Bug.update` no existe en Kiwi; el cierre formal, si Fabián lo
  quiere, es manual en `/admin`).
- **Resultado de QA independiente:** `accepted` — **17/17 PASSED**,
  ejecutado por Kimi K3 vía OpenCode, read-only, sobre un snapshot del
  commit `421b8cb`, sin haber escrito tests ni código. Dos de los
  diecisiete casos (`C05`, `C14`) no tenían test unitario propio —el
  número real sólo lo confirma un servicio de red, y la suite nunca toca
  la red por diseño— así que QA corrió `tokmd` a mano contra una copia del
  `CLAUDE.md` global incluida como fixture en el snapshot, y confirmó los
  mismos números que Desarrollo había verificado manualmente: **17.381**
  (`tokmd CLAUDE.md`), **`boundary drift: +0`** (`--sections`), y de
  regalo **10.742** (`--platform codex`, no pedido por Kiwi pero sí por el
  brief). Suite completa dentro del snapshot: 77 passed, 0 failed.
- **Aceptación del owner:** `approved` — Fabián Ferdgelis, 2026-09-27
  ("apruebo PBI-009, dalo por cerrado").
- **Bump de versión:** hecho, commit `657386e`. `pyproject.toml` y
  `test_version_flag_succeeds` a `2.0.0`, confirmado por Fabián (relayado
  por TTOK-05). Suite completa: 77 passed.
- **Documentación:** `README.md`/`README.es.md` actualizados, commit
  `8106bd1` — `--sections`, el desglose `own`/`total` con fila raíz y
  `boundary drift`, y el nuevo comportamiento por defecto.
- **Estado: `closed`.** Nada bloqueante pendiente. Los cuatro bugs
  (`pk=9,10,11,13`) siguen `abiertos` en Kiwi por el límite de API ya
  documentado (`Bug.update` no existe); cerrarlos es manual en `/admin`,
  a discreción de Fabián.
