# tokmd

[![CI](https://github.com/fferdgelis/tokmd/actions/workflows/ci.yml/badge.svg)](https://github.com/fferdgelis/tokmd/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tokmd.svg)](https://pypi.org/project/tokmd/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

*Disponible también en [English](README.md).*

`tokmd` es una herramienta de línea de comandos que cuenta tokens por sección de un archivo Markdown, utilizando el tokenizador correspondiente según la plataforma de IA de destino (Claude, OpenAI y más).

A diferencia de los contadores planos tradicionales, `tokmd` analiza documentos Markdown construyendo un árbol jerárquico de secciones a partir de los encabezados ATX (`#` a `######`) y el front matter YAML. Los conteos de tokens se acumulan a lo largo del árbol tal como lo hace `du` con los directorios: limitar la profundidad de visualización nunca pierde visibilidad sobre los tokens anidados.

---

## Instalación

### Desde PyPI (una vez publicado)

Podés ejecutarlo directamente sin instalación previa usando [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx tokmd --help
```

O instalarlo globalmente con `pip`:

```bash
pip install tokmd
```

### Desde el código fuente (desarrollo)

Cloná el repositorio y ejecutalo con [`uv`](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/fferdgelis/tokmd.git
cd tokmd
uv run tokmd --help
```

---

## Ejemplo Rápido (Salida Real)

Por defecto, `tokmd` imprime sólo el total de tokens del documento entero — una línea, sin configuración previa (`--platform` tiene por defecto `claude-code`):

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md
1322
```

Con `--sections` se obtiene el desglose sección por sección (en este ejemplo, `docs/ADR/ADR-004-empaquetado-y-publicacion.md` de este mismo repositorio):

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --sections
(document): total=1322
├─ (front matter): own=369 total=369
  └─ ADR-004 — Empaquetado y publicación: nombre, licencia y canal: own=30 total=948
       ├─ Historial de modificaciones: own=183 total=183
       ├─ Estado: own=49 total=49
       ├─ Contexto: own=136 total=136
       ├─ Decisiones: own=401 total=401
       ├─ Consecuencias: own=72 total=72
       └─ Verificación y reversibilidad: own=77 total=77

boundary drift: +0
1322
```

Aspectos a destacar:
- Cada fila muestra dos números: `own` (su propio texto solo) y `total` (propio más todos los descendientes). Una sección cuyo encabezado tiene contenido pero cuyo cuerpo está vacío ya no es indistinguible de una sección genuinamente vacía — la salida de una sola columna anterior no podía diferenciarlas.
- La fila raíz (`(document)`) lleva el total real del archivo completo, calculado directamente sobre el texto crudo — nunca sumando el árbol, que subcontaría.
- `boundary drift` informa cualquier diferencia entre el árbol y el total real. En un documento sano da `+0`; si no, algo en el parser o el tokenizador no concuerda con el conteo del archivo completo.

---

## Uso

```bash
tokmd [OPCIONES] ARCHIVO
```

### Plataformas

La opción `--platform` resuelve automáticamente el tokenizador y la codificación adecuada para el entorno objetivo. Por defecto es `claude-code`, porque `tokmd` existe primero para usuarios de Claude Code.

| Plataforma | Motor tokenizador | Modelo / codificación por defecto |
|---|---|---|
| `claude-code` (por defecto) | Anthropic Claude (`ctok`) | Familia Claude 3.5 / 4.x (`4.8`) |
| `codex` | OpenAI (`tiktoken`) | `o200k_base` (GPT-4o, GPT-5) |
| `opencode` | Resuelto dinámicamente | Requiere `--model` (ej. `--model claude-opus-5` o `--model gpt-5`) |
| `antigravity` | *Planificado para v1.1* | Se puede sobreescribir con `--tokenizer` |

### Opciones del comando

- `--platform [claude-code|codex|opencode|antigravity]`: Plataforma destino (por defecto: `claude-code`).
- `--sections`: Imprime el desglose sección por sección (fila raíz, columnas `own`/`total`, `boundary drift`) en vez de sólo el total.
- `--model TEXT`: Nombre del modelo, requerido cuando se usa `--platform opencode`.
- `--tokenizer [claude|openai]`: Sobreescribe la elección de tokenizador de la plataforma.
- `--format [table|md|json|csv]`: Formato de salida para `--sections` (por defecto: `table`).
  - `table`: Árbol con conectores (`├─`/`└─`) y pie con `boundary drift`.
  - `md`: Lista anidada con viñetas Markdown, incluye fila raíz.
  - `json`: Un único objeto `{"total", "drift", "rows"}`, cada fila con `title`, `level`, `own`, `total`.
  - `csv`: CSV con encabezados `level,title,own,total`, fila raíz primero.
- `--depth INTEGER`: Limita el desglose de `--sections` a secciones hasta este nivel de encabezado. Las secciones más profundas quedan sumadas en sus padres (la fila raíz siempre se muestra, sin importar la profundidad).
- `--sort [document|tokens]`: Orden de filas: orden original del documento (`document`, por defecto) o hermanos ordenados de mayor a menor por tokens acumulados (`tokens`).
- `--claude-family TEXT`: Sobreescribe la familia de Claude (`"3.0"`, `"4.7"`, `"4.8"`).
- `--encoding TEXT`: Sobreescribe la codificación de `tiktoken` (ej. `"o200k_base"`, `"cl100k_base"`).
- `--verify`: Contrasta el total contra la API real de Anthropic en vez de la reconstrucción offline de `ctok`. Necesita `ANTHROPIC_API_KEY` en el entorno. Sólo válido cuando el tokenizador resuelto es Claude.
- `--version`: Imprime la versión instalada y termina.
- `--help`: Muestra la ayuda y opciones disponibles.

---

## Ejemplos Avanzados

### Filtrar profundidad (`--depth`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --sections --depth 1
(document): total=1322
├─ (front matter): own=369 total=369
  └─ ADR-004 — Empaquetado y publicación: nombre, licencia y canal: own=30 total=948

boundary drift: +0
1322
```

### Ordenar por cantidad de tokens (`--sort tokens`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --sections --sort tokens
(document): total=1322
  ├─ ADR-004 — Empaquetado y publicación: nombre, licencia y canal: own=30 total=948
    │  ├─ Decisiones: own=401 total=401
    │  ├─ Historial de modificaciones: own=183 total=183
    │  ├─ Contexto: own=136 total=136
    │  ├─ Verificación y reversibilidad: own=77 total=77
    │  ├─ Consecuencias: own=72 total=72
    │  └─ Estado: own=49 total=49
└─ (front matter): own=369 total=369

boundary drift: +0
1322
```

### Salida en formato Markdown (`--format md`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --sections --format md
- (document): own=0 total=1322
- (front matter): own=369 total=369
  - ADR-004 — Empaquetado y publicación: nombre, licencia y canal: own=30 total=948
    - Historial de modificaciones: own=183 total=183
    - Estado: own=49 total=49
    - Contexto: own=136 total=136
    - Decisiones: own=401 total=401
    - Consecuencias: own=72 total=72
    - Verificación y reversibilidad: own=77 total=77
```

---

## Créditos y Agradecimientos

`tokmd` se apoya en el trabajo de la comunidad de software libre:

- **[`ctok`](https://github.com/sanderland/ctok)** de Sander Land (Licencia MIT): Utilizado para la reconstrucción offline y conteo de tokens con el tokenizador de Anthropic Claude, sin necesidad de claves de API ni conexión de red. `tokmd` no está afiliado con Anthropic ni con el proyecto `ctok`.
- **[`ttok`](https://github.com/simonw/ttok)** de Simon Willison (Licencia Apache 2.0): El diseño de la interfaz de línea de comandos y el enfoque centrado en plataformas de `tokmd` están inspirados en `ttok`.
- **[`tiktoken`](https://github.com/openai/tiktoken)** de OpenAI (Licencia MIT): Librería BPE de alta velocidad utilizada para el conteo de tokens de modelos OpenAI.

Para más contexto de arquitectura y decisiones, consultar el archivo `NOTICE` y `docs/ADR/ADR-001-eleccion-de-motores-de-tokenizacion.md`.

---

## Licencia

Este proyecto está distribuido bajo la licencia Apache License, Versión 2.0. Ver [LICENSE](LICENSE) para más información.

Copyright (c) 2026 Fabián Ferdgelis.
