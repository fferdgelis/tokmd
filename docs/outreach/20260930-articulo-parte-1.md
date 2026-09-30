---
title: "Artículo, parte 1: decir «hola» me costaba 17.381 tokens"
aliases:
  - "Articulo tokmd parte 1"
project: tokmd
document_type: outreach-draft
status: draft
version: 0.1.0
created: 2026-09-30
updated: 2026-09-30
language: es
owners:
  - project-founder
author_human: "Fabián Ferdgelis (voz); borrador redactado por LLM"
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
  - outreach
related_documents:
  - "[[20260930-show-hn-post]]"
  - "[[20260927-count-tokens-api-vs-tokmd-ctok-ttok]]"
  - "[[20260927-respuestas-14-preguntas-tokenizacion]]"
---

# Artículo, parte 1: decir «hola» me costaba 17.381 tokens

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Borrador a pedido de Fabián, en primera persona, para LinkedIn o blog. Dos cosas que él dijo y el texto corrige, con su motivo, en «Notas para Fabián» al final. |

## Notas para Fabián (no van en el artículo)

1. **El número «3.000» todavía no existe.** Medí tu `CLAUDE.md` global hoy
   con `tokmd 2.0.0`: **19.017 tokens** (42.336 bytes). Subió, no bajó:
   el bloque nuevo (COM/ROL) está **arriba** del contenido viejo, que sigue
   entero abajo. Los 3.000 van a ser verdad cuando saques lo viejo. El
   artículo tiene un `[NÚMERO FINAL]` para completar con la medición real
   del día que lo publiques; no puse 3.000 porque no está medido y la
   regla es no afirmar lo que no se verificó.
2. **El modo offline no es «muy aproximado» para Claude.** Está medido:
   `ctok` dio **exactamente** lo mismo que la API de Anthropic sobre tu
   archivo (17.381 = 17.381) y en todas las sondas. Lo aproximado es
   Gemini (parte 2). El artículo lo dice como es; decir «muy aproximado»
   de algo exacto sería regalar la mejor noticia del proyecto.
3. **«Hola mundo cuesta 17.000 tokens»** es cierto con un matiz que el
   texto conserva: el archivo viaja en **cada** llamada, pero después de la
   primera se cobra a tarifa de caché (una décima parte). El costo real
   no es sólo plata: es que un `CLAUDE.md` largo hace que el modelo siga
   peor las instrucciones — lo dice la doc de Anthropic. Eso es lo que
   engancha a un gerente, no los centavos.
4. La «plataforma de OpenAI que usaba mal» es `ttok`, que por dentro usa
   `tiktoken`. Lo nombro porque es un dato verificable, no para pegarle a
   nadie: la herramienta es buena para lo que es.

---

## Texto del artículo

# Decir «hola» me costaba 17.381 tokens

Hasta la semana pasada, cada vez que abría Claude Code y escribía «hola»,
antes de que el modelo leyera esa palabra ya había leído **17.381 tokens
míos**. No los de la conversación: los de un archivo que yo mismo escribí.

Si trabajás con Claude Code, Codex, Antigravity o cualquier asistente de
programación, tenés uno igual. Se llama `CLAUDE.md`, o `AGENTS.md`, o
`GEMINI.md`, y es donde le decís al modelo cómo querés que trabaje: reglas,
convenciones, qué no tocar. **Ese archivo se carga entero al principio de
cada sesión y viaja en cada llamada.** Es el primer gasto de cada request,
antes de que vos pidas nada. Y el mío, después de dos meses de agregarle
reglas cada vez que algo salía mal, pesaba 38 KB.

Lo que no sabía era cuánto era eso en tokens. Y lo que descubrí al medirlo
es el motivo de este artículo.

## Cada plataforma mide con su propia regla

Un token no es una palabra ni un carácter: es el pedazo de texto que el
modelo procesa de a uno, y **cada proveedor corta el texto de una manera
distinta**. El mismo archivo mío:

| Con la regla de | Tokens |
|---|---|
| Anthropic, modelos actuales (Sonnet 5, Opus 5) | **17.381** |
| Anthropic, modelos anteriores (Sonnet 4.6, Haiku 4.5) | 13.076 |
| OpenAI (GPT-5, Codex) | 10.742 |
| OpenAI, regla vieja (GPT-4) | 11.660 |

Mismo archivo, cuatro números, hasta 60 % de diferencia. No es que uno esté
bien y los otros mal: cada uno es correcto **para su plataforma**, y cada
plataforma te cobra con el suyo.

Yo venía midiendo con una herramienta de línea de comandos muy conocida
que usa el tokenizador de OpenAI. Para Claude, me estaba diciendo un
tercio menos de lo real. Durante meses tomé decisiones sobre qué recortar
con un número equivocado.

## Terminé haciendo mi propia herramienta

Se llama **tokmd**. Es un comando de terminal, gratis, de código abierto:

```
pip install tokmd
tokmd CLAUDE.md
17381
```

Un número. El que Anthropic va a contar. Con `--sections` te da el
desglose por sección del Markdown —un árbol, como `du` para carpetas—
para ver **qué parte** del archivo pesa, que es lo que necesitás para
decidir qué sacar.

Tiene dos modos, y vale la pena entender la diferencia:

- **Modo offline (el de siempre).** No necesita cuenta, key ni internet.
  Usa una reconstrucción del tokenizador de Anthropic hecha por un
  desarrollador independiente (Anthropic no publica el suyo). Lo verifiqué
  contra la API real sobre mi archivo entero: **dio exactamente el mismo
  número.** Para Claude, el modo offline es exacto, no aproximado.
- **Modo online (`--verify`).** Le pega al endpoint oficial de Anthropic
  que cuenta tokens. Es **gratis** —no se cobra ni la consulta ni la
  respuesta— y funciona con una cuenta de API en saldo cero; sólo hace
  falta tu propia key en el entorno. Es el oráculo: cuando querés la verdad
  de un modelo nuevo, o no confiás en nada, está ahí.

Para OpenAI usa el tokenizador oficial de ellos. Para Gemini y los modelos
abiertos (DeepSeek, GLM, Qwen, Llama, Mistral) viene la parte 2.

## Mi propia herramienta estaba mal, y cómo lo encontré

Esto es lo que más me interesa contar. Antes de publicar la versión 2,
hice algo que casi salteo: comparé el total de tokmd contra el endpoint
oficial. **Mi herramienta daba 8,5 % menos.** No contaba la línea del
título de cada sección: un `## Título` costaba tokens reales y tokmd lo
ignoraba. En un archivo con 44 títulos, eran 1.478 tokens que
desaparecían en silencio.

El tokenizador no era el problema —era exacto—; el problema era **mi**
código, la parte que decidía qué texto mandarle. Lo arreglé, y agregué un
control permanente: tokmd ahora imprime una línea de «deriva» que tiene
que dar cero. El día que no dé cero, la herramienta lo dice en vez de
esconderlo otra versión más.

La lección me sirve para cualquier cosa que mida algo: **si existe un
oráculo real y gratis, contrastá contra él antes de confiar en tu propia
aproximación.** Sobre todo en la que escribiste vos.

## El resultado

Con el número real en la mano, hice lo que hay que hacer con un archivo de
17.381 tokens que se carga en cada llamada: **lo reescribí.** Saqué lo que
era historia, lo que era desahogo, lo que ya estaba en otro lado. Anthropic
recomienda menos de 200 líneas para estos archivos, y da el motivo: un
`CLAUDE.md` largo no sólo cuesta más, **hace que el modelo siga peor las
instrucciones**. Lo comprobé de la peor manera durante meses.

Hoy mi `CLAUDE.md` pesa **[NÚMERO FINAL] tokens**. De 17.381 a eso. Medido
con la misma herramienta y contra la misma API.

## Qué sigue

Parte 2: que tokmd cuente bien para **todos** los modelos que un equipo usa
—Gemini, DeepSeek, GLM, Qwen, Llama, Mistral— dándolos de alta en un archivo
de configuración, sin tocar código. Porque el problema de fondo no es
Claude: es que cada plataforma mide con su regla, y nadie te presta la suya.

Código, mediciones y el informe completo del bug:
https://github.com/fferdgelis/tokmd

---

*Fabián Ferdgelis. 31 años en sistemas. Este proyecto lo planifiqué con
Claude Opus, lo desarrolló Claude Sonnet con tests escritos por DeepSeek y
QA independiente de Kimi K3, y lo medí contra la API de Anthropic. Los
números de arriba son los reales del 27 de septiembre de 2026.*
