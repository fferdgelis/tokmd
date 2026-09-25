# tokmd

[![CI](https://github.com/fferdgelis/tokmd/actions/workflows/ci.yml/badge.svg)](https://github.com/fferdgelis/tokmd/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tokmd.svg)](https://pypi.org/project/tokmd/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

*Read this in [Español](README.es.md).*

`tokmd` is a command-line tool that counts tokens per section of a Markdown file, using the right tokenizer for your target AI platform (Claude, OpenAI, and more).

Unlike flat counters, `tokmd` parses Markdown documents into a hierarchical section tree based on ATX headings (`#` through `######`) and YAML front matter. Token counts roll up through the hierarchy just like `du` rolls up directory sizes: limiting display depth never loses token visibility.

---

## Installation

### From PyPI (once published)

Run directly without manual installation using [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```bash
uvx tokmd --help
```

Or install via `pip`:

```bash
pip install tokmd
```

### From source (development)

Clone the repository and run with [`uv`](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/fferdgelis/tokmd.git
cd tokmd
uv run tokmd --help
```

---

## Quick Example (Real Output)

Given a Markdown document (in this example, `docs/ADR/ADR-004-empaquetado-y-publicacion.md` from this repository), running `tokmd` with the Claude tokenizer:

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

Notice that:
- Each section's token count includes its own text plus all nested subsections beneath it (e.g. `ADR-004` accumulates 868 tokens total).
- Front matter is identified and measured as its own block (368 tokens).

---

## Usage

```bash
tokmd [OPTIONS] FILE
```

### Platforms

The `--platform` option automatically selects the appropriate tokenizer and encoding for your target environment:

| Platform | Tokenizer engine | Default model / encoding |
|---|---|---|
| `claude-code` | Anthropic Claude (`ctok`) | Claude 3.5 / 4.x family (`4.8`) |
| `codex` | OpenAI (`tiktoken`) | `o200k_base` (GPT-4o, GPT-5) |
| `opencode` | Dynamically resolved | Requires `--model` (e.g. `--model claude-opus-5` or `--model gpt-5`) |
| `antigravity` | *Planned for v1.1* | Can be overridden using `--tokenizer` |

### Command Options

- `--platform [claude-code|codex|opencode|antigravity]` *(required)*: Target platform.
- `--model TEXT`: Model identifier, required when `--platform opencode` is selected.
- `--tokenizer [claude|openai]`: Override the platform's default tokenizer.
- `--format [table|md|json|csv]`: Output format (default: `table`).
  - `table`: Indented plain text hierarchy.
  - `md`: Indented Markdown bullet list.
  - `json`: JSON array with `title`, `level`, and accumulated `tokens`.
  - `csv`: CSV format with headers `level,title,tokens`.
- `--depth INTEGER`: Limit output to sections up to this heading level. Deeper sections are rolled up into their parent totals.
- `--sort [document|tokens]`: Order rows by original document order (`document`, default) or sort sibling sections by descending accumulated tokens (`tokens`).
- `--claude-family TEXT`: Override Claude tokenizer family (`"3.0"`, `"4.7"`, `"4.8"`).
- `--encoding TEXT`: Override `tiktoken` encoding (e.g. `"o200k_base"`, `"cl100k_base"`).
- `--version`: Show version and exit.
- `--help`: Show CLI help and options.

---

## Advanced Examples

### Limiting depth (`--depth`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --platform claude-code --depth 1
(front matter): 368
  ADR-004 — Empaquetado y publicación: nombre, licencia y canal: 868
```

### Sorting by token count (`--sort tokens`)

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

### Markdown list output (`--format md`)

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

## Credits & Acknowledgements

`tokmd` builds upon and is inspired by the work of the open-source community:

- **[`ctok`](https://github.com/sanderland/ctok)** by Sander Land (MIT License): Used for offline reconstruction and counting with Anthropic Claude's tokenizer without requiring API keys or network access. `tokmd` is not affiliated with Anthropic or the `ctok` project.
- **[`ttok`](https://github.com/simonw/ttok)** by Simon Willison (Apache License 2.0): The command-line interface design and platform-first philosophy of `tokmd` were inspired by `ttok`.
- **[`tiktoken`](https://github.com/openai/tiktoken)** by OpenAI (MIT License): Fast BPE tokenizer library used for OpenAI model token counts.

For further architectural context, see `NOTICE` and `docs/ADR/ADR-001-eleccion-de-motores-de-tokenizacion.md`.

---

## License

This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 Fabián Ferdgelis.
