from click.testing import CliRunner

from tokmd.cli import main


def test_claude_code_platform_succeeds(tmp_path):
    # AC-01
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "claude-code"])

    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_codex_platform_succeeds(tmp_path):
    # AC-02
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "codex"])

    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_opencode_platform_without_model_fails_cleanly(tmp_path):
    # AC-03
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "opencode"])

    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_opencode_platform_with_claude_model_succeeds(tmp_path):
    # AC-04
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")

    runner = CliRunner()
    result = runner.invoke(
        main, [str(file), "--platform", "opencode", "--model", "claude-opus-5"]
    )

    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_antigravity_platform_fails_with_planned_message(tmp_path):
    # AC-05
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")

    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--platform", "antigravity"])

    assert result.exit_code == 2
    assert "Gemini tokenizer: planned for 1.1" in result.output


def test_tokenizer_override_wins_over_antigravity(tmp_path):
    # AC-06
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")

    runner = CliRunner()
    result = runner.invoke(
        main, [str(file), "--platform", "antigravity", "--tokenizer", "claude"]
    )

    assert result.exit_code == 0


# Gap: tools/deepseek/specs/PBI-004-gap-01.md.prompt
def test_tokenizer_override_openai_succeeds(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world. This is a test.")
    result = CliRunner().invoke(
        main,
        [str(file), "--platform", "claude-code", "--tokenizer", "openai"],
    )
    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_opencode_platform_with_gpt_model_succeeds(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world. This is a test.")
    result = CliRunner().invoke(
        main,
        [str(file), "--platform", "opencode", "--model", "gpt-5"],
    )
    assert result.exit_code == 0
    assert result.output.strip() != ""


def test_opencode_platform_with_unrecognized_model_fails_cleanly(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world. This is a test.")
    result = CliRunner().invoke(
        main,
        [str(file), "--platform", "opencode", "--model", "some-random-model"],
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_version_flag_succeeds():
    # AC-03 (PBI-007)
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == "1.0.0"

