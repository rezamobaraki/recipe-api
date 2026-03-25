from pydantic import BaseModel


class IngredientMatch(BaseModel):
    ingredient: str
    count: int