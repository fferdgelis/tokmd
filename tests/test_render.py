import csv
import io
import json

from tokmd.render import render
from tokmd.sections import Section


def make_tree():
    return Section(
        title="(document)",
        level=0,
        own_text="",
        children=[
            Section(title="Intro", level=1, own_text="intro text", children=[
                Section(title="Background", level=2, own_text="background text", children=[]),
            ]),
            Section(title="Conclusion", level=1, own_text="conclusion text", children=[]),
        ],
    )


def word_count(text: str) -> int:
    return len(text.split())


# AC-01
def test_json_output_parses_and_has_accumulated_tokens():
    tree = make_tree()
    result = render(tree, word_count, fmt="json")
    data = json.loads(result)
    assert isinstance(data, list)

    by_title = {item["title"]: item for item in data}
    assert by_title["Intro"]["tokens"] == 4
    assert by_title["Background"]["tokens"] == 2


# AC-02
def test_table_is_default_and_indents_deeper_levels_more():
    tree = make_tree()
    explicit = render(tree, word_count, fmt="table")
    default = render(tree, word_count)
    assert explicit == default

    lines = explicit.splitlines()
    intro_line = next(line for line in lines if "Intro" in line)
    background_line = next(line for line in lines if "Background" in line)

    intro_indent = len(intro_line) - len(intro_line.lstrip())
    background_indent = len(background_line) - len(background_line.lstrip())
    assert background_indent > intro_indent


# AC-03
def test_depth_cutoff_rolls_up_tokens_into_visible_parent():
    tree = make_tree()
    result = render(tree, word_count, depth=1)
    assert "Background" not in result
    assert "Intro" in result
    assert "4" in result


# AC-04
def test_sort_tokens_reorders_siblings_descending():
    tree = make_tree()
    result = render(tree, word_count, sort="tokens")
    assert result.index("Intro") < result.index("Conclusion")

    appendix = Section(title="Appendix", level=1, own_text="one two three four five six", children=[])
    tree.children.append(appendix)
    result = render(tree, word_count, sort="tokens")
    assert result.index("Appendix") < result.index("Intro") < result.index("Conclusion")


# Gap: tools/deepseek/specs/PBI-005-gap-01.md.prompt
def test_csv_output_has_header_and_rows():
    output = render(make_tree(), word_count, fmt="csv")
    reader = csv.reader(io.StringIO(output))
    rows = list(reader)
    assert rows[0] == ["level", "title", "tokens"]
    assert ["1", "Intro", "4"] in rows
    assert ["2", "Background", "2"] in rows


def test_md_output_is_indented_bullet_list():
    output = render(make_tree(), word_count, fmt="md")
    lines = [line for line in output.splitlines() if line.strip()]
    assert all("- " in line for line in lines)

    intro_line = next(line for line in lines if "Intro" in line)
    background_line = next(line for line in lines if "Background" in line)

    intro_indent = len(intro_line) - len(intro_line.lstrip())
    background_indent = len(background_line) - len(background_line.lstrip())

    assert background_indent > intro_indent
