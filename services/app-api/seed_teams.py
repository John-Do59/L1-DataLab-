import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Compatibilité Docker (Flat) vs Local
try:
    from app.models.models import Team
except ImportError:
    from models.models import Team

# FORCE ASYNCPG
DATABASE_URL = "postgresql+asyncpg://l1user:l1password@db-app:5432/l1_app"

async def seed_teams():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    teams_data = [
        {"name": "Paris Saint-Germain", "elo": 1850.5, "form_5": 0.8, "avg_overall": 82.5, "squad_value": 800.0},
        {"name": "Marseille", "elo": 1650.2, "form_5": 0.6, "avg_overall": 78.0, "squad_value": 300.0},
        {"name": "Monaco", "elo": 1680.0, "form_5": 0.7, "avg_overall": 79.0, "squad_value": 350.0},
        {"name": "Lyon", "elo": 1620.4, "form_5": 0.5, "avg_overall": 77.5, "squad_value": 250.0},
        {"name": "Lille", "elo": 1640.8, "form_5": 0.65, "avg_overall": 77.0, "squad_value": 220.0},
        {"name": "Lens", "elo": 1610.0, "form_5": 0.55, "avg_overall": 76.0, "squad_value": 180.0},
        {"name": "Nice", "elo": 1605.5, "form_5": 0.6, "avg_overall": 76.5, "squad_value": 200.0},
        {"name": "Rennes", "elo": 1590.2, "form_5": 0.5, "avg_overall": 75.5, "squad_value": 190.0},
    ]

    async with async_session() as session:
        for data in teams_data:
            team = Team(**data)
            session.add(team)
        await session.commit()
    print("✅ Teams seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_teams())
