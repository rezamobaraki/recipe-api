from pydantic import BaseModel


class IngredientCooccurrenceItemResponse(BaseModel):
    ingredient: str
    count: int


class IngredientCooccurrenceResponse(BaseModel):
    ingredient: str
    cooccurrence: list[IngredientCooccurrenceItemResponse]
