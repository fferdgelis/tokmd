"""Render a Section tree with token counts as table/md/json/csv.

ADR-003/BUG-009: every row shows two numbers — `own` (its own text alone)
and `total` (own plus every descendant's, accumulated bottom-up) — and a
root row represents the whole document. `sort="tokens"` reorders SIBLINGS
by their own accumulated `total` (descending), never the whole flat list.

ADR-007/BUG-010: `render` takes the whole document's REAL total as an
explicit parameter — it never derives it by summing the tree (summing
undercounts by exactly one `frame`'s worth, per ADR-007's measurement).
`frame`, also explicit, lets the caller ask for a `boundary drift` figure
that should always land on `0` for a healthy document.
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
    """One visible line, other than the root row: a section's title, its
    nesting level, its own token count, and its accumulated total (own
    plus every descendant's)."""

    title: str
    level: int
    own: int
    total: int


def render(
    root: Section,
    count_fn: Callable[[str], int],
    total: int,
    frame: int = 0,
    fmt: str = "table",
    depth: int | None = None,
    sort: str = "document",
) -> str:
    """Render `root`'s children as `fmt`, plus a root row for `root` itself.

    `count_fn(text) -> int` counts one section's own text.
    `total`: the caller-supplied, authoritative whole-document total (e.g.
    from a raw, un-subtracted count of the full source) — the root row's
    total is set to exactly this value, never derived by summing children.
    `frame`: the fixed per-chunk cost `count_fn` already subtracts once per
    section internally, used only to compute `boundary drift` (see below).
    `fmt`: "table" (default, tree connectors, drift footer), "md" (indented
    bullets), "json" (a parseable object: `{"total", "drift", "rows"}`), or
    "csv" (header `level,title,own,total`, root row first, no drift).
    `depth`: only rows with `level <= depth` are shown — the root row is
    always shown regardless of `depth`. Totals still include everything
    below the cutoff (rollup, never lost).
    `sort`: "document" (default, original order) or "tokens" (siblings
    reordered by their own accumulated `total`, descending).

    Boundary drift: `drift = total - sum(row.own for every non-root row) -
    frame` — computed over every section regardless of `depth`, since
    `depth` only affects what's displayed, not the document's own data.
    """
    rows = _build_rows(root, count_fn, sort)
    own_sum = sum(row.own for row in rows)
    drift = total - own_sum - frame

    visible_rows = [row for row in rows if depth is None or row.level <= depth]

    if fmt == "json":
        return json.dumps(
            {
                "total": total,
                "drift": drift,
                "rows": [
                    {"title": r.title, "level": r.level, "own": r.own, "total": r.total}
                    for r in visible_rows
                ],
            }
        )
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(["level", "title", "own", "total"])
        writer.writerow([0, root.title, "", total])
        for r in visible_rows:
            writer.writerow([r.level, r.title, r.own, r.total])
        return buf.getvalue()
    if fmt == "md":
        lines = [f"- {root.title}: own=0 total={total}"]
        lines += [f"{'  ' * r.level}- {r.title}: own={r.own} total={r.total}" for r in visible_rows]
        return "\n".join(lines)

    # "table" (default): tree connectors + drift footer.
    lines = [f"{root.title}: total={total}"]
    lines += _table_lines(root, count_fn, sort, depth, prefix="")
    lines.append("")
    sign = "+" if drift >= 0 else ""
    lines.append(f"boundary drift: {sign}{drift}")
    return "\n".join(lines)


def _own_total(section: Section, count_fn: Callable[[str], int]) -> tuple[int, int]:
    own = count_fn(section.own_text) if section.own_text else 0
    total = own
    for child in section.children:
        _, child_total = _own_total(child, count_fn)
        total += child_total
    return own, total


def _sorted_children(section: Section, count_fn: Callable[[str], int], sort: str) -> list[Section]:
    children = list(section.children)
    if sort == "tokens":
        children.sort(key=lambda c: _own_total(c, count_fn)[1], reverse=True)
    return children


def _build_rows(section: Section, count_fn: Callable[[str], int], sort: str) -> list[Row]:
    """`section`'s children, flattened, pre-order — never a row for
    `section` itself (the root row is built separately by the caller)."""
    rows: list[Row] = []
    for child in _sorted_children(section, count_fn, sort):
        own, total = _own_total(child, count_fn)
        rows.append(Row(child.title, child.level, own, total))
        rows.extend(_build_rows(child, count_fn, sort))
    return rows


def _table_lines(
    section: Section,
    count_fn: Callable[[str], int],
    sort: str,
    depth: int | None,
    prefix: str,
) -> list[str]:
    lines: list[str] = []
    children = _sorted_children(section, count_fn, sort)
    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        own, total = _own_total(child, count_fn)
        if depth is None or child.level <= depth:
            connector = "└─ " if is_last else "├─ "
            # A leading literal-space indent (on top of the connector
            # prefix) so deeper levels still have more leading whitespace
            # than shallower ones — connector characters ("│", "├", "└")
            # are not whitespace, so a plain `str.lstrip()`-based
            # indentation check wouldn't see depth from them alone.
            indent = "  " * child.level
            lines.append(f"{indent}{prefix}{connector}{child.title}: own={own} total={total}")
        child_prefix = prefix + ("   " if is_last else "│  ")
        lines.extend(_table_lines(child, count_fn, sort, depth, child_prefix))
    return lines
