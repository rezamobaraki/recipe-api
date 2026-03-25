import logging

from src.domains import IngredientMatch, IngredientMatchResult
from src.core.exceptions import IngredientNotFoundError
from src.repositories import RepositoryProtocol

logger = logging.getLogger(__name__)


class MatchService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self._repository = repository

    def get_matches(self, ingredient: str, top_n: int = 10) -> IngredientMatchResult:
        normalized = ingredient.strip().lower()

        matches = self._repository.get_ingredient_matches(normalized, top_n)

        if not matches:
            raise IngredientNotFoundError(f"No matches found for ingredient: '{ingredient}'")

        logger.info(f"Found {len(matches)} matches for '{normalized}'")

        return IngredientMatchResult(
            ingredient=normalized,
            matches=matches,
        )
