from src.repositories.sqlite_repository import SQLiteRepository


class TestTask1Ingest:
    def test_builds_recipe_level_cooccurrence_counts(self, ingested_repository: SQLiteRepository) -> None:
        cooccurrences = ingested_repository.get_ingredient_cooccurrences("cinnamon")
        counts = {item.ingredient: item.count for item in cooccurrences}

        assert counts["sugar"] == 4
        assert counts["milk"] == 2
        assert counts["all-purpose flour"] == 2
        assert counts["butter"] == 2
        assert counts["salt"] == 1


class TestTask1Api:
    def test_endpoint_normalizes_query_input(self, client) -> None:
        response = client.get(
            "/api/ingredient-cooccurrence",
            params={"ingredient": "1 teaspoon cinnamon", "limit": 6},
        )

        body = response.json()

        assert response.status_code == 200
        assert body["ingredient"] == "cinnamon"
        assert body["cooccurrence"][0] == {"ingredient": "sugar", "count": 4}
        assert {item["ingredient"]: item["count"] for item in body["cooccurrence"]} == {
            "sugar": 4,
            "all-purpose flour": 2,
            "butter": 2,
            "milk": 2,
            "salt": 1,
            "vanilla extract": 1,
        }

    def test_endpoint_returns_404_for_unknown_ingredient(self, client) -> None:
        response = client.get("/api/ingredient-cooccurrence", params={"ingredient": "dragonfruit foam"})

        assert response.status_code == 404
        assert response.json() == {
            "detail": "No co-occurrences found for ingredient: 'dragonfruit foam'",
            "error_type": "IngredientNotFoundError",
        }
