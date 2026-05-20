from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    predictions: Mapped[List["Prediction"]] = relationship(back_populates="user")

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Stats dynamiques pour le ML
    elo: Mapped[float] = mapped_column(Float, default=1500.0)
    form_5: Mapped[float] = mapped_column(Float, default=0.5)
    avg_overall: Mapped[float] = mapped_column(Float, default=70.0)
    squad_value: Mapped[float] = mapped_column(Float, default=100.0)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    match_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    season: Mapped[str] = mapped_column(String(10))
    round: Mapped[int] = mapped_column(Integer)
    
    # Cotes (facultatif, pour le ML)
    odds_h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    odds_d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    odds_a: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="scheduled") # scheduled, finished
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    home_team: Mapped["Team"] = relationship("Team", foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship("Team", foreign_keys=[away_team_id])

class Prediction(Base):
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    predicted_result: Mapped[str] = mapped_column(String(1))  # H, D, A
    
    # Probabilités détaillées renvoyées par XGBoost
    prob_h: Mapped[float] = mapped_column(Float)
    prob_d: Mapped[float] = mapped_column(Float)
    prob_a: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="predictions")
    match: Mapped["Match"] = relationship("Match")
