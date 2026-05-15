-- ==========================================================
-- L1 DataLab - PostgreSQL Schema
-- Feature Branch: feature/data-modeling-etl
-- Ordre strict : teams → matches → players → enrichissement
-- ==========================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS unaccent;  -- pour la normalisation des noms

-- ==========================================================
-- 1. TABLE PIVOT : TEAMS (référence centrale)
-- Source de vérité unique pour tous les clubs
-- ==========================================================
CREATE TABLE IF NOT EXISTS teams (
    id              SERIAL PRIMARY KEY,
    internal_name   VARCHAR(100) NOT NULL UNIQUE, -- nom normalisé canonique
    display_name    VARCHAR(100) NOT NULL,         -- nom à afficher
    short_name      VARCHAR(20),
    acronym         VARCHAR(5),
    primary_color   VARCHAR(7),                   -- #RRGGBB
    secondary_color VARCHAR(7),
    logo_url        TEXT,
    stadium_id      VARCHAR(50),
    is_active       BOOLEAN DEFAULT TRUE,         -- actif en L1 cette saison
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ==========================================================
-- 2. TABLE MAPPING : cross-source entity resolution
-- Clé du projet : fait correspondre toutes les sources
-- ==========================================================
CREATE TABLE IF NOT EXISTS entity_mapping (
    id            SERIAL PRIMARY KEY,
    entity_type   VARCHAR(20) NOT NULL CHECK (entity_type IN ('team', 'player')),
    source        VARCHAR(30) NOT NULL CHECK (source IN ('api_ligue1', 'kaggle_historical', 'betting_fduk', 'transfermarkt', 'fc24')),
    external_id   VARCHAR(100),                  -- ID dans la source externe
    external_name VARCHAR(150) NOT NULL,         -- nom brut dans la source
    internal_id   INTEGER NOT NULL,              -- FK vers teams.id ou players.id
    confidence    FLOAT DEFAULT 1.0,             -- score de confiance du matching
    created_at    TIMESTAMP DEFAULT NOW(),
    UNIQUE (entity_type, source, external_name)
);

-- ==========================================================
-- 3. TABLE CENTRALE : MATCHES
-- Historique complet Kaggle + saison live API
-- ==========================================================
CREATE TABLE IF NOT EXISTS matches (
    id              SERIAL PRIMARY KEY,
    external_id     VARCHAR(100) UNIQUE,          -- ID source (ex: l1_championship_match_xxx)
    source          VARCHAR(30) NOT NULL,          -- 'api_ligue1' ou 'kaggle_historical'
    season          VARCHAR(10) NOT NULL,          -- ex: '2024/25' ou '2024'
    gameweek        INTEGER,
    kickoff         TIMESTAMP,
    home_team_id    INTEGER REFERENCES teams(id),
    away_team_id    INTEGER REFERENCES teams(id),
    home_score      SMALLINT,
    away_score      SMALLINT,
    result          CHAR(1) CHECK (result IN ('H', 'D', 'A')), -- Home/Draw/Away
    -- Half-time
    ht_home_score   SMALLINT,
    ht_away_score   SMALLINT,
    -- Contexte
    stadium         VARCHAR(100),
    status          VARCHAR(30),                  -- 'finished', 'scheduled', 'live'
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Index pour les requêtes ML les plus fréquentes
CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);
CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id, kickoff);
CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id, kickoff);

-- ==========================================================
-- 4. TABLE : PLAYERS (individus)
-- ==========================================================
CREATE TABLE IF NOT EXISTS players (
    id              SERIAL PRIMARY KEY,
    external_fc24_id    INTEGER UNIQUE,
    external_tm_id      INTEGER UNIQUE,           -- Transfermarkt player ID
    full_name           VARCHAR(150),
    short_name          VARCHAR(80),
    nationality         VARCHAR(80),
    date_of_birth       DATE,
    position            VARCHAR(50),
    current_team_id     INTEGER REFERENCES teams(id),
    created_at          TIMESTAMP DEFAULT NOW()
);

-- ==========================================================
-- 5. TABLE : BETTING_ODDS (cotes bookmakers)
-- Enrichissement prédictif majeur
-- ==========================================================
CREATE TABLE IF NOT EXISTS betting_odds (
    id            SERIAL PRIMARY KEY,
    match_id      INTEGER REFERENCES matches(id) ON DELETE CASCADE,
    bookmaker     VARCHAR(30) NOT NULL,           -- ex: 'B365', 'PSH', 'WHH'
    odd_home      FLOAT,
    odd_draw      FLOAT,
    odd_away      FLOAT,
    -- Implied probabilities (calculées à l'ingestion)
    prob_home     FLOAT,
    prob_draw     FLOAT,
    prob_away     FLOAT,
    -- Over/Under
    odd_over25    FLOAT,
    odd_under25   FLOAT,
    created_at    TIMESTAMP DEFAULT NOW(),
    UNIQUE (match_id, bookmaker)
);

-- ==========================================================
-- 6. TABLE : FC24_ATTRIBUTES (stats techniques joueurs)
-- Uniquement males (Ligue 1 masculine)
-- ==========================================================
CREATE TABLE IF NOT EXISTS fc24_attributes (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER REFERENCES players(id) ON DELETE CASCADE,
    fifa_version    FLOAT NOT NULL,              -- ex: 24.0
    overall         SMALLINT,
    potential       SMALLINT,
    value_eur       BIGINT,
    wage_eur        INTEGER,
    -- Attributes groupés
    pace            SMALLINT,
    shooting        SMALLINT,
    passing         SMALLINT,
    dribbling       SMALLINT,
    defending       SMALLINT,
    physic          SMALLINT,
    -- Détails clés
    preferred_foot  VARCHAR(5),
    weak_foot       SMALLINT,
    skill_moves     SMALLINT,
    work_rate       VARCHAR(30),
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (player_id, fifa_version)
);

-- ==========================================================
-- 7. TABLE : TRANSFERMARKT_VALUES (valeur marché)
-- ==========================================================
CREATE TABLE IF NOT EXISTS transfermarkt_values (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER REFERENCES players(id) ON DELETE CASCADE,
    market_value_eur BIGINT,
    valuation_date  DATE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ==========================================================
-- 8. TABLE/VIEW : TEAM_STATS_SNAPSHOT (forme récente)
-- Pré-calculé pour le Feature Engineering ML
-- ==========================================================
CREATE TABLE IF NOT EXISTS team_stats_snapshot (
    id              SERIAL PRIMARY KEY,
    team_id         INTEGER REFERENCES teams(id),
    season          VARCHAR(10) NOT NULL,
    as_of_date      DATE NOT NULL,
    -- Rolling 5 derniers matchs
    form_5          VARCHAR(5),                  -- ex: 'WWDLW'
    points_5        SMALLINT,
    goals_scored_5  SMALLINT,
    goals_conceded_5 SMALLINT,
    -- Saison globale
    played          SMALLINT,
    wins            SMALLINT,
    draws           SMALLINT,
    losses          SMALLINT,
    goals_for       SMALLINT,
    goals_against   SMALLINT,
    goal_diff       SMALLINT,
    points          SMALLINT,
    -- Strengths (feature ML)
    offensive_strength  FLOAT,
    defensive_strength  FLOAT,
    -- Squad value (Transfermarkt)
    squad_value_eur BIGINT,
    -- Squad strength (FC24)
    avg_overall     FLOAT,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (team_id, season, as_of_date)
);

-- ==========================================================
-- 9. COMMENTAIRES sur les tables (documentation)
-- ==========================================================
COMMENT ON TABLE teams IS 'Table pivot centrale - source de vérité pour tous les clubs';
COMMENT ON TABLE entity_mapping IS 'Mapping cross-source : résout les noms entre Kaggle/API/Transfermarkt/FC24';
COMMENT ON TABLE matches IS 'Historique complet des matchs (Kaggle 1999-2019 + API saison live)';
COMMENT ON TABLE players IS 'Joueurs tous clubs L1 confondus';
COMMENT ON TABLE betting_odds IS 'Cotes bookmakers - feature ML critique pour la prédiction';
COMMENT ON TABLE fc24_attributes IS 'Attributs techniques EA Sports FC24 (hommes uniquement)';
COMMENT ON TABLE transfermarkt_values IS 'Valeurs marchandes Transfermarkt pour enrichissement économique';
COMMENT ON TABLE team_stats_snapshot IS 'Snapshots pré-calculés pour le feature engineering ML';
