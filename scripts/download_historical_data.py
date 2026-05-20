import kagglehub
import shutil
import os
from pathlib import Path

def download_historical_data():
    print("🚀 Téléchargement du dataset historique Ligue 1 (1999-2019)...")
    
    # Téléchargement via kagglehub
    path = kagglehub.dataset_download("brunoo/ligue-1-results-1999-to-2019")
    
    # Définition de la destination dans le projet
    project_root = Path(__file__).resolve().parents[1]
    dest_dir = project_root / "data" / "historical"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Déplacement des fichiers vers data/historical
    print(f"📦 Extraction des fichiers vers {dest_dir}...")
    for filename in os.listdir(path):
        src_file = os.path.join(path, filename)
        dest_file = dest_dir / filename
        shutil.copy2(src_file, dest_file)
        print(f"✅ Fichier copié : {filename}")

def download_transfermarkt_data():
    print("🚀 Téléchargement du dataset Transfermarkt (David Cariboo)...")
    path = kagglehub.dataset_download("davidcariboo/player-scores")
    
    project_root = Path(__file__).resolve().parents[1]
    dest_dir = project_root / "data" / "transfermarkt"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for filename in os.listdir(path):
        src_file = os.path.join(path, filename)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dest_dir / filename)
            print(f"✅ Fichier copié : {filename}")

def download_fc24_data():
    print("🚀 Téléchargement du dataset EA Sports FC 24 (FIFA)...")
    path = kagglehub.dataset_download("stefanoleone992/ea-sports-fc-24-complete-player-dataset")
    
    project_root = Path(__file__).resolve().parents[1]
    dest_dir = project_root / "data" / "fc24"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for filename in os.listdir(path):
        src_file = os.path.join(path, filename)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dest_dir / filename)
            print(f"✅ Fichier copié : {filename}")

if __name__ == "__main__":
    try:
        download_historical_data()
        download_transfermarkt_data()
        download_fc24_data()
        print("\n✨ Toutes les sources externes sont prêtes dans data/")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
