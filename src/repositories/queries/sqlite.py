# Recipe API SQLite Queries

# Schema
CREATE_TABLES = '''
CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    canonical_name TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

CREATE TABLE IF NOT EXISTS ingredient_match (
    ingredient_a TEXT NOT NULL,
    ingredient_b TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (ingredient_a, ingredient_b)
);

CREATE INDEX IF NOT EXISTS idx_ingredient_match_a ON ingredient_match(ingredient_a);
'''

# Data operations
INSERT_RECIPE = 'INSERT OR IGNORE INTO recipes VALUES (?, ?, ?, ?)'
INSERT_INGREDIENT = 'INSERT INTO recipe_ingredients VALUES (?, ?, ?)'

BUILD_MATCHES = '''
INSERT OR REPLACE INTO ingredient_match 
SELECT a.canonical_name, b.canonical_name, COUNT(*)
FROM recipe_ingredients a
JOIN recipe_ingredients b ON a.recipe_id = b.recipe_id
WHERE a.canonical_name != b.canonical_name
  AND a.canonical_name IS NOT NULL 
  AND b.canonical_name IS NOT NULL
GROUP BY a.canonical_name, b.canonical_name
'''

GET_MATCHES = '''
SELECT ingredient_b as ingredient, count 
FROM ingredient_match 
WHERE ingredient_a = ? 
ORDER BY count DESC LIMIT ?
'''

FIND_BY_INGREDIENTS = '''
SELECT r.id, r.title, r.name,
       GROUP_CONCAT(ri.canonical_name) as canonical_names,
       GROUP_CONCAT(ri.raw_text) as raw_texts
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
WHERE ri.canonical_name IN ({placeholders})
GROUP BY r.id
ORDER BY COUNT(ri.canonical_name) DESC
LIMIT ?
'''

FIND_BY_TITLE = '''
SELECT r.id, r.title, r.name,
       GROUP_CONCAT(ri.canonical_name) as canonical_names,
       GROUP_CONCAT(ri.raw_text) as raw_texts
FROM recipes r
JOIN recipe_ingredients ri ON r.id = ri.recipe_id
WHERE r.title LIKE ? COLLATE NOCASE
GROUP BY r.id
LIMIT ?
'''

# Original flight capacity queries below
CREATE_TABLES_SCRIPT = """
    CREATE TABLE IF NOT EXISTS events (
        flight_id TEXT,
        date TEXT,
        time TEXT,
        equipment TEXT,
        flight_number TEXT,
        origin_iata TEXT,
        origin_icao TEXT,
        destination_iata TEXT,
        destination_icao TEXT,
        operator TEXT,
        registration TEXT
    );

    CREATE TABLE IF NOT EXISTS aircraft (
        code_icao TEXT PRIMARY KEY,
        code_iata TEXT NOT NULL,
        full_name TEXT NOT NULL,
        category TEXT NOT NULL,
        average_speed_mph REAL NOT NULL,
        volume REAL NOT NULL,
        payload REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS flights (
        flight_id TEXT PRIMARY KEY,
        flight_number TEXT,
        date TEXT NOT NULL,
        origin_iata TEXT,
        origin_icao TEXT,
        destination_iata TEXT,
        destination_icao TEXT,
        equipment TEXT,
        operator TEXT,
        registration TEXT
    );

    CREATE TABLE IF NOT EXISTS capacity (
        flight_id TEXT PRIMARY KEY,
        flight_number TEXT,
        date TEXT NOT NULL,
        origin_iata TEXT,
        origin_icao TEXT,
        destination_iata TEXT,
        destination_icao TEXT,
        equipment TEXT,
        aircraft_name TEXT,
        category TEXT,
        volume_m3 REAL,
        payload_kg REAL,
        operator TEXT,
        FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
        FOREIGN KEY (equipment) REFERENCES aircraft(code_icao)
    );

    CREATE INDEX IF NOT EXISTS idx_capacity_route
        ON capacity(origin_iata, destination_iata);
    CREATE INDEX IF NOT EXISTS idx_capacity_date
        ON capacity(date);
    CREATE INDEX IF NOT EXISTS idx_events_flight_id
        ON events(flight_id);

    CREATE TABLE IF NOT EXISTS processed_files (
        filename TEXT PRIMARY KEY,
        processed_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
"""

CHECK_IS_EXISTS = "SELECT COUNT(*) FROM capacity"

CHECK_FILE_PROCESSED = "SELECT 1 FROM processed_files WHERE filename = :filename"

MARK_FILE_PROCESSED = "INSERT INTO processed_files (filename) VALUES (:filename)"

AGGREGATE_FLIGHTS = """
    INSERT OR REPLACE INTO flights (
        flight_id, date, equipment, flight_number,
        origin_iata, origin_icao, destination_iata, destination_icao,
        operator, registration
    )
    SELECT
        flight_id,
        date,
        equipment,
        flight_number,
        origin_iata,
        origin_icao,
        destination_iata,
        destination_icao,
        operator,
        registration
    FROM (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY flight_id ORDER BY date DESC, time DESC) as rn
        FROM events
    )
    WHERE rn = 1;
"""

INSERT_EVENT = """
    INSERT INTO events (
        flight_id, date, time, equipment, flight_number,
        origin_iata, origin_icao, destination_iata, destination_icao,
        operator, registration
    ) VALUES (
        :flight_id, :date, :time, :equipment, :flight,
        :origin_iata, :origin_icao, :destination_iata, :destination_icao,
        :operator, :registration
    );
"""

INSERT_AIRCRAFT = """
    INSERT OR REPLACE INTO aircraft (
        code_icao, code_iata, full_name, category, 
        average_speed_mph, volume, payload
    ) VALUES (
        :code_icao, 
        :code_iata, 
        :full_name, 
        :category, 
        :average_speed_mph, 
        :volume, 
        :payload
    )
"""

INSERT_FLIGHT = """
    INSERT OR REPLACE INTO flights (
        flight_id, flight_number, date, origin_iata, origin_icao, 
        destination_iata, destination_icao, equipment, operator, registration
    ) VALUES (
        :flight_id, 
        :flight_number, 
        :date, 
        :origin_iata, 
        :origin_icao, 
        :destination_iata, 
        :destination_icao, 
        :equipment, 
        :operator, 
        :registration
    )
"""

INSERT_CAPACITY = """
    INSERT OR REPLACE INTO capacity (
        flight_id, flight_number, date, origin_iata, origin_icao, 
        destination_iata, destination_icao, equipment, aircraft_name, 
        category, volume_m3, payload_kg, operator
    ) VALUES (
        :flight_id, 
        :flight_number, 
        :date, 
        :origin_iata, 
        :origin_icao, 
        :destination_iata, 
        :destination_icao, 
        :equipment, 
        :aircraft_name, 
        :category, 
        :volume_m3, 
        :payload_kg, 
        :operator
    )
"""

CALCULATE_CAPACITY = """
    INSERT OR REPLACE INTO capacity (
        flight_id, flight_number, date,
        origin_iata, origin_icao,
        destination_iata, destination_icao,
        equipment, aircraft_name, category,
        volume_m3, payload_kg, operator
    )
    SELECT
        f.flight_id,
        f.flight_number,
        f.date,
        f.origin_iata,
        f.origin_icao,
        f.destination_iata,
        f.destination_icao,
        f.equipment,
        COALESCE(a.full_name, 'Unknown Aircraft'),
        COALESCE(a.category, 'unknown_aircraft'),
        a.volume,
        a.payload,
        f.operator
    FROM flights f
    LEFT JOIN aircraft a ON f.equipment = a.code_icao;
"""

SELECT_ALL_AIRCRAFT = "SELECT * FROM aircraft"

SELECT_CAPACITY_BASE = "SELECT * FROM capacity WHERE 1=1"

SELECT_CAPACITY_SUMMARY = """
    SELECT
        date,
        MAX(origin_iata) as origin_iata,
        MAX(destination_iata) as destination_iata,
        COUNT(*) as total_flights,
        COALESCE(ROUND(SUM(volume_m3), 2), 0.0) as total_volume_m3,
        COALESCE(ROUND(SUM(payload_kg), 2), 0.0) as total_payload_kg
    FROM capacity
    WHERE 1=1
"""
