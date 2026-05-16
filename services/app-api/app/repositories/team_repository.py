from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.models import Team

class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, team_id: int):
        query = select(Team).where(Team.id == team_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str):
        query = select(Team).where(Team.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self):
        query = select(Team)
        result = await self.session.execute(query)
        return result.scalars().all()
