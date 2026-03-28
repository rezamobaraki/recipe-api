from pydantic import BaseModel, Field


class IngredientCooccurrence(BaseModel):
    ingredient: str
    count: int


class IngredientCooccurrenceResult(BaseModel):
    ingredient: str
    cooccurrences: list[IngredientCooccurrence] = Field(default_factory=list)
