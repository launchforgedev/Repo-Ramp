
from types import SimpleNamespace

import pytest

from reporamp.ollama_client import (
    OllamaChatClient,
    OllamaClientError,
)


class FakeOllama:
    def __init__(self, chunks=None, error=None, models=None):
        self.chunks = chunks or []
        self.error = error
        self.models = models or []
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)

        if self.error is not None:
            raise self.error

        return iter(self.chunks)

    def list(self):
        return {"models": self.models}



def make_chunk(content):
    return SimpleNamespace(message=SimpleNamespace(content=content))


def test_streams_response_chunks():
    fake = FakeOllama(
        chunks=[
            make_chunk("There are "),
            make_chunk("three classes."),
        ]
    )
    chat = OllamaChatClient(model="test-model", client=fake)

    answer = "".join(
        chat.stream_answer(
            question="How many classes?",
            context="class A: ...\nclass B: ...\nclass C: ...",
        )
    )

    assert answer == "There are three classes."
    assert fake.calls[0]["model"] == "test-model"
    assert fake.calls[0]["stream"] is True


def test_passes_question_and_context_to_model():
    fake = FakeOllama(chunks=[make_chunk("Answer")])
    chat = OllamaChatClient(model="test-model", client=fake)

    list(
        chat.stream_answer(
            question="Explain app.py",
            context="app.py defines main().",
        )
    )

    messages = fake.calls[0]["messages"]

    assert messages[1]["content"] == "Explain app.py"
    assert "app.py defines main()" in messages[0]["content"]


def test_rejects_empty_question():
    chat = OllamaChatClient(
        model="test-model",
        client=FakeOllama(),
    )

    with pytest.raises(ValueError, match="Question cannot be empty"):
        list(chat.stream_answer(question="  ", context="some context"))


def test_wraps_ollama_errors():
    fake = FakeOllama(error=ConnectionError("server unavailable"))
    chat = OllamaChatClient(model="test-model", client=fake)

    with pytest.raises(OllamaClientError, match="Check that Ollama is running"):
        list(chat.stream_answer("Explain the project", "Project context"))


def test_rejects_empty_model():
    with pytest.raises(ValueError, match="model name cannot be empty"):
        OllamaChatClient(model="", client=FakeOllama())


def test_supports_dictionary_response_chunks():
    fake = FakeOllama(chunks=[{"message": {"content": "Dictionary response"}}])
    chat = OllamaChatClient(model="test-model", client=fake)

    answer = "".join(chat.stream_answer("Question", "Context"))

    assert answer == "Dictionary response"


def test_lists_installed_models():
    fake = FakeOllama(
        models=[
            {"model": "qwen2.5-coder:3b"},
            {"name": "llama3.2"},
            {"model": "qwen2.5-coder:3b"},
        ]
    )
    chat = OllamaChatClient(client=fake)

    assert chat.list_models() == [
        "llama3.2",
        "qwen2.5-coder:3b",
    ]


def test_lists_no_installed_models():
    chat = OllamaChatClient(client=FakeOllama())

    assert chat.list_models() == []
