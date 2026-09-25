import sys

from tokmd.verify import MissingApiKeyError, count_verified, get_client, measure_frame


# AC-01
def test_get_client_raises_missing_api_key_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        get_client()
    except MissingApiKeyError as exc:
        assert "ANTHROPIC_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected MissingApiKeyError was not raised")


# AC-02
class FakeCountTokensResponse:
    def __init__(self, input_tokens):
        self.input_tokens = input_tokens


class FakeMessages:
    def __init__(self):
        self.calls = []

    def count_tokens(self, model=None, messages=None):
        self.calls.append((model, messages))
        content = messages[0]["content"]
        # BUG-001: measure_frame's minimal content changed from " " to "."
        # (a lone space is rejected by the real API; this fake never
        # validated it, which is exactly how the bug went undetected here).
        if content == ".":
            return FakeCountTokensResponse(5)
        return FakeCountTokensResponse(100)


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()


def test_measure_frame_returns_minimal_content_tokens():
    fake_client = FakeClient()
    result = measure_frame(fake_client, "claude-opus-5")
    assert result == 5


def test_count_verified_returns_real_tokens_minus_frame():
    fake_client = FakeClient()
    result = count_verified(fake_client, "some real text", "claude-opus-5", frame=5)
    assert result == 95


# AC-03
def test_no_real_anthropic_import_in_this_module():
    assert "anthropic" not in sys.modules
