# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-09-27

### Changed
- **BREAKING:** `--platform` is now optional; it defaults to `claude-code`. Running `tokmd file.md` with no flags now prints a single number — the file's total token count — instead of requiring `--platform` and printing the section breakdown (PBI-009, AC-01/AC-03/AC-04).
- **BREAKING:** The default output is the whole file counted in a single pass (frame included), not the sum of the section rows. The two used to differ by the message frame counted once per section instead of once per document — see `ADR-007` (PBI-009, AC-02).
- The section-by-section breakdown moves behind the new `--sections` flag (PBI-009, AC-05).

### Added
- `--sections`: each row now reports both `own` and `total` token counts, plus a root row for the whole document and a `boundary drift: ±N` line when the row sum doesn't match the single-pass total (PBI-009, AC-12/AC-13/AC-15/AC-16; fixes `BUG-009` and `BUG-010`).
- Tree connectors (`├─`, `└─`, `│`) in the `--sections` output, replacing plain indentation.

### Fixed
- **BUG-008:** a section's own heading text (`## Title`) was never counted anywhere — every section's token count only covered the body below the heading line. Headings with no body (e.g. `#` used as a comment) used to report `0` tokens even though the heading itself costs tokens.
- **BUG-011:** on Windows, redirecting output to a file or pipe (not an interactive console) crashed with `UnicodeEncodeError` if any section title had a character outside cp1252 (`→`, `«`, `»`, `—`), in the `table`, `md`, and `csv` formats. Output is now forced to UTF-8.
- `ADR-002`'s claimed per-message frame cost was measured as 6 tokens for the Claude `4.8` family; the real cost per chunk boundary is 5, confirmed against `POST /v1/messages/count_tokens` (`ADR-007`).

Verified against the maintainer's own `~/.claude/CLAUDE.md` (38,185 bytes): `tokmd` reports `17381`, exactly matching Anthropic's `count_tokens` endpoint for `claude-sonnet-5` / `claude-opus-5` / `claude-opus-4-8`; `--sections` reports `boundary drift: +0`. Independent QA (Kimi K3 via OpenCode, read-only): 17/17 test cases passed (Kiwi Test Run 70).

## [1.0.0] - 2026-09-25

### Added
- **Section Parser** (`src/tokmd/sections.py`): Builds a hierarchical tree of markdown sections based on ATX headings (`#` through `######`) and YAML front matter (PBI-001).
- **Claude Tokenizer** (`src/tokmd/tokenizers.py`): Offline token counting for Anthropic Claude models using `ctok`, supporting Claude families including 3.0, 4.7, and 4.8 (PBI-002).
- **OpenAI Tokenizer** (`src/tokmd/tokenizers.py`): Fast token counting for OpenAI models using `tiktoken`, supporting `o200k_base` (GPT-4o, GPT-5) and `cl100k_base` encodings (PBI-003).
- **Command-Line Interface** (`src/tokmd/cli.py`): Unified Click-based CLI with `--platform` mapping (`claude-code`, `codex`, `opencode`, `antigravity`), `--model` flag, and explicit `--tokenizer` override support (PBI-004).
- **Multi-Format Rendering** (`src/tokmd/render.py`): Section tree roll-up rendering with support for `table`, `md`, `json`, and `csv` formats, depth filtering (`--depth`), and token sorting (`--sort tokens`) (PBI-005).
- **Anthropic API Verification Library** (`src/tokmd/verify.py`): Live token verification and message framing measurement against Anthropic's real API `count_tokens` endpoint (PBI-006).
- **Version Option** (`src/tokmd/cli.py`): Added `--version` CLI flag to report package version dynamically from installed metadata (PBI-007).
- **Packaging and CI/CD**:
  - GitHub Actions CI workflow (`.github/workflows/ci.yml`) running `pytest` across Ubuntu and Windows on Python 3.12 and 3.13 via `uv` (PBI-007).
  - GitHub Actions PyPI publishing workflow (`.github/workflows/publish.yml`) configured for PyPI Trusted Publishing via OIDC on `v*` tag push (PBI-007).
- **Documentation**: Comprehensive English (`README.md`) and Spanish (`README.es.md`) guides with real output examples and open-source acknowledgements (PBI-007).
