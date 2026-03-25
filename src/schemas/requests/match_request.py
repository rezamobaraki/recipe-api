from fastapi import Query
from pydantic import BaseModel


class MatchRequest(BaseModel):
    ingredient: str = Query(..., min_length=1, description="Ingredient name to find matches for")
    top_n: int = Query(default=10, ge=1, le=50, description="Number of matches to return")