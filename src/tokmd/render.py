"""Render a Section tree with token counts as table/md/json/csv.

ADR-003: a Section tree, not a flat cut. Each visible row's `tokens` is the
ACCUMULATED count — its own text plus every descendant's — so that limiting
`depth` never loses a token: a row at the cutoff still reports the full
weight of everything hidden beneath it, exactly as `du -d N` rolls up a
directory tree. `sort="tokens"` reorders SIBLINGS by that accumulated count
(descending), never the whole flat list — sorting the flat list would break
the indentation, since a level-2 row would drift away from its level-1
parent.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Callable

from .sections import Section


@dataclass(frozen=True)
class Row:
    """One visible line: a section's title, its nesting level, and its
    accumulated token count (own text plus every descendant's)."""

    title: str
    level: int
    tokens: int


def render(
    root: Section,
    count_fn: Callable[[str], int],
    fmt: str = "table",
    depth: int | None = None,
    sort: str = "document",
) -> str:
    """Render `root`'s children (not `root` itself) as `fmt`.

    `count_fn(text) -> int` counts one section's own text (e.g.
    `functools.partial(count_claude, family="4.8")`).
    `fmt`: "table" (default, indented plain text), "md" (indented Markdown
    bullet list), "json" (a JSON array of objects, parseable), or "csv"
    (header `level,title,tokens` plus one row per section).
    `depth`: if given, only rows with `level <= depth` are shown — their
    `tokens` still include everything below the cutoff.
    `sort`: "document" (default, original order) or "tokens" (siblings
    sorted by accumulated tokens, descending).
    """
    rows = _build_rows(root, count_fn, sort)
    if depth is not None:
        rows = [row for row in rows if row.level <= depth]

    if fmt == "json":
        return json.dumps([{"title": r.title, "level": r.level, "tokens": r.tokens} for r in rows])
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(["level", "title", "tokens"])
        for r in rows:
            writer.writerow([r.level, r.title, r.tokens])
        return buf.getvalue()
    if fmt == "md":
        return "\n".join(f"{'  ' * r.level}- {r.title}: {r.tokens}" for r in rows)
    return "\n".join(f"{'  ' * r.level}{r.title}: {r.tokens}" for r in rows)


def _build_rows(section: Section, count_fn: Callable[[str], int], sort: str) -> list[Row]:
    """Post-order accumulation, pre-order emission: each child's total is
    known before its row is built, but rows still come out parent-first."""
    total = count_fn(section.own_text) if section.own_text else 0
    computed_children: list[tuple[int, list[Row]]] = []
    for child in section.children:
        child_total, child_rows = _accumulate_and_flatten(child, count_fn, sort)
        computed_children.append((child_total, child_rows))
        total += child_total
    if sort == "tokens":
        computed_children.sort(key=lambda item: item[0], reverse=True)
    rows: list[Row] = []
    for _, child_rows in computed_children:
        rows.extend(child_rows)
    return rows


def _accumulate_and_flatten(
    section: Section, count_fn: Callable[[str], int], sort: str
) -> tuple[int, list[Row]]:
    total = count_fn(section.own_text) if section.own_text else 0
    computed_children: list[tuple[int, list[Row]]] = []
    for child in section.children:
        child_total, child_rows = _accumulate_and_flatten(child, count_fn, sort)
        computed_children.append((child_total, child_rows))
        total += child_total
    if sort == "tokens":
        computed_children.sort(key=lambda item: item[0], reverse=True)
    child_rows_flat: list[Row] = []
    for _, child_rows in computed_children:
        child_rows_flat.extend(child_rows)
    return total, [Row(section.title, section.level, total)] + child_rows_flat
