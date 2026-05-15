"""
ETL Step 6 - Transfermarkt Values Enrichissement
=================================================
Objectif : Ingérer les valeurs marchandes Transfermarkt
           dans la table `transfermarkt_values`, pour les
           joueurs déjà présents dans `players` (matching par DOB + nom).

Sources :
    - data/transfermarkt/player_valuations.csv
    - data/transfermarkt/players.csv (pour le mapping TM_id ↔ nom)

Stratégie de matching :
    1. On cherche d'abord par external_tm_id (si déjà résolu).
    2. Sinon, on tente un matching par (last_name, date_of_birth).

Dépendances : ETL Step 5 (players doit être peuplé)
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TM_PLAYERS_CSV = PROJECT_ROOT / "data" / "transfermarkt" / "players.csv"
TM_VALUES_CSV = PROJECT_ROOT / "data" / "transfermarkt" / "player_valuations.csv"


def resolve_player_id(cur, tm_player_id: int, last_name: str, dob: str) -> int | None:
    """Résout un tm_player_id vers notre players.id interne."""
    # 1. Matching direct via external_tm_id
    cur.execute("SELECT id FROM players WHERE external_tm_id = %s", (tm_player_id,))
    row = cur.fetchone()
    if row:
        return row["id"]

    # 2. Matching par nom + date de naissance
    if last_name and dob:
        cur.execute("""
            SELECT id FROM players
            WHERE LOWER(full_name) LIKE %s
              AND date_of_birth = %s::DATE
            LIMIT 1
        """, (f"%{last_name.lower()}%", dob[:10]))
        row = cur.fetchone()
        if row:
            # On enregistre le TM_id pour les prochaines fois
            cur.execute("""
                UPDATE players SET external_tm_id = %s WHERE id = %s
            """, (tm_player_id, row["id"]))
            return row["id"]
    return None


def run_etl(conn):
    if not TM_VALUES_CSV.exists() or not TM_PLAYERS_CSV.exists():
        print("❌ Fichiers Transfermarkt introuvables")
        return

    # Chargement des données TM (on garde uniquement les joueurs L1 actifs)
    df_players = pd.read_csv(TM_PLAYERS_CSV, low_memory=False)
    df_values = pd.read_csv(TM_VALUES_CSV, low_memory=False)

    print(f"✅ {len(df_values)} entrées de valuations chargées")

    # Jointure pour enrichir les valuations avec les infos joueurs
    df_merged = df_values.merge(
        df_players[["player_id", "last_name", "date_of_birth",
                    "current_club_domestic_competition_id"]],
        on="player_id",
        how="left"
    )

    # Filtre : uniquement Ligue 1 (competition_id = FR1)
    df_l1 = df_merged[
        df_merged["current_club_domestic_competition_id"].isin(["FR1", "L1"])
    ].copy()

    print(f"✅ {len(df_l1)} valuations Ligue 1 retenues")

    inserted = 0
    skipped = 0

    with conn.cursor() as cur:
        for _, row in df_l1.iterrows():
            tm_id = int(row["player_id"])
            last_name = str(row.get("last_name", "")).strip()
            dob = str(row.get("date_of_birth", "")).strip()

            player_db_id = resolve_player_id(cur, tm_id, last_name, dob)
            if not player_db_id:
                skipped += 1
                continue

            valuation_date = str(row.get("date", ""))[:10] if pd.notna(row.get("date")) else None
            market_value = int(row["market_value_in_eur"]) if pd.notna(row.get("market_value_in_eur")) else None

            cur.execute("""
                INSERT INTO transfermarkt_values (player_id, market_value_eur, valuation_date)
                VALUES (%s, %s, %s::DATE)
                ON CONFLICT DO NOTHING
            """, (player_db_id, market_value, valuation_date))
            inserted += 1

    conn.commit()
    print(f"\n✅ {inserted} valuations insérées")
    print(f"⚠️  {skipped} joueurs ignorés (non matchés)")
    print("✨ ETL Step 6 terminé : enrichissement Transfermarkt chargé.")


def main():
    print("🚀 ETL Step 6 — Transfermarkt Values")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_etl(conn)


if __name__ == "__main__":
    main()
