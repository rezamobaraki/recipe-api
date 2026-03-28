import logging
import sys

from src.core.settings import SETTINGS
from src.handlers.cli.ingest import IngestCommand
from src.repositories import SQLiteRepository
from src.services import IngestService, IngredientKeyService


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]

    if args != ["ingest"]:
        raise SystemExit("Usage: python -m src.cli ingest")

    logging.basicConfig(
        level=SETTINGS.LOG_LEVEL,
        format=SETTINGS.LOG_FORMAT,
    )

    repository = SQLiteRepository(SETTINGS.SQLITE_DB_PATH)
    ingest_service = IngestService(
        repository=repository,
        recipes_path=SETTINGS.RECIPES_PATH,
        ingredient_key_service=IngredientKeyService(),
    )

    try:
        IngestCommand(ingest_service).run()
    finally:
        repository.close()


if __name__ == "__main__":
    main()
