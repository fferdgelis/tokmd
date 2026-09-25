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
