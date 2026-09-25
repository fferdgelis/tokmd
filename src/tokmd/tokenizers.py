"""Count Claude tokens per section, net of the per-message frame.

ADR-001: `ctok` (offline reconstruction) is the default engine, no network
or API key required. ADR-002: `ctok.token_count` includes Anthropic's
message frame (roles and delimiters), which breaks additivity across
sections — a document's total is not the sum of its parts' raw counts.
`FRAME` is measured once per family (`ctok.token_count("", version)`,
pinned to ctok 1.3.0) and subtracted from every call, so section counts
stay approximately additive. This is a subtractive approximation, not an
exact partition: for a section small enough that its raw count is below
`FRAME`, the result goes negative. That is the documented cost of ADR-002's
option 2, not a bug — callers that need a non-negative display should clamp.
"""
from __future__ import annotations

import ctok

FRAME: dict[str, int] = {
    "3.0": 8,
    "4.7": 12,
    "4.8": 6,
}


def count_claude(text: str, family: str) -> int:
    """Count `text`'s Claude tokens for `family`, net of that family's FRAME.

    `family` must be one of `FRAME`'s keys ("3.0", "4.7", "4.8"), matching
    `ctok.token_count`'s `version` parameter directly.
    """
    if family not in FRAME:
        raise ValueError(f"Unknown Claude family: {family!r}, expected one of {sorted(FRAME)}")
    return ctok.token_count(text, family) - FRAME[family]
