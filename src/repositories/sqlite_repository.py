import logging
import sqlite3
from pathlib import Path
from typing import Iterable

from src.domains import Ingredient, IngredientCooccurrence, Recipe
from src.repositories.queries import (
    BUILD_COOCCURRENCES,
    CREATE_TABLES,
    GET_COOCCURRENCES,
    INSERT_INGREDIENT,
    INSERT_RECIPE,
    LIST_RECIPES,
    RESET_RECIPE_DATA,
)

logger = logging.getLogger(__name__)


class SQLiteRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self._get_conn() as conn:
            conn.executescript(CREATE_TABLES)
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(recipe_ingredients)").fetchall()
            }
            if "normalized_key" not in columns:
                conn.execute("ALTER TABLE recipe_ingredients ADD COLUMN normalized_key TEXT")
                if "canonical_name" in columns:
                    conn.execute(
                        """
                        UPDATE recipe_ingredients
                        SET normalized_key = canonical_name
                        WHERE normalized_key IS NULL
                        """
                    )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_normalized_key
                ON recipe_ingredients(normalized_key)
                """
            )
            legacy_table_exists = conn.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = 'ingredient_match'
                """
            ).fetchone()
            if legacy_table_exists:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO ingredient_cooccurrence (ingredient_a, ingredient_b, count)
                    SELECT ingredient_a, ingredient_b, count
                    FROM ingredient_match
                    """
                )
        logger.info("SQLite database initialized")

    def reset_recipe_data(self) -> None:
        with self._get_conn() as conn:
            conn.executescript(RESET_RECIPE_DATA)
        logger.info("SQLite recipe data reset")

    def bulk_insert_recipes(self, recipes: Iterable[Recipe]) -> int:
        recipe_rows = []
        ingredient_rows = []

        for recipe in recipes:
            recipe_rows.append(
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "name": recipe.name,
                    "description": recipe.description,
                }
            )
            for ing in recipe.ingredients:
                ingredient_rows.append(
                    {
                        "recipe_id": recipe.id,
                        "raw_text": ing.raw_text,
                        "normalized_key": ing.normalized_key,
                    }
                )

        with self._get_conn() as conn:
            conn.executemany(INSERT_RECIPE, recipe_rows)
            conn.executemany(INSERT_INGREDIENT, ingredient_rows)

        logger.info(f"Inserted {len(recipe_rows)} recipes, {len(ingredient_rows)} ingredients")
        return len(recipe_rows)

    def build_ingredient_cooccurrences(self) -> int:
        with self._get_conn() as conn:
            cursor = conn.execute(BUILD_COOCCURRENCES)
            count = cursor.rowcount
        logger.info("Built ingredient co-occurrences")
        return count or 0

    def get_ingredient_cooccurrences(
        self,
        ingredient: str,
        limit: int = 10,
    ) -> list[IngredientCooccurrence]:
        with self._get_conn() as conn:
            rows = conn.execute(
                GET_COOCCURRENCES,
                {
                    "ingredient": ingredient,
                    "limit": limit,
                },
            ).fetchall()

        return [IngredientCooccurrence(ingredient=row["ingredient"], count=row["count"]) for row in rows]

    def list_recipes(self) -> list[Recipe]:
        with self._get_conn() as conn:
            rows = conn.execute(LIST_RECIPES).fetchall()
        return [self._map_recipe(row) for row in rows]

    def _map_recipe(self, row: sqlite3.Row) -> Recipe:
        normalized_keys = row["normalized_keys"].split(",") if row["normalized_keys"] else []
        raw_texts = row["raw_texts"].split(",") if row["raw_texts"] else []

        ingredients = [
            Ingredient(raw_text=raw, normalized_key=normalized_key)
            for raw, normalized_key in zip(raw_texts, normalized_keys)
            if raw
        ]

        return Recipe(
            id=row["id"],
            title=row["title"],
            name=row["name"],
            description=row["description"],
            ingredients=ingredients,
        )

    def close(self) -> None:
        logger.info("SQLite connection closed")
