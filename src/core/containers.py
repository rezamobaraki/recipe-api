from src.core.settings import Settings, SETTINGS
from src.core.redis_cache import RedisCache
from src.repositories.postgres_repository import PostgresRepository
from src.repositories.sqlite_repository import SQLiteRepository
from src.services.match_service import MatchService
from src.services.duplicate_service import DuplicateService
from src.services.ingest_service import IngestService


class ContainerRegistry:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or SETTINGS

        self.cache = RedisCache(
            redis_url=self.settings.REDIS_URL,
            ttl=self.settings.REDIS_TTL,
        )

        # Choose database based on configuration
        if self.settings.DATABASE_TYPE.lower() == "sqlite":
            self.repository = SQLiteRepository(
                db_path=self.settings.SQLITE_DB_PATH,
                cache=self.cache,
            )
        else:
            self.repository = PostgresRepository(
                dsn=self.settings.POSTGRES_URL,
                cache=self.cache,
            )

        self.match_service = MatchService(self.repository)
        self.duplicate_service = DuplicateService(self.repository)
        self.ingest_service = IngestService(
            repository=self.repository,
            recipes_path=self.settings.RECIPES_PATH,
            ingredients_path=self.settings.INGREDIENTS_PATH,
        )


Containers = ContainerRegistry()
