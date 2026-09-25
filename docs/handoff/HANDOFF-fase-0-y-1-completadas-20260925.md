---
title: "Traspaso: tokmd — Fase 0 y Fase 1 cerradas, arranca Fase 2"
aliases:
  - "Handoff tokmd 20260925"
project: tokmd
document_type: work-plan
status: active
version: 0.1.0
created: 2026-09-25
updated: 2026-09-25
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
  - handoff
related_documents:
  - "[[ADR-005-gate-sonarqube-y-metodo-de-qa]]"
  - "[[ADR-006-separacion-tdd-desarrollo-qa-por-motor]]"
  - "[[PBI-002-tokenizador-claude]]"
---

# Traspaso: tokmd — Fase 0 y Fase 1 cerradas, arranca Fase 2

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-25 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, al cerrar la sesión anterior por el hook de tope de 300 llamadas a herramientas. |

## En una línea

Fase 0 (relevamiento + estructura documental + catálogo/planes de Kiwi) y Fase 1
(PBI-001, parser de secciones) están cerradas: código, tests con autoría separada,
gate de Sonar y QA independiente en Kiwi, todo verde. Sigue Fase 2: PBI-002
(tokenizador Claude) y PBI-003 (tokenizador OpenAI) — leer la sección «Dos cosas a
corregir desde acá» antes de escribir una línea.

## Repositorio y commit actual

`C:\IA\Projects\Claude-Tokenizer`, rama `main`, sin remoto todavía (no se hizo push:
eso es PBI-007, y necesita confirmación explícita de Fabián por ser una acción
pública). Último commit al cerrar esta sesión: `f5e6615` — verificar con
`git log --oneline -8` si hace falta el estado exacto.

## Qué existe y dónde (no releer todo, son punteros)

- **Plan aprobado por Fabián:** `C:\Users\fferdgelis\.claude\plans\claude-claude-hoy-existe-wise-mist.md` — el diseño completo de tokmd, las 8 fases, la estructura del repo.
- **Relevamiento de tokenizadores:** `docs/investigation/20260924-tokenizadores-por-plataforma.md`.
- **ADR:** `docs/ADR/ADR-001` a `ADR-006`, todos `status: proposed` — **Fabián no los aceptó formalmente todavía**, sólo confirmó los 20 Test Case de Kiwi. Preguntarle si los da por aceptados o quiere ajustar algo antes de seguir generando más.
- **PBI:** `docs/PBI/PBI-001` (cerrado) a `PBI-008` (sin empezar). PBI-006/007/008 no tienen Test Case en Kiwi todavía — se cargan al empezar cada fase, por diseño (no es un olvido).
- **Dev-log con todo el diagnóstico crudo de hoy:** `docs/dev-log/2026-09-24.md` — ahí están los dos bugs de DeepSeek diagnosticados (truncamiento por `thinking`, extracción de fence no-greedy) y el bug de PS7 en el Quality Gate.

## Kiwi TCMS — ids para no tener que releer todo

- Producto `tokmd` id=6, clasificación «Herramientas de desarrollo» id=6, versión `1.0.0` id=10.
- Categorías: Functional=33, Error=34, Edge case=35, Performance=36, Security=37.
- Componentes: Sections parser=10, Tokenizers=11, CLI=12, Render=13, Verify=14, Packaging=15, SonarQube gate=16.
- Planes: PBI-001=21 … PBI-008=28 (Unit), «Release 1.0.0»=29 (Acceptance).
- Casos PBI-001..005 confirmados por Fabián, ids 340-359 (ver `tools/kiwi/cargar_casos.py` para el detalle exacto por PBI).
- **PBI-001 cerrado:** Test Run id=61 (build id=24, commit `6be061d`), Test Execution ids 221-225, las cinco `PASSED` con evidencia de QA real (`docs/handoff/qa/fase-1-kimi-k3.txt`).

## SonarQube

- Proyecto `tokmd` existe en `http://127.0.0.1:9000`. Primer análisis (commit `6be061d`): **Quality Gate: OK**. Evidencia en `C:\IA\Data\sonarqube\reports\tokmd\20260925-024139\gate-status.json`.
- **Pendiente de Fabián:** fijar el período de código nuevo (`Project settings → New code → Specific analysis`) — sin eso, `Invoke-SonarGate.ps1` con `-RequireGate:$true` va a exigir algo que todavía no está configurado.
- **Hueco real, sin resolver:** nunca se probó que el gate de *este* proyecto sea capaz de dar `ERROR`. El precedente es `whatsapp-mcp/tools/sonarqube/Test-QualityGateFailure.ps1`, que analiza un proyecto sintético (`sonarqube-negative-fixture`) sin cobertura y exige que el escáner falle con gate `ERROR`. tokmd no tiene su equivalente. Recomendado: construirlo antes de dar la infraestructura de Sonar por confiable, no necesariamente antes de seguir con PBI-002.

## Dos cosas a corregir desde PBI-002 en adelante (pedido explícito de Fabián, 25/09)

1. **Orden real de TDD, no sólo autoría separada.** En PBI-001, Desarrollo (Claude) escribió `sections.py` completo y DESPUÉS le pidió los tests a DeepSeek — los tests nunca estuvieron en rojo contra el código real, sólo se verificó que autoría fuera independiente (ADR-006). Para PBI-002: primero Desarrollo escribe sólo la firma pública vacía (o que levanta `NotImplementedError`) en `tokenizers.py`; TDD (DeepSeek) escribe `test_tokenizers.py` contra esa firma; se confirma que la suite da **rojo de verdad**; recién ahí Desarrollo implementa hasta ponerla en verde.
2. **Canario de Sonar.** Construir algo equivalente a `Test-QualityGateFailure.ps1` para `tokmd`, para probar que el gate puede fallar. Se puede hacer como una tarea aparte, no necesita bloquear PBI-002.

## Herramientas ya construidas (reusar, no reescribir)

- `tools/kiwi/`: `rpc_client.py`, `crear_catalogo.py`, `crear_planes.py`, `cargar_casos.py`, `crear_run.py`, `registrar_resultados.py`. Todos idempotentes, corren dentro de `kiwi_web` vía `docker cp` + `docker exec` (password por stdin desde DPAPI `kiwi-tcms/qa-bot-password`).
- `tools/deepseek/`: `Invoke-TddDeepSeek.ps1` (rol TDD — usa el módulo compartido `C:\IA\modulo-conexion-deepseek` sin tocarlo, con extracción de código propia porque `Get-CodeFromMarkdown` corta en el primer fence), `specs/*.md.prompt` (specs ya usadas para PBI-001).
- `tools/sonarqube/`: `Invoke-SonarGate.ps1`, `sonar-project.properties`.
- `tools/qa/`: `Invoke-QA-Kimi.ps1` (QA independiente — OpenCode + `openrouter/moonshotai/kimi-k3`, read-only por convención sobre un snapshot), `brief-qa.md.prompt` (plantilla del brief de PBI-001, adaptar por fase).

## Trampas ya pagadas hoy (no las vuelvas a pisar)

- **Cualquier `.md` escrito con Write/Edit pasa por un guardián global** (`framework-multi-ai/devsecops/hooks/core/Test-IA-Markdown.ps1`) que exige front matter completo + sección «Historial de modificaciones» + tabla. Para prompts/specs/fixtures que NO deben llevar ese esquema (contenido de test, prompts a DeepSeek o a Kimi K3), usar extensión `.md.prompt` o `.md.fixture`, no `.md`.
- **Kiwi rechaza `TestRun.add_case` sobre un caso `PROPOSED`** (`Fault -32603: status is not confirmed`). Fabián tiene que confirmarlos primero; Desarrollo no se los autoaprueba (mismo motivo que separar TDD/Dev/QA).
- **`Invoke-DeepSeekChat` con `thinking` habilitado puede truncar la respuesta** porque el razonamiento visible consume el mismo `max_tokens` que la respuesta. Usar `-DisableThinking` para tareas mecánicas de generación desde spec precisa.
- **`Get-CodeFromMarkdown` (módulo compartido) corta en el primer ` ``` `** con regex no-greedy. Si el archivo generado necesita un fence embebido (por ejemplo, un test que ilustra un bloque de código), no sirve — usar la extracción propia ya escrita en `Invoke-TddDeepSeek.ps1` (del primer fence de apertura al último ` ``` ` de toda la respuesta).
- **PowerShell 7: el cuerpo de un error de `Invoke-RestMethod` está en `$_.ErrorDetails.Message`**, no en `$_.Exception.Response.GetResponseStream()` (eso es .NET Framework / PowerShell 5.1).
- **`/tmp/work` no existe por defecto en `kiwi_web`** tras un restart del contenedor: `docker exec kiwi_web mkdir -p /tmp/work` antes del primer `docker cp`.
- **`git archive HEAD` + `tar` funciona bien desde PowerShell** (`git archive HEAD | & tar -x -C $dir`), usando el `tar` de Git Bash (`/usr/bin/tar`), no hace falta nada más.

## Pendiente de decisión de Fabián (no bloquea seguir con PBI-002, pero hay que preguntarle en algún momento)

1. Aceptar/corregir los ADR-001 a 006 (todos `proposed`).
2. Fijar el período de código nuevo en la UI de Sonar.
3. Cuenta PyPI + pending publisher para Trusted Publishing (PBI-007).
4. Si los docs en español de metodología van públicos junto con el código, o se separan.
5. Si construir el canario de Sonar es una tarea propia o entra en el flujo de PBI-002.

## Próximo paso concreto

Empezar PBI-002 (`docs/PBI/PBI-002-tokenizador-claude.md`) con el orden corregido del
punto 1 de arriba. El FRAME medido hoy para referencia (no re-medir de cero):
`ctok.token_count("", v)` → familia `3.0`=8, `4.7`=12, `4.8`=6. Hay deriva de borde
confirmada al concatenar dos secciones (1 token de diferencia en el ejemplo medido) —
ADR-002 ya la anticipa, PBI-002 tiene que dejarla medida formalmente en
`docs/investigation/20260924-ctok-marco-y-deriva.md` (archivo todavía no creado).
