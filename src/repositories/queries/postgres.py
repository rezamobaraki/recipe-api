CREATE_RECIPES_TABLE = """
CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT
);
"""

CREATE_INGREDIENTS_TABLE = """
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id SERIAL PRIMARY KEY,
    recipe_id TEXT REFERENCES recipes(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    canonical_name TEXT
);
"""

CREATE_INGREDIENT_MATCH_TABLE = """
CREATE TABLE IF NOT EXISTS ingredient_match (
    ingredient_a TEXT NOT NULL,
    ingredient_b TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (ingredient_a, ingredient_b)
);
"""

CREATE_INGREDIENT_MATCH_INDEX = """
CREATE INDEX IF NOT EXISTS idx_ingredient_match_a 
ON ingredient_match (ingredient_a);
"""

BULK_INSERT_RECIPE = """
INSERT INTO recipes (id, title, name, description)
VALUES %s
ON CONFLICT (id) DO NOTHING;
"""

BULK_INSERT_INGREDIENT = """
INSERT INTO recipe_ingredients (recipe_id, raw_text, canonical_name)
VALUES %s;
"""

BUILD_INGREDIENT_MATCHES = """
INSERT INTO ingredient_match (ingredient_a, ingredient_b, count)
SELECT a.canonical_name, b.canonical_name, COUNT(*) as count
FROM recipe_ingredients a
JOIN recipe_ingredients b
    ON a.recipe_id = b.recipe_id
    AND a.canonical_name != b.canonical_name
WHERE a.canonical_name IS NOT NULL
  AND b.canonical_name IS NOT NULL
GROUP BY a.canonical_name, b.canonical_name
ON CONFLICT (ingredient_a, ingredient_b)
DO UPDATE SET count = EXCLUDED.count;
"""

GET_INGREDIENT_MATCHES = """
SELECT ingredient_b AS ingredient, count
FROM ingredient_match
WHERE ingredient_a = %(ingredient)s
ORDER BY count DESC
LIMIT %(top_n)s;
"""

SEARCH_RECIPES_BY_INGREDIENTS = """
SELECT r.id, r.title, r.name,
       array_agg(ri.canonical_name) AS canonical_names,
       array_agg(ri.raw_text) AS raw_texts
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
WHERE ri.canonical_name = ANY(%(ingredients)s)
GROUP BY r.id
ORDER BY COUNT(ri.canonical_name) DESC
LIMIT %(limit)s;
"""

SEARCH_RECIPES_BY_TITLE = """
SELECT r.id, r.title, r.name,
       array_agg(ri.canonical_name) AS canonical_names,
       array_agg(ri.raw_text) AS raw_texts
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
WHERE LOWER(r.title) LIKE LOWER(%(title)s)
GROUP BY r.id
LIMIT %(limit)s;
"""