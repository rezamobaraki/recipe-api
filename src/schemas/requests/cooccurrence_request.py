from fastapi import Query
from pydantic import BaseModel


class IngredientCooccurrenceRequest(BaseModel):
    ingredient: str = Query(..., min_length=1, description="Ingredient name to find co-occurring pairs for")
    limit: int = Query(default=10, ge=1, le=50, description="Number of co-occurring ingredients to return")
