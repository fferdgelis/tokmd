"""`--verify`: cross-check the offline count against Anthropic's real API.

ADR-001, option 3: `ctok` is the default engine (no network, no key);
`--verify` is the opt-in exact check via `POST /v1/messages/count_tokens`.
The API's own count includes a message frame too, same problem as
`ctok` (ADR-002) — `measure_frame` nets it out with one minimal-content
call, cached and reused for every section, so `count_verified`'s numbers
are directly comparable to `count_claude`'s.

The API key itself is never printed, logged, or returned by any function
here — only read from the environment by `get_client`.
"""
from __future__ import annotations

import os
from typing import Any, Protocol


class MissingApiKeyError(Exception):
    """`ANTHROPIC_API_KEY` isn't set in the environment."""


class CountTokensClient(Protocol):
    """Shaped like `anthropic.Anthropic`, but only the one attribute this
    module actually touches (`.messages.count_tokens(...)`) — a `Protocol`,
    not the real SDK class, so tests can pass a lightweight fake instead
    (AC-03: no real network call anywhere in the test suite)."""

    messages: Any


def get_client() -> CountTokensClient:
    """Build a real `anthropic.Anthropic` client.

    Raises `MissingApiKeyError` with a readable message (never the key
    itself) if `ANTHROPIC_API_KEY` isn't set — `anthropic` is imported here,
    lazily, so importing this module never requires the `verify` extra
    unless `--verify` is actually used.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise MissingApiKeyError(
            "ANTHROPIC_API_KEY is not set. --verify calls Anthropic's real API and needs "
            "it in the environment (never pass a key as a CLI flag — it would end up in "
            "your shell history)."
        )
    import anthropic

    return anthropic.Anthropic()


def measure_frame(client: CountTokensClient, model: str) -> int:
    """Raw API token count for a minimal-content message under `model` —
    the frame to subtract from every section so `count_verified`'s numbers
    line up with `count_claude`'s netted-out ones.

    BUG-001: the original minimal content was a single space (" "), which
    passed every test (all of them use a fake client that never validates
    content) but was never exercised against the real API until PBI-008's
    smoke test — the real `count_tokens` endpoint rejects it with
    `400 invalid_request_error: text content blocks must contain
    non-whitespace text`. "." is the smallest content that both endpoints
    (real and fake) accept.
    """
    return _raw_count(client, ".", model)


def count_verified(client: CountTokensClient, text: str, model: str, frame: int) -> int:
    """`text`'s real API token count for `model`, net of `frame`."""
    return _raw_count(client, text, model) - frame


def _raw_count(client: CountTokensClient, text: str, model: str) -> int:
    response = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": text}])
    return response.input_tokens
