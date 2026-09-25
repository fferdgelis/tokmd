"""`tokmd FILE --platform <p>`: resolve the tokenizer, render the section tree.

ADR-001: platforms map to a tokenizer + parameter without the user having to
know which one. `--tokenizer` (an explicit "claude"/"openai" choice) always
wins over whatever `--platform` would have picked — stated in PBI-004's risk
section, so a caller who knows better than the platform mapping is never
blocked by it, including on `antigravity` (not implemented as a platform,
but still overridable). `--format`/`--depth`/`--sort` (PBI-005) are thin
pass-throughs to `render.render`; this module's own job stops at resolving
"which tokenizer" and building the `count_fn` closure it's called with.

`--verify` (PBI-008): cross-checks against Anthropic's real API instead of
ctok's offline reconstruction. Only valid when the resolved tokenizer is
"claude" — `verify.py`'s `count_tokens` endpoint has no OpenAI counterpart
here. `get_client`/`measure_frame`/`count_verified` are imported by name
(not the module) so tests can `monkeypatch.setattr("tokmd.cli.get_client",
...)` without a real `ANTHROPIC_API_KEY` or network call — same pattern
`verify.py`'s own tests use against a fake client.
"""
from __future__ import annotations

from functools import partial
import importlib.metadata
from pathlib import Path

import click

from .render import render
from .sections import parse_sections
from .tokenizers import count_claude, count_openai
from .verify import MissingApiKeyError, count_verified, get_client, measure_frame

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
    verify: bool,
) -> None:
    kind, param = resolve_tokenizer(platform, model, tokenizer, claude_family, encoding)
    if verify:
        if kind != "claude":
            raise click.UsageError("--verify only supports the Claude tokenizer, not OpenAI.")
        try:
            client = get_client()
        except MissingApiKeyError as exc:
            raise click.ClickException(str(exc)) from exc
        verify_model = model or DEFAULT_VERIFY_MODEL
        frame = measure_frame(client, verify_model)
        count_fn = lambda section_text: count_verified(client, section_text, verify_model, frame)  # noqa: E731
    else:
        count_fn = partial(count_claude, family=param) if kind == "claude" else partial(count_openai, encoding=param)
    text = file.read_text(encoding="utf-8")
    root = parse_sections(text)
    click.echo(render(root, count_fn, fmt=fmt, depth=depth, sort=sort))
