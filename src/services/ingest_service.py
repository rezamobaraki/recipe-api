import json
import logging
import re
from collections.abc import Iterator
from pathlib import Path

from src.domains import Ingredient, Recipe
from src.repositories import SQLiteRepository
from src.services.ingredient_key_service import IngredientKeyService

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(
        self,
        repository: SQLiteRepository,
        recipes_path: Path,
        ingredient_key_service: IngredientKeyService,
    ) -> None:
        self._repository = repository
        self._recipes_path = recipes_path
        self._ingredient_key_service = ingredient_key_service

    def run(self) -> None:
        self._repository.initialize()
        self._repository.reset_recipe_data()

        count = self._repository.bulk_insert_recipes(self._parse_recipes())
        logger.info(f"Inserted {count} recipes")

        cooccurrence_count = self._repository.build_ingredient_cooccurrences()
        logger.info(f"Built {cooccurrence_count} ingredient co-occurrence pairs")

    def _parse_recipes(self) -> Iterator[Recipe]:
        content = self._recipes_path.read_text(encoding="utf-8")
        content = re.sub(r",\s*]", "]", content)

        for raw in json.loads(content):
            ingredients = [
                Ingredient(
                    raw_text=raw_text,
                    normalized_key=self._ingredient_key_service.normalize(raw_text),
                )
                for raw_text in raw.get("ingredients", [])
            ]
            yield Recipe(
                id=raw["id"],
                title=raw.get("title") or raw.get("name", ""),
                name=raw.get("name", ""),
                description=raw.get("description") or "",
                ingredients=ingredients,
            )
