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
