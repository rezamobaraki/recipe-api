class RecipeAPIError(Exception):
    pass


class IngredientNotFoundError(RecipeAPIError):
    pass


class RecipeNotFoundError(RecipeAPIError):
    pass