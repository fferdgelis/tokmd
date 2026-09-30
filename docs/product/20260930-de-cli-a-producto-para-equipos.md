---
title: "De CLI a producto para equipos: escaneo recursivo, dashboard y qué se puede cobrar"
aliases:
  - "tokmd producto para equipos"
project: tokmd
document_type: research
status: active
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
  - product
related_documents:
  - "[[20260930-show-hn-post]]"
  - "[[20260927-respuestas-14-preguntas-tokenizacion]]"
  - "[[ROADMAP]]"
---

# De CLI a producto para equipos: escaneo recursivo, dashboard y qué se puede cobrar

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. Respuesta al planteo de Fabián: ampliar tokmd para equipos y poder cobrarlo; dos ideas suyas (escaneo recursivo por CLI, dashboard con FastAPI para tech leads y gerentes). Carpeta `docs/product/` nueva: no había lugar para estrategia de producto; es el nombre más obvio. |

## Aclaración previa

Lo que sigue es criterio, no medición. Todo lo que dice «el mercado quiere»
es hipótesis hasta que alguien de afuera lo confirme instalando, pidiendo o
pagando. El único dato de demanda real que tenemos es cero: la 2.0.0 tiene
tres días en PyPI y todavía no la vio nadie. Por eso la recomendación
termina en «validar antes de construir la parte paga», no en un plan de
negocios.

## Las dos ideas de Fabián, evaluadas por separado

### Idea 1 — Escaneo recursivo: `tokmd .` y una tabla con todos los `.md`

**Qué es.** Desde la raíz del proyecto hacia abajo, una tabla
(directorio, archivo, tokens) ordenada por peso, con el total. El `du` de
los tokens.

**Veredicto: sí, y es lo primero.** Es la extensión natural de lo que ya
existe (el parser y el conteo no cambian; se agrega recorrer carpetas y
sumar), es lo que un desarrollador pide a los cinco minutos de usar la
herramienta, y es barato: un PBI chico. Ya estaba en el ROADMAP como
«ranking de varios archivos».

Tres cosas para que valga más que una tabla:

1. **Distinguir lo que viaja en cada llamada de lo que no.** No todos los
   `.md` cuestan igual: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, los de
   `.claude/` se cargan en **cada** request; un `docs/ADR-004.md` sólo si
   alguien lo lee. La tabla tiene que marcar cuáles son «harness» (se pagan
   siempre) y cuáles son «contenido» (se pagan a demanda). Sin esa columna,
   el número grande asusta por el motivo equivocado.
2. **Un tope con código de salida:** `tokmd . --max-harness-tokens 5000`
   falla (exit 1) si el harness supera el límite. Es lo que convierte la
   herramienta de «informe» en **control**: se pone en el CI y nadie vuelve
   a subir un `CLAUDE.md` de 17.000 tokens sin que salte.
3. **Salida `--format json`** del escaneo, porque es lo que consume cualquier
   cosa que se construya después (la idea 2 incluida).

4. **Salida `--html informe.html`** (agregado el 30/09 tras el escenario de
   Fabián: Diego copia todos los proyectos a su disco y corre
   `tokmd -r C:\Projects`). Con decenas de proyectos la tabla ASCII no
   alcanza; un HTML **estático** —tabla ordenable y filtrable, sin
   servidor— se abre con doble clic y se manda por mail o WhatsApp. Cubre
   el 100 % de lo que una pantalla FastAPI daría en ese escenario, sin
   puerto, sin proceso corriendo, sin dependencia pesada. FastAPI queda
   para la opción C, donde sí hay algo que un archivo no puede hacer
   (historia, agregación, alertas). Primer usuario real de este PBI:
   Diego, sobre `C:\Projects`.

**FastAPI o línea de comando para esto:** línea de comando, sin discusión.
El desarrollador de la idea 1 vive en la terminal; una pantalla web para
ver cuánto pesa un archivo es peor experiencia que `tokmd .`, y además hay
que hostearla. FastAPI no es para esta idea.

### Idea 2 — Dashboard con FastAPI para tech leads y gerentes, y cobrarlo

**Qué es.** Una pantalla para quien está más arriba: ver qué está pasando
con los `CLAUDE.md` / `AGENTS.md` de los proyectos que le reportan.

**Veredicto: la intuición del público es correcta; la forma, todavía no.**

La intuición correcta: el gerente de desarrollo es quien paga los primeros
17.000 tokens de cada llamada de cada desarrollador, y hoy no tiene forma de
verlos. Ese es un problema real de alguien con presupuesto. Bien visto.

Lo que no cierra es «dashboard = pantalla sobre el CLI». Un gerente no paga
por ver el número de hoy; el CLI gratis se lo da a cualquiera de su equipo
en diez segundos. Paga por lo que el CLI **no puede** dar:

| Lo que un gerente compra | Por qué el CLI gratis no lo da |
|---|---|
| **Historia:** el harness del proyecto X pasó de 3.000 a 17.000 tokens en dos meses, ¿cuándo, en qué commit, quién? | el CLI mide un instante; la historia necesita guardar mediciones |
| **Agregación:** los 12 repos del equipo, ordenados por costo de harness | el CLI mide un repo |
| **Plata:** tokens × precio del modelo × llamadas por día ≈ dólares por mes por repo | el CLI no sabe cuántas llamadas hace el equipo |
| **Alertas y política:** «avisame si algún repo pasa de N» / «bloqueá el PR» | eso vive en el CI o en un servicio, no en una terminal |
| **Multi-plataforma:** el mismo equipo usa Claude Code, Codex y Antigravity; cada uno cobra su tokenizador | tokmd ya lo hace por archivo; la agregación por plataforma es lo que falta |

O sea: **el producto pago es la base de datos de mediciones en el tiempo y
las reglas encima, no la pantalla.** FastAPI sirve perfectamente como
backend de eso, pero es un detalle de implementación, no el producto. Y la
forma de entrega que un gerente adopta no es «instalen mi web app»: es un
**GitHub App / GitHub Action** que comenta en cada PR cuánto cambió el
harness, y un panel hosteado que ya tiene la historia porque la Action se
la manda. La adopción entra por el CI, no por un login.

## Lo que hay que decir con todas las letras sobre cobrar

1. **El CLI ya es Apache 2.0 y está publicado. No se puede volver atrás.**
   Cualquiera puede usarlo, copiarlo y venderlo. Eso no es un problema si se
   entiende bien: el CLI gratis es la **puerta**; lo que se cobra es lo que
   está detrás (historia, agregación, alertas, soporte). Es el modelo
   *open-core* de Sentry, GitLab, Grafana: el motor abierto, el servicio y la
   escala pagos. Vender licencias del CLI está muerto como modelo; no
   intentarlo.
2. **El pitch de «ahorrá plata» es débil en dólares y fuerte en otra cosa.**
   17.381 tokens × USD 2/M (Sonnet 5) = **USD 0,035 por llamada**. Un
   desarrollador hace cientos de llamadas por día (cada uso de herramienta
   es una llamada; con caché, la mayoría se cobra al 10 %). Para un equipo
   de 20 son decenas de dólares por mes, no miles. **Nadie compra una
   herramienta para ahorrar USD 40.** Lo que sí compra es lo que Anthropic
   dice en su propia doc de Claude Code: un `CLAUDE.md` largo **reduce la
   adherencia** — el modelo sigue peor las instrucciones. Y lo que el
   propio caso de Fabián muestra: 17.000 → 3.000 tokens no es un ahorro,
   es un harness que funciona. **El pitch es calidad y gobierno del
   contexto, no centavos.**
3. **El foso es fino y hay que saberlo.** Claude Code ya tiene `/context`.
   Que Anthropic o GitHub agreguen «tokens de tu CLAUDE.md» de forma nativa
   es cuestión de tiempo, y ese día el CLI de un solo archivo pierde
   sentido. Lo que ninguno de ellos va a hacer es lo **multi-plataforma**
   (Claude + OpenAI + Gemini, con el tokenizador correcto de cada uno) ni la
   **historia por organización**. Ahí conviene pararse.
4. **Antes de construir lo pago, hay que ver si alguien tira de lo gratis.**
   El post de difusión (`20260930-show-hn-post.md`) es el experimento:
   si trae estrellas, issues y gente pidiendo «esto para mi equipo», la
   idea 2 tiene demanda. Si no trae nada, construir un SaaS encima es
   construir sobre una hipótesis.

## Opciones

| | Qué | Impacto | Riesgo | Dónde queda registrado |
|---|---|---|---|---|
| **A** | **Escaneo recursivo en el CLI gratis** (`tokmd .`, columna harness/contenido, `--max-harness-tokens` con exit code, `--format json`) | convierte tokmd de «curiosidad» en herramienta de CI; es lo que la gente va a pedir primero | **bajo (~10 %)**: extensión directa de lo que hay, un PBI, sin dependencias nuevas | PBI-010 en `docs/PBI/`, ROADMAP actualizado |
| **B** | **A + GitHub Action gratis** que comenta en cada PR el delta de tokens del harness | mete tokmd donde el equipo ya trabaja; es el canal de adopción que después alimenta lo pago | **medio-bajo (~25 %)**: la Action es simple, pero es un repo y un marketplace más que mantener | PBI-011, repo `tokmd-action` |
| **C** | **A + B + servicio hosteado pago** (FastAPI + base de datos): historia por repo, agregación por equipo, alertas, dólares estimados, multi-plataforma | es el producto que un gerente compra; sin A y B antes, no tiene quién lo alimente ni quién lo conozca | **alto (~60 %)** si se arranca hoy: sin demanda verificada, con hosting, cuentas, cobro, soporte y el riesgo de que la feature básica la absorba Claude Code | ADR nuevo (modelo open-core, qué queda gratis y qué no), PBI-012+, y una decisión de precio que es tuya |
| **D** | Dashboard FastAPI como está planteado (pantalla local sobre el CLI, sin historia ni agregación) | poco: muestra lo mismo que el CLI, con más fricción | **alto (~70 %)** de construirlo y que nadie lo prefiera al CLI | — (no se recomienda) |

## Recomendación

**A ahora, B enseguida, C sólo si A y B muestran tracción. D no.**

El orden importa porque cada paso es el canal de adopción del siguiente:
el CLI gratis lleva a la Action; la Action, corriendo en los PR de equipos
reales, es la que genera la historia y hace evidente por qué alguien
querría el panel. Construir C primero es construir la pantalla antes de
tener los datos y antes de tener a nadie mirándola.

Y una cosa que ya tenés y vale más que todo lo anterior: **el caso propio.**
«Mi `CLAUDE.md` global pesaba 17.381 tokens medidos contra la API real; lo
llevé a 3.000.» Ese antes/después, con los números verificados y el método
publicado, es el material de venta —para el post de hoy y para el pitch a
un gerente mañana— y ninguna feature lo reemplaza. Cuando el nuevo
`CLAUDE.md` esté terminado, medirlo con `tokmd` y guardar el número al lado
del viejo.

## Qué queda para decidir (Fabián)

1. ¿Arranco con A como PBI-010 (escaneo recursivo, harness/contenido, tope
   con exit code, JSON)?
2. ¿B entra en el mismo PBI o aparte?
3. Para C, antes de cualquier código: ¿qué señal de demanda te alcanza para
   decidirlo? (Por ejemplo: N estrellas, N issues pidiendo features de
   equipo, o una empresa que lo pida por nombre.)
