import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import IngredientNotFoundError, RecipeAPIError
from src.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(IngredientNotFoundError)
    async def ingredient_not_found_handler(
        request: Request, exc: IngredientNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                detail=str(exc),
                error_type="IngredientNotFoundError",
            ).model_dump(),
        )

    @app.exception_handler(RecipeAPIError)
    async def recipe_api_error_handler(
        request: Request, exc: RecipeAPIError
    ) -> JSONResponse:
        logger.error(f"Unexpected API error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                detail=str(exc),
                error_type="RecipeAPIError",
            ).model_dump(),
        )