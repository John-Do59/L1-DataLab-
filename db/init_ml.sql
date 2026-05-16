-- Schéma minimal pour l'API ML
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE,
    season VARCHAR(10),
    kickoff TIMESTAMP,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    result VARCHAR(1),
    status VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    internal_name VARCHAR(100)
);
