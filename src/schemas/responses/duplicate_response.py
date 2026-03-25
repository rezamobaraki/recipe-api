from pydantic import BaseModel


class RecipeDuplicateResponse(BaseModel):
    name: str
    similarity: float


class DuplicateResponse(BaseModel):
    duplicates: list[RecipeDuplicateResponse]