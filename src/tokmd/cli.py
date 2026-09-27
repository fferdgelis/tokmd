"""`tokmd FILE [--platform <p>]`: resolve the tokenizer, print the total.

ADR-001: platforms map to a tokenizer + parameter without the user having to
know which one. `--tokenizer` (an explicit "claude"/"openai" choice) always
wins over whatever `--platform` would have picked — stated in PBI-004's risk
section, so a caller who knows better than the platform mapping is never
blocked by it, including on `antigravity` (not implemented as a platform,
but still overridable).

PBI-009: `--platform` now defaults to `"claude-code"` (tokmd exists for
Claude Code users first). The default output is just the whole document's
total — one line, no breakdown — computed with `count_claude_total`/
`count_openai` directly on the raw source text, never by summing sections
(ADR-007: summing undercounts by one `frame`). `--sections` restores the
old section-by-section breakdown via `render.render`, root row and total
included.

BUG-011: `sys.stdout`/`sys.stderr` are reconfigured to UTF-8 unconditionally
at import time — on Windows, a non-console stdout (a redirected file or
pipe) otherwise opens in the platform's ANSI code page (`cp1252` on this
project's machine) with `errors="strict"`, so any title with a character
outside that code page (`→`, `«`, `»`, `—`, ...) crashes with
`UnicodeEncodeError` before a single line is written. `reconfigure` is a
no-op on platforms/streams that don't support it (falls back silently via
the `hasattr` guard) and never touches file *reading*, which was already
explicit UTF-8.

`--verify` (PBI-008): cross-checks against Anthropic's real API instead of
ctok's offline reconstruction. Only valid when the resolved tokenizer is
"claude" — `verify.py`'s `count_tokens` endpoint has no OpenAI counterpart
here. `get_client`/`measure_frame`/`count_verified` are imported by name
(not the module) so tests can `monkeypatch.setattr("tokmd.cli.get_client",
...)` without a real `ANTHROPIC_API_KEY` or network call — same pattern
`verify.py`'s own tests use against a fake client.
"""
from __future__ import annotations

import json
import sys
from functools import partial
import importlib.metadata
from pathlib import Path

import click

from .render import render
from .sections import parse_sections
from .tokenizers import FRAME, count_claude, count_claude_total, count_openai
from .verify import MissingApiKeyError, count_verified, get_client, measure_frame

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

PLATFORMS = ["claude-code", "codex", "opencode", "antigravity"]

# Real Anthropic model id for --verify's API calls — independent of
# --claude-family, which names ctok's own offline version strings ("3.0",
# "4.7", "4.8"), not a real model id `count_tokens` accepts.
DEFAULT_VERIFY_MODEL = "claude-sonnet-5"


class PlatformNotSupportedError(click.ClickException):
    """A recognized platform with no tokenizer yet (e.g. antigravity)."""

    exit_code = 2


def _resolve_opencode(model: str | None, claude_family: str | None, encoding: str | None) -> tuple[str, str]:
    if not model:
        raise click.UsageError("--model is required when --platform is opencode")
    if model.startswith("claude"):
        return "claude", claude_family or "4.8"
    if model.startswith("gpt"):
        return "openai", encoding or "o200k_base"
    raise click.UsageError(f"Unrecognized --model for --platform opencode: {model!r}")


def resolve_tokenizer(
    platform: str,
    model: str | None,
    tokenizer: str | None,
    claude_family: str | None,
    encoding: str | None,
) -> tuple[str, str]:
    """Return (kind, param): kind is "claude" or "openai", param is what
    to pass to `count_claude`/`count_openai` respectively.

    Raises `click.UsageError` for a bad combination of flags (e.g. missing
    `--model` for `--platform opencode`), or `PlatformNotSupportedError`
    for a platform with no tokenizer yet.
    """
    if tokenizer == "claude":
        return "claude", claude_family or "4.8"
    if tokenizer == "openai":
        return "openai", encoding or "o200k_base"

    if platform == "claude-code":
        return "claude", claude_family or "4.8"
    if platform == "codex":
        return "openai", encoding or "o200k_base"
    if platform == "opencode":
        return _resolve_opencode(model, claude_family, encoding)
    raise PlatformNotSupportedError("Gemini tokenizer: planned for 1.1")


@click.command()
@click.version_option(version=importlib.metadata.version("tokmd"), message="%(version)s")
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--platform",
    type=click.Choice(PLATFORMS),
    default="claude-code",
    help="Default: claude-code.",
)
@click.option("--model", default=None, help="Model name, required when --platform is opencode.")
@click.option(
    "--tokenizer",
    type=click.Choice(["claude", "openai"]),
    default=None,
    help="Override --platform's tokenizer choice.",
)
@click.option("--claude-family", default=None, help='Claude family override ("3.0", "4.7", "4.8").')
@click.option("--encoding", default=None, help='tiktoken encoding override ("o200k_base", "cl100k_base").')
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["table", "md", "json", "csv"]),
    default="table",
    help="Output format.",
)
@click.option("--depth", type=int, default=None, help="Only show sections up to this heading level.")
@click.option(
    "--sort",
    type=click.Choice(["document", "tokens"]),
    default="document",
    help="Row order: original document order, or siblings by tokens descending.",
)
@click.option(
    "--sections",
    "sections",
    is_flag=True,
    default=False,
    help="Print the section-by-section breakdown (with the total) instead of just the total.",
)
@click.option(
    "--verify",
    "verify",
    is_flag=True,
    default=False,
    help=(
        "Cross-check counts against Anthropic's real API instead of ctok's offline "
        "count. Needs ANTHROPIC_API_KEY in the environment. Only valid when the "
        "resolved tokenizer is Claude (platform claude-code, --tokenizer claude, or "
        "opencode with a claude* --model). Uses --model as the API model id if given, "
        "else claude-sonnet-5."
    ),
)
def main(
    file: Path,
    platform: str,
    model: str | None,
    tokenizer: str | None,
    claude_family: str | None,
    encoding: str | None,
    fmt: str,
    depth: int | None,
    sort: str,
    sections: bool,
    verify: bool,
) -> None:
    kind, param = resolve_tokenizer(platform, model, tokenizer, claude_family, encoding)
    text = file.read_text(encoding="utf-8")

    if verify:
        if kind != "claude":
            raise click.UsageError("--verify only supports the Claude tokenizer, not OpenAI.")
        try:
            client = get_client()
        except MissingApiKeyError as exc:
            raise click.ClickException(str(exc)) from exc
        verify_model = model or DEFAULT_VERIFY_MODEL
        frame_value = measure_frame(client, verify_model)
        # BUG-001 (same root cause, second call site): the real API rejects
        # ANY whitespace-only text content block, not just measure_frame's
        # internal probe — a section whose own_text is blank lines (a
        # heading directly followed by another heading) hits the same 400.
        # render.py already treats a falsy own_text as 0 tokens without
        # calling count_fn; this extends "empty" to "no non-whitespace
        # content" for the real-API path specifically, without touching
        # render.py's contract for the offline (ctok/tiktoken) paths, which
        # never had this problem.
        count_fn = lambda section_text: (  # noqa: E731
            count_verified(client, section_text, verify_model, frame_value) if section_text.strip() else 0
        )
        # PBI-009/ADR-007: the document's real total is its own single,
        # whole-text measurement — never derived by summing sections (that
        # undercounts by one frame's worth) — same principle as the offline
        # path below, just against the real API instead of ctok.
        doc_total = count_verified(client, text, verify_model, frame_value) if text.strip() else 0
    elif kind == "claude":
        count_fn = partial(count_claude, family=param)
        # AC-09: an empty file is 0 tokens — count_claude_total("", family)
        # would return that family's raw empty-string cost instead (e.g. 6
        # for "4.8"), which is the frame, not "how many tokens is this
        # file", so it's special-cased rather than routed through it.
        doc_total = count_claude_total(text, family=param) if text.strip() else 0
        frame_value = FRAME[param]
    else:
        count_fn = partial(count_openai, encoding=param)
        # OpenAI/tiktoken has no per-message frame to net out (tokenizers.py:
        # "exact partition, additive across sections with zero drift"), so
        # the whole-text count IS the sum of sections already — no separate
        # "total" function needed, and no frame to report.
        doc_total = count_openai(text, encoding=param)
        frame_value = 0

    root = parse_sections(text)
    breakdown = render(root, count_fn, total=doc_total, frame=frame_value, fmt=fmt, depth=depth, sort=sort)

    if sections:
        click.echo(breakdown)
        click.echo(doc_total)
    elif fmt == "json":
        click.echo(json.dumps({"total": doc_total}))
    else:
        click.echo(doc_total)
