class TestTask2Api:
    def test_duplicate_endpoint_returns_similar_recipes(self, client) -> None:
        response = client.post(
            "/api/recipe-duplicates",
            json={
                "recipe": {
                    "name": "Cinnamon Bun Bread",
                    "ingredients": [
                        {"name": "all-purpose flour", "quantity": "3 cups"},
                        {"name": "sugar", "quantity": "1 cup"},
                        {"name": "cinnamon", "quantity": "2 teaspoons"},
                        {"name": "butter", "quantity": "1/2 cup"},
                    ],
                }
            },
        )

        body = response.json()
        duplicates = body["duplicates"]

        assert response.status_code == 200
        assert len(duplicates) == 5
        assert [item["name"] for item in duplicates[:2]] == [
            "Cinnamon Bun Bread",
            "Cinnamon Swirl Bread",
        ]
        assert duplicates[0]["similarity"] >= duplicates[1]["similarity"] > 0

    def test_duplicate_endpoint_returns_empty_list_for_unrelated_recipe(self, client) -> None:
        response = client.post(
            "/api/recipe-duplicates",
            json={
                "recipe": {
                    "name": "Liquid Nitrogen Cloud",
                    "ingredients": [
                        {"name": "dragonfruit foam", "quantity": "1 cup"},
                        {"name": "liquid nitrogen", "quantity": "1 splash"},
                    ],
                }
            },
        )

        assert response.status_code == 200
        assert response.json() == {"duplicates": []}
