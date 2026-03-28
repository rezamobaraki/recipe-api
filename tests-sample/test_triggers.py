from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.core import container as container_module
from src.handlers.http import capacity, health, triggers


@pytest.fixture
def app(repository, pipeline):
    app = FastAPI(title="Test")
    app.include_router(health.router)
    app.include_router(capacity.router)
    app.include_router(triggers.router)

    app.dependency_overrides[container_module.get_repository] = lambda: repository
    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_trigger_pipeline_endpoint(client):

    with patch("src.handlers.http.triggers.container.pipeline.run", new_callable=MagicMock) as mock_run:
        response = await client.post("/api/v1/commands/ingest")

        assert response.status_code == 202
        assert response.json()["status"] == "accepted"
