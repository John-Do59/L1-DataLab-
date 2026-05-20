import requests
import pandas as pd
from pathlib import Path

def download_betting_odds():
    print("🚀 Téléchargement des cotes et résultats récents (Football-Data.co.uk)...")
    
    # URL pour la Ligue 1 (F1) de la saison en cours (24/25)
    # Note: L'URL change selon la saison, on peut automatiser la boucle si besoin
    url = "https://www.football-data.co.uk/mmz4281/2425/F1.csv"
    
    project_root = Path(__file__).resolve().parents[1]
    dest_dir = project_root / "data" / "betting"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        dest_file = dest_dir / "ligue1_2425_odds.csv"
        with open(dest_file, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Fichier sauvegardé : {dest_file}")
        
        # Petit aperçu pour valider
        df = pd.read_csv(dest_file)
        print(f"📊 Colonnes récupérées : {list(df.columns[:10])}...")
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")

if __name__ == "__main__":
    download_betting_odds()
