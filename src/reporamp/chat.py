"""Interactive RepoRamp Ollama terminal."""

from pathlib import Path

import typer

from reporamp.ollama_client import (
    OllamaChatClient,
    OllamaClientError,
)


BANNER = r"""
 ____                  ____                             
|  _ \ ___ _ __   ___ |  _ \ __ _ _ __ ___  _ __  
| |_) / _ \ '_ \ / _ \| |_) / _` | '_ ` _ \| '_ \ 
|  _ <  __/ |_) | (_) |  __/ (_| | | | | | | |_) |
|_| \_\___| .__/ \___/|_|   \__,_|_| |_| |_| .__/ 
          |_|                               |_|    

          R E P O R A M P   O L L A M A
          LOCAL CODEBASE INTELLIGENCE
"""


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
            "No Ollama models are installed.\n"
            "Install one first, for example: ollama pull llama3.2",
            err=True,
        )
        raise typer.Exit(code=1)

    if len(models) == 1:
        typer.echo(f"Automatically selected model: {models[0]}")
        return models[0]

    typer.echo("\nInstalled Ollama models:")
    for index, name in enumerate(models, start=1):
        typer.echo(f"  [{index}] {name}")

    while True:
        choice = typer.prompt("Select model number", type=int)

        if 1 <= choice <= len(models):
            return models[choice - 1]

        typer.echo(
            f"Enter a number between 1 and {len(models)}.",
            err=True,
        )


def show_header(repository: Path, model: str, report_path: Path) -> None:
    """Display the branded terminal header and session details."""
    typer.secho(BANNER, fg=typer.colors.BRIGHT_CYAN, bold=True)

    typer.secho("  SESSION INFORMATION", fg=typer.colors.BRIGHT_WHITE, bold=True)
    typer.echo(f"  Repository : {repository.resolve()}")
    typer.echo(f"  Model      : {model}")
    typer.echo(f"  Report     : {report_path.resolve()}")
    typer.secho("  Connection : Ollama local runtime", fg=typer.colors.GREEN)
    typer.echo()
    typer.secho("  Type /help to see available commands.", fg=typer.colors.YELLOW)
    typer.echo("  " + "─" * 58)
    typer.echo()


def show_help() -> None:
    """Display available interactive commands."""
    typer.secho("\n  REporRAMP COMMANDS", fg=typer.colors.BRIGHT_CYAN, bold=True)
    typer.echo("  /help       Show this help menu")
    typer.echo("  /models     List locally installed Ollama models")
    typer.echo("  /model      Switch the active Ollama model")
    typer.echo("  /summary    Ask for a repository summary")
    typer.echo("  /exit       Close the Ollama terminal")
    typer.echo()


def change_model(client: OllamaChatClient) -> str:
    """Display installed models and switch the active model."""
    models = client.list_models()

    if not models:
        typer.echo("No models found. Install one using: ollama pull llama3.2")
        return client.model or ""

    typer.echo("\nInstalled models:")
    for index, name in enumerate(models, start=1):
        current = " (current)" if name == client.model else ""
        typer.echo(f"  [{index}] {name}{current}")

    while True:
        choice = typer.prompt("Select model number", type=int)

        if 1 <= choice <= len(models):
            selected = models[choice - 1]
            client.set_model(selected)
            typer.secho(
                f"\nActive model changed to: {selected}\n",
                fg=typer.colors.GREEN,
            )
            return selected

        typer.echo(
            f"Enter a number between 1 and {len(models)}.",
            err=True,
        )


def ask_question(client: OllamaChatClient, question: str, context: str) -> None:
    """Stream an answer from the selected Ollama model."""
    typer.secho("\n  RepoRamp Ollama", fg=typer.colors.GREEN, bold=True)
    typer.echo()

    try:
        for chunk in client.stream_answer(
            question=question,
            context=context,
        ):
            typer.echo(chunk, nl=False)

        typer.echo("\n")

    except OllamaClientError as exc:
        typer.echo(f"\nOllama error: {exc}", err=True)


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

    show_header(repository, selected_model, report_path)

    while True:
        try:
            question = typer.prompt(
                typer.style("RepoRamp", fg=typer.colors.BRIGHT_CYAN),
                prompt_suffix=" > ",
            ).strip()

        except (EOFError, KeyboardInterrupt):
            typer.echo("\nSession closed.")
            return

        if not question:
            continue

        command = question.lower()

        if command in {"/exit", "exit", "quit"}:
            typer.secho("\nRepoRamp Ollama session closed.", fg=typer.colors.YELLOW)
            return

        if command == "/help":
            show_help()
            continue

        if command == "/models":
            try:
                models = client.list_models()
                typer.echo("\nInstalled Ollama models:")
                for name in models:
                    marker = "  < active" if name == client.model else ""
                    typer.echo(f"  - {name}{marker}")
                typer.echo()
            except OllamaClientError as exc:
                typer.echo(f"Error: {exc}", err=True)
            continue

        if command == "/model":
            try:
                selected_model = change_model(client)
            except OllamaClientError as exc:
                typer.echo(f"Error: {exc}", err=True)
            continue

        if command == "/summary":
            question = (
                "Summarize this repository analysis. Explain its structure, "
                "important modules, dependencies, and notable findings. "
                "Only use information present in the report."
            )

        ask_question(client, question, context)
