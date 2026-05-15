"""
ETL Step 3 - API Ligue 1 (Live Season) Ingestion
==================================================
Objectif : Ingérer les matchs de la saison en cours depuis
           data/raw/l1_matches/*.json dans la table `matches`.

Dépendances : ETL Step 1 (teams + entity_mapping)
"""

import glob
import json
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATCHES_PATTERN = str(PROJECT_ROOT / "data" / "raw" / "l1_matches" / "*.json")


def resolve_team_by_external_id(cur, external_id: str) -> int | None:
    cur.execute("""
        SELECT internal_id FROM entity_mapping
        WHERE entity_type = 'team' AND source = 'api_ligue1' AND external_id = %s
    """, (external_id,))
    row = cur.fetchone()
    return row["internal_id"] if row else None


def infer_result(home: int | None, away: int | None) -> str | None:
    if home is None or away is None:
        return None
    if home > away:
        return "H"
    elif home < away:
        return "A"
    return "D"


def run_etl(conn):
    files = sorted(glob.glob(MATCHES_PATTERN))
    if not files:
        print("❌ Aucun fichier de matchs trouvé dans data/raw/l1_matches/")
        return

    inserted = 0
    updated = 0

    with conn.cursor() as cur:
        for filepath in files:
            with open(filepath) as f:
                matches = json.load(f)

            print(f"📂 Traitement : {Path(filepath).name} ({len(matches)} matchs)")

            for match in matches:
                external_id = match.get("match_id")
                home_ext = match.get("home_team_id")
                away_ext = match.get("away_team_id")

                home_id = resolve_team_by_external_id(cur, home_ext) if home_ext else None
                away_id = resolve_team_by_external_id(cur, away_ext) if away_ext else None

                # Parsing de la date ISO
                kickoff = None
                if match.get("kickoff"):
                    try:
                        kickoff = datetime.fromisoformat(
                            match["kickoff"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                home_score = match.get("home_score")
                away_score = match.get("away_score")
                result = infer_result(home_score, away_score)
                season = str(match.get("season", "")) if match.get("season") else "2024/25"

                cur.execute("""
                    INSERT INTO matches (
                        external_id, source, season, gameweek,
                        kickoff, home_team_id, away_team_id,
                        home_score, away_score, result, status
                    )
                    VALUES (%s, 'api_ligue1', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (external_id) DO UPDATE SET
                        home_score  = EXCLUDED.home_score,
                        away_score  = EXCLUDED.away_score,
                        result      = EXCLUDED.result,
                        status      = EXCLUDED.status,
                        kickoff     = EXCLUDED.kickoff
                    RETURNING (xmax = 0) AS inserted
                """, (
                    external_id,
                    season,
                    match.get("gameweek"),
                    kickoff,
                    home_id, away_id,
                    home_score, away_score,
                    result,
                    match.get("status", "scheduled"),
                ))
                row = cur.fetchone()
                if row and row["inserted"]:
                    inserted += 1
                else:
                    updated += 1

    conn.commit()
    print(f"\n✅ {inserted} matchs insérés, {updated} mis à jour")
    print("✨ ETL Step 3 terminé : saison actuelle chargée.")


def main():
    print("🚀 ETL Step 3 — API Ligue 1 (Live Season)")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_etl(conn)


if __name__ == "__main__":
    main()
