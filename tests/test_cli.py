import json
import os
import subprocess
import sys

import pytest
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


# --- PBI-009 (28/09/2026): --platform pasa a tener default "claude-code",
# la salida por defecto es el total (no el desglose), y BUG-011 (encoding
# de Windows).
#
# Autoría (ADR-006): escrito por DeepSeek (deepseek-v4-pro), rol TDD, a
# partir de tools/deepseek/specs/PBI-009-cli.md.prompt — el contrato
# público actualizado de tokmd.cli y los AC-01..09/AC-18/AC-19 de esa
# spec, SIN ver cli.py. Corrida real: 27/09/2026, costo USD 0,0023,
# thinking deshabilitado. Desarrollo (Claude) revisó el archivo generado
# y no lo editó.
#
# NOTA para quien implemente: test_version_flag_succeeds (arriba) espera
# "1.0.0"; este PBI sube la versión a "2.0.0" (decisión de Fabián,
# 27/09/2026). Ese test hay que actualizarlo aparte — es un dato de
# release, no una decisión de contrato de TDD.


# AC-01
def test_default_platform_no_missing_option(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")
    runner = CliRunner()
    result = runner.invoke(main, [str(file)])
    assert result.exit_code == 0
    assert "Missing option" not in result.output


# AC-02
def test_default_output_is_digits_only_and_matches_claude_code(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")
    runner = CliRunner()
    result_default = runner.invoke(main, [str(file)])
    result_explicit = runner.invoke(main, [str(file), "--platform", "claude-code"])
    assert result_default.exit_code == 0
    assert result_default.output.strip().isdigit()
    assert result_default.output == result_explicit.output


# AC-03
def test_omitting_platform_equals_explicit_claude_code(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")
    runner = CliRunner()
    result_omitted = runner.invoke(main, [str(file)])
    result_explicit = runner.invoke(main, [str(file), "--platform", "claude-code"])
    assert result_omitted.exit_code == 0
    assert result_explicit.exit_code == 0
    assert result_omitted.output == result_explicit.output


# AC-04
def test_explicit_codex_platform_not_overridden(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")
    runner = CliRunner()
    result_codex = runner.invoke(main, [str(file), "--platform", "codex"])
    result_claude = runner.invoke(main, [str(file), "--platform", "claude-code"])
    assert result_codex.exit_code == 0
    assert result_claude.exit_code == 0
    assert result_codex.output != result_claude.output


# AC-05
def test_sections_output_has_breakdown_and_total(tmp_path):
    file = tmp_path / "sample.md"
    file.write_text("# Title\nSome body text here.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--sections"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert len(lines) > 1
    assert any(line.strip().isdigit() for line in lines)


# AC-06
def test_json_format_without_sections_has_total_int(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello world, this is a test file with some text content.")
    runner = CliRunner()
    result = runner.invoke(main, [str(file), "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert "total" in parsed
    assert isinstance(parsed["total"], int)


# AC-07
def test_nonexistent_file_fails_cleanly():
    runner = CliRunner()
    result = runner.invoke(main, ["/no/such/file.md"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


def test_directory_path_fails_cleanly(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code != 0
    assert "Traceback" not in result.output


# AC-08
def test_no_headings_file_outputs_digits_only(tmp_path):
    file = tmp_path / "no_headings.md"
    file.write_text("Just a paragraph, no headings here at all.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(file)])
    assert result.exit_code == 0
    assert result.output.strip().isdigit()


# AC-09
def test_empty_file_outputs_zero(tmp_path):
    file = tmp_path / "empty.md"
    file.write_text("")
    runner = CliRunner()
    result = runner.invoke(main, [str(file)])
    assert result.exit_code == 0
    assert "Traceback" not in result.output
    assert result.output.strip() == "0"


# Gap: tools/deepseek/specs/PBI-009-cli-gap-01.md.prompt — write_text sin
# encoding="utf-8" rompía escribiendo el propio fixture en cp1252 (el
# default de esta máquina), antes de tocar el CLI. Corrida real:
# 27/09/2026, costo USD 0,0008.
@pytest.mark.skipif(sys.platform != "win32", reason="Windows encoding bug only")
@pytest.mark.parametrize("fmt", ["table", "md", "csv", "json"])
def test_windows_encoding_no_unicode_encode_error(tmp_path, fmt):
    file = tmp_path / "unicode_heading.md"
    file.write_text("## Flecha → « comillas » — guion\nBody text.\n", encoding="utf-8")
    env = os.environ.copy()
    env.pop("PYTHONIOENCODING", None)
    result = subprocess.run(
        ["tokmd", str(file), "--platform", "claude-code", "--sections", "--format", fmt],
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert "UnicodeEncodeError" not in stderr


@pytest.mark.skipif(sys.platform != "win32", reason="Windows encoding bug only")
def test_windows_encoding_arrow_survives(tmp_path):
    file = tmp_path / "unicode_heading.md"
    file.write_text("## Flecha → « comillas » — guion\nBody text.\n", encoding="utf-8")
    env = os.environ.copy()
    env.pop("PYTHONIOENCODING", None)
    result = subprocess.run(
        ["tokmd", str(file), "--platform", "claude-code", "--sections", "--format", "table"],
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0
    stdout = result.stdout.decode("utf-8")
    assert "→" in stdout

