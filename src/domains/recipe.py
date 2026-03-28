from pydantic import BaseModel, Field

from src.domains.ingredient import Ingredient


class Recipe(BaseModel):
    id: str
    title: str
    name: str
    description: str = ""
    ingredients: list[Ingredient] = Field(default_factory=list)
