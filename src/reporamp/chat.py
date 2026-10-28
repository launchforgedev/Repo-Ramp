
"""Interactive terminal chat for RepoRamp."""

from pathlib import Path

import typer

from reporamp.ollama_client import (
    OllamaChatClient,
    OllamaClientError,
)


def select_model(client: OllamaChatClient, model: str | None) -> str:
    """Select an explicitly requested model or prompt from installed models."""
    if model is not None:
        if not model.strip():
            typer.echo("Error: model name cannot be empty.", err=True)
            raise typer.Exit(code=1)
        return model.strip()

    try:
        models = client.list_models()
    except OllamaClientError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if not models:
        typer.echo(
            "Error: no Ollama models are installed.\n"
            "Install one first, for example: ollama pull llama3.2",
            err=True,
        )
        raise typer.Exit(code=1)

    if len(models) == 1:
        typer.echo(f"Automatically selected installed model: {models[0]}")
        return models[0]

    typer.echo("\nInstalled Ollama models:")
    for index, name in enumerate(models, start=1):
        typer.echo(f"  {index}. {name}")

    while True:
        choice = typer.prompt(
            "Choose a model number",
            type=int,
        )

        if 1 <= choice <= len(models):
            selected = models[choice - 1]
            typer.echo(f"Selected model: {selected}")
            return selected

        typer.echo(
            f"Please enter a number between 1 and {len(models)}.",
            err=True,
        )


def run_chat(
    repository: Path,
    report_path: Path,
    model: str | None = None,
) -> None:
    """Start an interactive chat about an analyzed repository."""
    if not report_path.is_file():
        typer.echo(
            f"Error: analysis report not found: {report_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        context = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        typer.echo(f"Error reading report: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    try:
        client = OllamaChatClient(model=model)
        selected_model = select_model(client, model)
        client.set_model(selected_model)
    except OllamaClientError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.secho(
        "\nRepoRamp Codebase Assistant",
        fg=typer.colors.BRIGHT_CYAN,
        bold=True,
    )
    typer.echo(f"Repository: {repository.resolve()}")
    typer.echo(f"Model:      {selected_model}")
    typer.echo("Ask questions about the analyzed codebase.")
    typer.echo("Commands: exit, quit\n")

    while True:
        try:
            question = typer.prompt("You", prompt_suffix=" > ").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo("\nChat closed.")
            return

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            typer.echo("Chat closed.")
            return

        typer.secho("\nRepoRamp > ", fg=typer.colors.GREEN, bold=True)

        try:
            for chunk in client.stream_answer(
                question=question,
                context=context,
            ):
                typer.echo(chunk, nl=False)
            typer.echo("\n")
        except OllamaClientError as exc:
            typer.echo(f"\nOllama error: {exc}", err=True)
