# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
