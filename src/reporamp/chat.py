
"""Interactive terminal chat for RepoRamp."""

from pathlib import Path

import typer

from reporamp.ollama_client import (
    DEFAULT_OLLAMA_MODEL,
    OllamaChatClient,
    OllamaClientError,
)


def run_chat(
    repository: Path,
    report_path: Path,
    model: str = DEFAULT_OLLAMA_MODEL,
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
    except OllamaClientError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.secho("\nRepoRamp Codebase Assistant", fg=typer.colors.BRIGHT_CYAN, bold=True)
    typer.echo(f"Repository: {repository.resolve()}")
    typer.echo(f"Model:      {model}")
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
