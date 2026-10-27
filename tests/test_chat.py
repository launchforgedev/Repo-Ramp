from pathlib import Path

import pytest
import typer

from reporamp.chat import run_chat


def test_missing_report_exits(tmp_path: Path):
    with pytest.raises(typer.Exit) as exc_info:
        run_chat(
            repository=tmp_path,
            report_path=tmp_path / "missing.json",
        )

    assert exc_info.value.exit_code == 1
