from src.core.settings import Settings
from src.repositories import PostgresRepository


class ContainerRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

        self.repository = PostgresRepository(self.settings.POSTGRES_URL)
        self.cache = CacheService(self.settings.REDIS_URL, self.settings.REDIS_TTL)

        self.match_service = MatchService(self.repository, self.cache)
        self.duplicate_service = DuplicateService(self.repository)
        self.ingest_service = IngestService(
            self.repository, self.settings.RECIPES_PATH, ...
        )
