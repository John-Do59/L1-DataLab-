from ..models.models import Team

class FeatureService:
    @staticmethod
    def prepare_features(home_team: Team, away_team: Team, odds_h: float = 0.33, odds_d: float = 0.33, odds_a: float = 0.33) -> dict:
        """
        Calcule et prépare les features exactes attendues par le modèle XGBoost
        à partir des statistiques en direct des équipes.
        """
        # Calcul des différences (Ingénierie de caractéristiques)
        elo_diff = home_team.elo - away_team.elo
        
        return {
            "home_elo": float(home_team.elo),
            "away_elo": float(away_team.elo),
            "elo_diff": float(elo_diff),
            "home_form_5": float(home_team.form_5),
            "away_form_5": float(away_team.form_5),
            "home_avg_overall": float(home_team.avg_overall),
            "away_avg_overall": float(away_team.avg_overall),
            "home_squad_value": float(home_team.squad_value),
            "away_squad_value": float(away_team.squad_value),
            # Cotes (facultatif ou à récupérer depuis une autre source live, mockées ici par défaut si absentes)
            "odds_prob_home": float(odds_h),
            "odds_prob_draw": float(odds_d),
            "odds_prob_away": float(odds_a)
        }
