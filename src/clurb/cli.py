"""Command line interface."""

from typer import Typer

app = Typer()


@app.command()
def prepare() -> None:
    """Prepare a paper for journal club."""
    ...
