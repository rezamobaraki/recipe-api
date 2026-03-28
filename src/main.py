import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.core.exception_handler import setup_exception_handlers
from src.core.settings import SETTINGS, Settings
from src.handlers.http import health
from src.handlers.http.cooccurrence import IngredientCooccurrenceHandler
from src.handlers.http.duplicate import DuplicateHandler
from src.repositories import SQLiteRepository
from src.services import CooccurrenceService, DuplicateService, IngredientKeyService


def create_app(
    settings: Settings | None = None,
    repository: SQLiteRepository | None = None,
    cooccurrence_service: CooccurrenceService | None = None,
    duplicate_service: DuplicateService | None = None,
) -> FastAPI:
    settings = settings or SETTINGS
    repository = repository or SQLiteRepository(settings.SQLITE_DB_PATH)
    repository.initialize()
    ingredient_key_service = IngredientKeyService()
    cooccurrence_service = cooccurrence_service or CooccurrenceService(
        repository=repository,
        ingredient_key_service=ingredient_key_service,
    )
    duplicate_service = duplicate_service or DuplicateService(repository)

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
            repository.close()

    app = FastAPI(
        title="Recipe Intelligence API",
        version="0.1.0",
        description="Ingredient pairing and duplicate detection for Allrecipes dataset.",
        lifespan=lifespan,
    )

    ingredient_handler = IngredientCooccurrenceHandler(cooccurrence_service)
    duplicate_handler = DuplicateHandler(duplicate_service)

    app.include_router(health.router)
    app.include_router(ingredient_handler.router)
    app.include_router(duplicate_handler.router)

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    setup_exception_handlers(app)

    return app


if __name__ == "__main__":
    uvicorn.run("src.main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)
