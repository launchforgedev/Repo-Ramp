from pathlib import Path

from typer.testing import CliRunner

from reporamp.cli import app

runner = CliRunner()


def test_chat_command_help():
    result = runner.invoke(app, ["chat", "--help"])

    assert result.exit_code == 0
    assert "--report" in result.output
    assert "--repository" in result.output
    assert "--model" in result.output


def test_ask_rejects_markdown_only_output(tmp_path: Path):
    result = runner.invoke(
        app,
        [
            "analyze",
            str(tmp_path),
            "--ask",
            "--format",
            "md",
        ],
    )

    assert result.exit_code != 0
    assert "--ask requires JSON output" in result.output


def test_existing_analyze_help_still_works():
    result = runner.invoke(app, ["analyze", "--help"])

    assert result.exit_code == 0
    assert "--ask" in result.output
    assert "--model" in result.output
    assert "--ai" in result.output
