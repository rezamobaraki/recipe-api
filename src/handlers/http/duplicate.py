from fastapi import APIRouter

from src.schemas.requests import DuplicateRequest
from src.schemas.responses import DuplicateResponse, RecipeDuplicateResponse
from src.services.duplicate_service import DuplicateService


class DuplicateHandler:
    def __init__(self, duplicate_service: DuplicateService) -> None:
        self._duplicate_service = duplicate_service
        self.router = APIRouter(prefix="/api", tags=["duplicates"])
        self.router.add_api_route(
            "/recipe-duplicates",
            self.find_recipe_duplicates,
            methods=["POST"],
            response_model=DuplicateResponse,
        )

    async def find_recipe_duplicates(self, body: DuplicateRequest) -> DuplicateResponse:
        result = self._duplicate_service.find_duplicates(
            name=body.recipe.name,
            ingredients=[ing.name for ing in body.recipe.ingredients],
        )
        return DuplicateResponse(
            duplicates=[
                RecipeDuplicateResponse(name=d.name, similarity=d.similarity)
                for d in result.duplicates
            ]
        )
