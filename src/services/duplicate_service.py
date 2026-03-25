import logging
from difflib import SequenceMatcher

from src.domains import Recipe, RecipeDuplicate, RecipeDuplicateResult
from src.repositories import RepositoryProtocol

logger = logging.getLogger(__name__)

TITLE_WEIGHT = 0.35
INGREDIENT_WEIGHT = 0.65


class DuplicateService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self._repository = repository

    def find_duplicates(
        self,
        name: str,
        ingredients: list[str],
        top_n: int = 5,
    ) -> RecipeDuplicateResult:
        query_set = set(ingredients)

        candidates = self._repository.search_recipes_by_ingredients(ingredients)

        if not candidates:
            candidates = self._repository.search_recipes_by_title(name)

        scored = [(candidate.title, self._score(name, query_set, candidate)) for candidate in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"Found {len(scored)} duplicate candidates for '{name}'")

        return RecipeDuplicateResult(
            duplicates=[RecipeDuplicate(name=title, similarity=score) for title, score in scored[:top_n]]
        )

    def _score(self, name: str, query_set: set[str], candidate: Recipe) -> float:
        title_sim = SequenceMatcher(None, name.lower(), candidate.title.lower()).ratio()

        candidate_set = {ing.canonical_name for ing in candidate.ingredients if ing.canonical_name}
        jaccard = len(query_set & candidate_set) / len(query_set | candidate_set) if query_set | candidate_set else 0.0

        return round(TITLE_WEIGHT * title_sim + INGREDIENT_WEIGHT * jaccard, 4)
