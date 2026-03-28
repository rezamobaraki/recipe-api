from pydantic import BaseModel


class DuplicateIngredient(BaseModel):
    name: str
    quantity: str


class RecipePayload(BaseModel):
    name: str
    ingredients: list[DuplicateIngredient]


class DuplicateRequest(BaseModel):
    recipe: RecipePayload
