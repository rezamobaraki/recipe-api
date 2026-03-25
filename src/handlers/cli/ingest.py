import typer

from src.core.containers import Containers

cli = typer.Typer()


@cli.command()
def ingest() -> None:
    Containers.ingest_service.run()
    typer.echo("✓ Ingest complete")
