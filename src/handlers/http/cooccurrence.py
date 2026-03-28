from fastapi import APIRouter, Depends

from src.schemas.requests import IngredientCooccurrenceRequest
from src.schemas.responses import (
    ErrorResponse,
    IngredientCooccurrenceItemResponse,
    IngredientCooccurrenceResponse,
)
from src.services.cooccurrence_service import CooccurrenceService


class IngredientCooccurrenceHandler:
    def __init__(self, cooccurrence_service: CooccurrenceService) -> None:
        self._cooccurrence_service = cooccurrence_service
        self.router = APIRouter(prefix="/api", tags=["ingredients"])
        self.router.add_api_route(
            "/ingredient-cooccurrence",
            self.get_ingredient_cooccurrence,
            methods=["GET"],
            response_model=IngredientCooccurrenceResponse,
            responses={404: {"model": ErrorResponse}},
        )

    async def get_ingredient_cooccurrence(
        self,
        params: IngredientCooccurrenceRequest = Depends(),
    ) -> IngredientCooccurrenceResponse:
        result = self._cooccurrence_service.get_cooccurrences(
            ingredient=params.ingredient,
            limit=params.limit,
        )
        return IngredientCooccurrenceResponse(
            ingredient=result.ingredient,
            cooccurrence=[
                IngredientCooccurrenceItemResponse(
                    ingredient=item.ingredient,
                    count=item.count,
                )
                for item in result.cooccurrences
            ],
        )
