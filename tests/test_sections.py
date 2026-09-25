"""Tests for tokmd.sections — the section tree parser (PBI-001).

Case ids map to the Kiwi TestCase ids loaded in tools/kiwi/cargar_casos.py:
TOK-001-C01 .. TOK-001-C05.
"""
from pathlib import Path

import pytest

from tokmd.sections import Section, parse_sections

FIXTURES = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def find_child(section: Section, title: str) -> Section:
    for child in section.children:
        if child.title == title:
            return child
    raise AssertionError(f"no child titled {title!r} among {[c.title for c in section.children]}")


# TOK-001-C01 — front matter is its own row
def test_front_matter_is_its_own_row():
    root = parse_sections(read_fixture("sample.md.fixture"))
    fm = find_child(root, "(front matter)")
    assert fm.level == 0
    assert fm.own_text.startswith("---\n")
    assert 'title: "Sample"' in fm.own_text
    assert fm.own_text.rstrip().endswith("---")


# TOK-001-C02 — preamble before the first heading
def test_preamble_before_first_heading():
    root = parse_sections(read_fixture("sample.md.fixture"))
    preamble = find_child(root, "(preamble)")
    assert "This is the preamble" in preamble.own_text
    # the preamble must not leak into the first heading's own text
    section_one = find_child(root, "Section One")
    assert "preamble" not in section_one.own_text


# TOK-001-C03 — level skip (## then ####, no ### in between)
def test_level_skip_attaches_to_nearest_ancestor():
    root = parse_sections(read_fixture("sample.md.fixture"))
    section_one = find_child(root, "Section One")
    assert section_one.level == 2
    deep = find_child(section_one, "Deep subsection (level skip)")
    assert deep.level == 4
    assert "level-skip subsection" in deep.own_text


# TOK-001-C04 — a '#' inside a fenced code block is not a heading
def test_heading_inside_code_fence_is_ignored():
    root = parse_sections(read_fixture("sample.md.fixture"))
    section_two = find_child(root, "Section Two")
    titles_under_two = [c.title for c in section_two.children]
    assert "This looks like a heading but is inside a code fence" not in titles_under_two
    assert section_two.children == []
    assert "looks like a heading" in section_two.own_text
    assert "still owned by Section Two" in section_two.own_text


# TOK-001-C05 — file with no headings, and a fully empty file
def test_file_with_no_headings():
    root = parse_sections(read_fixture("no_headings.md.fixture"))
    assert len(root.children) == 1
    preamble = root.children[0]
    assert preamble.title == "(preamble)"
    assert "Just a paragraph" in preamble.own_text


def test_empty_file_does_not_raise():
    root = parse_sections(read_fixture("empty.md.fixture"))
    assert root.children == []


def test_empty_string_does_not_raise():
    root = parse_sections("")
    assert root.children == []


def test_document_without_front_matter_has_no_front_matter_row():
    root = parse_sections("# Only a heading\n\nbody text\n")
    titles = [c.title for c in root.children]
    assert "(front matter)" not in titles
    heading = find_child(root, "Only a heading")
    assert heading.own_text.strip() == "body text"


def test_two_top_level_headings_are_siblings():
    root = parse_sections("# One\n\ntext one\n\n# Two\n\ntext two\n")
    one = find_child(root, "One")
    two = find_child(root, "Two")
    assert one.level == 1 and two.level == 1
    assert "text one" in one.own_text
    assert "text one" not in two.own_text
    assert "text two" in two.own_text
