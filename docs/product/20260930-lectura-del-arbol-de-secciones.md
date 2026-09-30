---
title: "La tabla de --sections es ilegible con archivos grandes: opciones de visualización"
aliases:
  - "Legibilidad de --sections"
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
  - product
related_documents:
  - "[[20260930-de-cli-a-producto-para-equipos]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
---

# La tabla de `--sections` es ilegible con archivos grandes

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-30 | 0.1.0 | Anthropic / claude-sonnet-5 / Claude Code Desktop / subscription | Creación. Fabián mostró una captura de `tokmd --sections` sobre su `CLAUDE.md` real: títulos largos que envuelven, árbol de conectores que se rompe visualmente con la nesting profunda. Propuso una vista tipo SpaceSniffer (treemap: rectángulos proporcionales al tamaño, como los visualizadores de espacio en disco). |

## El problema, con evidencia

La captura que trajo Fabián: `tokmd CLAUDE.md --sections` en una consola
angosta. Con títulos largos y varios niveles de anidamiento, cada fila
envuelve en 2-3 líneas y los conectores del árbol (`├─`, `└─`, `│`) quedan
descolgados del texto al que pertenecen. Es legible con un archivo chico
de pocas secciones; con un `CLAUDE.md` real de 40+ encabezados, no.

**Causa de fondo:** una tabla de texto con nesting profundo no escala con
el ancho de una terminal. No es un bug puntual de formato — es un límite
del medio (texto plano en una consola de 80-120 columnas) contra el
contenido (árboles profundos, títulos largos, muchas filas).

## Opciones

### Opción A — Arreglar la tabla de consola (barato, ya)

- Truncar cada título al ancho real de la terminal
  (`shutil.get_terminal_size()`), con `…` al final, en vez de envolver.
- Los conectores del árbol nunca se separan del texto: una sola línea por
  fila, siempre.
- Colapsar automáticamente ramas chicas: `--sections` ya soporta
  `--depth`; agregar un umbral (`+8 secciones más, 340 tokens` en una
  línea) para hojas por debajo de, por ejemplo, el 1% del total.
- **Pros:** cero dependencias nuevas, arregla el dolor de hoy en un PBI
  chico, sigue funcionando por SSH o en un pipe.
- **Contras:** sigue siendo texto: para «ver de un vistazo qué pesa más»,
  un humano igual tiene que leer números, no comparar áreas.
- **Impacto:** alto para el dolor inmediato (la captura de hoy). **Riesgo:
  bajo (~10%).**

### Opción B — Treemap en HTML (la idea de Fabián, sin la parte Java)

Un treemap es exactamente lo que pide la captura de SpaceSniffer:
rectángulos anidados, cada uno con área proporcional a su peso — acá,
tokens en vez de bytes de disco. **La parte de SpaceSniffer que no
conviene copiar es que sea una app nativa.** tokmd ya evita
deliberadamente cualquier dependencia pesada (se descartó `torch` en
ADR-008 por el mismo motivo), y ya está planeado un flag `--html` para el
escaneo recursivo multi-archivo (`[[20260930-de-cli-a-producto-para-equipos]]`,
opción A). **Este treemap es el mismo flag, aplicado a un solo archivo en
vez de a un árbol de carpetas:**

```
tokmd CLAUDE.md --sections --html arbol.html
```

Un único archivo HTML **estático**: `<div>`s anidados con `width`/`height`
proporcionales al token count (CSS puro, sin D3 ni ninguna librería de
gráficos — un treemap de "squarified layout" simple se calcula con
aritmética, no hace falta una dependencia), con el título completo visible
al pasar el mouse (`title=`) para los rectángulos chicos donde el texto no
entra. Se abre con doble clic, se manda por mail, no necesita servidor.

- **Pros:** resuelve el problema de fondo (comparar tamaños de un
  vistazo, no leer una tabla), reusa el flag `--html` que ya vamos a
  construir para el escaneo recursivo — mismo motor de render para las dos
  cosas, no dos features separadas. Cero dependencias nuevas.
- **Contras:** para archivos con muy pocas secciones, un treemap es menos
  útil que la tabla (un rectángulo grande y dos chiquitos no dice mucho
  más que los números). No reemplaza el uso en terminal/CI, es un
  complemento.
- **Impacto:** alto para el caso que motivó esto (archivos grandes,
  comparar de un vistazo). **Riesgo: bajo-medio (~15%)** — el layout de
  treemap tiene algo de matemática (algoritmo "squarified"), pero es
  conocido y acotado.

### Opción C — Interfaz nativa tipo SpaceSniffer (Java, Electron, Tauri, etc.)

Una aplicación de escritorio separada que dibuje el treemap con una
librería gráfica nativa.

- **Pros:** más pulido visualmente, interactivo (zoom, clic para entrar a
  una carpeta), que es lo que SpaceSniffer hace bien.
- **Contras:** es exactamente la dirección contraria a la que viene tokmd:
  hoy pesa lo que pesa porque no arrastra nada pesado. Una app de
  escritorio es un instalador, un runtime (Java, o Electron con Chromium
  embebido, cientos de MB), y mantenimiento de UI en una plataforma nueva.
  Es la opción D del informe de producto (`de-cli-a-producto-para-equipos.md`,
  «dashboard sin historia ni agregación») con el mismo veredicto: no se
  recomienda.
- **Impacto:** el mismo que B, en una forma mucho más cara de construir y
  mantener. **Riesgo: alto (~55%)** — cambia la naturaleza del proyecto
  (de CLI a app de escritorio) para resolver un problema que B resuelve
  con un archivo.

## Recomendación

**A ahora (barato, arregla la captura de hoy), B como parte del mismo PBI
del `--html` que ya está planeado para el escaneo recursivo — no dos
features, una sola con dos casos de uso** (un archivo con `--sections
--html`, o un árbol de carpetas con `-r --html`). **C no.**

No hace falta que mandes las capturas de SpaceSniffer para arrancar con A
o para decidir B: el concepto de treemap está bien definido y no depende
de los detalles visuales de esa herramienta puntual. Si en algún momento
querés un comportamiento específico de SpaceSniffer replicado exactamente
(por ejemplo, algo de cómo colorea o cómo deja entrar el mouse a explorar),
ahí sí valen las capturas — para lo que hay definido hasta acá, no son
necesarias.

## Qué queda para decidir (Fabián)

1. ¿A entra como parte de PBI-011 (que ya toca `cli.py`) o como PBI propio?
   Dado que es texto puro sin dependencias, cualquiera de los dos cierra
   rápido.
2. ¿B se escribe ahora como PBI (compartiendo diseño con el escaneo
   recursivo aunque ese todavía no tenga PBI número) o se espera a que el
   escaneo recursivo tenga su propio PBI y se agrega ahí?
