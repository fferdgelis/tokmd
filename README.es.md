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

Tomando un documento Markdown de este mismo repositorio (`docs/ADR/ADR-004-empaquetado-y-publicacion.md`), ejecutamos `tokmd` con el tokenizador de Claude:

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --platform claude-code
(front matter): 368
  ADR-004 — Empaquetado y publicación: nombre, licencia y canal: 868
    Historial de modificaciones: 172
    Estado: 44
    Contexto: 130
    Decisiones: 394
    Consecuencias: 64
    Verificación y reversibilidad: 64
```

Aspectos a destacar:
- El conteo de tokens de cada sección incluye su propio texto más el de todas las subsecciones anidadas debajo (por ejemplo, `ADR-004` acumula 868 tokens en total).
- El front matter es identificado y medido como su propio bloque inicial (368 tokens).

---

## Uso

```bash
tokmd [OPCIONES] ARCHIVO
```

### Plataformas

La opción `--platform` resuelve automáticamente el tokenizador y la codificación adecuada para el entorno objetivo:

| Plataforma | Motor tokenizador | Modelo / codificación por defecto |
|---|---|---|
| `claude-code` | Anthropic Claude (`ctok`) | Familia Claude 3.5 / 4.x (`4.8`) |
| `codex` | OpenAI (`tiktoken`) | `o200k_base` (GPT-4o, GPT-5) |
| `opencode` | Resuelto dinámicamente | Requiere `--model` (ej. `--model claude-opus-5` o `--model gpt-5`) |
| `antigravity` | *Planificado para v1.1* | Se puede sobreescribir con `--tokenizer` |

### Opciones del comando

- `--platform [claude-code|codex|opencode|antigravity]` *(requerido)*: Plataforma destino.
- `--model TEXT`: Nombre del modelo, requerido cuando se usa `--platform opencode`.
- `--tokenizer [claude|openai]`: Sobreescribe la elección de tokenizador de la plataforma.
- `--format [table|md|json|csv]`: Formato de salida (por defecto: `table`).
  - `table`: Jerarquía indentada en texto plano.
  - `md`: Lista anidada con viñetas Markdown.
  - `json`: Arreglo JSON estructurado con `title`, `level` y `tokens` acumulados.
  - `csv`: Formato tabular CSV con encabezados `level,title,tokens`.
- `--depth INTEGER`: Muestra secciones sólo hasta este nivel de encabezado. Las secciones más profundas quedan sumadas en sus padres.
- `--sort [document|tokens]`: Orden de filas: orden original del documento (`document`, por defecto) o hermanos ordenados de mayor a menor por tokens acumulados (`tokens`).
- `--claude-family TEXT`: Sobreescribe la familia de Claude (`"3.0"`, `"4.7"`, `"4.8"`).
- `--encoding TEXT`: Sobreescribe la codificación de `tiktoken` (ej. `"o200k_base"`, `"cl100k_base"`).
- `--version`: Imprime la versión instalada y termina.
- `--help`: Muestra la ayuda y opciones disponibles.

---

## Ejemplos Avanzados

### Filtrar profundidad (`--depth`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --platform claude-code --depth 1
(front matter): 368
  ADR-004 — Empaquetado y publicación: nombre, licencia y canal: 868
```

### Ordenar por cantidad de tokens (`--sort tokens`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --platform claude-code --sort tokens
  ADR-004 — Empaquetado y publicación: nombre, licencia y canal: 868
    Decisiones: 394
    Historial de modificaciones: 172
    Contexto: 130
    Consecuencias: 64
    Verificación y reversibilidad: 64
    Estado: 44
(front matter): 368
```

### Salida en formato Markdown (`--format md`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --platform claude-code --format md
- (front matter): 368
  - ADR-004 — Empaquetado y publicación: nombre, licencia y canal: 868
    - Historial de modificaciones: 172
    - Estado: 44
    - Contexto: 130
    - Decisiones: 394
    - Consecuencias: 64
    - Verificación y reversibilidad: 64
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
