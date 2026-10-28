
from pathlib import Path
from unittest.mock import Mock

import pytest
import typer

from reporamp.chat import run_chat, select_model
from reporamp.ollama_client import OllamaClientError


def test_missing_report_exits(tmp_path: Path):
    with pytest.raises(typer.Exit) as exc_info:
        run_chat(
            repository=tmp_path,
            report_path=tmp_path / "missing.json",
        )

    assert exc_info.value.exit_code == 1


def test_selects_explicit_model():
    client = Mock()

    selected = select_model(client, "llama3.2")

    assert selected == "llama3.2"
    client.list_models.assert_not_called()


def test_selects_only_installed_model(monkeypatch):
    client = Mock()
    client.list_models.return_value = ["llama3.2"]

    monkeypatch.setattr("typer.echo", lambda *args, **kwargs: None)

    selected = select_model(client, None)

    assert selected == "llama3.2"


def test_prompts_when_multiple_models_are_installed(monkeypatch):
    client = Mock()
    client.list_models.return_value = ["llama3.2", "qwen2.5-coder:3b"]
    monkeypatch.setattr("typer.echo", lambda *args, **kwargs: None)
    monkeypatch.setattr("typer.prompt", lambda *args, **kwargs: 2)

    selected = select_model(client, None)

    assert selected == "qwen2.5-coder:3b"


def test_reprompts_for_invalid_model_number(monkeypatch):
    client = Mock()
    client.list_models.return_value = ["llama3.2", "qwen2.5-coder:3b"]
    monkeypatch.setattr("typer.echo", lambda *args, **kwargs: None)

    choices = iter([0, 3, 1])
    monkeypatch.setattr("typer.prompt", lambda *args, **kwargs: next(choices))

    selected = select_model(client, None)

    assert selected == "llama3.2"


def test_exits_when_no_models_are_installed(monkeypatch):
    client = Mock()
    client.list_models.return_value = []
    monkeypatch.setattr("typer.echo", lambda *args, **kwargs: None)

    with pytest.raises(typer.Exit) as exc_info:
        select_model(client, None)

    assert exc_info.value.exit_code == 1


def test_exits_when_model_discovery_fails(monkeypatch):
    client = Mock()
    client.list_models.side_effect = OllamaClientError("Ollama unavailable")
    monkeypatch.setattr("typer.echo", lambda *args, **kwargs: None)

    with pytest.raises(typer.Exit) as exc_info:
        select_model(client, None)

    assert exc_info.value.exit_code == 1
