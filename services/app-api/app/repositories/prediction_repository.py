from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from ..models.models import Prediction, Match

class PredictionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_prediction(self, user_id: int, match_id: int, result: str, prob_h: float, prob_d: float, prob_a: float):
        prediction = Prediction(
            user_id=user_id,
            match_id=match_id,
            predicted_result=result,
            prob_h=prob_h,
            prob_d=prob_d,
            prob_a=prob_a
        )
        self.session.add(prediction)
        await self.session.flush()
        return prediction

    async def get_user_predictions(self, user_id: int):
        query = (
            select(Prediction)
            .options(
                joinedload(Prediction.match).joinedload(Match.home_team),
                joinedload(Prediction.match).joinedload(Match.away_team),
            )
            .where(Prediction.user_id == user_id)
            .order_by(Prediction.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()
