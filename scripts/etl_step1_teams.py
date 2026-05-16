"""
ETL Step 1 - Teams Normalization
=================================
Objectif : Créer la table `teams` (source de vérité unique)
           et peupler `entity_mapping` pour les 18 clubs L1.

Sources utilisées :
    - data/raw/l1_clubs/*.json (API Ligue 1 — logos, couleurs, stades)
    - Dictionnaire de mapping manuel pour Kaggle & Betting

Ordre d'exécution : PREMIER (aucune dépendance)
"""

import os
import json
import glob
import unicodedata
import re
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

# ==========================================================
# CONFIG
# ==========================================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_CLUBS_PATTERN = str(PROJECT_ROOT / "data" / "raw" / "l1_clubs" / "*.json")


# ==========================================================
# MAPPING MANUEL : noms externes → nom canonique interne
# Résout le problème cross-source
# ==========================================================
TEAM_NAME_MAPPING = {
    # API Ligue 1 → canonical
    "Paris Saint-Germain":      "paris-saint-germain",
    "Olympique de Marseille":   "olympique-de-marseille",
    "Olympique Lyonnais":       "olympique-lyonnais",
    "AS Monaco":                "as-monaco",
    "Stade Rennais FC":         "stade-rennais",
    "RC Lens":                  "rc-lens",
    "Lille OSC":                "lille-osc",
    "OGC Nice":                 "ogc-nice",
    "Stade de Reims":           "stade-de-reims",
    "FC Nantes":                "fc-nantes",
    "Montpellier HSC":          "montpellier-hsc",
    "RC Strasbourg Alsace":     "rc-strasbourg",
    "Toulouse FC":              "toulouse-fc",
    "Le Havre AC":              "le-havre",
    "FC Lorient":               "fc-lorient",
    "Clermont Foot 63":         "clermont-foot",
    "Metz":                     "fc-metz",
    "Auxerre":                  "aja-auxerre",
    "Brest":                    "stade-brestois",
    "Angers SCO":               "angers-sco",

    # Kaggle Historical → canonical
    "Paris SG":     "paris-saint-germain",
    "Marseille":    "olympique-de-marseille",
    "Lyon":         "olympique-lyonnais",
    "Monaco":       "as-monaco",
    "Rennes":       "stade-rennais",
    "Lens":         "rc-lens",
    "Lille":        "lille-osc",
    "Nice":         "ogc-nice",
    "Reims":        "stade-de-reims",
    "Nantes":       "fc-nantes",
    "Montpellier":  "montpellier-hsc",
    "Strasbourg":   "rc-strasbourg",
    "Toulouse":     "toulouse-fc",
    "Le Havre":     "le-havre",
    "Lorient":      "fc-lorient",
    "Clermont":     "clermont-foot",
    "Metz":         "fc-metz",
    "Auxerre":      "aja-auxerre",
    "Brest":        "stade-brestois",
    "Angers":       "angers-sco",
    "St Etienne":   "saint-etienne",
    "Bordeaux":     "girondins-bordeaux",
    "Caen":         "sm-caen",
    "Bastia":       "sc-bastia",
    "Gueugnon":     "gueugnon",
    "Sedan":        "cs-sedan",
    "Nancy":        "as-nancy",
    "Troyes":       "estac-troyes",
    "Amiens":       "amiens-sc",
    "Dijon":        "dfco-dijon",
    "Guingamp":     "en-avant-guingamp",
    "Valenciennes": "valenciennes-fc",
    "Sochaux":      "fc-sochaux",
    "Evian":        "evian-thonon",
    "Ajaccio":      "ac-ajaccio",

    # Betting (Football-Data.co.uk) → canonical
    "Paris SG":     "paris-saint-germain",  # déjà mappé
}


def normalize_name(name: str) -> str:
    """Crée un slug canonique : 'Paris Saint-Germain' → 'paris-saint-germain'"""
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^a-z0-9\s-]", "", name.lower())
    name = re.sub(r"[\s]+", "-", name.strip())
    return name


def get_latest_clubs_file() -> Path | None:
    files = sorted(glob.glob(RAW_CLUBS_PATTERN))
    return Path(files[-1]) if files else None


def load_clubs_from_api() -> list[dict]:
    """Charge le dernier fichier de clubs scrappé depuis l'API."""
    filepath = get_latest_clubs_file()
    if not filepath:
        print("⚠️  Aucun fichier de clubs trouvé dans data/raw/l1_clubs/")
        return []
    with open(filepath) as f:
        return json.load(f)


def run_etl(conn):
    clubs = load_clubs_from_api()
    if not clubs:
        return

    print(f"✅ {len(clubs)} clubs chargés depuis l'API")

    with conn.cursor() as cur:
        for club in clubs:
            api_name = club.get("name", "")
            canonical = TEAM_NAME_MAPPING.get(api_name) or normalize_name(api_name)

            # Upsert dans teams
            cur.execute("""
                INSERT INTO teams (
                    internal_name, display_name, short_name,
                    primary_color, secondary_color, logo_url, stadium_id, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (internal_name) DO UPDATE SET
                    display_name    = EXCLUDED.display_name,
                    short_name      = EXCLUDED.short_name,
                    primary_color   = EXCLUDED.primary_color,
                    secondary_color = EXCLUDED.secondary_color,
                    logo_url        = EXCLUDED.logo_url,
                    stadium_id      = EXCLUDED.stadium_id
                RETURNING id
            """, (
                canonical,
                club.get("name"),
                club.get("short_name"),
                club.get("primary_color"),
                club.get("secondary_color"),
                club.get("logo_url"),
                club.get("stadium"),
            ))
            row = cur.fetchone()
            team_db_id = row["id"]
            print(f"  🟢 Team: {api_name} → {canonical} (id={team_db_id})")

            # Mapping source API
            cur.execute("""
                INSERT INTO entity_mapping (entity_type, source, external_id, external_name, internal_id, confidence)
                VALUES ('team', 'api_ligue1', %s, %s, %s, 1.0)
                ON CONFLICT (entity_type, source, external_name) DO UPDATE SET
                    external_id = EXCLUDED.external_id,
                    internal_id = EXCLUDED.internal_id
            """, (club.get("club_id"), api_name, team_db_id))

        # Mapping Kaggle & Betting depuis le dictionnaire
        for external_name, canonical in TEAM_NAME_MAPPING.items():
            # Cherche l'id correspondant
            cur.execute("SELECT id FROM teams WHERE internal_name = %s", (canonical,))
            result = cur.fetchone()
            if not result:
                continue
            team_id = result["id"]

            for source in ("kaggle_historical", "betting_fduk"):
                cur.execute("""
                    INSERT INTO entity_mapping (entity_type, source, external_name, internal_id, confidence)
                    VALUES ('team', %s, %s, %s, 0.95)
                    ON CONFLICT (entity_type, source, external_name) DO NOTHING
                """, (source, external_name, team_id))

    conn.commit()
    print("\n✨ ETL Step 1 terminé : teams + entity_mapping peuplés.")


def main():
    print("🚀 ETL Step 1 — Normalisation des équipes")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        run_etl(conn)


if __name__ == "__main__":
    main()
