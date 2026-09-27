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

By default, `tokmd` prints just the whole document's token total — one line, no setup required (`--platform` defaults to `claude-code`):

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md
1322
```

Pass `--sections` for the section-by-section breakdown (in this example, `docs/ADR/ADR-004-empaquetado-y-publicacion.md` from this repository):

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

Notice that:
- Every row shows two numbers: `own` (its own text alone) and `total` (own plus every descendant's). A section whose heading has content but whose body is empty is no longer indistinguishable from a genuinely empty section — the old single-column output couldn't tell them apart.
- The root row (`(document)`) carries the whole file's real total, computed directly from the raw source — never by summing the tree, which would undercount.
- `boundary drift` reports any mismatch between the tree and the real total. It reads `+0` on a healthy document; if it doesn't, something in the parser or tokenizer disagrees with the whole-file count.

---

## Usage

```bash
tokmd [OPTIONS] FILE
```

### Platforms

The `--platform` option automatically selects the appropriate tokenizer and encoding for your target environment. It defaults to `claude-code`, since `tokmd` exists for Claude Code users first.

| Platform | Tokenizer engine | Default model / encoding |
|---|---|---|
| `claude-code` (default) | Anthropic Claude (`ctok`) | Claude 3.5 / 4.x family (`4.8`) |
| `codex` | OpenAI (`tiktoken`) | `o200k_base` (GPT-4o, GPT-5) |
| `opencode` | Dynamically resolved | Requires `--model` (e.g. `--model claude-opus-5` or `--model gpt-5`) |
| `antigravity` | *Planned for v1.1* | Can be overridden using `--tokenizer` |

### Command Options

- `--platform [claude-code|codex|opencode|antigravity]`: Target platform (default: `claude-code`).
- `--sections`: Print the section-by-section breakdown (root row, `own`/`total` columns, `boundary drift`) instead of just the total.
- `--model TEXT`: Model identifier, required when `--platform opencode` is selected.
- `--tokenizer [claude|openai]`: Override the platform's default tokenizer.
- `--format [table|md|json|csv]`: Output format for `--sections` (default: `table`).
  - `table`: Tree with connectors (`├─`/`└─`) and a `boundary drift` footer.
  - `md`: Indented Markdown bullet list, root row included.
  - `json`: A single object `{"total", "drift", "rows"}`, each row with `title`, `level`, `own`, `total`.
  - `csv`: CSV with headers `level,title,own,total`, root row first.
- `--depth INTEGER`: Limit the `--sections` breakdown to sections up to this heading level. Deeper sections are rolled up into their parent totals (the root row always shows regardless of depth).
- `--sort [document|tokens]`: Order rows by original document order (`document`, default) or sort sibling sections by descending accumulated tokens (`tokens`).
- `--claude-family TEXT`: Override Claude tokenizer family (`"3.0"`, `"4.7"`, `"4.8"`).
- `--encoding TEXT`: Override `tiktoken` encoding (e.g. `"o200k_base"`, `"cl100k_base"`).
- `--verify`: Cross-check the total against Anthropic's real API instead of `ctok`'s offline reconstruction. Needs `ANTHROPIC_API_KEY` in the environment. Only valid when the resolved tokenizer is Claude.
- `--version`: Show version and exit.
- `--help`: Show CLI help and options.

---

## Advanced Examples

### Limiting depth (`--depth`)

```bash
$ tokmd docs/ADR/ADR-004-empaquetado-y-publicacion.md --sections --depth 1
(document): total=1322
├─ (front matter): own=369 total=369
  └─ ADR-004 — Empaquetado y publicación: nombre, licencia y canal: own=30 total=948

boundary drift: +0
1322
```

### Sorting by token count (`--sort tokens`)

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

### Markdown list output (`--format md`)

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
