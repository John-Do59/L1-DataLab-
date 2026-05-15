"""
ETL Step 2 - Kaggle Historical Matches Ingestion
================================================
Objectif : Ingérer 'data/historical/Ligue1 Championship.csv'
           dans la table `matches`.

Dépendances : ETL Step 1 (teams + entity_mapping) doit avoir tournée.

Ce dataset est la base ML principale : 20 ans de résultats.
"""

import os
import re
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

# ==========================================================
# CONFIG
# ==========================================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
KAGGLE_CSV = PROJECT_ROOT / "data" / "historical" / "Ligue1 Championship.csv"


def resolve_team_id(cur, name: str, source: str = "kaggle_historical") -> int | None:
    """Résout le nom d'une équipe en internal_id via entity_mapping."""
    cur.execute("""
        SELECT internal_id FROM entity_mapping
        WHERE entity_type = 'team' AND source = %s AND external_name = %s
    """, (source, name))
    row = cur.fetchone()
    if row:
        return row["internal_id"]
    
    # Fallback : essai direct sur teams.display_name (fuzzy)
    cur.execute("""
        SELECT id FROM teams WHERE display_name ILIKE %s
    """, (f"%{name}%",))
    row = cur.fetchone()
    return row["id"] if row else None


def normalize_season(season_str: str) -> str:
    """'1999/00' → '1999/00' (déjà bon), '2023' → '2023/24' si nécessaire."""
    return season_str.strip()


def infer_result(home: int, away: int) -> str:
    if home > away:
        return "H"
    elif home < away:
        return "A"
    return "D"


def run_etl(conn):
    if not KAGGLE_CSV.exists():
        print(f"❌ Fichier introuvable : {KAGGLE_CSV}")
        return

    df = pd.read_csv(KAGGLE_CSV, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    print(f"✅ {len(df)} matchs chargés depuis Kaggle")

    inserted = 0
    skipped_team = 0

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            home_name = str(row.get("Home Team", "")).strip()
            away_name = str(row.get("Away Team", "")).strip()
            season = normalize_season(str(row.get("Season", "")))

            try:
                home_goals = int(row.get("Home Team Goals", 0))
                away_goals = int(row.get("Away Team Goals", 0))
            except (ValueError, TypeError):
                home_goals = away_goals = None

            home_id = resolve_team_id(cur, home_name)
            away_id = resolve_team_id(cur, away_name)

            if not home_id or not away_id:
                skipped_team += 1
                if skipped_team <= 5:
                    print(f"  ⚠️  Équipe non résolue : '{home_name}' vs '{away_name}'")
                continue

            result = infer_result(home_goals, away_goals) if home_goals is not None else None

            cur.execute("""
                INSERT INTO matches (
                    source, season,
                    home_team_id, away_team_id,
                    home_score, away_score,
                    result, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'finished')
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                "kaggle_historical",
                season,
                home_id, away_id,
                home_goals, away_goals,
                result,
            ))
            if cur.fetchone():
                inserted += 1

    conn.commit()
    print(f"\n✅ {inserted} matchs insérés")
    print(f"⚠️  {skipped_team} matchs ignorés (équipes non mappées)")
    print("✨ ETL Step 2 terminé : historique Kaggle chargé.")


def main():
    print("🚀 ETL Step 2 — Kaggle Historical Matches")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_etl(conn)


if __name__ == "__main__":
    main()
