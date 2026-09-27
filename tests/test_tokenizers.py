"""Tests for tokmd.tokenizers — Claude/OpenAI token counting (PBI-002, PBI-009).

Retrofit completo (ADR-006, mismo patrón que PBI-001): FRAME["4.8"] pasó de
6 a 5 (ADR-007) y se agregó count_claude_total, así que los AC-01..05 de
PBI-002 quedaron parcialmente obsoletos (AC-01 daba count_claude("","4.8")
== 0, y ahora da 1). Este archivo reemplaza al anterior completo, con los
AC de PBI-002 adaptados a family "4.8" por separado (AC-01a/AC-01b) más los
AC-06..11 nuevos de PBI-009.

Autoría: escrito por DeepSeek (deepseek-v4-pro), rol TDD, a partir de
tools/deepseek/specs/PBI-009-tokenizers-retrofit.md.prompt — el contrato
público completo, SIN ver tokenizers.py. Corrida real: 27/09/2026, costo
USD 0,0015, thinking deshabilitado. Desarrollo (Claude) revisó el archivo
generado y no lo editó.
"""
from tokmd.tokenizers import FRAME, count_claude, count_claude_total, count_openai


# AC-01a
def test_count_claude_empty_3_0_and_4_7_are_zero():
    assert count_claude("", "3.0") == 0
    assert count_claude("", "4.7") == 0


# AC-01b
def test_count_claude_empty_4_8_is_one():
    assert count_claude("", "4.8") == 1


# AC-02
def test_count_claude_deterministic():
    text = "This is a deterministic test sentence for token counting."
    family = "4.7"
    first = count_claude(text, family)
    second = count_claude(text, family)
    assert first == second


# AC-03
def test_count_claude_4_7_greater_than_3_0_for_non_empty_text():
    text = (
        "Tokenization behavior differs across Claude model families. "
        "Newer families tend to produce more tokens for the same input text. "
        "This is a multi-sentence paragraph used to verify that relationship."
    )
    assert count_claude(text, "4.7") > count_claude(text, "3.0")


# AC-04
def test_count_claude_unknown_family_raises():
    for bad_family in ("5.0", "claude-3", ""):
        try:
            count_claude("some text", bad_family)
        except Exception:
            pass
        else:
            raise AssertionError(
                f"count_claude did not raise for unknown family {bad_family!r}"
            )


# AC-05
def test_count_claude_positive_and_grows_with_length():
    short_text = "Hello world."
    assert count_claude(short_text, "3.0") > 0
    assert count_claude(short_text, "3.0") < count_claude(short_text * 5, "3.0")


# AC-06
def test_frame_golden_values():
    assert FRAME["4.8"] == 5
    assert FRAME["3.0"] == 8
    assert FRAME["4.7"] == 12


# AC-07
def test_count_claude_total_empty_4_8_is_six():
    assert count_claude_total("", "4.8") == 6


# AC-08
def test_count_claude_total_equals_net_plus_frame_for_all_families():
    text = "Hello, this is a test sentence for tokenization."
    for family in FRAME:
        assert count_claude_total(text, family) == count_claude(text, family) + FRAME[family]


# AC-09
def test_count_claude_total_unknown_family_raises():
    try:
        count_claude_total("some text", "5.0")
    except Exception:
        pass
    else:
        raise AssertionError("count_claude_total did not raise for unknown family '5.0'")


# AC-10
def test_count_claude_total_deterministic_and_grows_with_length():
    short_text = "Hello world."
    family = "4.8"
    first = count_claude_total(short_text, family)
    second = count_claude_total(short_text, family)
    assert first == second
    assert count_claude_total(short_text, family) < count_claude_total(short_text * 5, family)


# AC-11
def test_count_openai_unchanged():
    text = "Hello, this is a test sentence for tokenization."
    encoding = "o200k_base"
    assert count_openai(text, encoding) > 0
    assert count_openai("", encoding) == 0
