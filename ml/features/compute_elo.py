import os
import pandas as pd
import psycopg
from psycopg.rows import dict_row
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
K_FACTOR = 32  # Sensibilité de l'ajustement Elo
INITIAL_ELO = 1500

def get_expected_score(rating_a, rating_b):
    """Calcule le score attendu (probabilité de victoire) pour l'équipe A."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating, actual_score, expected_score):
    """Met à jour le score Elo après un match."""
    return rating + K_FACTOR * (actual_score - expected_score)

def run_elo_calculation():
    print("🚀 Calcul des scores Elo historiques...")
    
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # Récupérer tous les matchs terminés par ordre chronologique
            cur.execute("""
                SELECT id, kickoff, home_team_id, away_team_id, result
                FROM matches
                WHERE result IS NOT NULL
                ORDER BY kickoff ASC NULLS FIRST
            """)
            matches = cur.fetchall()
            
            if not matches:
                print("❌ Aucun match trouvé pour le calcul Elo.")
                return

            # Dictionnaire pour stocker les Elo actuels {team_id: current_elo}
            elo_history = {}
            match_elos = [] # Liste de dict {match_id: X, home_elo: X, away_elo: X}

            for m in matches:
                h_id = m["home_team_id"]
                a_id = m["away_team_id"]
                res = m["result"]

                # Initialisation si équipe inconnue
                if h_id not in elo_history: elo_history[h_id] = INITIAL_ELO
                if a_id not in elo_history: elo_history[a_id] = INITIAL_ELO

                h_elo_pre = elo_history[h_id]
                a_elo_pre = elo_history[a_id]

                # Stocker les Elo AVANT le match pour le dataset ML
                match_elos.append({
                    "match_id": m["id"],
                    "home_elo": round(h_elo_pre, 1),
                    "away_elo": round(a_elo_pre, 1)
                })

                # Calcul des scores réels
                # H wins: home=1, away=0
                # D: home=0.5, away=0.5
                # A wins: home=0, away=1
                if res == 'H':
                    actual_h, actual_a = 1.0, 0.0
                elif res == 'D':
                    actual_h, actual_a = 0.5, 0.5
                else:
                    actual_h, actual_a = 0.0, 1.0

                # Calcul des scores attendus
                exp_h = get_expected_score(h_elo_pre, a_elo_pre)
                exp_a = get_expected_score(a_elo_pre, h_elo_pre)

                # Mise à jour
                elo_history[h_id] = update_elo(h_elo_pre, actual_h, exp_h)
                elo_history[a_id] = update_elo(a_elo_pre, actual_a, exp_a)

            # 1. Export des Elos par match (Historique)
            df_elos = pd.DataFrame(match_elos)
            output_path = Path(__file__).resolve().parents[2] / "ml" / "features" / "match_elos.csv"
            df_elos.to_csv(output_path, index=False)
            
            # 2. Export des derniers Elos connus (pour Inférence Future)
            latest_elos_path = Path(__file__).resolve().parents[2] / "ml" / "features" / "latest_elos.json"
            import json
            with open(latest_elos_path, 'w') as f:
                json.dump(elo_history, f)
            
            print(f"✅ Calcul terminé.")
            print(f"📊 Historique : {output_path}")
            print(f"🔮 Derniers Elos : {latest_elos_path}")
            
            # Afficher le Top 5 actuel
            cur.execute("SELECT id, internal_name FROM teams")
            team_names = {t["id"]: t["internal_name"] for t in cur.fetchall()}
            
            print("\n🏆 Top 5 Elo Actuel (en fin d'historique) :")
            sorted_teams = sorted(elo_history.items(), key=lambda x: x[1], reverse=True)
            for tid, score in sorted_teams[:5]:
                print(f"- {team_names.get(tid, 'Inconnu')}: {score:.1f}")

if __name__ == "__main__":
    run_elo_calculation()
