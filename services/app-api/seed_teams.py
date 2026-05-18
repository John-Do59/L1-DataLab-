import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

try:
    from app.models.models import Team
except ImportError:
    from models.models import Team

DATABASE_URL = "postgresql+asyncpg://l1user:l1password@db-app:5432/l1_app"

async def seed_teams():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    teams_data = [
        # 8 Clubs Historiques
        {"name": "Paris Saint-Germain", "elo": 1850.5, "form_5": 0.8, "avg_overall": 82.5, "squad_value": 800.0},
        {"name": "Marseille", "elo": 1650.2, "form_5": 0.6, "avg_overall": 78.0, "squad_value": 300.0},
        {"name": "Monaco", "elo": 1680.0, "form_5": 0.7, "avg_overall": 79.0, "squad_value": 350.0},
        {"name": "Lyon", "elo": 1620.4, "form_5": 0.5, "avg_overall": 77.5, "squad_value": 250.0},
        {"name": "Lille", "elo": 1640.8, "form_5": 0.65, "avg_overall": 77.0, "squad_value": 220.0},
        {"name": "Lens", "elo": 1610.0, "form_5": 0.55, "avg_overall": 76.0, "squad_value": 180.0},
        {"name": "Nice", "elo": 1605.5, "form_5": 0.6, "avg_overall": 76.5, "squad_value": 200.0},
        {"name": "Rennes", "elo": 1590.2, "form_5": 0.5, "avg_overall": 75.5, "squad_value": 190.0},
        
        # Autres clubs de Ligue 1 (2025/2026)
        {"name": "Reims", "elo": 1550.0, "form_5": 0.5, "avg_overall": 74.5, "squad_value": 120.0},
        {"name": "Brest", "elo": 1585.0, "form_5": 0.6, "avg_overall": 75.0, "squad_value": 110.0},
        {"name": "Toulouse FC", "elo": 1520.0, "form_5": 0.45, "avg_overall": 73.5, "squad_value": 85.0},
        {"name": "Strasbourg", "elo": 1510.0, "form_5": 0.45, "avg_overall": 73.0, "squad_value": 90.0},
        {"name": "Montpellier", "elo": 1495.0, "form_5": 0.4, "avg_overall": 72.5, "squad_value": 75.0},
        {"name": "Havre AC", "elo": 1470.0, "form_5": 0.35, "avg_overall": 71.0, "squad_value": 45.0},
        {"name": "FC Nantes", "elo": 1490.0, "form_5": 0.4, "avg_overall": 72.5, "squad_value": 70.0},
        {"name": "AJ Auxerre", "elo": 1480.0, "form_5": 0.45, "avg_overall": 71.5, "squad_value": 48.0},
        {"name": "Angers SCO", "elo": 1460.0, "form_5": 0.3, "avg_overall": 70.5, "squad_value": 35.0},
        {"name": "Saint-Étienne", "elo": 1485.0, "form_5": 0.4, "avg_overall": 72.0, "squad_value": 55.0},
        
        # Clubs promotion/relégation (selon calendrier)
        {"name": "FC Lorient", "elo": 1480.0, "form_5": 0.4, "avg_overall": 72.0, "squad_value": 50.0},
        {"name": "FC Metz", "elo": 1465.0, "form_5": 0.35, "avg_overall": 71.0, "squad_value": 40.0},
        {"name": "Paris FC", "elo": 1455.0, "form_5": 0.35, "avg_overall": 70.5, "squad_value": 30.0}
    ]

    async with async_session() as session:
        # Nettoyage propre avant ré-insertion
        await session.execute(text("TRUNCATE TABLE teams CASCADE;"))
        for data in teams_data:
            team = Team(**data)
            session.add(team)
        await session.commit()
    print("✅ All 21 Ligue 1 teams seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_teams())
