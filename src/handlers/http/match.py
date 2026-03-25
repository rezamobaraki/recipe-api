from fastapi import APIRouter, Depends

from src.core.container import container
from src.core.exceptions import IngredientNotFoundError
from src.schemas.requests import MatchRequest
from src.schemas.responses import MatchResponse, IngredientMatchResponse, ErrorResponse

router = APIRouter(prefix="/api", tags=["matches"])


@router.get(
    "/ingredient-matches",
    response_model=MatchResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_ingredient_matches(params: MatchRequest = Depends()) -> MatchResponse:
    result = container.match_service.get_matches(
        ingredient=params.ingredient,
        top_n=params.top_n,
    )
    return MatchResponse(
        ingredient=result.ingredient,
        matches=[
            IngredientMatchResponse(ingredient=m.ingredient, count=m.count)
            for m in result.matches
        ],
    )
