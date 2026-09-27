"""Count tokens per section, one function per target platform.

ADR-001: `ctok` (offline reconstruction) is the default Claude engine, no
network or API key required; `tiktoken` covers OpenAI/Codex.

Claude (`count_claude`): ADR-002/ADR-007: `ctok.token_count` includes
Anthropic's message frame, which breaks additivity across sections — a
document's total is not the sum of its parts' raw counts. `FRAME` is the
fixed cost of one additional chunk when a document is split into pieces —
**not** `ctok.token_count("", version)`, which over-counts by one token for
family `"4.8"` (ADR-007, verified against Anthropic's real API on 17
real documents: the per-chunk cost is 5, not 6). `3.0` and `4.7` keep
their `token_count("")` values — this project has only verified `4.8`
against a real oracle so far. `count_claude` subtracts `FRAME[family]`
once per call, so section counts stay additive when summed **plus one
more `FRAME`** (see `count_claude_total`, and `render.py`'s `frame`
parameter, which does that addition back for the caller).

`count_claude_total`: the raw, un-subtracted whole-document count — the
exact number Anthropic's API bills for a document taken as a single
request. Unlike `count_claude`, never subtracts `FRAME`: the per-chunk
cost only applies when a document has been split into pieces summed
together, never to a single whole-document count.

OpenAI (`count_openai`): `tiktoken` counts raw content tokens with no
per-message frame to subtract, so section counts are exactly additive
(unlike Claude) — verified in `docs/investigation/20260924-ctok-marco-y-deriva.md`'s
counterpart for PBI-003.
"""
from __future__ import annotations

import ctok
import tiktoken

FRAME: dict[str, int] = {
    "3.0": 8,
    "4.7": 12,
    "4.8": 5,
}


def _raw_claude(text: str, family: str) -> int:
    if family not in FRAME:
        raise ValueError(f"Unknown Claude family: {family!r}, expected one of {sorted(FRAME)}")
    return ctok.token_count(text, family)


def count_claude(text: str, family: str) -> int:
    """Count `text`'s Claude tokens for `family`, net of that family's FRAME.

    `family` must be one of `FRAME`'s keys ("3.0", "4.7", "4.8"), matching
    `ctok.token_count`'s `version` parameter directly.
    """
    return _raw_claude(text, family) - FRAME[family]


def count_claude_total(text: str, family: str) -> int:
    """Count `text`'s Claude tokens for `family` as a RAW total — the exact
    number Anthropic's API would bill for `text` as a whole. Unlike
    `count_claude`, this does NOT subtract `FRAME[family]`.

    `family` must be one of `FRAME`'s keys, same validation as `count_claude`.
    """
    return _raw_claude(text, family)


OPENAI_ENCODINGS: dict[str, str] = {
    "gpt-5": "o200k_base",
    "gpt-4o": "o200k_base",
    "gpt-4": "cl100k_base",
}


def count_openai(text: str, encoding: str) -> int:
    """Count `text`'s OpenAI tokens for `encoding`.

    `encoding` is a `tiktoken` encoding name ("o200k_base", "cl100k_base",
    ...), not a model name — callers pick one via `OPENAI_ENCODINGS` or pass
    a `tiktoken.encoding_for_model` name directly. No frame to subtract:
    unlike `count_claude`, this is an exact partition, additive across
    sections with zero drift.
    """
    return len(tiktoken.get_encoding(encoding).encode(text))
