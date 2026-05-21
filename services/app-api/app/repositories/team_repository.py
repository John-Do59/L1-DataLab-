from typing import Optional
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

    async def get_or_create(
        self,
        name: str,
        *,
        elo: float = 1500.0,
        form_5: float = 0.5,
        avg_overall: float = 70.0,
        squad_value: float = 100.0,
        logo_url: Optional[str] = None,
    ) -> Team:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        team = Team(
            name=name,
            logo_url=logo_url or "https://ligue1.com/images/Logo_Ligue_1.webp",
            elo=elo,
            form_5=form_5,
            avg_overall=avg_overall,
            squad_value=squad_value,
        )
        self.session.add(team)
        await self.session.flush()
        return team
