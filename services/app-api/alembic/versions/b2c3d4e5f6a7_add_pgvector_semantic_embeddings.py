"""add pgvector semantic embeddings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None  # type: ignore


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    dim = 768
    if Vector is None:
        raise RuntimeError("pgvector package required for this migration")

    op.add_column(
        "rag_messages",
        sa.Column("embedding", Vector(dim), nullable=True),
    )
    op.add_column(
        "rag_conversations",
        sa.Column("summary_vector", Vector(dim), nullable=True),
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_rag_messages_embedding_hnsw
        ON rag_messages USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_rag_messages_embedding_hnsw")
    op.drop_column("rag_conversations", "summary_vector")
    op.drop_column("rag_messages", "embedding")
