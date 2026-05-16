"""
ETL Step 4 - Betting Odds Enrichissement
=========================================
Objectif : Ingérer data/betting/ligue1_2425_odds.csv
           dans la table `betting_odds` en jointant sur `matches`.

Colonnes clés Football-Data.co.uk :
    Date, HomeTeam, AwayTeam
    B365H, B365D, B365A  (Bet365)
    PSH, PSD, PSA         (Pinnacle)
    MaxH, MaxD, MaxA      (Meilleure cote)
    AvgH, AvgD, AvgA      (Moyenne marchés)
    B365>2.5, B365<2.5    (Over/Under)

Dépendances : ETL Step 1 + 3 (matches de la saison actuelle)
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BETTING_CSV = PROJECT_ROOT / "data" / "betting" / "ligue1_2425_odds.csv"

# Bookmakers à ingérer (source → colonnes H/D/A)
BOOKMAKERS = {
    "B365": ("B365H", "B365D", "B365A"),
    "PSH":  ("PSH", "PSD", "PSA"),
    "Max":  ("MaxH", "MaxD", "MaxA"),
    "Avg":  ("AvgH", "AvgD", "AvgA"),
}


def implied_prob(odd: float | None) -> float | None:
    """Convertit une cote en probabilité implicite."""
    if odd and odd > 1:
        return round(1 / odd, 4)
    return None


def resolve_match_id(cur, home_name: str, away_name: str, season: str = "2024/25") -> int | None:
    """Trouve un match_id en résolvant les noms via entity_mapping."""
    cur.execute("""
        SELECT m.id FROM matches m
        JOIN entity_mapping eh ON eh.internal_id = m.home_team_id
            AND eh.entity_type = 'team' AND eh.source = 'betting_fduk'
        JOIN entity_mapping ea ON ea.internal_id = m.away_team_id
            AND ea.entity_type = 'team' AND ea.source = 'betting_fduk'
        WHERE eh.external_name = %s
          AND ea.external_name = %s
          AND m.season = %s
        LIMIT 1
    """, (home_name, away_name, season))
    row = cur.fetchone()
    return row["id"] if row else None


def run_etl(conn):
    betting_files = [
        ("2024/25", PROJECT_ROOT / "data" / "betting" / "ligue1_2425_odds.csv"),
        ("2025/26", PROJECT_ROOT / "data" / "betting" / "ligue1_2526_odds.csv")
    ]

    total_inserted = 0
    total_skipped = 0

    with conn.cursor() as cur:
        for season_label, filepath in betting_files:
            if not filepath.exists():
                print(f"⚠️  Fichier ignoré (introuvable) : {filepath.name}")
                continue

            print(f"📂 Traitement des cotes : {filepath.name} (Saison {season_label})")
            df = pd.read_csv(filepath, encoding="utf-8-sig")
            df.columns = [c.strip() for c in df.columns]

            for _, row in df.iterrows():
                home = str(row.get("HomeTeam", "")).strip()
                away = str(row.get("AwayTeam", "")).strip()

                if not home or not away:
                    continue

                match_id = resolve_match_id(cur, home, away, season=season_label)
                if not match_id:
                    total_skipped += 1
                    continue

                for bookmaker, (col_h, col_d, col_a) in BOOKMAKERS.items():
                    oh = row.get(col_h)
                    od = row.get(col_d)
                    oa = row.get(col_a)

                    if pd.isna(oh) and pd.isna(od) and pd.isna(oa):
                        continue

                    oh = float(oh) if not pd.isna(oh) else None
                    od = float(od) if not pd.isna(od) else None
                    oa = float(oa) if not pd.isna(oa) else None

                    over25 = float(row.get("B365>2.5")) if bookmaker == "B365" and not pd.isna(row.get("B365>2.5")) else None
                    under25 = float(row.get("B365<2.5")) if bookmaker == "B365" and not pd.isna(row.get("B365<2.5")) else None

                    cur.execute("""
                        INSERT INTO betting_odds (
                            match_id, bookmaker,
                            odd_home, odd_draw, odd_away,
                            prob_home, prob_draw, prob_away,
                            odd_over25, odd_under25
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (match_id, bookmaker) DO UPDATE SET
                            odd_home  = EXCLUDED.odd_home,
                            odd_draw  = EXCLUDED.odd_draw,
                            odd_away  = EXCLUDED.odd_away,
                            prob_home = EXCLUDED.prob_home,
                            prob_draw = EXCLUDED.prob_draw,
                            prob_away = EXCLUDED.prob_away
                    """, (
                        match_id, bookmaker,
                        oh, od, oa,
                        implied_prob(oh), implied_prob(od), implied_prob(oa),
                        over25, under25,
                    ))
                    total_inserted += 1

    conn.commit()
    print(f"\n✅ {total_inserted} entrées de cotes insérées au total")
    print(f"⚠️  {total_skipped} matchs ignorés")
    print("✨ ETL Step 4 terminé.")


def main():
    print("🚀 ETL Step 4 — Betting Odds Enrichissement")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_etl(conn)


if __name__ == "__main__":
    main()
