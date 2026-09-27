"""Tests for tokmd.render — Section tree rendering (PBI-005, PBI-009).

Retrofit completo (ADR-006, mismo patrón que PBI-001): Row pasó de un solo
campo (tokens) a dos (own/total), render() ganó los parámetros `total`
(obligatorio) y `frame` (opcional), y --format json pasó de un array plano
a un objeto {total, drift, rows} (ADR-007, BUG-009, BUG-010). Los AC-01..04
de PBI-005 quedaban rotos por la firma nueva (TypeError por falta de
`total`), así que este archivo reemplaza al anterior completo: esos cuatro
adaptados al contrato nuevo, más los AC-05/06/12..16/20 nuevos de PBI-009.

Autoría: escrito por DeepSeek (deepseek-v4-pro), rol TDD, a partir de
tools/deepseek/specs/PBI-009-render-retrofit.md.prompt — el contrato
público completo, SIN ver render.py. Corrida real: 27/09/2026, costo
USD 0,0031, thinking deshabilitado. Un intento anterior de la spec de sólo
los AC nuevos (sin retrofit) tenía un defecto propio (la fórmula de deriva
pedía un `FRAME` que render() no recibía como parámetro): corregido antes
de esta corrida agregando `frame` a la firma pública. Desarrollo (Claude)
revisó el archivo generado y no lo editó.
"""
import csv
import io
import json

from tokmd.render import render
from tokmd.sections import Section


def make_word_tree():
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


FRAME = 2


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


def count_fn(text: str) -> int:
    return max(len(text.split()) - FRAME, 0)


def make_uneven_tree():
    return Section(
        title="(document)",
        level=0,
        own_text="",
        children=[
            Section(title="ShortParent", level=1, own_text="short", children=[
                Section(
                    title="LongChild",
                    level=2,
                    own_text="one two three four five six seven eight nine ten",
                    children=[],
                ),
            ]),
        ],
    )


# AC-01
def test_json_output_is_object_with_rows_and_totals():
    output = render(make_word_tree(), word_count, total=100, fmt="json")
    data = json.loads(output)
    assert isinstance(data, dict)
    rows = data["rows"]
    intro = next(row for row in rows if row["title"] == "Intro")
    background = next(row for row in rows if row["title"] == "Background")
    assert intro["total"] == 4
    assert intro["own"] == 2
    assert background["total"] == 2


# AC-02
def test_table_indentation_and_default_fmt():
    explicit = render(make_word_tree(), word_count, total=100, fmt="table")
    default = render(make_word_tree(), word_count, total=100)
    assert explicit == default

    intro_line = next(line for line in explicit.splitlines() if "Intro" in line)
    background_line = next(line for line in explicit.splitlines() if "Background" in line)
    assert len(background_line) - len(background_line.lstrip()) > len(intro_line) - len(intro_line.lstrip())


# AC-03
def test_depth_cutoff_keeps_parent_total():
    output = render(make_word_tree(), word_count, total=100, depth=1)
    assert "Background" not in output
    intro_line = next(line for line in output.splitlines() if "Intro" in line)
    assert "4" in intro_line


# AC-04
def test_sort_tokens_reorders_top_level_siblings():
    output = render(make_word_tree(), word_count, total=100, sort="tokens")
    assert output.index("Intro") < output.index("Conclusion")

    tree = make_word_tree()
    tree.children.append(Section(title="Appendix", level=1, own_text="one two three four five six", children=[]))
    output = render(tree, word_count, total=100, sort="tokens")
    assert output.index("Appendix") < output.index("Intro") < output.index("Conclusion")


# AC-05 / AC-12
def test_table_shows_root_and_section_rows_and_uneven_own_total():
    output = render(make_tree(), count_fn, total=5, fmt="table")
    root_line = next(line for line in output.splitlines() if "(document)" in line)
    assert "5" in root_line
    assert "Intro" in output
    assert "Background" in output
    assert "Conclusion" in output

    uneven_output = render(make_uneven_tree(), count_fn, total=5, fmt="table")
    short_parent_line = next(line for line in uneven_output.splitlines() if "ShortParent" in line)
    assert "0" in short_parent_line
    assert "8" in short_parent_line


# AC-13
def test_root_total_is_injected_value_not_summed():
    output = render(make_tree(), count_fn, total=5, fmt="table")
    root_line = next(line for line in output.splitlines() if "(document)" in line)
    assert "5" in root_line
    assert "0" not in root_line


# AC-14
def test_uneven_parent_own_less_than_total():
    output = render(make_uneven_tree(), count_fn, total=5, fmt="table")
    short_parent_line = next(line for line in output.splitlines() if "ShortParent" in line)
    assert "own=0" in short_parent_line
    assert "total=8" in short_parent_line


# AC-15
def test_drift_positive_and_negative():
    output = render(make_tree(), count_fn, total=5, frame=FRAME, fmt="table")
    drift_line = next(line for line in output.splitlines() if "boundary drift" in line)
    assert "3" in drift_line

    output = render(make_tree(), count_fn, total=-3, frame=FRAME, fmt="table")
    drift_line = next(line for line in output.splitlines() if "boundary drift" in line)
    assert "-5" in drift_line


# AC-16
def test_drift_zero():
    output = render(make_tree(), count_fn, total=2, frame=FRAME, fmt="table")
    drift_line = next(line for line in output.splitlines() if "boundary drift" in line)
    assert "0" in drift_line


# AC-06
def test_json_drift_and_rows_exclude_root():
    output = render(make_tree(), count_fn, total=5, frame=FRAME, fmt="json")
    data = json.loads(output)
    assert data["total"] == 5
    assert data["drift"] == 3
    rows = data["rows"]
    titles = {row["title"] for row in rows}
    assert titles == {"Intro", "Background", "Conclusion"}
    for row in rows:
        assert set(row.keys()) == {"title", "level", "own", "total"}


# csv regression
def test_csv_format_no_drift():
    output = render(make_tree(), count_fn, total=5, fmt="csv")
    reader = csv.reader(io.StringIO(output))
    rows = list(reader)
    assert rows[0] == ["level", "title", "own", "total"]
    assert rows[1][0] == "0"
    assert rows[1][3] == "5"
    assert len(rows) == 5  # header + root + 3 sections
    assert "drift" not in output


# AC-20
def test_tree_connectors_table_only():
    table_output = render(make_tree(), count_fn, total=5, fmt="table")
    assert "├─" in table_output
    assert "└─" in table_output
    assert "│" in table_output

    md_output = render(make_tree(), count_fn, total=5, fmt="md")
    assert "├─" not in md_output
    assert "└─" not in md_output

    csv_output = render(make_tree(), count_fn, total=5, fmt="csv")
    assert "├─" not in csv_output
    assert "└─" not in csv_output
