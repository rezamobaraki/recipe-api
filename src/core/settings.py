from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR.parent / "data"

    #POSTGRES
    POSTGRES_URL: str = "postgresql://user:pass@localhost:5432/recipes"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600  # 1 hour cache

    # Data paths
    RECIPES_PATH: Path = ...
    INGREDIENTS_PATH: Path = ...

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
