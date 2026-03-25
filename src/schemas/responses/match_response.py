from pydantic import BaseModel


class IngredientMatchResponse(BaseModel):
    ingredient: str
    count: int


class MatchResponse(BaseModel):
    ingredient: str
    matches: list[IngredientMatchResponse]