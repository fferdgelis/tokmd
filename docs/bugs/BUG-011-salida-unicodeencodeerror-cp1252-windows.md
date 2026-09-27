---
title: "BUG-011 — tokmd revienta con UnicodeEncodeError en Windows cuando la salida no es una consola y un título tiene caracteres fuera de cp1252"
aliases:
  - "BUG-011 salida cp1252"
project: tokmd
document_type: bug
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
  - bug
related_documents:
  - "[[PBI-005-render-de-salida]]"
  - "[[PBI-009-defaults-del-cli-y-total]]"
  - "[[BUG-008-texto-de-los-encabezados-no-se-cuenta]]"
  - "[[20260927-count-tokens-api-vs-tokmd-ctok-ttok]]"
---

# BUG-011 — tokmd revienta con `UnicodeEncodeError` en Windows cuando la salida no es una consola

## Historial de modificaciones

| Fecha | Versión | Modificado por | Descripción |
|---|---|---|---|
| 2026-09-27 | 0.1.0 | Anthropic / claude-fable-5-1 / Claude Code Desktop / subscription | Creación. Encontrado en la sesión TTOK-05 al medir el `CLAUDE.md` global contra la API de Anthropic. Se numeró 011 porque 008, 009 y 010 ya estaban tomados en la rama `worktree-ttok04-pbi009-ronda2`. |

## 1. Clasificación

- **Título:** En Windows, si la salida de `tokmd` va a un archivo o a otro proceso (no a una consola) y algún título de sección tiene un carácter fuera de cp1252 (`→`, `«`, `»`, `—`), el programa termina con traceback en los formatos `table`, `md` y `csv`. `json` no falla porque escapa a ASCII.
- **Estado:** `verified` (arreglado y confirmado por QA independiente el 2026-09-27)
- **Tipo:** `product-defect`
- **Severidad:** `2-high` — el archivo real del owner lo dispara; y redirigir la salida (`> medicion.txt`, un pipe, un script, CI) es uso normal de una herramienta de línea de comandos.
- **PBI relacionado:** `[[PBI-005-render-de-salida]]` (origen: `click.echo` sin codificación fijada). Propuesto para entrar en `[[PBI-009-defaults-del-cli-y-total]]`, que ya toca `cli.py` y `render.py` y sube a `2.0.0`; lo decide Fabián.
- **Registro en Kiwi:** **Bug `pk=13`**, severidad `High`, estado abierto, build
  `d9c42ff` (registrado 2026-09-27 por TTOK-04, a partir del reporte de TTOK-05).
- **Casos de Kiwi relacionados:** `TOK-009-C16` (id 392) y `TOK-009-C17` (id 393),
  `PROPOSED`, en el plan **30** «PBI-009 - Defaults del CLI y total».
- **Reportado por:** Desarrollo, sesión TTOK-05 (Claude Fable 5.1), reproducido tres veces
- **Fecha de detección:** 2026-09-27

## 2. Contexto reproducible

- **Build/commit:** `808b009` (`main`) y `d9c42ff` (rama `worktree-ttok04-pbi009-ronda2`). También `v1.0.0` en PyPI: **está en producción**.
- **Canal de QA:** ninguno. Lo encontró Desarrollo corriendo la herramienta con la salida capturada.
- **Workspace:** `C:\IA\Projects\Claude-Tokenizer`
- **Precondiciones:** Windows; Python 3.12.13 del `.venv`; `PYTHONUTF8` **no** definida (es el estado por defecto de la máquina); la salida estándar redirigida a archivo o pipe; un Markdown con al menos un título con un carácter fuera de cp1252. `C:\Users\fferdgelis\.claude\claude.md` cumple (tiene `→`, `«`, `»`, `—` en títulos).

## 3. Reproducción

Desde Git Bash o PowerShell, con la salida redirigida:

```
uv run tokmd "C:\Users\fferdgelis\.claude\claude.md" --platform claude-code --depth 1 > salida.txt
```

Resultado por formato (misma corrida, `2>err.txt`):

| `--format` | Resultado |
|---|---|
| `table` | `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 159` |
| `md` | `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 165` |
| `csv` | `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 182` |
| `json` | OK (`json.dumps` escapa `→` como `\u2192`) |

Con `PYTHONUTF8=1` en el entorno los cuatro formatos salen bien. En una consola
interactiva de Windows **no** falla, porque Python escribe a la consola en
UTF-16 por la API nativa y `sys.stdout.encoding` es `utf-8`; por eso Fabián
pudo ver la tabla en pantalla al reportar BUG-008 y este bug no apareció antes.

## 4. Impacto

- **Cualquier uso no interactivo revienta** con un archivo como el del owner:
  guardar la medición a un archivo, encadenarla con otro comando, correrla
  desde un script o desde CI en Windows. Es el uso que tiene sentido para una
  herramienta de medición.
- **La salida vacía deja un archivo de medición a medias**: `salida.txt` queda
  con las filas anteriores al primer título con `→` y nada más, sin que el
  archivo diga que está incompleto (el traceback va a `stderr`).
- Todo Markdown en castellano con tipografía normal («», —, →) lo dispara; los
  17 documentos de `docs/` de este repo tienen esos caracteres.

## 5. Evidencia

Traceback completo (formato `table`):

```
  File "C:\IA\Projects\Claude-Tokenizer\src\tokmd\cli.py", line 163, in main
    click.echo(render(root, count_fn, fmt=fmt, depth=depth, sort=sort))
  File "C:\IA\Projects\Claude-Tokenizer\.venv\Lib\site-packages\click\utils.py", line 345, in echo
    file.write(out)  # type: ignore
  File "C:\Users\fferdgelis\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 159: character maps to <undefined>
```

Estado de `stdout` en la reproducción:

```
$ uv run python -c "import sys; print(sys.version.split()[0], sys.stdout.encoding, sys.stdout.isatty())"
3.12.13 cp1252 False
```

## 6. Causa

`src/tokmd/cli.py:163` escribe con `click.echo`, que va a `sys.stdout` tal
cual está configurado. En Windows, cuando `stdout` no es una consola, Python
3.12 lo abre con la página de códigos ANSI del sistema (`cp1252` en esta
máquina) y `errors="strict"`. La lectura del archivo sí está bien
(`cli.py:161`, `encoding="utf-8"` explícito); el problema es sólo la
**escritura**.

`json` se salva por casualidad: `json.dumps` usa `ensure_ascii=True` por
defecto y convierte todo lo no ASCII a `\uXXXX` antes de que llegue a `stdout`.

## 7. Corrección

> **Implementada el 2026-09-27, commit `421b8cb`.** `sys.stdout`/`sys.stderr`
> reconfigurados a UTF-8 al importar `cli.py` (la opción propuesta abajo, sin
> `errors="replace"`). Detalle completo en el PBI-009 y su dev-log.


**Sin implementar.** Propuesta, para decidir dónde entra (PBI-009 o PBI
propio):

1. Al arrancar el CLI, fijar la salida a UTF-8 sin depender del entorno:

   ```python
   for stream in (sys.stdout, sys.stderr):
       if hasattr(stream, "reconfigure"):
           stream.reconfigure(encoding="utf-8")
   ```

   Es la regla del proyecto propuesta en
   `[[20260927-respuestas-14-preguntas-tokenizacion]]`, pregunta 10: **todo
   archivo se lee como UTF-8 y toda salida se escribe como UTF-8**, en las dos
   puntas.
2. Caso de prueba que lo cace: un archivo con un título `## Flecha → «comillas» — guion`,
   corrido con `stdout` capturado (que es como lo corre `CliRunner` de click
   **si** se le fuerza cp1252; si no, hay que correrlo por `subprocess` con
   `PYTHONIOENCODING=cp1252` para reproducir el entorno) y los cuatro formatos.
   Sin ese caso el arreglo no se puede verificar en Linux, donde el bug no
   existe.

**No se propone** `errors="replace"`: reemplazar un carácter por `?` en la
salida haría que la herramienta mienta en silencio, que es peor que
reventar (el caso de `ttok` leyendo `stdin` en cp1252 dio 13.075 tokens en vez
de 11.660 sin ningún error — está en
`[[20260927-count-tokens-api-vs-tokmd-ctok-ttok]]`, sección 4).

## 8. Verificación independiente

- **Arreglado el 2026-09-27**, por Desarrollo (Claude): `sys.stdout`/`stderr`
  reconfigurados a UTF-8 al importar `cli.py`.
- **Registrado en Kiwi el 2026-09-27** (Bug `pk=13`), con los casos de regresión
  `TOK-009-C16` y `TOK-009-C17` cargados como `PROPOSED` **antes** de arreglar
  nada.
- **QA independiente: `PASSED`.** Kimi K3/OpenCode, read-only, sobre el commit
  `421b8cb`. Test Run **70**, Test Execution **275** y **276**, linkeadas a
  este Bug. Las cuatro variantes de `--format` (`table`/`md`/`csv`/`json`)
  corrieron en verde. Log crudo:
  `docs/handoff/qa/fase-6-pbi009-kimi-k3.txt`.
- **Estado del registro Bug:** `cerrado` en Kiwi (2026-09-27). `Bug.update`
  no existe en la API, así que el cierre se hizo por la interfaz web
  (`/bugs/13/`, acción "Close" con comentario), a pedido de Fabián.
