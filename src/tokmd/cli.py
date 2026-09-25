"""`tokmd FILE --platform <p>`: resolve the tokenizer, render the section tree.

ADR-001: platforms map to a tokenizer + parameter without the user having to
know which one. `--tokenizer` (an explicit "claude"/"openai" choice) always
wins over whatever `--platform` would have picked — stated in PBI-004's risk
section, so a caller who knows better than the platform mapping is never
blocked by it, including on `antigravity` (not implemented as a platform,
but still overridable). `--format`/`--depth`/`--sort` (PBI-005) are thin
pass-throughs to `render.render`; this module's own job stops at resolving
"which tokenizer" and building the `count_fn` closure it's called with.
"""
from __future__ import annotations

from functools import partial
from pathlib import Path

import click

from .render import render
from .sections import parse_sections
from .tokenizers import count_claude, count_openai

PLATFORMS = ["claude-code", "codex", "opencode", "antigravity"]


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
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--platform", type=click.Choice(PLATFORMS), required=True)
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
) -> None:
    kind, param = resolve_tokenizer(platform, model, tokenizer, claude_family, encoding)
    count_fn = partial(count_claude, family=param) if kind == "claude" else partial(count_openai, encoding=param)
    text = file.read_text(encoding="utf-8")
    root = parse_sections(text)
    click.echo(render(root, count_fn, fmt=fmt, depth=depth, sort=sort))
