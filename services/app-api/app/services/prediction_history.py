from app.models.models import Prediction, Team
from app.schemas.schemas import PredictionHistoryResponse, MatchResponse, TeamResponse


def team_to_response(team: Team) -> TeamResponse:
    return TeamResponse(
        id=team.id,
        name=team.name,
        elo_rating=team.elo,
        logo=team.logo_url,
    )


def prediction_to_history(pred: Prediction) -> PredictionHistoryResponse:
    match = pred.match
    return PredictionHistoryResponse(
        id=pred.id,
        match=MatchResponse(
            id=match.id,
            home_team=team_to_response(match.home_team),
            away_team=team_to_response(match.away_team),
            match_date=match.match_date,
            status=match.status,
        ),
        predicted_result=pred.predicted_result,
        prob_h=pred.prob_h,
        prob_d=pred.prob_d,
        prob_a=pred.prob_a,
        created_at=pred.created_at,
        real_home_score=match.home_score,
        real_away_score=match.away_score,
        real_status=match.status,
    )
