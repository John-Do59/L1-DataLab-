"""
Feature Engineering - Create ML Dataset
========================================
Objectif : Transformer les tables DB en un dataset ML propre
           prêt pour l'entraînement d'un modèle de prédiction.

Features calculées :
    - rolling_form_5       : Résultats des 5 derniers matchs (points)
    - goals_scored_5       : Buts marqués sur 5 matchs
    - goals_conceded_5     : Buts concédés sur 5 matchs
    - offensive_strength   : Moyenne de buts marqués / match
    - defensive_strength   : Moyenne de buts concédés / match
    - home_win_rate        : Taux de victoire à domicile (historique)
    - away_win_rate        : Taux de victoire à l'extérieur
    - squad_avg_overall    : Moyenne FC24 overall de l'équipe
    - squad_total_value    : Valeur marchande totale (Transfermarkt)
    - odds_prob_home       : Probabilité implicite cote domicile (Avg)
    - odds_prob_draw       : Probabilité implicite match nul
    - odds_prob_away       : Probabilité implicite victoire extérieur

Label (cible) :
    - result : 'H' (Home win), 'D' (Draw), 'A' (Away win)

Output :
    - ml/features/ml_dataset.csv  (fichier complet)
    - ml/features/ml_dataset_l1_only.csv  (saison actuelle uniquement)
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "ml" / "features"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def compute_team_rolling_stats(matches_df: pd.DataFrame, team_id: int, before_date) -> dict:
    """Calcule les stats rolling des 5 derniers matchs d'une équipe avant une date."""
    team_matches = matches_df[
        ((matches_df["home_team_id"] == team_id) | (matches_df["away_team_id"] == team_id)) &
        (matches_df["kickoff"] < before_date) &
        (matches_df["result"].notna())
    ].sort_values("kickoff", ascending=False).head(5)

    if len(team_matches) == 0:
        return {
            "rolling_form_5": 0.0,
            "goals_scored_5": 0.0,
            "goals_conceded_5": 0.0,
            "offensive_strength": 0.0,
            "defensive_strength": 0.0,
        }

    points = 0
    scored = 0
    conceded = 0

    for _, m in team_matches.iterrows():
        is_home = m["home_team_id"] == team_id
        if is_home:
            gs = m["home_score"] or 0
            gc = m["away_score"] or 0
            result = m["result"]
            pts = {"H": 3, "D": 1, "A": 0}[result]
        else:
            gs = m["away_score"] or 0
            gc = m["home_score"] or 0
            result = m["result"]
            pts = {"A": 3, "D": 1, "H": 0}[result]

        points += pts
        scored += gs
        conceded += gc

    n = len(team_matches)
    return {
        "rolling_form_5": round(points / n, 3),
        "goals_scored_5": round(scored / n, 3),
        "goals_conceded_5": round(conceded / n, 3),
        "offensive_strength": round(scored / n, 3),
        "defensive_strength": round(conceded / n, 3),
    }


def get_squad_stats(cur, team_id: int) -> dict:
    """Récupère les stats FC24 et valeurs TM agrégées d'une équipe."""
    cur.execute("""
        SELECT
            AVG(fa.overall)::FLOAT      AS avg_overall,
            SUM(tv.market_value_eur)    AS total_value
        FROM players p
        LEFT JOIN fc24_attributes fa ON fa.player_id = p.id
        LEFT JOIN (
            SELECT DISTINCT ON (player_id)
                player_id, market_value_eur
            FROM transfermarkt_values
            ORDER BY player_id, valuation_date DESC
        ) tv ON tv.player_id = p.id
        WHERE p.current_team_id = %s
    """, (team_id,))
    row = cur.fetchone()
    return {
        "squad_avg_overall": round(row["avg_overall"] or 0, 2),
        "squad_total_value": int(row["total_value"] or 0),
    }


def get_betting_features(cur, match_id: int) -> dict:
    """Récupère les probabilités implicites moyennes pour un match."""
    cur.execute("""
        SELECT prob_home, prob_draw, prob_away
        FROM betting_odds
        WHERE match_id = %s AND bookmaker = 'Avg'
        LIMIT 1
    """, (match_id,))
    row = cur.fetchone()
    if row:
        return {
            "odds_prob_home": row["prob_home"],
            "odds_prob_draw": row["prob_draw"],
            "odds_prob_away": row["prob_away"],
        }
    return {"odds_prob_home": None, "odds_prob_draw": None, "odds_prob_away": None}


def run_feature_engineering(conn):
    with conn.cursor() as cur:
        # Chargement de TOUS les matchs (terminés et à venir)
        cur.execute("""
            SELECT m.id, m.season, m.kickoff, m.gameweek,
                   m.home_team_id, m.away_team_id,
                   m.home_score, m.away_score, m.result,
                   m.status,
                   ht.internal_name AS home_team_name,
                   at_.internal_name AS away_team_name
            FROM matches m
            JOIN teams ht  ON ht.id  = m.home_team_id
            JOIN teams at_ ON at_.id = m.away_team_id
            ORDER BY m.kickoff ASC NULLS FIRST
        """)
        matches_raw = cur.fetchall()

    if not matches_raw:
        print("❌ Aucun match trouvé en base.")
        return

    matches_df = pd.DataFrame(matches_raw)
    if "kickoff" not in matches_df.columns:
        matches_df["kickoff"] = pd.NaT
    else:
        matches_df["kickoff"] = pd.to_datetime(matches_df["kickoff"], utc=True, errors="coerce")

    print(f"✅ {len(matches_df)} matchs chargés (historique + futur)")

    # Chargement des scores Elo pré-calculés
    elos_path = PROJECT_ROOT / "ml" / "features" / "match_elos.csv"
    latest_elos_path = PROJECT_ROOT / "ml" / "features" / "latest_elos.json"
    
    import json
    if elos_path.exists():
        elos_df = pd.read_csv(elos_path)
    else:
        elos_df = pd.DataFrame(columns=["match_id", "home_elo", "away_elo"])

    latest_elos = {}
    if latest_elos_path.exists():
        with open(latest_elos_path, 'r') as f:
            latest_elos = json.load(f)

    rows = []
    with conn.cursor() as cur:
        for _, match in matches_df.iterrows():
            home_id = match["home_team_id"]
            away_id = match["away_team_id"]
            
            # Pour les matchs futurs, on prend "maintenant" comme date de référence pour les stats rolling
            ref_date = match["kickoff"] if pd.notna(match["kickoff"]) else pd.Timestamp.now(tz="UTC")

            # Rolling stats (basées sur les matchs terminés AVANT ce match)
            home_stats = compute_team_rolling_stats(matches_df, home_id, ref_date)
            away_stats = compute_team_rolling_stats(matches_df, away_id, ref_date)

            # Squad stats
            home_squad = get_squad_stats(cur, home_id)
            away_squad = get_squad_stats(cur, away_id)

            # Betting odds
            betting = get_betting_features(cur, match["id"])

            # Elo Ratings
            match_elo = elos_df[elos_df["match_id"] == match["id"]]
            if not match_elo.empty:
                h_elo = match_elo.iloc[0]["home_elo"]
                a_elo = match_elo.iloc[0]["away_elo"]
            else:
                # Fallback sur les derniers Elos connus (pour le futur)
                h_elo = latest_elos.get(str(home_id), 1500.0)
                a_elo = latest_elos.get(str(away_id), 1500.0)

            row = {
                "match_id":         match["id"],
                "season":           match["season"],
                "gameweek":         match.get("gameweek"),
                "status":           match["status"],
                "home_team":        match["home_team_name"],
                "away_team":        match["away_team_name"],
                # Elo features
                "home_elo":         h_elo,
                "away_elo":         a_elo,
                "elo_diff":         h_elo - a_elo,
                # Home features
                "home_form_5":      home_stats["rolling_form_5"],
                "home_goals_scored_5":   home_stats["goals_scored_5"],
                "home_goals_conceded_5": home_stats["goals_conceded_5"],
                "home_offensive_str":    home_stats["offensive_strength"],
                "home_defensive_str":    home_stats["defensive_strength"],
                "home_avg_overall":      home_squad["squad_avg_overall"],
                "home_squad_value":      home_squad["squad_total_value"],
                # Away features
                "away_form_5":      away_stats["rolling_form_5"],
                "away_goals_scored_5":   away_stats["goals_scored_5"],
                "away_goals_conceded_5": away_stats["goals_conceded_5"],
                "away_offensive_str":    away_stats["offensive_strength"],
                "away_defensive_str":    away_stats["defensive_strength"],
                "away_avg_overall":      away_squad["squad_avg_overall"],
                "away_squad_value":      away_squad["squad_total_value"],
                # Betting
                **betting,
                # Label
                "result":           match["result"],
            }
            rows.append(row)

    df_all = pd.DataFrame(rows)

    # 1. Dataset d'entraînement (matchs terminés)
    df_train = df_all[df_all["result"].notna()].copy()
    train_path = OUTPUT_DIR / "ml_dataset.csv"
    df_train.to_csv(train_path, index=False)
    print(f"\n✅ Dataset d'entraînement exporté : {train_path} ({len(df_train)} lignes)")

    # 2. Dataset d'inférence (matchs à venir)
    df_upcoming = df_all[df_all["result"].isna()].copy()
    upcoming_path = OUTPUT_DIR / "ml_upcoming.csv"
    df_upcoming.to_csv(upcoming_path, index=False)
    print(f"✅ Dataset d'inférence exporté : {upcoming_path} ({len(df_upcoming)} lignes)")

    # Affichage info distributions (sur le train)
    print(f"\n📊 Distribution des résultats (Train) :")
    print(df_train["result"].value_counts(normalize=True).round(3))


def main():
    print("🚀 Feature Engineering — Création du Dataset ML")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_feature_engineering(conn)


if __name__ == "__main__":
    main()
