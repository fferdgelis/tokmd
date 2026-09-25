"""`tokmd FILE --platform <p>`: resolve the right tokenizer, print a total.

ADR-001: platforms map to a tokenizer + parameter without the user having to
know which one. `--tokenizer` (an explicit "claude"/"openai" choice) always
wins over whatever `--platform` would have picked — stated in PBI-004's risk
section, so a caller who knows better than the platform mapping is never
blocked by it, including on `antigravity` (not implemented as a platform,
but still overridable). Per-section rendering (`--depth`, `--sort`, output
formats) is PBI-005's `render.py`, not this module — this one only resolves
"which tokenizer" and prints a whole-file total.
"""
from __future__ import annotations

from pathlib import Path

import click

from .tokenizers import count_claude, count_openai

PLATFORMS = ["claude-code", "codex", "opencode", "antigravity"]


class PlatformNotSupportedError(click.ClickException):
    """A recognized platform with no tokenizer yet (e.g. antigravity)."""

    exit_code = 2


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
        if not model:
            raise click.UsageError("--model is required when --platform is opencode")
        if model.startswith("claude"):
            return "claude", claude_family or "4.8"
        if model.startswith("gpt"):
            return "openai", encoding or "o200k_base"
        raise click.UsageError(f"Unrecognized --model for --platform opencode: {model!r}")
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
def main(
    file: Path,
    platform: str,
    model: str | None,
    tokenizer: str | None,
    claude_family: str | None,
    encoding: str | None,
) -> None:
    kind, param = resolve_tokenizer(platform, model, tokenizer, claude_family, encoding)
    text = file.read_text(encoding="utf-8")
    count = count_claude(text, param) if kind == "claude" else count_openai(text, param)
    click.echo(f"{count} tokens ({kind} {param})")
