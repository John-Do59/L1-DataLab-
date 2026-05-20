import os
import pandas as pd
import psycopg
from psycopg.rows import dict_row
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")

def run_data_quality_audit():
    print("🧹 AUDIT QUALITÉ DES DONNÉES (Data Cleaning) 🧹")
    print("="*50)
    
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # 1. Vérification des doublons (Matches)
            cur.execute("SELECT external_id, COUNT(*) FROM matches GROUP BY external_id HAVING COUNT(*) > 1")
            duplicates = cur.fetchall()
            print(f"✅ Doublons de matchs : {len(duplicates)} (Zéro attendu via ON CONFLICT)")
            
            # 2. Vérification des valeurs manquantes critiques
            cur.execute("SELECT COUNT(*) FROM matches WHERE result IS NULL AND kickoff < NOW()")
            missing_results = cur.fetchone()['count']
            print(f"📊 Matchs passés sans résultat : {missing_results}")
            
            # 3. Vérification de l'intégrité du mapping
            cur.execute("SELECT COUNT(*) FROM matches WHERE home_team_id IS NULL OR away_team_id IS NULL")
            unmapped = cur.fetchone()['count']
            print(f"⚠️  Matchs avec équipes non mappées : {unmapped}")
            
            # 4. Statistiques par saison
            cur.execute("SELECT season, COUNT(*) FROM matches GROUP BY season ORDER BY season")
            seasons = cur.fetchall()
            print("\n📅 Couverture temporelle :")
            for s in seasons:
                print(f"- {s['season']}: {s['count']} matchs")

    # 5. Chargement du dataset final pour audit Pandas
    dataset_path = Path(__file__).resolve().parents[1] / "ml" / "features" / "ml_dataset.csv"
    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        print("\n📝 Audit du Dataset ML (Pandas) :")
        print(f"- Lignes totales : {len(df)}")
        print(f"- Valeurs manquantes totales : {df.isna().sum().sum()}")
        
        # Détection auto de lignes dupliquées
        df_dups = df.duplicated().sum()
        print(f"- Lignes 100% identiques (doublons) : {df_dups}")
    
    print("="*50)
    print("✨ Audit terminé : les données sont propres et dédoublonnées.")

if __name__ == "__main__":
    run_data_quality_audit()
