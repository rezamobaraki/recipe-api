import logging
import math
import re
import unicodedata
from collections import Counter

from src.domains import Recipe, RecipeDuplicate, RecipeDuplicateResult
from src.repositories import SQLiteRepository

logger = logging.getLogger(__name__)


class DuplicateService:
    def __init__(self, repository: SQLiteRepository) -> None:
        self._repository = repository

    def find_duplicates(
        self,
        name: str,
        ingredients: list[str],
        top_n: int = 5,
    ) -> RecipeDuplicateResult:
        candidates = self._repository.list_recipes()
        if not candidates:
            return RecipeDuplicateResult()

        query_tokens = self._tokenize(self._build_text(name, ingredients))
        if not query_tokens:
            return RecipeDuplicateResult()

        candidate_tokens = [self._tokenize(self._build_recipe_text(candidate)) for candidate in candidates]
        idf = self._build_idf(candidate_tokens)
        query_vector = self._to_tfidf_vector(query_tokens, idf, len(candidate_tokens))

        scored = []
        for candidate, tokens in zip(candidates, candidate_tokens):
            score = self._cosine_similarity(query_vector, self._to_tfidf_vector(tokens, idf, len(candidate_tokens)))
            if score > 0:
                scored.append((candidate.title, round(score, 4)))

        scored.sort(key=lambda item: item[1], reverse=True)
        logger.info(f"Found {len(scored)} duplicate candidates for '{name}'")

        return RecipeDuplicateResult(
            duplicates=[RecipeDuplicate(name=title, similarity=score) for title, score in scored[:top_n]]
        )

    def _build_recipe_text(self, recipe: Recipe) -> str:
        return self._build_text(recipe.title, [ingredient.raw_text for ingredient in recipe.ingredients])

    def _build_text(self, title: str, ingredients: list[str]) -> str:
        return " ".join([title, *ingredients]).strip()

    def _tokenize(self, text: str) -> list[str]:
        normalized = unicodedata.normalize("NFKC", text).lower()
        return re.findall(r"[a-z0-9]+", normalized)

    def _build_idf(self, documents: list[list[str]]) -> dict[str, float]:
        document_count = len(documents)
        doc_frequency = Counter()
        for tokens in documents:
            doc_frequency.update(set(tokens))
        return {
            token: math.log((document_count + 1) / (count + 1)) + 1
            for token, count in doc_frequency.items()
        }

    def _to_tfidf_vector(
        self,
        tokens: list[str],
        idf: dict[str, float],
        document_count: int,
    ) -> dict[str, float]:
        if not tokens:
            return {}

        term_frequency = Counter(tokens)
        token_count = len(tokens)
        max_idf = math.log(document_count + 1) + 1

        return {
            token: (count / token_count) * idf.get(token, max_idf)
            for token, count in term_frequency.items()
        }

    def _cosine_similarity(self, left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0

        dot_product = sum(value * right.get(token, 0.0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))

        if left_norm == 0 or right_norm == 0:
            return 0.0

        return dot_product / (left_norm * right_norm)
