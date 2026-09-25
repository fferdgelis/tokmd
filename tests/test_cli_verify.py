from click.testing import CliRunner

from tokmd.cli import main


class _Recorder:
    def __init__(self, return_value):
        self.calls = []
        self.return_value = return_value

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.return_value


# AC-01
def test_codex_verify_fails_cleanly(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("# Title\n\nSome text.\n\n## Sub\n\nMore text here.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "codex", "--verify"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


# AC-02
def test_claude_code_verify_missing_api_key_fails_cleanly(tmp_path, monkeypatch):
    from tokmd.cli import MissingApiKeyError

    file = tmp_path / "sample.txt"
    file.write_text("# Title\n\nSome text.\n\n## Sub\n\nMore text here.\n")

    def fake_get_client():
        raise MissingApiKeyError("ANTHROPIC_API_KEY is not set. Please set it.")

    monkeypatch.setattr("tokmd.cli.get_client", fake_get_client)

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "claude-code", "--verify"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "ANTHROPIC_API_KEY" in result.output


# AC-03
def test_claude_code_verify_default_model_measure_frame(tmp_path, monkeypatch):
    file = tmp_path / "sample.txt"
    file.write_text("# Title\n\nSome text.\n\n## Sub\n\nMore text here.\n")

    measure_recorder = _Recorder(5)
    count_recorder = _Recorder(50)

    monkeypatch.setattr("tokmd.cli.get_client", lambda: object())
    monkeypatch.setattr("tokmd.cli.measure_frame", measure_recorder)
    monkeypatch.setattr("tokmd.cli.count_verified", count_recorder)

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "claude-code", "--verify"])
    assert result.exit_code == 0

    assert len(measure_recorder.calls) == 1
    args, kwargs = measure_recorder.calls[0]
    assert args[1] == "claude-sonnet-5"


# AC-04
def test_opencode_claude_model_verify_measure_frame(tmp_path, monkeypatch):
    file = tmp_path / "sample.txt"
    file.write_text("# Title\n\nSome text.\n\n## Sub\n\nMore text here.\n")

    measure_recorder = _Recorder(5)
    count_recorder = _Recorder(50)

    monkeypatch.setattr("tokmd.cli.get_client", lambda: object())
    monkeypatch.setattr("tokmd.cli.measure_frame", measure_recorder)
    monkeypatch.setattr("tokmd.cli.count_verified", count_recorder)

    runner = CliRunner()
    result = runner.invoke(
        main,
        [str(file), "--platform", "opencode", "--model", "claude-opus-5", "--verify"],
    )
    assert result.exit_code == 0

    assert len(measure_recorder.calls) == 1
    args, kwargs = measure_recorder.calls[0]
    assert args[1] == "claude-opus-5"


# AC-05
def test_claude_code_verify_count_verified_all_calls_default_model(tmp_path, monkeypatch):
    file = tmp_path / "sample.txt"
    file.write_text("# Title\n\nSome text.\n\n## Sub\n\nMore text here.\n")

    measure_recorder = _Recorder(5)
    count_recorder = _Recorder(50)

    monkeypatch.setattr("tokmd.cli.get_client", lambda: object())
    monkeypatch.setattr("tokmd.cli.measure_frame", measure_recorder)
    monkeypatch.setattr("tokmd.cli.count_verified", count_recorder)

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "claude-code", "--verify"])
    assert result.exit_code == 0

    assert len(count_recorder.calls) >= 1
    for args, kwargs in count_recorder.calls:
        assert args[2] == "claude-sonnet-5"
