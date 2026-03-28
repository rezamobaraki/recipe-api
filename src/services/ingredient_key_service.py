import re
import unicodedata


UNITS_PATTERN = re.compile(
    r"\b(cups?|tablespoons?|tbsp|teaspoons?|tsp|ounces?|oz|pounds?|lbs?|grams?|"
    r"g|kilograms?|kg|liters?|litres?|l|milliliters?|millilitres?|ml|pinch|dash|"
    r"packages?|packets?|cans?|jars?|bottles?)\b",
    flags=re.IGNORECASE,
)
QUANTITY_PATTERN = re.compile(r"\b\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?\b")
FRACTION_PATTERN = re.compile(r"[¼½¾⅓⅔⅛⅜⅝⅞]")
PREPARATION_PATTERN = re.compile(
    r"\b(chopped|minced|diced|sliced|fresh|dried|ground|whole|optional|divided|"
    r"softened|melted|beaten|crushed|peeled|seeded|shredded|grated|warm|cold|"
    r"large|medium|small|extra-virgin|extra virgin|to taste)\b",
    flags=re.IGNORECASE,
)
NON_ALPHANUMERIC_PATTERN = re.compile(r"[^a-z0-9\s-]")
WHITESPACE_PATTERN = re.compile(r"\s+")

ALIASES = {
    "eggs": "egg",
    "garlic cloves": "garlic",
    "cloves garlic": "garlic",
    "confectioners sugar": "powdered sugar",
}


class IngredientKeyService:
    def normalize(self, raw_text: str) -> str | None:
        text = unicodedata.normalize("NFKC", raw_text).lower()
        text = text.replace("&", " and ")
        text = FRACTION_PATTERN.sub(" ", text)
        text = re.sub(r"\([^)]*\)", " ", text)
        text = QUANTITY_PATTERN.sub(" ", text)
        text = UNITS_PATTERN.sub(" ", text)
        text = PREPARATION_PATTERN.sub(" ", text)
        text = NON_ALPHANUMERIC_PATTERN.sub(" ", text)
        text = WHITESPACE_PATTERN.sub(" ", text).strip(" -")

        if not text:
            return None

        words = [self._singularize(word) for word in text.split() if len(word) > 1]
        normalized = " ".join(words).strip()
        if not normalized:
            return None

        return ALIASES.get(normalized, normalized)

    def normalize_query(self, ingredient: str) -> str | None:
        return self.normalize(ingredient)

    def _singularize(self, word: str) -> str:
        if word in {"asparagus", "couscous", "molasses"}:
            return word
        if word.endswith("ies") and len(word) > 3:
            return f"{word[:-3]}y"
        if word.endswith("oes") and len(word) > 3:
            return word[:-2]
        if word.endswith("es") and len(word) > 4 and not word.endswith(("ses", "zes")):
            return word[:-2]
        if word.endswith("s") and len(word) > 3 and not word.endswith(("ss", "us")):
            return word[:-1]
        return word
