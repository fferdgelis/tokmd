from tokmd.tokenizers import FRAME, count_claude


# AC-01
def test_empty_string_returns_zero_for_each_family():
    for family in FRAME:
        assert count_claude("", family) == 0


# AC-02
def test_deterministic_same_text_and_family():
    text = "This is a deterministic test sentence."
    family = "4.7"
    first = count_claude(text, family)
    second = count_claude(text, family)
    assert first == second


# AC-03
def test_4_7_greater_than_3_0_for_same_text():
    text = (
        "Claude is a family of large language models developed by Anthropic. "
        "These models are designed to be helpful, harmless, and honest. "
        "Tokenization is the process of splitting text into smaller units. "
        "Different model versions may tokenize the same text differently."
    )
    count_3_0 = count_claude(text, "3.0")
    count_4_7 = count_claude(text, "4.7")
    assert count_4_7 > count_3_0


# AC-04
def test_invalid_family_raises_exception():
    text = "Some text to tokenize."
    for invalid_family in ["5.0", "claude-3", ""]:
        try:
            count_claude(text, invalid_family)
        except Exception:
            pass
        else:
            raise AssertionError(
                f"Expected an exception for family {invalid_family!r}"
            )


# AC-05
def test_token_count_grows_with_text_length():
    short_text = "Hello world."
    repeated_text = short_text * 5
    short_count = count_claude(short_text, "3.0")
    repeated_count = count_claude(repeated_text, "3.0")
    assert short_count > 0
    assert short_count < repeated_count
