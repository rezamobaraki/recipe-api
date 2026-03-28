CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    normalized_key TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

CREATE TABLE IF NOT EXISTS ingredient_cooccurrence (
    ingredient_a TEXT NOT NULL,
    ingredient_b TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (ingredient_a, ingredient_b)
);

CREATE INDEX IF NOT EXISTS idx_ingredient_cooccurrence_a ON ingredient_cooccurrence(ingredient_a);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
"""

INSERT_RECIPE = """
INSERT OR IGNORE INTO recipes (id, title, name, description)
VALUES (:id, :title, :name, :description)
"""
INSERT_INGREDIENT = """
INSERT INTO recipe_ingredients (recipe_id, raw_text, normalized_key)
VALUES (:recipe_id, :raw_text, :normalized_key)
"""

BUILD_COOCCURRENCES = """
INSERT OR REPLACE INTO ingredient_cooccurrence
WITH distinct_recipe_ingredients AS (
    SELECT DISTINCT recipe_id, normalized_key
    FROM recipe_ingredients
    WHERE normalized_key IS NOT NULL
)
SELECT a.normalized_key, b.normalized_key, COUNT(*)
FROM distinct_recipe_ingredients a
JOIN distinct_recipe_ingredients b
  ON a.recipe_id = b.recipe_id
 AND a.normalized_key != b.normalized_key
GROUP BY a.normalized_key, b.normalized_key
"""

RESET_RECIPE_DATA = """
DELETE FROM ingredient_cooccurrence;
DELETE FROM recipe_ingredients;
DELETE FROM recipes;
"""

GET_COOCCURRENCES = """
SELECT ingredient_b AS ingredient, count
FROM ingredient_cooccurrence
WHERE ingredient_a = :ingredient
ORDER BY count DESC, ingredient_b ASC
LIMIT :limit
"""

LIST_RECIPES = """
SELECT r.id, r.title, r.name, r.description,
       GROUP_CONCAT(ri.normalized_key) AS normalized_keys,
       GROUP_CONCAT(ri.raw_text) AS raw_texts
FROM recipes r
LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
GROUP BY r.id
ORDER BY r.title
"""
