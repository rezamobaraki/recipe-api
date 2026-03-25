from pydantic import BaseModel


class Recipe(BaseModel):
    id: str
    title: str
    name: str
    ingredients: list[Ingredient]
