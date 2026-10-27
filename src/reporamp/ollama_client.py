"""Client for generating local codebase answers with Ollama."""

from collections.abc import Iterator
from typing import Any

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:3b"


class OllamaClientError(RuntimeError):
    """Raised when RepoRamp cannot obtain a response from Ollama."""


class OllamaChatClient:
    """Generate streaming responses using a local Ollama model."""

    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_MODEL,
        host: str = DEFAULT_OLLAMA_HOST,
        timeout: float = 120.0,
        client: Any | None = None,
    ) -> None:
        if not model.strip():
            raise ValueError("Ollama model name cannot be empty.")

        if not host.strip():
            raise ValueError("Ollama host cannot be empty.")

        self.model = model
        self.host = host
        self.timeout = timeout

        if client is None:
            try:
                import ollama
            except ImportError as exc:
                raise OllamaClientError(
                    "Ollama support is not installed. Run "
                    'pip install "reporamp[ollama]".'
                ) from exc

            client = ollama.Client(host=host, timeout=timeout)

        self._client = client

    def stream_answer(
        self,
        question: str,
        context: str,
        system_prompt: str = (
            "You are RepoRamp, a Python codebase assistant. "
            "Answer using the supplied repository context. "
            "Do not invent functions, classes, files, or metrics. "
            "If the context is insufficient, say what is missing."
        ),
    ) -> Iterator[str]:
        """Yield response text incrementally from the selected model."""
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        messages = [
            {
                "role": "system",
                "content": f"{system_prompt}\n\nRepository context:\n{context}",
            },
            {"role": "user", "content": question},
        ]

        try:
            response_stream = self._client.chat(
                model=self.model,
                messages=messages,
                stream=True,
            )

            for chunk in response_stream:
                message = getattr(chunk, "message", None)

                if message is None and isinstance(chunk, dict):
                    message = chunk.get("message", {})

                if isinstance(message, dict):
                    content = message.get("content", "")
                else:
                    content = getattr(message, "content", "")

                if content:
                    yield content

        except Exception as exc:
            raise OllamaClientError(
                f"Could not get a response from Ollama at {self.host}. "
                "Check that Ollama is running, the model is installed, "
                f"and the request is valid. Details: {exc}"
            ) from exc
