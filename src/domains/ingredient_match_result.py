class IngredientMatchResult(BaseModel):
    ingredient: str
    matches: list[IngredientMatch]
