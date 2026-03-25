import typer

from src.core.containers import container

cli = typer.Typer()


@cli.command()
def ingest() -> None:
    container.ingest_service.run()
    typer.echo("✓ Ingest complete")
