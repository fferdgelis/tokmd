"""Parse a Markdown document into a tree of sections.

ADR-003: a full heading tree (not a flat, single-level cut), with the YAML
front matter and any preamble text as their own top-level rows. Headings
inside fenced code blocks are not treated as real headings — this comes for
free from using a real CommonMark parser (markdown-it-py) instead of a
naive line-by-line regex.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from markdown_it import MarkdownIt

FRONT_MATTER_RE = re.compile(r"\A---\r?\n(?:.*?\r?\n)?---[ \t]*\r?\n?", re.DOTALL)

_PARSER = MarkdownIt("commonmark")


@dataclass
class Section:
    """One row of the section tree.

    `level` is 0 for the document root and for the special `(front matter)`
    and `(preamble)` rows, and 1-6 for real Markdown headings (H1-H6).
    `own_text` is the section's own content, excluding its children's text.
    """

    title: str
    level: int
    own_text: str
    children: list["Section"] = field(default_factory=list)


def _split_front_matter(text: str) -> tuple[str | None, str]:
    """Return (front_matter_block_or_None, remaining_text)."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(0), text[match.end() :]


def _find_headings(body: str) -> list[tuple[int, str, int, int]]:
    """Return [(level, title, heading_line, content_start_line), ...] in order.

    Lines are 0-indexed, into `body.splitlines(keepends=True)`. Headings
    inside fenced code blocks are never emitted by markdown-it, so they
    never appear here.
    """
    tokens = _PARSER.parse(body)
    headings: list[tuple[int, str, int, int]] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == "heading_open" and token.map:
            level = int(token.tag[1])
            heading_line = token.map[0]
            content_start = token.map[1]
            title = ""
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                title = tokens[i + 1].content.strip()
            headings.append((level, title, heading_line, content_start))
        i += 1
    return headings


def parse_sections(text: str) -> Section:
    """Parse `text` (a full Markdown document) into a Section tree."""
    root = Section(title="(document)", level=0, own_text="")

    front_matter, body = _split_front_matter(text)
    if front_matter is not None:
        root.children.append(Section(title="(front matter)", level=0, own_text=front_matter))

    headings = _find_headings(body)
    lines = body.splitlines(keepends=True)

    if not headings:
        if body.strip():
            root.children.append(Section(title="(preamble)", level=0, own_text=body))
        return root

    first_heading_line = headings[0][2]
    preamble_text = "".join(lines[:first_heading_line])
    if preamble_text.strip():
        root.children.append(Section(title="(preamble)", level=0, own_text=preamble_text))

    # Stack of (level, Section), root is level 0. A new heading closes every
    # open section whose level is >= its own, then attaches to whatever is
    # left on the stack — this is what makes an out-of-order level skip
    # (## followed directly by ####) attach to the nearest real ancestor.
    stack: list[tuple[int, Section]] = [(0, root)]
    for idx, (level, title, _heading_line, content_start) in enumerate(headings):
        end_line = headings[idx + 1][2] if idx + 1 < len(headings) else len(lines)
        own_text = "".join(lines[content_start:end_line])
        node = Section(title=title, level=level, own_text=own_text)
        while stack[-1][0] >= level:
            stack.pop()
        stack[-1][1].children.append(node)
        stack.append((level, node))

    return root
