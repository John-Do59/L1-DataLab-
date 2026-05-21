import os
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from pgvector.sqlalchemy import Vector
from ..core.database import Base

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    predictions: Mapped[List["Prediction"]] = relationship(back_populates="user")
    rag_conversations: Mapped[List["RagConversation"]] = relationship(back_populates="user")

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


class RagConversation(Base):
    __tablename__ = "rag_conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), default="Nouvelle analyse")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    summary_embedding: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    summary_vector: Mapped[Optional[list]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="rag_conversations")
    messages: Mapped[List["RagMessage"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class RagMessage(Base):
    __tablename__ = "rag_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("rag_conversations.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    embedding_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    embedding: Mapped[Optional[list]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["RagConversation"] = relationship(back_populates="messages")
