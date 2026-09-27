---
title: "Catorce preguntas sobre tokenización: baseline, ctok, familias y riesgo de dependencia"
aliases:
  - "Respuestas TTOK-05 sobre count_tokens, ctok y familias"
project: tokmd
document_type: research
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
  - reference/tokens
related_documents:
  - "[[20260927-count-tokens-api-vs-tokmd-ctok-ttok]]"
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
  - "[[ADR-002-manejo-del-marco-y-la-deriva-de-ctok]]"
  - "[[ADR-003-parseo-de-secciones]]"
---

# Catorce preguntas sobre tokenización: baseline, ctok, familias y riesgo de dependencia

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. Respuestas a las 14 preguntas de Fabián de la sesión TTOK-05, con datos traídos por cuatro agentes Sonnet (docs de Anthropic, repo de ctok, tiktoken/Codex/Antigravity/OpenCode, historia del repo tokmd). |

## Método

Fabián pidió no responder de memoria. Cuatro agentes Sonnet leyeron fuentes
primarias (documentación de Anthropic en `platform.claude.com` y
`code.claude.com`, el repo y el código instalado de `ctok`, el código de
`tiktoken`, Codex CLI, OpenCode, las docs de Gemini/Antigravity y de Kimi, y
el propio repo tokmd) y trajeron citas. Además se corrieron sondas propias
contra `count_tokens` (scratchpad `probe-frame.ps1`). Las cifras del archivo
`C:\Users\fferdgelis\.claude\claude.md` vienen de
`20260927-count-tokens-api-vs-tokmd-ctok-ttok.md`.

---

## 1. ¿El baseline es 17.381, con certeza del 100 %?

**Sí, con esta definición exacta:** 17.381 es lo que el endpoint oficial
`POST /v1/messages/count_tokens` devuelve hoy (27/09/2026) para ese archivo
como único mensaje `user`, en los modelos que usan el tokenizador introducido
con Opus 4.7: **Sonnet 5, Opus 5, Opus 4.8** (y 4.7). Es la fuente de verdad
por definición: es el número que Anthropic cuenta.

Tres salvedades que no le quitan validez pero hay que dejar escritas:

- **El baseline es por familia de tokenizador, no universal.** El mismo
  archivo vale 13.076 en Sonnet 4.6 / Haiku 4.5 (tokenizador anterior) y
  17.383 en Fable 5.1. La doc dice que Fable 5.1 usa el mismo tokenizador que
  Opus 4.8; los 2 tokens de diferencia son marco del mensaje, no contenido
  (el README de ctok documenta lo mismo para Opus 5.5: «counts two tokens more
  than Opus 5»). Un baseline sin modelo y fecha al lado no es un baseline.
- **Incluye el marco.** count_tokens cuenta el mensaje entero: contenido más
  rol y delimitadores (medido: 6 tokens en la familia 4.8). El contenido puro
  del archivo son ~17.375.
- **Puede incluir tokens de sistema no facturados.** La doc dice: «Token
  counts may include tokens added automatically by Anthropic for system
  optimizations. You are not billed for system-added tokens». Para
  presupuestar es indistinguible; para facturación exacta el número final es
  `usage.input_tokens` de una llamada real.

**Recomendación:** fijar el baseline como una tabla versionada
`(archivo, sha256, modelo, fecha, tokens)` con tres filas: Sonnet 5 = 17.381,
Sonnet 4.6 = 13.076, Fable 5.1 = 17.383. Todas las pruebas de tokmd se miden
contra esa tabla, no contra un número suelto.

## 2. ¿Puedo tener la cuenta de API sin cargarle dinero?

**Sí, y ya lo estás haciendo.** La key de la bóveda funcionó hoy para 12
llamadas a `count_tokens` con la cuenta «en cero». La doc de soporte dice que
la suscripción Pro/Max **no** incluye la API ni la Console, que la API se paga
con créditos prepagos y que «if you run out of credits you can no longer call
the API» — pero eso aplica a los endpoints facturables. `count_tokens` es
gratis (pregunta 3), y la evidencia empírica de hoy es que responde con saldo
cero. La doc de pricing menciona además «a small amount of free credits» para
usuarios nuevos.

Lo que **no** vas a poder hacer con saldo cero: `/v1/messages` (inferencia).
Para el uso que le damos —verificar conteos— no hace falta.

## 3. ¿count_tokens cobra?

**No.** Cita textual: «Token counting is free to use but subject to requests
per minute rate limits based on your usage tier». Tiene rate limit propio,
separado del de mensajes: 5.000 RPM en el tier Start. Se puede llamar miles de
veces sin gastar un centavo — es lo que hizo el autor de ctok para reconstruir
el vocabulario.

## 4. ¿En qué repo está ctok?

`https://github.com/sanderland/ctok` — autor Sander Land, licencia MIT,
descripción del repo: «Claude's Tokenizer, Offline, Kinda». En PyPI como
`ctok`; instalado 1.3.0 (01/09/2026). Repo creado el 28/07/2026, 24 commits,
**1 contribuidor**, 78 estrellas, 6 forks, último push 25/09/2026. Artículo
de investigación del autor:
`https://tokencontributions.substack.com/p/on-the-biology-of-claudes-tokenizer`.

## 5. ¿ctok habló con la API con mi credencial, o cuenta offline?

**100 % offline. No tocó tu credencial ni la red.** Verificado en el código
instalado: cero referencias a `requests`, `httpx`, `urllib`, `socket`,
`api.anthropic`, `x-api-key` o `count_tokens` en los siete módulos. El README
lo dice: «reconstructs Claude token counts offline, with no API call or
network access».

**Cómo llega al mismo número.** No tiene el algoritmo de Anthropic (nadie lo
tiene: Anthropic no publica el tokenizador; su único paquete oficial,
`@anthropic-ai/tokenizer`, está archivado y dice «As of the Claude 3 models,
this algorithm is no longer accurate»). Lo que tiene es una **reconstrucción
por ingeniería inversa**:

1. Un **vocabulario embebido** en JSON (48.792 piezas para la familia vieja,
   15.283 para la nueva; 4,7 MB en total). Cada pieza viene con un
   «testigo» (*witness*): la sonda que se mandó a `count_tokens` y demostró
   que esa pieza cuesta exactamente 1 token en la API real.
2. Una **normalización** del texto (NFC, plegado de comillas, marcadores de
   mayúscula y de borde de palabra) con tablas de caracteres medidas una por
   una, porque ninguna regla Unicode las reproduce.
3. Un **teselado de costo mínimo** (programación dinámica sobre un trie
   invertido): cubre el texto con la menor cantidad de piezas del
   vocabulario; lo que no cubre ninguna pieza cae a bytes UTF-8, 1 token por
   byte.
4. Suma el **marco** medido del mensaje (6 tokens en 4.8).

O sea: el autor gastó millones de llamadas gratis a `count_tokens` para
descubrir el vocabulario, y lo congeló en el paquete. Exactitud que declara:
962.053 de 962.054 textos exactos en su corpus grande; «0 of 2,276,929 v3
texts and 0 of 2,328,425 v4.7 texts» con subconteo. Nuestra medición de hoy:
exacto en el archivo entero (17.381 = 17.381) y en las cuatro sondas cortas.

## 6. ¿Por qué ctok 3.0 da 13.076 y lo marqué «exacto»?

Porque «3.0» en ctok es el vocabulario del **tokenizador anterior**, el que
usan Claude 3.x, Opus 4.5/4.6, Sonnet 4.5/4.6 y Haiku 4.5 (`FAMILIES["v3"]`
apunta a `pieces_v3.json` y se calibró contra `claude-opus-4-5`). La API
devuelve 13.076 para Sonnet 4.6 y Haiku 4.5; ctok 3.0 devuelve 13.076. Es
exacto **contra esos modelos**. No es «una versión vieja de ctok»: es la
familia vieja de Anthropic, y ctok las trae las dos porque los dos
tokenizadores siguen vivos en producción.

## 7. Riesgo de depender de ctok. ¿Podemos hacer uno propio?

**El riesgo real no es que desaparezca; es que quede desactualizado.**

- *Desaparecer:* es MIT. El código (60 KB de Python) y el vocabulario
  (4,7 MB de JSON) están en nuestro `.venv` y en el caché de `uv`. Si el
  autor borra GitHub y PyPI mañana, seguimos teniendo 1.3.0 y podemos
  publicarlo como fork. Costo de blindarse: vendorizar (copiar el paquete al
  repo bajo `vendor/ctok/` con su LICENSE) o al menos fijar `ctok==1.3.0` con
  hash en `uv.lock`. Media hora.
- *Cambiar de forma que nos pegue:* ya está pasando en chico. El README del
  repo (commit del 25/09, posterior al 1.3.0 instalado) dice: «Opus 5.5 counts
  two tokens more than Opus 5. This offset is not yet modeled in ctok». Y ctok
  es de un solo autor con dos meses de vida.
- *Quedar atrás cuando Anthropic cambie de tokenizador:* ADR-001 ya lo
  registra como consecuencia aceptada. Lo que no hay es un **mecanismo** que
  lo detecte: ningún test compara ctok contra la API real (todos los tests de
  `--verify` usan un cliente falso), ningún job periódico lo mide.

**¿Podemos hacer un ctok propio?** Técnicamente sí: el método está publicado
(artículo del autor + código MIT), el endpoint para sondear es gratis y sin
límite práctico (5.000 RPM). Pero es un proyecto de **investigación**, no de
desarrollo: reconstruir un vocabulario de 15.000–49.000 piezas con testigos y
tablas de normalización medidas carácter por carácter es lo que al autor le
llevó su trabajo de meses. Rehacerlo para tener lo mismo que ya tenemos con
licencia MIT no se justifica.

**Lo que sí se justifica (propuesta, para que decidas):**

| Opción | Qué implica | Costo | Cubre |
|---|---|---|---|
| A. Vendorizar ctok 1.3.0 en el repo | copiar paquete + LICENSE, importar desde `vendor/` | ~30 min | desaparición |
| B. Gate de deriva contra la API | corpus dorado (10–20 archivos) con conteo de `count_tokens` guardado; test que corre ctok y compara; job semanal que re-mide contra la API (gratis) | ~medio PBI | desactualización, silenciosa hoy |
| C. `--verify` como camino exacto | ya existe; hacerlo comparar el **documento entero** además de sección por sección | chico | exactitud cuando hay key |
| D. ctok propio | reconstrucción desde cero | meses | nada que A+B+C no cubran |

Recomendación: **A + B + C**. D no.

## 8. ¿Por qué los PBIs no tuvieron en cuenta los encabezados?

> **Actualización del mismo día:** la sesión TTOK-04 ya lo había registrado
> como **BUG-008** y lo metió en el alcance de **PBI-009** («defaults del CLI
> y total», AC-10/AC-11), junto con BUG-009 (falta `Own`/`Total`/raíz de
> ADR-003) y BUG-010 (la línea `boundary drift` de ADR-002 no existe), todo en
> la rama `worktree-ttok04-pbi009-ronda2`, todavía sin mezclar a `main`. Lo de
> abajo describe el estado de `main` al momento de investigar y sigue siendo
> la explicación de fondo.

**Porque nadie lo escribió como criterio.** Hallazgo del agente que recorrió
el repo:

- No hay ADR, PBI, criterio de aceptación ni test que diga «el encabezado no
  cuenta» ni «el total del documento tiene que ser igual al conteo del
  archivo entero». `docs/decisions/` está vacía.
- El recorte nació en el único commit de `sections.py` (`d54f948`,
  25/09/2026, PBI-001): `content_start = token.map[1]` toma la línea
  **siguiente** al heading, y `own_text` arranca ahí. Es un efecto colateral
  del parseo, no una decisión.
- `--verify` (PBI-006) compara **sección por sección**, nunca el archivo
  entero, así que no podía ver la diferencia. Y `docs/CONSULTA-PBI-009…`
  ya había marcado como «afirmación falsa» que PBI-008 hubiese medido offline
  vs API: «nunca se midió».

Es decir: faltó **un** criterio de aceptación en PBI-001 —«la suma de todas
las secciones más el marco es igual a `count_tokens` del archivo entero»— y
un test que lo ejecute. Con eso, el desvío de 1.478 tokens habría saltado el
25/09. Es el ejemplo de manual de por qué los casos se registran antes de
ejecutar: el parser se probó contra lo que el parser hacía, no contra el
oráculo.

## 9. ¿Los encabezados pesan siempre, en cualquier plataforma?

**Sí.** Tres razones, todas verificadas:

1. **Los tokenizadores no saben qué es Markdown.** BPE (tiktoken) y el
   teselado de ctok operan sobre bytes/caracteres; `#` es un carácter más.
   Sonda de hoy contra la API de Anthropic:
   `## Motores de IA disponibles para delegar trabajo\n` = **25 tokens**.
2. **Ningún harness limpia el archivo antes de mandarlo.** Claude Code carga
   CLAUDE.md «in full» (hasta 4 MiB) como mensaje de usuario, concatenando los
   de todos los niveles. Codex CLI concatena AGENTS.md tal cual hasta
   `project_doc_max_bytes = 32768` (32 KB; el único procesamiento es
   `trim().is_empty()`). OpenCode hace
   `Instructions from: <path>\n<contenido crudo>`. No se encontró evidencia de
   ningún harness que resuma o filtre encabezados.
3. **Cada proveedor cobra sus propios tokens** del texto completo que recibe:
   Anthropic con su tokenizador, OpenAI con o200k, Google con el de Gemini
   (~4 caracteres por token, `countTokens` gratis), Kimi con el suyo
   (`POST /v1/tokenizers/estimate-token-count`).

Si un archivo va al contexto, pesa entero: encabezados, comentarios, líneas
en blanco, todo.

## 10. ¿Forzar UTF-8 en todo el software que mide archivos?

**Sí, y en las dos puntas.** Estado actual de tokmd:

- **Lectura:** ya está bien: `cli.py:161` lee con `encoding="utf-8"`
  explícito. Es la única lectura del programa.
- **Escritura a consola:** ahí está el bug. `click.echo` escribe a `stdout`,
  que en una consola de Windows sale en cp1252; cualquier título con `→`,
  `«`, `—` revienta con `UnicodeEncodeError`. `PYTHONUTF8=1` es un parche de
  entorno, no del programa.

Regla propuesta para el proyecto: **todo archivo se lee como UTF-8 y toda
salida se escribe como UTF-8**, con un caso de prueba que tenga un título con
`→` y `«»` y que corra en Windows. Implementación mínima:
`sys.stdout.reconfigure(encoding="utf-8")` al arrancar el CLI. Registrado
como **BUG-011** (`docs/bugs/BUG-011-salida-unicodeencodeerror-cp1252-windows.md`,
rama `worktree-ttok04-pbi009-ronda2`; falla en `table`, `md` y `csv`, no en
`json`).

Cosa aparte, ya vista hoy en ttok: leer `stdin` sin UTF-8 en Windows no rompe,
**miente**: dio 13.075 en vez de 11.660 porque cada acento se partió en más
tokens. Un error de codificación puede pasar inadvertido y cambiar el número.

## 11. ¿Qué son cl100k y o200k, y por qué dan tan por debajo?

Son los **vocabularios BPE de OpenAI** que usa `tiktoken`:

| Encoding | Tamaño aprox. | Modelos |
|---|---|---|
| `cl100k_base` | ~100.000 tokens | GPT-4, GPT-3.5, embeddings |
| `o200k_base` | ~200.000 tokens | GPT-4o, GPT-4.1, GPT-5, o1/o3, **Codex CLI** (`gpt-5.1-codex` cae en el prefijo `gpt-5`) |

`ttok` usa `cl100k_base` por defecto y no cubre Claude (el README no menciona
Anthropic). Dan menos (11.660 y 10.742 contra 17.381) por dos motivos que se
suman: un vocabulario más grande cubre el mismo texto con menos piezas
(o200k < cl100k), y el tokenizador nuevo de Anthropic es deliberadamente más
caro (~30 % más tokens que el anterior, según su propia doc de pricing).

**Comparar conteos entre proveedores no dice nada por sí solo.** 10.742
tokens de OpenAI y 17.381 de Anthropic no son la misma unidad; lo comparable
es tokens × precio del proveedor. OpenAI, además, ya tiene endpoint oficial de
conteo (`POST /v1/responses/input_tokens`) y advierte que `tiktoken` sólo
cubre texto plano.

## 12. ¿Qué pasa cuando sale una familia nueva?

Ya pasó una vez (Opus 4.7: +30 %) y a medias otra (Opus 5.5: +2 tokens de
marco). La doc lo dice sin vueltas: «Do not reuse token counts … measured on
the old model; re-baseline with `count_tokens`».

Cómo lo maneja tokmd hoy: `--claude-family 3.0|4.7|4.8` elige el vocabulario
de ctok; `FRAME` por familia está congelado como dato dorado contra ctok
1.3.0. Si Anthropic saca familia nueva: (1) ctok tiene que sacar versión —
depende de un tercero; (2) tokmd tiene que remedir FRAME y actualizar datos
dorados; (3) hasta entonces, el default miente sin avisar.

Lo que falta y propongo (es la opción B de la pregunta 7): **una tabla
modelo → familia en tokmd**, que falle en voz alta con un modelo desconocido,
y un **gate periódico gratis** contra `count_tokens` sobre un corpus dorado.
El día que un modelo nuevo dé distinto, el gate lo dice; no hace falta
adivinar. Y `--verify` sigue siendo exacto siempre, porque pregunta a la API.

## 13. ¿Dónde empieza y termina cada familia?

Los límites son **por tokenizador, no por nombre comercial**:

| Familia | Modelos | ctok | Este archivo |
|---|---|---|---|
| Anterior | Claude 3.x, Opus 4.5, Opus 4.6, Sonnet 4.5, **Sonnet 4.6**, **Haiku 4.5** | `3.0` | 13.076 |
| «Opus 4.7» | Opus 4.7, Opus 4.8, Opus 5, Opus 5.5 (+2), **Sonnet 5**, Fable 5 / 5.1 (+2), Mythos | `4.7` / `4.8` | 17.381 (17.383) |

Nota: Sonnet 5 cruzó de familia; Haiku 4.5 no. El nombre no alcanza para
saberlo: hay que sondear con `count_tokens`. Dentro de la familia nueva, ctok
distingue `4.7` de `4.8` sólo por el marco (12 vs 6 tokens), mismo
vocabulario.

## 14. ¿Conviene un harness agnóstico que use modelos viejos para quemar menos tokens?

**No, y la cuenta lo muestra.** Es cierto que el mismo archivo pesa 25 %
menos en la familia vieja (13.076 vs 17.381). Pero lo que se paga es
tokens × precio, y Anthropic bajó el precio al cambiar el tokenizador:

| Modelo | Tokens | $/M entrada | Costo de este archivo por llamada |
|---|---|---|---|
| Sonnet 4.6 | 13.076 | 3,00 | **$0,0392** |
| Sonnet 5 | 17.381 | 2,00 | **$0,0348** ← más barato con más tokens |
| Opus 4.6 | 13.076 | 5,00 | $0,0654 |
| Opus 5 | 17.381 | 5,00 | $0,0869 |
| Opus 5.5 | ~17.383 | 4,00 | $0,0695 |
| Haiku 4.5 | 13.076 | 1,00 | $0,0131 |

Conclusiones:

- En Sonnet, el nuevo es más barato que el viejo por llamada. En Opus, el
  viejo es 25 % más barato, pero es un modelo anterior (calidad menor, y
  Anthropic ya publica fechas de retiro para la generación anterior:
  Haiku 4.5 «no antes del 15-oct-2026»).
- **Con Claude Code por suscripción esto ni aplica:** no pagás por token, el
  límite es la ventana de uso; y no elegís Sonnet 4.6.
- Donde sí se gasta por token (API, DeepSeek, OpenRouter), la palanca que
  vale es otra: **achicar lo que viaja en cada llamada**. Anthropic recomienda
  CLAUDE.md «under 200 lines» y mover instrucciones específicas a skills que
  cargan a demanda. Tu CLAUDE.md global tiene 17.381 tokens y va en **cada**
  llamada de **cada** sesión.

El harness agnóstico tiene sentido por otra razón (medir y elegir motor por
tarea, que ya hacés), no por «modelo viejo = menos tokens».

---

## Qué queda para decidir (Fabián)

1. Fijar el baseline como tabla versionada (pregunta 1).
2. Opción A+B+C de la pregunta 7 (vendorizar, gate de deriva, `--verify` de
   documento entero): ¿un PBI o tres?
3. ~~PBI para incluir el encabezado en `own_text`~~ — ya existe: PBI-009 en
   la rama de TTOK-04 (pregunta 8). Acordado con TTOK-04 el mismo día: el
   **total que muestra tokmd tiene que ser 17.381, igual al `count_tokens`
   de la API, marco incluido** (el archivo viaja como contenido de un mensaje
   real y el marco se cuenta). 17.376 es la suma de `Own` sin marco, un
   componente interno: `Own 17.376 + marco 5 = TOTAL 17.381`. Está así en
   ADR-007 v0.3.0 y PBI-009 de esa rama, con la sonda de esta sesión citada
   como segunda medición independiente de K=5.
4. BUG-011: salida UTF-8 en Windows (pregunta 10). ¿Entra en PBI-009 o va
   aparte?
5. Recorte del CLAUDE.md global (pregunta 14) — ya estaba en el handoff como
   pendiente tuyo.
