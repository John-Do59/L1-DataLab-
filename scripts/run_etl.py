"""
ETL Orchestrator - Lance tous les scripts dans l'ordre strict.
Usage : python3 scripts/run_etl.py
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

STEPS = [
    ("Step 1 - Teams Normalization",   "etl_step1_teams.py"),
    ("Step 2 - Kaggle Historical",      "etl_step2_kaggle.py"),
    ("Step 3 - API Ligue 1 (Live)",     "etl_step3_api.py"),
    ("Step 4 - Betting Odds",           "etl_step4_betting.py"),
    ("Step 5 - FC24 Players",           "etl_step5_players.py"),
    ("Step 6 - Transfermarkt Values",   "etl_step6_values.py"),
]

ML_STEP = ("Feature Engineering",
           str(Path(__file__).parents[1] / "ml" / "features" / "create_ml_dataset.py"))


def run_step(label: str, script: str) -> bool:
    print(f"\n{'='*60}")
    print(f"🚀 {label}")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, str(SCRIPTS_DIR / script)])
    if result.returncode != 0:
        print(f"❌ ÉCHEC : {label}")
        return False
    print(f"✅ SUCCÈS : {label}")
    return True


def main():
    print("🏁 Démarrage du pipeline ETL complet — L1 DataLab\n")

    for label, script in STEPS:
        if not run_step(label, script):
            print(f"\n⛔ Pipeline arrêté à l'étape : {label}")
            sys.exit(1)

    # Feature Engineering optionnel
    label, script = ML_STEP
    run_step(label, script)

    print("\n\n🎉 Pipeline ETL complet terminé avec succès !")
    print("📁 Dataset ML disponible dans : ml/features/")


if __name__ == "__main__":
    main()
