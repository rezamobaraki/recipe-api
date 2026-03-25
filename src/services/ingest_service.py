import json
import logging
import re
from pathlib import Path
from typing import cast

from src.domains import Ingredient, Recipe
from src.repositories import RepositoryProtocol

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(
        self,
        repository: RepositoryProtocol,
        recipes_path: Path,
        ingredients_path: Path,
    ) -> None:
        self._repository = repository
        self._recipes_path = recipes_path
        self._ingredients_path = ingredients_path
        self._known_terms: list[str] = []

    def run(self) -> None:
        logger.info(f"Starting ingest from {self._recipes_path}")

        self._known_terms = self._load_known_terms()
        logger.info(f"Loaded {len(self._known_terms)} known ingredient terms")

        recipes = list(self._parse_recipes())
        count = self._repository.bulk_insert_recipes(recipes)
        logger.info(f"Inserted {count} recipes")

        match_count = self._repository.build_ingredient_matches()
        logger.info(f"Built {match_count} ingredient match pairs")

    def _load_known_terms(self) -> list[str]:
        raw = json.loads(self._ingredients_path.read_text(encoding="utf-8"))
        terms = [entry["term"].strip().lower() for entry in raw]
        # longest-first so "black pepper" matches before "pepper"
        return cast(list[str], sorted(terms, key=len, reverse=True))

    def _parse_recipes(self):
        content = self._recipes_path.read_text(encoding="utf-8")
        # fix trailing comma quirk in Allrecipes export
        content = re.sub(r",\s*]", "]", content)
        raw_recipes = json.loads(content)

        for raw in raw_recipes:
            ingredients = [
                Ingredient(
                    raw_text=raw_text,
                    canonical_name=self._extract_canonical(raw_text),
                )
                for raw_text in raw.get("ingredients", [])
            ]
            yield Recipe(
                id=raw["id"],
                title=raw.get("title") or raw.get("name", ""),
                name=raw.get("name", ""),
                ingredients=ingredients,
            )

    def _extract_canonical(self, raw: str) -> str | None:
        text = raw.lower().strip()

        # strip leading quantities and units
        text = re.sub(r"^[\d\s/¼½¾⅓⅔⅛⅜⅝⅞,.-]+", "", text).strip()
        text = re.sub(
            r"^(cups?|tablespoons?|tbsp|teaspoons?|tsp|ounces?|oz|pounds?|lbs?|"
            r"grams?|kg|liters?|ml|pinch(?:es)?|cloves?|slices?|pieces?|cans?|"
            r"large|medium|small|fresh|dried|ground|whole|chopped|minced|"
            r"sliced|diced|cooked|optional)\s+",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

        return next(
            (term for term in self._known_terms if term in text),
            None,
        )
