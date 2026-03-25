from typing import Iterable, Protocol

from src.domains import (
    IngredientMatch,
    Recipe,
)


class RepositoryProtocol(Protocol):
    def initialize(self) -> None: ...

    def bulk_insert_recipes(self, recipes: Iterable[Recipe]) -> int: ...

    def build_ingredient_matches(self) -> int: ...

    def get_ingredient_matches(
        self, ingredient: str, top_n: int = 10
    ) -> list[IngredientMatch]: ...

    def search_recipes_by_ingredients(
        self, ingredients: list[str], limit: int = 20
    ) -> list[Recipe]: ...

    def search_recipes_by_title(self, title: str, limit: int = 20) -> list[Recipe]: ...

    def close(self) -> None: ...
