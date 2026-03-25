from pydantic import BaseModel
from src.domains.recipe_duplicate import RecipeDuplicate

class RecipeDuplicateResult(BaseModel):
    duplicates: list[RecipeDuplicate]