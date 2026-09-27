"""Tests for tokmd.sections — the section tree parser (PBI-001).

Autoría (ADR-006): escrito por DeepSeek (deepseek-v4-pro), rol TDD, a partir
de tools/deepseek/specs/PBI-001.md.prompt — el contrato público de
Section/parse_sections y los AC-01..05 del PBI, SIN ver sections.py. Corrida
real: 25/09/2026, costo USD 0,0008, thinking deshabilitado (ver dev-log:
con thinking habilitado el razonamiento agotaba el presupuesto de tokens
antes de terminar el archivo). Desarrollo (Claude) verificó que corre en
verde contra la implementación y no lo editó.
"""
from tokmd.sections import Section, parse_sections


def _collect_sections(root: Section) -> list[Section]:
    """Return all sections in the tree, including the root."""
    result = [root]
    for child in root.children:
        result.extend(_collect_sections(child))
    return result


def _find_by_title(root: Section, title: str) -> Section | None:
    for section in _collect_sections(root):
        if section.title == title:
            return section
    return None


# AC-01
def test_front_matter_becomes_root_child_with_content():
    text = """---
title: Example
author: Tester
---
# Heading
Body text.
"""
    root = parse_sections(text)

    front_matter = _find_by_title(root, "(front matter)")
    assert front_matter is not None
    assert front_matter.level == 0
    assert "title: Example" in front_matter.own_text
    assert "author: Tester" in front_matter.own_text
    assert front_matter in root.children


# AC-02
def test_preamble_text_does_not_leak_into_first_heading():
    text = """Intro paragraph before any heading.
Still preamble text.

# First Heading
Heading body text.
"""
    root = parse_sections(text)

    preamble = _find_by_title(root, "(preamble)")
    assert preamble is not None
    assert preamble.level == 0
    assert "Intro paragraph before any heading." in preamble.own_text
    assert "Still preamble text." in preamble.own_text

    first_heading = _find_by_title(root, "First Heading")
    assert first_heading is not None
    assert "Intro paragraph before any heading." not in first_heading.own_text
    assert "Still preamble text." not in first_heading.own_text
    assert "Heading body text." in first_heading.own_text


# AC-03
def test_heading_level_skip_attaches_to_nearest_ancestor():
    text = """## Parent Heading
Parent content.

#### Deep Child Heading
Child content.
"""
    root = parse_sections(text)

    parent = _find_by_title(root, "Parent Heading")
    deep_child = _find_by_title(root, "Deep Child Heading")

    assert parent is not None
    assert deep_child is not None
    assert deep_child.level == 4
    assert deep_child in parent.children
    assert deep_child not in root.children


# AC-04
def test_hash_inside_fenced_code_block_is_not_heading():
    text = """# Real Heading
Before fence.

```python
# This is a comment, not a heading
def foo():
    pass
```

After fence.
"""
    root = parse_sections(text)

    all_titles = [section.title for section in _collect_sections(root)]
    assert "# This is a comment, not a heading" not in all_titles
    assert "This is a comment, not a heading" not in all_titles

    real_heading = _find_by_title(root, "Real Heading")
    assert real_heading is not None
    assert "# This is a comment, not a heading" in real_heading.own_text
    assert "```python" in real_heading.own_text
    assert "```" in real_heading.own_text


# AC-05
def test_empty_string_does_not_raise():
    root = parse_sections("")
    assert root.title == "(document)"
    assert root.level == 0
    assert root.children == []


# AC-05
def test_no_headings_but_text_creates_preamble():
    text = "Just some text.\nNo headings here."
    root = parse_sections(text)

    preamble = _find_by_title(root, "(preamble)")
    assert preamble is not None
    assert preamble.level == 0
    assert "Just some text." in preamble.own_text
    assert "No headings here." in preamble.own_text
    assert preamble in root.children


# Hueco de cobertura encontrado por Desarrollo (98% tras la primera tanda:
# "stack.pop()" nunca se ejercitaba), pedido a DeepSeek como incremento
# puntual — no lo escribió Desarrollo (ADR-006).
def test_two_headings_at_the_same_level_are_siblings():
    text = "# One\n\nBody of one.\n\n# Two\n\nBody of two.\n"
    root = parse_sections(text)

    assert len(root.children) == 2
    one, two = root.children

    assert one.title == "One"
    assert two.title == "Two"

    assert one in root.children
    assert two in root.children
    assert one not in two.children
    assert two not in one.children

    assert "Body of two." not in one.own_text
    assert "Body of one." not in two.own_text


# --- PBI-009 (28/09/2026): el heading pasa a contar dentro de su propia
# sección, y el front matter absorbe las líneas en blanco que le siguen.
#
# Autoría (ADR-006): escrito por DeepSeek (deepseek-v4-pro), rol TDD, a
# partir de tools/deepseek/specs/PBI-009-sections.md.prompt — el contrato
# público actualizado de Section/parse_sections y los AC-01..05 de esa
# spec, SIN ver sections.py. Corrida real: 27/09/2026, costo USD 0,0015,
# thinking deshabilitado. Desarrollo (Claude) revisó el archivo generado
# y no lo editó.


def _concat_own_text(root: Section) -> str:
    """Walk the tree in pre-order, document order, concatenating own_text."""
    parts = [root.own_text]
    for child in root.children:
        parts.append(_concat_own_text(child))
    return "".join(parts)


def _find_section(root: Section, title: str) -> Section | None:
    for child in root.children:
        if child.title == title:
            return child
        found = _find_section(child, title)
        if found is not None:
            return found
    return None


# AC-01
def test_heading_own_text_includes_heading_line_and_invariant_holds():
    text = "# Only Title\nSome body text.\n"
    root = parse_sections(text)

    section = _find_section(root, "Only Title")
    assert section is not None
    assert section.own_text.startswith("# Only Title")

    assert _concat_own_text(root) == text


# AC-02
def test_heading_only_sections_have_nonempty_own_text():
    text = (
        "# First comment line\n"
        "# Second comment line\n"
        "# Third comment line\n"
        "# Real heading with body\n"
        "Some actual content here.\n"
    )
    root = parse_sections(text)

    headings = [
        child
        for child in root.children
        if child.level > 0
    ]
    assert len(headings) == 4

    for heading in headings:
        assert heading.own_text.strip() != ""


# AC-03
def test_front_matter_blank_line_not_in_whitespace_only_preamble():
    text = "---\nkey: value\n---\n\n# Heading\nBody text.\n"
    root = parse_sections(text)

    assert _concat_own_text(root) == text

    for child in root.children:
        if child.level == 0 and child.title == "(preamble)":
            assert child.own_text.strip() != ""


# AC-04
def test_front_matter_real_preamble_and_nested_headings():
    text = (
        "---\n"
        'title: "x"\n'
        "---\n"
        "This is a real preamble paragraph, not blank.\n"
        "\n"
        "# H1\n"
        "H1 body.\n"
        "\n"
        "## H2\n"
        "H2 body.\n"
    )
    root = parse_sections(text)

    preamble = _find_section(root, "(preamble)")
    assert preamble is not None
    assert "real preamble paragraph" in preamble.own_text

    h1 = _find_section(root, "H1")
    assert h1 is not None
    assert h1.own_text.startswith("# H1")

    h2 = _find_section(root, "H2")
    assert h2 is not None
    assert h2.own_text.startswith("## H2")
    assert h2 in h1.children

    assert _concat_own_text(root) == text


# AC-05
def test_plain_two_sibling_headings_invariant_holds():
    text = (
        "# First\n"
        "First body.\n"
        "\n"
        "# Second\n"
        "Second body.\n"
    )
    root = parse_sections(text)

    assert _concat_own_text(root) == text
