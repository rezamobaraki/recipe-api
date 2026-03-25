import logging
from typing import Iterable, Iterator

import psycopg2
import psycopg2.extras

from src.domains import (
    Ingredient,
    IngredientMatch,
    Recipe,
)
from src.repositories import RepositoryProtocol
from src.repositories.queries.postgres import (
    CREATE_RECIPES_TABLE,
    CREATE_INGREDIENTS_TABLE,
    CREATE_INGREDIENT_MATCH_TABLE,
    CREATE_INGREDIENT_MATCH_INDEX,
    BULK_INSERT_RECIPE,
    BULK_INSERT_INGREDIENT,
    BUILD_INGREDIENT_MATCHES,
    GET_INGREDIENT_MATCHES,
    SEARCH_RECIPES_BY_INGREDIENTS,
    SEARCH_RECIPES_BY_TITLE,
)

logger = logging.getLogger(__name__)


class PostgresRepository(RepositoryProtocol):
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._conn = None

    def _get_conn(self):
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
                psycopg2.extras.execute_values(
                    cur, BULK_INSERT_INGREDIENT, ingredient_rows
                )

        logger.info(
            "Inserted %d recipes, %d ingredients",
            len(recipe_rows),
            len(ingredient_rows),
        )
        return len(recipe_rows)

    def build_ingredient_matches(self) -> int:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(BUILD_INGREDIENT_MATCHES)
                count = cur.rowcount

        logger.info("Built ingredient match index: %d pairs", count)
        return count

    def get_ingredient_matches(
        self, ingredient: str, top_n: int = 10
    ) -> list[IngredientMatch]:
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

        return [IngredientMatch(**row) for row in rows]

    def search_recipes_by_ingredients(
        self, ingredients: list[str], limit: int = 20
    ) -> list[Recipe]:
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
