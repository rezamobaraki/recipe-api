import os
from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))

    RECIPES_PATH: Path = Path(
        os.getenv(
            "RECIPES_PATH",
            str(DATA_DIR / "allrecipes.com_database_12042020000000.json"),
        )
    )
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "data" / "recipes.db"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


SETTINGS = Settings()
