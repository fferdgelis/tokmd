import pytest
import tiktoken

from tokmd.tokenizers import OPENAI_ENCODINGS, count_openai


# AC-01
def test_count_openai_o200k_matches_tiktoken_exactly():
    text = (
        "The quick brown fox jumps over the lazy dog. "
        "Pack my box with five dozen liquor jugs. "
        "How vexingly quick daft zebras jump!"
    )
    expected = len(tiktoken.get_encoding("o200k_base").encode(text))
    assert count_openai(text, "o200k_base") == expected


# AC-02 (corregido, ver tools/deepseek/specs/PBI-003-gap-01.md.prompt: la
# aditividad exacta que asumia el PBI-003 original es falsa, medido).
def test_count_openai_additivity_is_not_guaranteed():
    parts = [
        "The quick brown fox jumps over the lazy dog. ",
        "Pack my box with five dozen liquor jugs. ",
        "How vexingly quick daft zebras jump! ",
        "Sphinx of black quartz, judge my vow.",
    ]
    joined = "".join(parts)

    per_part_sum = sum(count_openai(p, "o200k_base") for p in parts)
    whole_count = count_openai(joined, "o200k_base")

    assert per_part_sum == 43
    assert whole_count == 40
    assert per_part_sum != whole_count


# AC-03
def test_count_openai_cl100k_matches_encoding_for_model_gpt4():
    text = (
        "A journey of a thousand miles begins with a single step. "
        "To be or not to be, that is the question. "
        "All that glitters is not gold."
    )
    expected = len(tiktoken.encoding_for_model("gpt-4").encode(text))
    assert count_openai(text, "cl100k_base") == expected


# AC-04 (corregido: SonarQube marco pytest.raises(Exception) como demasiado
# amplio, tools/deepseek/specs/PBI-003-gap-02.md.prompt)
def test_count_openai_invalid_encoding_raises():
    with pytest.raises(ValueError):
        count_openai("some text", "not-a-real-encoding")


# AC-05
def test_count_openai_empty_text_returns_zero():
    assert count_openai("", "o200k_base") == 0
