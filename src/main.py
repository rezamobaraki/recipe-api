import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.core.containers import Containers
from src.core.exception_handler import setup_exception_handlers
from src.handlers.http import health, match, duplicate


def create_app() -> FastAPI:
    logging.basicConfig(
        level=Containers.settings.LOG_LEVEL,
        format=Containers.settings.LOG_FORMAT,
    )

    app = FastAPI(
        title="Recipe Intelligence API",
        version="0.1.0",
        description="Ingredient pairing and duplicate detection for Allrecipes dataset.",
    )

    app.include_router(health.router)
    app.include_router(match.router)
    app.include_router(duplicate.router)

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")

    setup_exception_handlers(app)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
