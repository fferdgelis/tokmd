from click.testing import CliRunner

from tokmd.cli import main


def test_claude_code_verify_skips_count_verified_for_whitespace_only_section(
    tmp_path, monkeypatch
):
    file = tmp_path / "doc.md"
    file.write_text("# Outer\n## Inner\n\nReal text under Inner.\n")

    calls = []

    class FakeClient:
        pass

    fake_client = FakeClient()

    monkeypatch.setattr("tokmd.cli.get_client", lambda: fake_client)
    monkeypatch.setattr("tokmd.cli.measure_frame", lambda client, model: 100)

    def fake_count_verified(client, text, model, frame):
        calls.append((client, text, model, frame))
        return 10

    monkeypatch.setattr("tokmd.cli.count_verified", fake_count_verified)

    runner = CliRunner()
    result = runner.invoke(
        main, [str(file), "--platform", "claude-code", "--verify"]
    )

    assert result.exit_code == 0
    assert calls, "expected at least one call to count_verified"
    for client, text, model, frame in calls:
        assert text.strip() != ""
