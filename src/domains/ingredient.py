from pydantic import BaseModel


class Ingredient(BaseModel):
    raw_text: str
    normalized_key: str | None
