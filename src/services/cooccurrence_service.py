import logging

from src.core.exceptions import IngredientNotFoundError
from src.domains import IngredientCooccurrenceResult
from src.repositories import SQLiteRepository
from src.services.ingredient_key_service import IngredientKeyService

logger = logging.getLogger(__name__)


class CooccurrenceService:
    def __init__(
        self,
        repository: SQLiteRepository,
        ingredient_key_service: IngredientKeyService,
    ) -> None:
        self._repository = repository
        self._ingredient_key_service = ingredient_key_service

    def get_cooccurrences(self, ingredient: str, limit: int = 10) -> IngredientCooccurrenceResult:
        normalized = self._ingredient_key_service.normalize_query(ingredient)
        if normalized is None:
            raise IngredientNotFoundError(f"No co-occurrences found for ingredient: '{ingredient}'")
        cooccurrences = self._repository.get_ingredient_cooccurrences(normalized, limit)

        if not cooccurrences:
            raise IngredientNotFoundError(f"No co-occurrences found for ingredient: '{ingredient}'")

        logger.info(f"Found {len(cooccurrences)} co-occurrences for '{normalized}'")

        return IngredientCooccurrenceResult(
            ingredient=normalized,
            cooccurrences=cooccurrences,
        )
