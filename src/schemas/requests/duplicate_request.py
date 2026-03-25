from pydantic import BaseModel


class DuplicateIngredient(BaseModel):
    name: str
    quantity: str


class DuplicateRequest(BaseModel):
    recipe: RecipePayload


class RecipePayload(BaseModel):
    name: str
    ingredients: list[DuplicateIngredient]