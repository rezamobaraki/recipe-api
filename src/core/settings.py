from pathlib import Path
from functools import cache


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    RECIPES_PATH: Path = DATA_DIR / "allrecipes-sample.json"
    INGREDIENTS_PATH: Path = DATA_DIR / "ingredient-list.json"

    POSTGRES_URL: str = "postgresql://user:pass@localhost:5432/recipes"

    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600


settings = Settings()

