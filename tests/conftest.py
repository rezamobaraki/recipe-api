import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.repositories.sqlite_repository import SQLiteRepository
from src.services import CooccurrenceService, DuplicateService, IngestService, IngredientKeyService


@pytest.fixture
def sample_recipes() -> list[dict]:
    return [
        {
            "id": "1",
            "name": "spiced-milk",
            "title": "Spiced Milk",
            "description": "Warm milk with cinnamon",
            "ingredients": [
                "1 cup sugar",
                "1 teaspoon cinnamon",
                "1 cup milk",
            ],
        },
        {
            "id": "2",
            "name": "sweet-toast",
            "title": "Sweet Toast",
            "description": "Toast with cinnamon sugar",
            "ingredients": [
                "sugar",
                "cinnamon",
                "milk",
            ],
        },
        {
            "id": "3",
            "name": "savory-spice",
            "title": "Savory Spice",
            "description": "Cinnamon with salt",
            "ingredients": [
                "cinnamon",
                "salt",
            ],
        },
        {
            "id": "4",
            "name": "cinnamon-bun-bread",
            "title": "Cinnamon Bun Bread",
            "description": "Sweet cinnamon bread",
            "ingredients": [
                "3 cups all-purpose flour",
                "1 cup sugar",
                "2 teaspoons cinnamon",
                "1/2 cup butter",
            ],
        },
        {
            "id": "5",
            "name": "cinnamon-swirl-bread",
            "title": "Cinnamon Swirl Bread",
            "description": "Bread with cinnamon and vanilla",
            "ingredients": [
                "3 cups all-purpose flour",
                "1 cup sugar",
                "2 teaspoons cinnamon",
                "1/2 cup butter",
                "1 teaspoon vanilla extract",
            ],
        },
        {
            "id": "6",
            "name": "tomato-soup",
            "title": "Tomato Soup",
            "description": "Simple tomato soup",
            "ingredients": [
                "4 tomatoes",
                "1 onion",
                "1 teaspoon salt",
            ],
        },
    ]


@pytest.fixture
def ingredient_key_service() -> IngredientKeyService:
    return IngredientKeyService()


@pytest.fixture
def recipes_path(tmp_path, sample_recipes) -> Path:
    path = tmp_path / "recipes.json"
    path.write_text(json.dumps(sample_recipes), encoding="utf-8")
    return path


@pytest.fixture
def repository(tmp_path) -> SQLiteRepository:
    repo = SQLiteRepository(str(tmp_path / "recipes.db"))
    try:
        yield repo
    finally:
        repo.close()


@pytest.fixture
def ingest_service(
    repository: SQLiteRepository,
    recipes_path: Path,
    ingredient_key_service: IngredientKeyService,
) -> IngestService:
    return IngestService(
        repository=repository,
        recipes_path=recipes_path,
        ingredient_key_service=ingredient_key_service,
    )


@pytest.fixture
def ingested_repository(repository: SQLiteRepository, ingest_service: IngestService) -> SQLiteRepository:
    ingest_service.run()
    return repository


@pytest.fixture
def client(ingested_repository: SQLiteRepository, ingredient_key_service: IngredientKeyService) -> TestClient:
    app = create_app(
        repository=ingested_repository,
        cooccurrence_service=CooccurrenceService(
            repository=ingested_repository,
            ingredient_key_service=ingredient_key_service,
        ),
        duplicate_service=DuplicateService(ingested_repository),
    )
    with TestClient(app) as test_client:
        yield test_client
