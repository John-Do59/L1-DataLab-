"""
ETL Step 5 - EA Sports FC24 Players Ingestion
==============================================
Objectif : Ingérer data/fc24/male_players.csv
           dans les tables `players` et `fc24_attributes`.

IMPORTANT : On ne traite que les joueurs évoluant en Ligue 1.
            Les fichiers female_*.csv sont ignorés.

Colonnes clés du CSV FC24 :
    player_id, long_name, short_name, player_positions
    club_name, league_name, nationality_name, dob
    overall, potential, value_eur, wage_eur
    pace, shooting, passing, dribbling, defending, physic
    preferred_foot, weak_foot, skill_moves

Dépendances : ETL Step 1 (teams)
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FC24_CSV = PROJECT_ROOT / "data" / "fc24" / "male_players.csv"

LIGUE1_LEAGUE_NAME = "Ligue 1"


def resolve_team_id(cur, club_name: str) -> int | None:
    """Résout le nom de club FC24 vers un internal_id."""
    cur.execute("""
        SELECT internal_id FROM entity_mapping
        WHERE entity_type = 'team' AND source = 'fc24'
          AND external_name = %s
        LIMIT 1
    """, (club_name,))
    row = cur.fetchone()
    if row:
        return row["internal_id"]

    # Fallback : recherche approchée sur teams.display_name
    cur.execute("""
        SELECT id FROM teams
        WHERE display_name ILIKE %s
           OR short_name ILIKE %s
        LIMIT 1
    """, (f"%{club_name}%", f"%{club_name}%"))
    row = cur.fetchone()
    if row:
        # On enregistre ce mapping pour la prochaine fois
        cur.execute("""
            INSERT INTO entity_mapping (entity_type, source, external_name, internal_id, confidence)
            VALUES ('team', 'fc24', %s, %s, 0.8)
            ON CONFLICT DO NOTHING
        """, (club_name, row["id"]))
        return row["id"]
    return None


def safe_int(val) -> int | None:
    try:
        return int(val) if pd.notna(val) else None
    except (ValueError, TypeError):
        return None


def safe_float(val) -> float | None:
    try:
        return float(val) if pd.notna(val) else None
    except (ValueError, TypeError):
        return None


def run_etl(conn):
    if not FC24_CSV.exists():
        print(f"❌ Fichier introuvable : {FC24_CSV}")
        return

    # Chargement et filtre Ligue 1 uniquement
    df = pd.read_csv(FC24_CSV, encoding="utf-8-sig", low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    # Filtre : uniquement la version la plus récente (FIFA 24) + Ligue 1
    df_l1 = df[
        (df["league_name"] == LIGUE1_LEAGUE_NAME) &
        (df["fifa_version"] == df["fifa_version"].max())
    ].copy()

    print(f"✅ {len(df_l1)} joueurs Ligue 1 (FC {int(df['fifa_version'].max())}) chargés")

    inserted_players = 0
    inserted_attrs = 0
    skipped = 0

    with conn.cursor() as cur:
        for _, row in df_l1.iterrows():
            club_name = str(row.get("club_name", "")).strip()
            team_id = resolve_team_id(cur, club_name)

            if not team_id:
                skipped += 1
                continue

            fc24_player_id = safe_int(row.get("player_id"))
            dob = row.get("dob") if pd.notna(row.get("dob", float("nan"))) else None

            # Upsert player
            cur.execute("""
                INSERT INTO players (
                    external_fc24_id, full_name, short_name,
                    nationality, date_of_birth,
                    position, current_team_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (external_fc24_id) DO UPDATE SET
                    full_name        = EXCLUDED.full_name,
                    current_team_id  = EXCLUDED.current_team_id,
                    position         = EXCLUDED.position
                RETURNING id
            """, (
                fc24_player_id,
                str(row.get("long_name", "")).strip(),
                str(row.get("short_name", "")).strip(),
                str(row.get("nationality_name", "")).strip(),
                dob,
                str(row.get("player_positions", "")).split(",")[0].strip(),
                team_id,
            ))
            player_db = cur.fetchone()
            if not player_db:
                continue
            player_db_id = player_db["id"]
            inserted_players += 1

            # Upsert fc24_attributes
            cur.execute("""
                INSERT INTO fc24_attributes (
                    player_id, fifa_version,
                    overall, potential, value_eur, wage_eur,
                    pace, shooting, passing, dribbling, defending, physic,
                    preferred_foot, weak_foot, skill_moves, work_rate
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, fifa_version) DO UPDATE SET
                    overall   = EXCLUDED.overall,
                    potential = EXCLUDED.potential,
                    value_eur = EXCLUDED.value_eur
            """, (
                player_db_id,
                safe_float(row.get("fifa_version")),
                safe_int(row.get("overall")),
                safe_int(row.get("potential")),
                safe_int(row.get("value_eur")),
                safe_int(row.get("wage_eur")),
                safe_int(row.get("pace")),
                safe_int(row.get("shooting")),
                safe_int(row.get("passing")),
                safe_int(row.get("dribbling")),
                safe_int(row.get("defending")),
                safe_int(row.get("physic")),
                str(row.get("preferred_foot", "")).strip() or None,
                safe_int(row.get("weak_foot")),
                safe_int(row.get("skill_moves")),
                str(row.get("work_rate", "")).strip() or None,
            ))
            inserted_attrs += 1

    conn.commit()
    print(f"\n✅ {inserted_players} joueurs insérés/mis à jour")
    print(f"✅ {inserted_attrs} attributs FC24 insérés/mis à jour")
    print(f"⚠️  {skipped} joueurs ignorés (club non mappé)")
    print("✨ ETL Step 5 terminé : joueurs FC24 chargés.")


def main():
    print("🚀 ETL Step 5 — EA Sports FC24 Players (Ligue 1 Males uniquement)")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_etl(conn)


if __name__ == "__main__":
    main()
