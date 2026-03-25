from pydantic import BaseModel

from src.domains import IngredientMatch


class IngredientMatchResult(BaseModel):
    ingredient: str
    matches: list[IngredientMatch]
