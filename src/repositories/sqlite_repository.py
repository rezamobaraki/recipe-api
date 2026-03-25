import logging
import sqlite3
from typing import Iterable

from src.core.redis_cache import RedisCache
from src.domains import Ingredient, IngredientMatch, Recipe
from .protocol import RepositoryProtocol
from src.repositories.queries.sqlite import (
    CREATE_TABLES,
    INSERT_RECIPE,
    INSERT_INGREDIENT,
    BUILD_MATCHES,
    GET_MATCHES,
    FIND_BY_INGREDIENTS,
    FIND_BY_TITLE,
)

logger = logging.getLogger(__name__)


class SQLiteRepository(RepositoryProtocol):
    def __init__(self, db_path: str, cache: RedisCache) -> None:
        self._db_path = db_path
        self._cache = cache

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self._get_conn() as conn:
            conn.executescript(CREATE_TABLES)
        logger.info("SQLite database initialized")

    def bulk_insert_recipes(self, recipes: Iterable[Recipe]) -> int:
        recipe_rows = []
        ingredient_rows = []

        for recipe in recipes:
            recipe_rows.append(
                (
                    recipe.id,
                    recipe.title,
                    recipe.name,
                    getattr(recipe, 'description', ''),
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
            conn.executemany(INSERT_RECIPE, recipe_rows)
            conn.executemany(INSERT_INGREDIENT, ingredient_rows)

        logger.info(f"Inserted {len(recipe_rows)} recipes, {len(ingredient_rows)} ingredients")
        return len(recipe_rows)

    def build_ingredient_matches(self) -> int:
        with self._get_conn() as conn:
            cursor = conn.execute(BUILD_MATCHES)
            count = cursor.rowcount
        logger.info(f"Built ingredient matches")
        return count or 0

    def get_ingredient_matches(self, ingredient: str, top_n: int = 10) -> list[IngredientMatch]:
        key = RedisCache.make_key("ingredient_match", ingredient=ingredient, top_n=top_n)

        if cached := self._cache.get(key):
            logger.debug(f"Cache hit for ingredient: {ingredient}")
            return [IngredientMatch(**item) for item in cached["matches"]]

        with self._get_conn() as conn:
            rows = conn.execute(GET_MATCHES, (ingredient, top_n)).fetchall()

        result = [IngredientMatch(ingredient=row["ingredient"], count=row["count"]) for row in rows]
        self._cache.set(key, {"matches": [r.model_dump() for r in result]})

        logger.debug(f"Cache set for ingredient: {ingredient}")
        return result

    def search_recipes_by_ingredients(self, ingredients: list[str], limit: int = 20) -> list[Recipe]:
        placeholders = ",".join("?" * len(ingredients))
        query = FIND_BY_INGREDIENTS.format(placeholders=placeholders)
        
        with self._get_conn() as conn:
            rows = conn.execute(query, ingredients + [limit]).fetchall()
        return [self._map_recipe(row) for row in rows]

    def search_recipes_by_title(self, title: str, limit: int = 20) -> list[Recipe]:
        with self._get_conn() as conn:
            rows = conn.execute(FIND_BY_TITLE, (f"%{title}%", limit)).fetchall()
        return [self._map_recipe(row) for row in rows]

    def _map_recipe(self, row: sqlite3.Row) -> Recipe:
        canonical_names = row["canonical_names"].split(",") if row["canonical_names"] else []
        raw_texts = row["raw_texts"].split(",") if row["raw_texts"] else []
        
        ingredients = [
            Ingredient(raw_text=raw, canonical_name=canonical)
            for raw, canonical in zip(raw_texts, canonical_names)
            if raw and canonical
        ]
        
        return Recipe(
            id=row["id"],
            title=row["title"],
            name=row["name"],
            ingredients=ingredients,
        )

    def close(self) -> None:
        logger.info("SQLite connection closed")