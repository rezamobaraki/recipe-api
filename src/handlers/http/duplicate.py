from fastapi import APIRouter

from src.core.container import container
from src.schemas.requests import DuplicateRequest
from src.schemas.responses import DuplicateResponse, RecipeDuplicateResponse

router = APIRouter(prefix="/api", tags=["duplicates"])


@router.post(
    "/recipe-duplicates",
    response_model=DuplicateResponse,
)
async def find_recipe_duplicates(body: DuplicateRequest) -> DuplicateResponse:
    result = container.duplicate_service.find_duplicates(
        name=body.recipe.name,
        ingredients=[ing.name for ing in body.recipe.ingredients],
    )
    return DuplicateResponse(
        duplicates=[
            RecipeDuplicateResponse(name=d.name, similarity=d.similarity)
            for d in result.duplicates
        ]
    )