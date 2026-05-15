-- ==========================================================
-- L1 DataLab - Seed Minimal (Validation DB)
-- Objectif : valider le schéma avant ETL massif
-- 5 équipes, 10 matchs, 2 joueurs
-- ==========================================================

-- 5 équipes de référence (Ligue 1 2024/25)
INSERT INTO teams (internal_name, display_name, short_name, acronym, primary_color, secondary_color, is_active)
VALUES
    ('paris-saint-germain', 'Paris Saint-Germain', 'PSG', 'PSG', '#004070', '#E30613', TRUE),
    ('olympique-de-marseille', 'Olympique de Marseille', 'OM', 'MAR', '#0B4A89', '#FFFFFF', TRUE),
    ('stade-de-reims', 'Stade de Reims', 'Reims', 'REI', '#FF0000', '#FFFFFF', TRUE),
    ('rc-lens', 'RC Lens', 'Lens', 'LEN', '#FFD700', '#E2001A', TRUE),
    ('olympique-lyonnais', 'Olympique Lyonnais', 'OL', 'LYO', '#0033A0', '#FFFFFF', TRUE)
ON CONFLICT (internal_name) DO NOTHING;

-- Mapping initial pour ces 5 équipes (source Kaggle)
INSERT INTO entity_mapping (entity_type, source, external_name, internal_id, confidence)
SELECT 'team', 'kaggle_historical', external_name, t.id, 1.0
FROM (VALUES
    ('Paris SG',  'paris-saint-germain'),
    ('Marseille', 'olympique-de-marseille'),
    ('Reims',     'stade-de-reims'),
    ('Lens',      'rc-lens'),
    ('Lyon',      'olympique-lyonnais')
) AS mapping(external_name, internal_name)
JOIN teams t ON t.internal_name = mapping.internal_name
ON CONFLICT (entity_type, source, external_name) DO NOTHING;

-- Mapping source API Ligue 1
INSERT INTO entity_mapping (entity_type, source, external_id, external_name, internal_id, confidence)
SELECT 'team', 'api_ligue1', external_id, external_name, t.id, 1.0
FROM (VALUES
    ('l1_championship_club_2025_13', 'Paris Saint-Germain', 'paris-saint-germain'),
    ('l1_championship_club_2025_1',  'Olympique de Marseille', 'olympique-de-marseille'),
    ('l1_championship_club_2025_15', 'Stade de Reims', 'stade-de-reims'),
    ('l1_championship_club_2025_14', 'RC Lens', 'rc-lens'),
    ('l1_championship_club_2025_6',  'Olympique Lyonnais', 'olympique-lyonnais')
) AS mapping(external_id, external_name, internal_name)
JOIN teams t ON t.internal_name = mapping.internal_name
ON CONFLICT (entity_type, source, external_name) DO NOTHING;

-- 10 matchs historiques (Kaggle, saison 1999/00 et 2000/01)
INSERT INTO matches (source, season, kickoff, home_team_id, away_team_id, home_score, away_score, result, status)
SELECT
    'kaggle_historical',
    season,
    NULL,
    home.id,
    away.id,
    home_score,
    away_score,
    CASE
        WHEN home_score > away_score THEN 'H'
        WHEN home_score < away_score THEN 'A'
        ELSE 'D'
    END,
    'finished'
FROM (VALUES
    ('1999/00', 'paris-saint-germain', 'olympique-de-marseille', 2, 1),
    ('1999/00', 'olympique-lyonnais',  'stade-de-reims',         3, 0),
    ('1999/00', 'rc-lens',             'paris-saint-germain',    1, 1),
    ('1999/00', 'stade-de-reims',      'rc-lens',                2, 2),
    ('1999/00', 'olympique-de-marseille', 'olympique-lyonnais',  1, 2),
    ('2000/01', 'paris-saint-germain', 'olympique-lyonnais',     3, 2),
    ('2000/01', 'rc-lens',             'olympique-de-marseille', 0, 0),
    ('2000/01', 'olympique-de-marseille', 'paris-saint-germain', 1, 3),
    ('2000/01', 'stade-de-reims',      'olympique-lyonnais',     0, 1),
    ('2000/01', 'olympique-lyonnais',  'rc-lens',                2, 1)
) AS m(season, home_name, away_name, home_score, away_score)
JOIN teams home ON home.internal_name = m.home_name
JOIN teams away ON away.internal_name = m.away_name
ON CONFLICT DO NOTHING;

-- 2 joueurs de test
INSERT INTO players (full_name, short_name, nationality, position, current_team_id)
SELECT 'Kylian Mbappé Lottin', 'K. Mbappé', 'France', 'ST', t.id
FROM teams t WHERE t.internal_name = 'paris-saint-germain'
ON CONFLICT DO NOTHING;

INSERT INTO players (full_name, short_name, nationality, position, current_team_id)
SELECT 'Wissam Ben Yedder', 'W. Ben Yedder', 'France', 'ST', t.id
FROM teams t WHERE t.internal_name = 'paris-saint-germain'
ON CONFLICT DO NOTHING;
