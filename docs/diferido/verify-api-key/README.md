---
title: "Diferido — cómo configura el usuario la API key opcional del --verify"
aliases:
  - "Diferido verify api key"
project: tokmd
document_type: reference
status: deferred
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
  - diferido
---

# Diferido — la API key opcional del `--verify`

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-opus-5 / Claude Code / subscription | Creación. Fabián difirió este tema y reasignó el número PBI-009 a los defaults del CLI. Todo el material de las dos rondas de consulta se movió acá con `git mv`, sin renombrar nada. |

## Por qué está acá

**Decisión de Fabián, 27/09/2026:** cómo hace un usuario común para configurar
su API key de Anthropic y usar `--verify` es *«lo último de lo último de lo
último»* que le interesa para la versión pública. El tema queda **diferido**, no
descartado: el trabajo está hecho y sirve entero cuando se retome.

## Ojo con el número: PBI-009 ahora es otra cosa

Los archivos de esta carpeta dicen «PBI-009» porque así se llamaba el tema
mientras se consultó. **Ese PBI nunca se escribió** — no hay ni hubo un
`docs/PBI/PBI-009-*.md` sobre la API key; sólo existen las dos consultas.

El 27/09/2026 Fabián **reasignó el número PBI-009** a un tema distinto y más
urgente: los valores por defecto del CLI (que `tokmd archivo.md` funcione solo,
con plataforma Claude y mostrando el total). Ese es
`docs/PBI/PBI-009-defaults-del-cli-y-total.md`.

**Los nombres de archivo de acá no se cambiaron a propósito**, para no romper
los enlaces `[[...]]` de Obsidian que apuntan a ellos desde el dev-log y los
traspasos. Si querés renombrarlos, hay que arreglar esos enlaces a mano.

## Qué hay adentro

| Archivo | Qué es |
|---|---|
| `CONSULTA-PBI-009-api-key-opcional-20260926.md` | Consolidado de la **ronda 1** (planteo v1). Seis motores. |
| `CONSULTA-PBI-009-RONDA-2-20260927.md` | Consolidado de la **ronda 2** (planteo v2). Seis motores, con el hallazgo de que la ronda 2 no fue independiente de la ronda 1. |
| `consulta-pbi009/` | Las salidas crudas de los doce llamados (seis por ronda), byte a byte, más los textos exactos que se enviaron. |

## Lo que quedó decidido y lo que no

**Decidido por los seis motores, y verificado por separado contra el código:**
guardar la key en una variable de entorno persistente del sistema no sirve —
en Windows la terminal ya abierta no la ve, y en Linux/macOS esa variable no
existe sin editarle al usuario los archivos de arranque del shell.

**Sin decidir, y es de Fabián:** dónde se guarda entonces. Archivo de
configuración en la carpeta del usuario (4 de 6) o almacén de credenciales del
sistema vía `keyring` (2 de 6). El detalle está en la sección 8 del consolidado
de la ronda 2.

## Los dos huecos del producto que salieron de acá y NO están diferidos

Los encontró esta consulta pero valen por sí solos, así que **no** se difieren
con el resto:

1. **`README.md` no menciona `--verify`.** La función existe, está testeada y
   publicada en PyPI, y ningún usuario tiene forma de enterarse.
2. **Sin `tokmd[verify]` instalado, `--verify` termina con un
   `ModuleNotFoundError` crudo** en vez de un mensaje que diga qué instalar.

Ninguno de los dos depende de decidir dónde va la key.
