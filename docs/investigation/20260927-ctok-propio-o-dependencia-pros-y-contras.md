---
title: "¿tokmd tiene que dejar de apoyarse en ctok? Pros, contras y recomendación"
aliases:
  - "ctok propio o dependencia"
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
  - "[[20260927-respuestas-14-preguntas-tokenizacion]]"
  - "[[ADR-001-eleccion-de-motores-de-tokenizacion]]"
  - "[[ADR-007-costo-fijo-por-trozo-y-aditividad-del-arbol]]"
---

# ¿tokmd tiene que dejar de apoyarse en ctok? Pros, contras y recomendación

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. Respuesta al planteo de Fabián: con Fable 5.1, Astra 6, Opus 5.5 y cien modelos más a disposición, ¿qué nos frena para tener un tokenizador propio y que tokmd sea un producto de extremo a extremo? |

## La pregunta, reformulada

No es «¿podemos reescribir ctok?». Eso sí se puede: son 60 KB de Python y
cualquiera de los tres modelos grandes lo reescribe en una tarde. La pregunta
es **qué parte de ctok es la que vale**, y esa parte no es el código.

## Qué es ctok en realidad: 5 % código, 95 % medición

| Componente | Tamaño | Cómo se hizo | ¿Un modelo lo regenera? |
|---|---|---|---|
| Motor (teselado de costo mínimo, trie invertido) | ~8 KB | algoritmo conocido | **Sí**, trivial |
| Normalización (NFC, comillas, mayúsculas, bordes de palabra) | ~26 KB, tablas medidas carácter por carácter | **sondeando la API**: ninguna regla Unicode las reproduce | **No**: hay que medirlas |
| Vocabulario (48.792 piezas v3, 15.283 v4.7), cada una con su testigo | 4,7 MB de JSON | **millones de llamadas a `count_tokens`** | **No**: hay que medirlo |
| Marco por familia, reglas raras (Opus 5: espacios finales gratis; Opus 5.5: +2) | escalares | medición por modelo | **No**: hay que medirlo |

**El activo de ctok es un experimento, no un programa.** Sander Land no
«pensó» el tokenizador de Claude: lo midió, pieza por pieza, contra el
endpoint gratis, y congeló el resultado. Un modelo de IA, por más grande que
sea, **no sabe** cómo tokeniza Anthropic; sólo puede hacer lo mismo que él:
sondear y reconstruir. La inteligencia ayuda a diseñar las sondas; no las
reemplaza.

## Por qué las historias de «lo hice en tres días» no aplican acá

Son verdaderas y son de otra forma de problema: una app de transporte o un
Mortal Kombat con Trump son **construcción sobre APIs documentadas**, donde el
modelo ya sabe todo lo que hay que saber y sólo hay que escribirlo. Un
tokenizador ajeno es **ingeniería inversa de un sistema no documentado**: la
verdad está afuera, en un servidor, y sólo entra por medición. El costo de
escribir código bajó diez veces; el costo de medir, verificar y descubrir
casos raros (¿qué pasa con `’` curva? ¿con un emoji con selector de
variación? ¿con espacios finales en Opus 5?) **no bajó**: está limitado por
llamadas, por corpus de prueba y por disciplina de QA. Y el propio repo tiene
la medición de esto: delegar generación desde una spec da 17/17; delegar
depuración de lo que no se entiende da retorno negativo.

## Lo que cambia el diagnóstico: el riesgo no es «que ctok desaparezca»

Con los ejemplos de Fabián:

- **Dapper parado** no producía números equivocados; producía un ORM sin
  novedades. Se podía convivir.
- **Un tokenizador parado produce números equivocados en silencio.** Cuando
  Anthropic saque la familia siguiente, tokmd va a seguir informando un
  número con cara de exacto que ya no lo es. Eso es peor que Dapper y peor
  que Asterisk: es el producto mintiendo.

Y la conclusión que importa: **tener el código de ctok en el repo no arregla
ese riesgo.** Si mañana somos dueños del fork y Anthropic cambia el
tokenizador, estamos exactamente donde estaría Sander: hay que volver a
medir. **La independencia real no es tener el tokenizador; es tener la
fábrica del tokenizador** —la tubería que, dado un modelo nuevo, sondea,
reconstruye, verifica contra un corpus dorado y emite el vocabulario— y un
detector que avise cuando el que tenemos dejó de coincidir con la API.

Eso es lo que Fabián hizo en Despegar con Asterisk: no reescribió Asterisk;
contrató a dos personas que sabían cómo se construía y las puso a controlar
el proceso.

## Opciones

### A. Seguir como hoy: `ctok>=1.3` como dependencia

- **Pros:** costo cero.
- **Contras:** un solo mantenedor; nada detecta cuándo queda viejo (hoy ya
  no modela el +2 de Opus 5.5); si publica una 1.4 con un vocabulario
  distinto, tokmd cambia de número sin que nadie decida nada.

### B. Blindar la dependencia (vendorizar + gate de deriva + `--verify` de documento entero)

- Copiar ctok 1.3.0 al repo con su LICENSE (MIT lo permite), fijar versión.
- Corpus dorado de 10–20 archivos con su `count_tokens` guardado por modelo;
  test que corre ctok contra ese corpus; job periódico gratis que re-mide
  contra la API y avisa si cambió.
- `--verify` compara el archivo entero, no sólo sección por sección.
- **Pros:** una semana de trabajo; **convierte el riesgo silencioso en una
  alarma**; no depende de que Sander siga vivo.
- **Contras:** cuando la alarma suene, alguien tiene que remedir el
  vocabulario. Si es Sander, esperamos; si no, hace falta C.

### C. Ser dueños de la fábrica: la tubería de reconstrucción en el repo

- Empezar por lo que ya viene regalado: ctok trae **un testigo por pieza**
  (la sonda y su conteo). Re-verificar las 15.283 piezas de la familia 4.8
  contra `count_tokens` es gratis y, a 5.000 RPM, tarda minutos. Eso solo ya
  nos dice si sabemos reproducir su resultado.
- Después: herramienta que, dado un modelo, deriva marco, reglas de
  espacios y diferencias de vocabulario respecto de la familia conocida, y
  emite un `pieces_<familia>.json` en el mismo formato que ctok — para poder
  **contribuir upstream** en vez de bifurcar en silencio.
- **Pros:** independencia de verdad; capacidad de cubrir un modelo nuevo el
  día que sale; tokmd pasa a ser de extremo a extremo por el lado que
  importa (medición), no por el lado que no importa (el código del motor).
- **Contras:** es investigación, no desarrollo: tiene incertidumbre. El
  único dato real de duración es el de ctok mismo: 18 días del primer commit
  a la 1.0.0 y 35 días a la 1.3.0, para una persona que ya había hecho la
  investigación previa (su artículo). Con modelos grandes ayudando y con la
  tubería de Sander como guía, es razonable pensar en semanas de sesiones,
  no en meses; pero no hay forma de estimarlo mejor que corriendo el spike.

### D. Reescribir desde cero, sin ctok

- Tirar código MIT y 4,7 MB de mediciones ya verificadas para hacerlas de
  nuevo. **No.** Es el orgullo del equipo de Visma que armó su propio módulo
  de usuarios teniendo Auth0.

## Recomendación

**B ahora, C como spike acotado, D nunca.**

1. **B esta semana** (un PBI): vendorizar, corpus dorado, gate contra la API,
   `--verify` de documento entero. Es lo que hace que tokmd no mienta en
   silencio, sea quien sea el dueño del vocabulario.
2. **Spike de C, una sesión con criterio de éxito medible:** «re-verificar las
   15.283 piezas de la familia 4.8 con sus testigos contra `count_tokens`; si
   coinciden todas, sabemos reproducir a Sander; si no, sabemos exactamente
   dónde no». Costo: cero dólares (endpoint gratis), una sesión. El resultado
   decide si C es un PBI o queda en el cajón.
3. Si el spike da verde, **C como PBI propio**, con la tubería en formato
   compatible con ctok, y la primera contribución upstream: el +2 de Opus 5.5
   que hoy nadie modela. Es exactamente la jugada de Asterisk: entrar al
   proyecto, no reemplazarlo.

## Qué es lo que nos frena, con todas las letras

Nada técnico. Lo que frena es que **el cuello de botella se mudó**: ya no
está en escribir código —eso lo hacen los tres modelos grandes— sino en
medir, verificar y sostener la disciplina de QA que este mismo proyecto
viene aprendiendo a los golpes (BUG-008 pasó porque nadie comparó contra el
oráculo). Ser dueños de la fábrica del tokenizador es posible; lo que cuesta
no son los tokens de los modelos, es el método. Y ese método ya está
escrito en `CLAUDE.md`: los casos se registran antes de ejecutar, todo se
compara contra el oráculo, y un instrumento que nunca falló no prueba nada.

## Nota al margen

El «Auth0 open source en Java» que Fabián no recordaba es **Keycloak**
(Red Hat, Java). Hay otros (Authentik en Python, Ory y Zitadel en Go), pero
el de Java es Keycloak.
