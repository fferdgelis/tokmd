---
title: "ADR-006 — Separación de TDD, Desarrollo y QA por motor independiente"
aliases:
  - "tokmd ADR-006"
project: tokmd
document_type: architecture-decision-record
adr_id: ADR-006
status: accepted
decision_date: 2026-09-25
created: 2026-09-25
updated: 2026-09-25
version: 0.1.0
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
tags:
  - project/tokmd
  - adr
  - qa/metodo
related_documents:
  - "[[ADR-005-gate-sonarqube-y-metodo-de-qa]]"
  - "[[PBI_TEMPLATE]]"
---

# ADR-006 — Separación de TDD, Desarrollo y QA por motor independiente

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-25 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación, a pedido de Fabián: los tests de PBI-001 los escribió la misma sesión que el código, sin control cruzado. |
| 2026-09-25 | 0.2.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Aceptado por Fabián. Aplicado por primera vez de punta a punta en PBI-002 (rojo real confirmado antes de implementar). |

## Estado

`accepted`. Aceptado por Fabián Ferdgelis el 2026-09-25, tal cual estaba escrito.

## Contexto

Al cerrar PBI-001, la misma sesión (Claude, este harness) escribió `sections.py` y
`tests/test_sections.py`. Fabián lo señaló: quiere tres roles ejercidos por motores
distintos, sin que ninguno revise su propio trabajo — TDD (escribe los tests desde la
especificación, sin ver la implementación), Desarrollo (escribe la implementación para
pasar tests que no escribió), QA (verifica ambos, sin haber escrito ninguno).

**Verificación del CLAUDE.md global, pedida explícitamente por Fabián.** El archivo
global (`~/.claude/CLAUDE.md`) tiene una sección «Desarrollador y QA son roles
separados, y el bug se reporta» (16/08/2026): establece que Desarrollador y QA son
roles distintos, y protocoliza que un bug encontrado por Desarrollo se reporta a la
sesión de metodología de QA de `framework-multi-ai`, con casos registrados antes de
ejecutar. **Esa sección no menciona un tercer rol de TDD independiente de Desarrollo.**
El patrón de tres roles (TDD / Programación / QA, ninguno superpuesto) existe como
decisión de proyecto en `ia-evaluator` (`ADR-001-role-separation-and-evaluation-flow.md`)
y en la plantilla `PBI_TEMPLATE.md` de varios proyectos (secciones «Handoff a TDD»,
«Handoff a Desarrollo», «Handoff a QA»), pero no está escrito como regla general en el
archivo global. Se lo señala acá tal cual se encontró, sin asumir que ya estaba.

## Opciones

1. Mantener a Claude escribiendo código y tests, con QA (Kimi K3) como único control
   cruzado. Es lo que se hizo en PBI-001; dos de tres roles quedan en el mismo motor.
2. Tres roles, tres motores: DeepSeek escribe los tests desde la especificación (AC del
   PBI) sin ver la implementación; Claude escribe la implementación para pasar esos
   tests sin poder editarlos (salvo reportar un defecto de test, ver más abajo); Kimi K3
   (OpenCode/OpenRouter, ya establecido en ADR-005) hace la verificación independiente
   final y marca Kiwi.
3. Rotar completamente los tres roles entre sesiones humanas, sin motores de IA. Fuera
   de alcance: este proyecto se hace con agentes.

## Decisión propuesta

Opción 2. Mecanismo verificado hoy, sin escribir nada nuevo en el módulo compartido
`C:\IA\modulo-conexion-deepseek`:

- **TDD → DeepSeek**, vía `Invoke-DeepSeekChat` (Modo A del módulo: «tareas acotadas y
  bien especificadas», el caso medido con mejor retorno: 17/17 en el benchmark de
  generación desde spec precisa). *No* se usa `Invoke-DeepSeekCodeTask` para esto: esa
  función genera la implementación contra un test ya existente en Node — es el rol
  inverso al que se necesita acá. El wrapper de este proyecto
  (`tools/deepseek/generar_tests.ps1`, a crear) arma la especificación con: el
  contrato público del módulo (nombres de función, clases, tipos — nunca el cuerpo de
  la implementación), los AC del PBI en formato Dado/cuando/entonces, y el pedido
  explícito de devolver *sólo* un archivo `pytest` en un bloque de código. Extrae el
  código con `Get-CodeFromMarkdown` (exportada por el módulo) y lo escribe en
  `tests/test_<módulo>.py`.
- **Desarrollo → Claude** (esta sesión/harness). Escribe la implementación en
  `src/tokmd/` para pasar los tests que dejó TDD, sin modificarlos. Si un test está mal
  escrito (contradice el AC, o asume una firma que el PBI no pidió — la lección del
  20/08/2026 sobre `module.exports = { fn }` en el CLAUDE.md global es exactamente este
  riesgo), Desarrollo no lo edita en silencio: abre un `BUG-XXX` con `BUG_TEMPLATE.md`,
  tipo `test-defect`, y lo deja para que TDD (una nueva llamada a DeepSeek, con el
  síntoma) lo corrija.
- **QA → Kimi K3** (ya establecido en ADR-005), sin cambios: verifica código y tests
  juntos contra el snapshot, read-only, marca Kiwi.

**Retrofit de PBI-001.** Los tests actuales de `sections.py` los escribió Desarrollo
(este harness), sin TDD independiente. Se pide a DeepSeek una versión de
`tests/test_sections.py` a partir de los AC-01..05 del PBI y el contrato público de
`Section`/`parse_sections`, sin mostrarle `sections.py`. Si la versión de DeepSeek pasa
contra la implementación ya escrita y cubre los mismos AC, reemplaza a la actual (que
se conserva en el historial de git, no se borra la evidencia). Si DeepSeek escribe un
test que asume una firma distinta a la que expone el módulo, es una discrepancia
esperable de spec-vs-implementación: se decide caso por caso, documentando cuál de las
dos partes estaba mal (test o código), nunca ajustando ambas para que coincidan sin
registrar por qué.

## Consecuencias

Cada PBI cuesta una llamada extra a DeepSeek (centavos, medido en el CLAUDE.md global)
y un paso más de coordinación (Desarrollo no puede tocar los tests). A cambio, ningún
motor certifica su propio trabajo: DeepSeek no ve la implementación, Claude no escribe
el criterio de aceptación ejecutable, Kimi K3 no escribió ni tests ni código.

## Verificación y reversibilidad

Se verifica con: (a) el archivo de test tiene autoría de DeepSeek registrada en su
docstring o en el dev-log, con el prompt usado; (b) Desarrollo nunca commitea un cambio
a un archivo `test_*.py` en el mismo commit que un cambio a `src/tokmd/` salvo que el
commit sea justamente la corrección de un `BUG-XXX` de tipo `test-defect`, citado en el
mensaje. Cambiar esta separación requiere reemplazar este ADR.
