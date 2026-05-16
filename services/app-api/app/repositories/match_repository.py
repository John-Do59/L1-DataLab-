from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from ..models.models import Match

class MatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, match_id: int):
        query = select(Match).options(
            joinedload(Match.home_team),
            joinedload(Match.away_team)
        ).where(Match.id == match_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self):
        query = select(Match).options(
            joinedload(Match.home_team),
            joinedload(Match.away_team)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
