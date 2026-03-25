from pydantic import BaseModel


class RecipeDuplicate(BaseModel):
    name: str
    similarity: float