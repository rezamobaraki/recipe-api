import logging
from typing import Iterable

import psycopg2
import psycopg2.extras

from src.core.redis_cache import RedisCache
from src.domains import Ingredient, IngredientMatch, Recipe
from .protocol import RepositoryProtocol
from src.repositories.queries.postgres import (
    BUILD_INGREDIENT_MATCHES,
    BULK_INSERT_INGREDIENT,
    BULK_INSERT_RECIPE,
    CREATE_INGREDIENT_MATCH_INDEX,
    CREATE_INGREDIENT_MATCH_TABLE,
    CREATE_INGREDIENTS_TABLE,
    CREATE_RECIPES_TABLE,
    GET_INGREDIENT_MATCHES,
    SEARCH_RECIPES_BY_INGREDIENTS,
    SEARCH_RECIPES_BY_TITLE,
)

logger = logging.getLogger(__name__)


class PostgresRepository(RepositoryProtocol):
    def __init__(self, dsn: str, cache: RedisCache) -> None:
        self._dsn = dsn
        self._cache = cache
        self._conn: psycopg2.extensions.connection | None = None

    def _get_conn(self) -> psycopg2.extensions.connection:
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self._dsn)
        return self._conn

    def initialize(self) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_RECIPES_TABLE)
                cur.execute(CREATE_INGREDIENTS_TABLE)
                cur.execute(CREATE_INGREDIENT_MATCH_TABLE)
                cur.execute(CREATE_INGREDIENT_MATCH_INDEX)
        logger.info("Database initialized")

    def bulk_insert_recipes(self, recipes: Iterable[Recipe]) -> int:
        recipe_rows = []
        ingredient_rows = []

        for recipe in recipes:
            recipe_rows.append(
                (
                    recipe.id,
                    recipe.title,
                    recipe.name,
                    recipe.description,
                )
            )
            for ing in recipe.ingredients:
                ingredient_rows.append(
                    (
                        recipe.id,
                        ing.raw_text,
                        ing.canonical_name,
                    )
                )

        with self._get_conn() as conn:
            with conn.cursor() as cur:
                psycopg2.extras.execute_values(cur, BULK_INSERT_RECIPE, recipe_rows)
                psycopg2.extras.execute_values(cur, BULK_INSERT_INGREDIENT, ingredient_rows)

        logger.info(f"Inserted {len(recipe_rows)} recipes, {len(ingredient_rows)} ingredients")
        return len(recipe_rows)

    def build_ingredient_matches(self) -> int:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(BUILD_INGREDIENT_MATCHES)
                count = cur.rowcount

        logger.info(f"Built {count} ingredient match pairs")
        return count

    def get_ingredient_matches(self, ingredient: str, top_n: int = 10) -> list[IngredientMatch]:
        key = RedisCache.make_key("ingredient_match", ingredient=ingredient, top_n=top_n)

        if cached := self._cache.get(key):
            logger.debug(f"Cache hit for ingredient: {ingredient}")
            return [IngredientMatch(**item) for item in cached["matches"]]

        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    GET_INGREDIENT_MATCHES,
                    {
                        "ingredient": ingredient,
                        "top_n": top_n,
                    },
                )
                rows = cur.fetchall()

        result = [IngredientMatch(**row) for row in rows]
        self._cache.set(key, {"matches": [r.model_dump() for r in result]})

        logger.debug(f"Cache set for ingredient: {ingredient}")
        return result

    def search_recipes_by_ingredients(self, ingredients: list[str], limit: int = 20) -> list[Recipe]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    SEARCH_RECIPES_BY_INGREDIENTS,
                    {
                        "ingredients": ingredients,
                        "limit": limit,
                    },
                )
                rows = cur.fetchall()

        return [self._map_recipe(row) for row in rows]

    def search_recipes_by_title(self, title: str, limit: int = 20) -> list[Recipe]:
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    SEARCH_RECIPES_BY_TITLE,
                    {
                        "title": f"%{title}%",
                        "limit": limit,
                    },
                )
                rows = cur.fetchall()

        return [self._map_recipe(row) for row in rows]

    def _map_recipe(self, row: dict) -> Recipe:
        ingredients = [
            Ingredient(raw_text=raw, canonical_name=canonical)
            for raw, canonical in zip(
                row["raw_texts"] or [],
                row["canonical_names"] or [],
            )
        ]
        return Recipe(
            id=row["id"],
            title=row["title"],
            name=row["name"],
            ingredients=ingredients,
        )

    def close(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()
            logger.info("Database connection closed")
