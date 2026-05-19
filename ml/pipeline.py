"""
Orchestrateur MLOps Principal - Ligue 1 DataLab
Ce script coordonne l'ensemble du cycle de vie du modèle :
Ingestion/ETL -> Qualité -> Features -> Entraînement Challenger -> Calibration -> Champion/Challenger -> Promotion/Hot-Serving.

Usage : python3 ml/pipeline.py [--skip-etl]
"""
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import joblib

# Ajouter la racine du projet au PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# Imports du module d'entraînement
from ml.training.train_models import train_and_evaluate

MODELS_DIR = PROJECT_ROOT / "ml" / "models"
METADATA_PATH = MODELS_DIR / "metadata.json"
HISTORY_PATH = MODELS_DIR / "runs_history.json"

def run_subprocess_script(script_path: Path, label: str) -> bool:
    print(f"\n🚀 Exécution de : {label}...")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Échec de {label} !")
        print(f"--- Erreurs --- \n{result.stderr}")
        return False
    print(f"✅ {label} complété avec succès.")
    # Optionnel: afficher une partie de la sortie
    if result.stdout:
        print("\n".join(result.stdout.strip().split("\n")[-5:]))
    return True

def load_current_champion_metadata():
    if METADATA_PATH.exists():
        try:
            with open(METADATA_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de metadata.json : {e}")
    return None

def archive_run(run_metadata):
    history = []
    if HISTORY_PATH.exists():
        try:
            with open(HISTORY_PATH, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    
    history.append(run_metadata)
    # Limiter à 50 exécutions historiques pour économiser de l'espace
    history = history[-50:]
    
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Pipeline MLOps Ligue 1 DataLab")
    parser.add_argument("--skip-etl", action="store_true", help="Ignorer la phase d'extraction scraping/ETL")
    args = parser.parse_args()

    print("\n" + "="*80)
    print(f"🏁 LANCEMENT DU PIPELINE MLOPS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 1. Scraping & Ingestion ETL (Optionnel)
    if not args.skip_etl:
        etl_script = PROJECT_ROOT / "scripts" / "run_etl.py"
        if etl_script.exists():
            if not run_subprocess_script(etl_script, "Scraping & ETL Ingestion"):
                print("⛔ Pipeline stoppé en raison d'un échec de l'ETL.")
                sys.exit(1)
        else:
            print("⚠️ Script run_etl.py introuvable, étape ignorée.")
    else:
        print("⏭️ Étape Scraping/ETL ignorée à la demande de l'utilisateur.")

    # 2. Calcul ELO Historique
    elo_script = PROJECT_ROOT / "ml" / "features" / "compute_elo.py"
    match_elos_file = PROJECT_ROOT / "ml" / "features" / "match_elos.csv"
    latest_elos_file = PROJECT_ROOT / "ml" / "features" / "latest_elos.json"
    
    if elo_script.exists():
        if not run_subprocess_script(elo_script, "Calcul des Elos Historiques"):
            if match_elos_file.exists() and latest_elos_file.exists():
                print("\n⚠️  Connexion PostgreSQL impossible ou erreur de calcul Elo.")
                print("👉 Mode offline activé : utilisation de match_elos.csv et latest_elos.json existants.")
            else:
                print("⛔ Pipeline stoppé : fichiers Elo inexistants et base de données injoignable.")
                sys.exit(1)
    else:
        print("❌ Script compute_elo.py introuvable !")
        sys.exit(1)

    # 3. Features ML Dataset Creation
    dataset_script = PROJECT_ROOT / "ml" / "features" / "create_ml_dataset.py"
    ml_dataset_file = PROJECT_ROOT / "ml" / "features" / "ml_dataset.csv"
    
    if dataset_script.exists():
        if not run_subprocess_script(dataset_script, "Création du Dataset ML"):
            if ml_dataset_file.exists():
                print("\n⚠️  Connexion PostgreSQL impossible ou erreur de création du dataset.")
                print("👉 Mode offline activé : utilisation du ml_dataset.csv existant.")
            else:
                print("⛔ Pipeline stoppé : dataset ML inexistant et base de données injoignable.")
                sys.exit(1)
    else:
        print("❌ Script create_ml_dataset.py introuvable !")
        sys.exit(1)

    # 4. Audit Qualité des Données (Data Cleaning Post-Dataset)
    quality_script = PROJECT_ROOT / "scripts" / "validate_data_quality.py"
    if quality_script.exists():
        # L'audit de qualité peut échouer si PostgreSQL est hors-ligne, on le traite comme non-bloquant en offline
        if not run_subprocess_script(quality_script, "Audit Qualité des Données"):
            print("\n⚠️  L'audit qualité a échoué (PostgreSQL probablement hors-ligne). Mode offline : poursuite du pipeline.")
    else:
        print("⚠️ Script validate_data_quality.py introuvable, étape d'audit ignorée.")

    # 5. Entraînement et Calibration Platt vs Isotonic des Challengers
    print("\n🤖 Entraînement et Calibration des Challengers...")
    
    # Entraîner avec Sigmoïde
    results_sigmoid = train_and_evaluate(calibration_method="sigmoid")
    # Entraîner avec Isotonic
    results_isotonic = train_and_evaluate(calibration_method="isotonic")
    
    # Extraire les métriques
    rf_sig_brier = results_sigmoid["rf_metrics"]["brier_score"]
    rf_iso_brier = results_isotonic["rf_metrics"]["brier_score"]
    xgb_sig_brier = results_sigmoid["xgb_metrics"]["brier_score"]
    xgb_iso_brier = results_isotonic["xgb_metrics"]["brier_score"]
    
    print("\n🔬 --- Benchmark des Challengers (Validation temporelle) ---")
    print(f"- Random Forest (Platt Sigmoid)    : Brier Score = {rf_sig_brier:.4f}, Accuracy = {results_sigmoid['rf_metrics']['accuracy']:.2%}")
    print(f"- Random Forest (Isotonic Reg)     : Brier Score = {rf_iso_brier:.4f}, Accuracy = {results_isotonic['rf_metrics']['accuracy']:.2%}")
    print(f"- XGBoost Classifier (Platt Sig)  : Brier Score = {xgb_sig_brier:.4f}, Accuracy = {results_sigmoid['xgb_metrics']['accuracy']:.2%}")
    print(f"- XGBoost Classifier (Isotonic Reg): Brier Score = {xgb_iso_brier:.4f}, Accuracy = {results_isotonic['xgb_metrics']['accuracy']:.2%}")

    # Déterminer la meilleure combinaison
    challengers = [
        {"model_name": "RandomForestCalibrated", "calibration": "sigmoid", "results": results_sigmoid, "metrics": results_sigmoid["rf_metrics"], "model": results_sigmoid["rf_model"], "file_prefix": "rf"},
        {"model_name": "RandomForestCalibrated", "calibration": "isotonic", "results": results_isotonic, "metrics": results_isotonic["rf_metrics"], "model": results_isotonic["rf_model"], "file_prefix": "rf"},
        {"model_name": "XGBoostCalibrated", "calibration": "sigmoid", "results": results_sigmoid, "metrics": results_sigmoid["xgb_metrics"], "model": results_sigmoid["xgb_model"], "file_prefix": "xgb"},
        {"model_name": "XGBoostCalibrated", "calibration": "isotonic", "results": results_isotonic, "metrics": results_isotonic["xgb_metrics"], "model": results_isotonic["xgb_model"], "file_prefix": "xgb"}
    ]
    
    # Trier par Brier Score (le plus bas est le meilleur)
    challengers_sorted = sorted(challengers, key=lambda x: x["metrics"]["brier_score"])
    best_challenger = challengers_sorted[0]
    
    print(f"\n🎯 Meilleur Challenger identifié : {best_challenger['model_name']} ({best_challenger['calibration']}) avec un Brier Score de {best_challenger['metrics']['brier_score']:.4f}")

    # 6. Confrontation Champion vs Challenger
    champion_meta = load_current_champion_metadata()
    should_promote = False
    
    if not champion_meta:
        print("🆕 Aucun modèle Champion actif détecté. Promotion automatique du Challenger !")
        should_promote = True
        champion_brier = 999.0
    else:
        chosen_prod = champion_meta.get("chosen_production_model", "RandomForestCalibrated")
        # Trouver la métrique active du Champion
        active_model_details = champion_meta.get("models", {}).get(chosen_prod, {})
        champion_brier = active_model_details.get("metrics", {}).get("brier_score", 999.0)
        champion_acc = active_model_details.get("metrics", {}).get("accuracy", 0.0)
        
        print(f"\n👑 Champion en titre : {chosen_prod} | Brier Score = {champion_brier:.4f} | Accuracy = {champion_acc:.2%}")
        
        # Comparaison : Le challenger doit être strictement supérieur (Brier Score plus bas)
        # Seuil minimal de gain de 0.2%
        gain = champion_brier - best_challenger["metrics"]["brier_score"]
        if gain > 0.002: # gain significatif
            print(f"🔥 LE CHALLENGER EST SUPÉRIEUR ! Gain de Brier Score = {gain:.4f}")
            should_promote = True
        else:
            print(f"💤 Challenger rejeté. Gain insuffisant ({gain:.4f}) pour justifier une promotion.")

    # 7. Promotion et Sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_id = f"v_{timestamp}"
    
    # Chemins de fichiers pour le nouveau run
    model_filename = f"{best_challenger['file_prefix']}_{version_id}.joblib"
    encoder_filename = f"label_encoder_{version_id}.joblib"
    
    # Métadonnées de l'exécution courante
    run_info = {
        "timestamp": datetime.now().isoformat(),
        "version": version_id,
        "model_name": best_challenger["model_name"],
        "calibration_method": best_challenger["calibration"],
        "metrics": best_challenger["metrics"],
        "features_used": best_challenger["results"]["features_used"],
        "promoted": should_promote
    }

    if should_promote:
        print(f"\n🏆 PROMOTION DU MODÈLE : {best_challenger['model_name']} ({version_id})")
        
        # 1. Sauvegarde physique du modèle versionné
        joblib.dump(best_challenger["model"], MODELS_DIR / model_filename)
        joblib.dump(best_challenger["results"]["label_encoder"], MODELS_DIR / encoder_filename)
        
        # 2. Sauvegarde des fichiers champions standards (pour compatibilité ascendante)
        joblib.dump(best_challenger["model"], MODELS_DIR / f"{best_challenger['file_prefix']}_v1.joblib")
        joblib.dump(best_challenger["results"]["label_encoder"], MODELS_DIR / "label_encoder_v1.joblib")
        
        with open(MODELS_DIR / "classes.txt", "w") as f:
            for c in best_challenger["results"]["label_encoder"].classes_:
                f.write(f"{c}\n")

        # 3. Mise à jour de metadata.json
        new_metadata = best_challenger["results"]["metadata"]
        new_metadata["chosen_production_model"] = best_challenger["model_name"]
        new_metadata["active_model_file"] = model_filename
        new_metadata["active_encoder_file"] = encoder_filename
        new_metadata["active_version"] = version_id
        
        # Structurer les modèles
        new_metadata["models"] = {
            best_challenger["model_name"]: {
                "version": version_id,
                "file": model_filename,
                "metrics": best_challenger["metrics"]
            }
        }
        
        with open(METADATA_PATH, "w") as f:
            json.dump(new_metadata, f, indent=2)
            
        print(f"📢 Modèle champion déployé à chaud : {model_filename}")
    else:
        print("\n🔒 Maintien du modèle Champion en production.")

    # 8. Archivage dans l'historique
    archive_run(run_info)
    
    print("\n" + "="*80)
    print(f"🎉 PIPELINE TERMINÉ AVEC SUCCÈS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
