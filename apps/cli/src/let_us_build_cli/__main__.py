"""`let-us-build` CLI. M0: `init` works; `start` is a scaffold (full boot lands in M2, LUB-003)."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer

app = typer.Typer(
    help="let-us-build — an AI software company in a box.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def init(
    directory: Path = typer.Option(Path("."), help="Project directory to scaffold config in."),
) -> None:
    """Scaffold local config: create .env from .env.example if it doesn't exist yet."""
    example = directory / ".env.example"
    env = directory / ".env"
    if not example.exists():
        typer.secho(f"No .env.example found in {directory.resolve()}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    if env.exists():
        typer.secho(".env already exists — leaving it untouched.", fg=typer.colors.YELLOW)
        return
    shutil.copyfile(example, env)
    typer.secho("Created .env — fill in your provider API keys.", fg=typer.colors.GREEN)


@app.command()
def start(
    port: int = typer.Option(8300, help="Core API port."),
    no_open: bool = typer.Option(False, "--no-open", help="Do not open the browser."),
    config: Path | None = typer.Option(None, help="Path to a .env config file."),
) -> None:
    """Boot the core API + web UI and open the browser.

    Scaffold only in M0: the full boot sequence (health checks, web server, browser, graceful
    shutdown) is implemented in M2 (LUB-003). For now, run the API directly with:
        uv run uvicorn lub_api.main:create_app --factory --port 8300
    """
    typer.secho(
        "start: full boot lands in M2 (LUB-003). "
        "Run the API meanwhile: uv run uvicorn lub_api.main:create_app --factory --port "
        f"{port}",
        fg=typer.colors.CYAN,
    )
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
