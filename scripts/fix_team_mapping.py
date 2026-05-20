import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/l1_datalab")

# Mapping Team Name -> (Internal Name, External ID Suffix 2024, Betting Name)
TEAMS_2024 = {
    "Paris Saint-Germain": ("paris-saint-germain", "13", "Paris SG"),
    "Olympique de Marseille": ("olympique-de-marseille", "1", "Marseille"),
    "AS Monaco": ("as-monaco", "9", "Monaco"),
    "LOSC Lille": ("lille-osc", "158", "Lille"),
    "Olympique Lyonnais": ("olympique-lyonnais", "159", "Lyon"),
    "OGC Nice": ("ogc-nice", "30", "Nice"),
    "RC Lens": ("rc-lens", "6", "Lens"),
    "Stade de Reims": ("stade-de-reims", "41", "Reims"),
    "Stade Rennais FC": ("stade-rennais", "14", "Rennes"),
    "Toulouse FC": ("toulouse-fc", "16", "Toulouse"),
    "Montpellier HSC": ("montpellier-hsc", "10", "Montpellier"),
    "RC Strasbourg Alsace": ("rc-strasbourg", "15", "Strasbourg"),
    "FC Nantes": ("fc-nantes", "12", "Nantes"),
    "Havre Athletic Club": ("le-havre", "5", "Le Havre"),
    "Stade Brestois 29": ("stade-brestois", "44", "Brest"),
    "AJ Auxerre": ("aja-auxerre", "2", "Auxerre"),
    "Angers SCO": ("angers-sco", "37", "Angers"),
    "AS Saint-Étienne": ("saint-etienne", "31", "St Etienne"),
}

def run_fix():
    print("🚀 Fixing Team Mapping and matches...")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            for display_name, (internal_name, suffix, betting_name) in TEAMS_2024.items():
                # 1. Ensure team exists in teams table
                cur.execute("""
                    INSERT INTO teams (internal_name, display_name, is_active)
                    VALUES (%s, %s, TRUE)
                    ON CONFLICT (internal_name) DO UPDATE SET
                        display_name = EXCLUDED.display_name
                    RETURNING id
                """, (internal_name, display_name))
                team_id = cur.fetchone()["id"]

                # 2. Add 2024 mapping
                ext_id_2024 = f"l1_championship_club_2024_{suffix}"
                cur.execute("""
                    INSERT INTO entity_mapping (entity_type, source, external_id, external_name, internal_id, confidence)
                    VALUES ('team', 'api_ligue1', %s, %s, %s, 1.0)
                    ON CONFLICT (source, external_id) DO UPDATE SET
                        internal_id = EXCLUDED.internal_id,
                        external_name = EXCLUDED.external_name
                """, (ext_id_2024, display_name, team_id))

                # 3. Add 2025 mapping
                ext_id_2025 = f"l1_championship_club_2025_{suffix}"
                cur.execute("""
                    INSERT INTO entity_mapping (entity_type, source, external_id, external_name, internal_id, confidence)
                    VALUES ('team', 'api_ligue1', %s, %s, %s, 1.0)
                    ON CONFLICT (source, external_id) DO UPDATE SET
                        internal_id = EXCLUDED.internal_id,
                        external_name = EXCLUDED.external_name
                """, (ext_id_2025, display_name, team_id))
                
                # 4. Add betting mapping for consistency
                cur.execute("""
                    INSERT INTO entity_mapping (entity_type, source, external_id, external_name, internal_id, confidence)
                    VALUES ('team', 'betting_fduk', %s, %s, %s, 0.95)
                    ON CONFLICT (source, external_id) DO UPDATE SET
                        internal_id = EXCLUDED.internal_id,
                        external_name = EXCLUDED.external_name
                """, (betting_name, betting_name, team_id))

                print(f"  ✅ Team: {display_name} (id={team_id}) -> {ext_id_2024} & {ext_id_2025} & Betting: {betting_name}")

            # 5. Fix already ingested matches by deleting them so they can be re-ingested correctly
            cur.execute("DELETE FROM matches WHERE season = '2024/25' AND source = 'api_ligue1'")
            print(f"  🗑️ Deleted {cur.rowcount} orphan matches from season 2024/25")

        conn.commit()
    print("✨ Fix completed.")

if __name__ == "__main__":
    run_fix()
