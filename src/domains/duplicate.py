from pydantic import BaseModel, Field


class RecipeDuplicate(BaseModel):
    name: str
    similarity: float


class RecipeDuplicateResult(BaseModel):
    duplicates: list[RecipeDuplicate] = Field(default_factory=list)
