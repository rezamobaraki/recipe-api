from src.core.settings import Settings, get_settings
from src.core.redis_cache import RedisCache
from src.repositories.postgres_repository import PostgresRepository
from src.services.match_service import MatchService
from src.services.duplicate_service import DuplicateService


class Container:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        self.cache = RedisCache(
            redis_url=self.settings.REDIS_URL,
            ttl=self.settings.REDIS_TTL,
        )

        self.repository = PostgresRepository(
            dsn=self.settings.POSTGRES_URL,
            cache=self.cache,
        )

        self.match_service = MatchService(self.repository)
        self.duplicate_service = DuplicateService(self.repository)


container = Container()