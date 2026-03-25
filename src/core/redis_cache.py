import json
import logging

import redis

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, redis_url: str, ttl: int) -> None:
        self._client = redis.from_url(redis_url)
        self._ttl = ttl

    def get(self, key: str) -> dict | None:
        try:
            value = self._client.get(key)
            if value is None:
                logger.debug(f"Cache miss: {key}")
                return None
            logger.debug(f"Cache hit: {key}")
            return json.loads(value)
        except redis.RedisError as e:
            logger.warning(f"Redis get failed, bypassing cache: {e}")
            return None

    def set(self, key: str, value: dict) -> None:
        try:
            self._client.setex(key, self._ttl, json.dumps(value))
        except redis.RedisError as e:
            logger.warning(f"Redis set failed, bypassing cache: {e}")

    @staticmethod
    def make_key(prefix: str, **kwargs) -> str:
        parts = ":".join(str(v) for v in kwargs.values())
        return f"{prefix}:{parts}"