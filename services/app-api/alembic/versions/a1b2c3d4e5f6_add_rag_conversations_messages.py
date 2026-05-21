"""add rag conversations and messages

Revision ID: a1b2c3d4e5f6
Revises: 979d21af5881
Create Date: 2026-05-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "979d21af5881"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "rag_conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("summary_embedding", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_conversations_user_id", "rag_conversations", ["user_id"])
    op.create_table(
        "rag_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding_json", sa.JSON(), nullable=True),
        sa.Column("message_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["rag_conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rag_messages_conversation_id", "rag_messages", ["conversation_id"])

def downgrade() -> None:
    op.drop_index("ix_rag_messages_conversation_id", table_name="rag_messages")
    op.drop_table("rag_messages")
    op.drop_index("ix_rag_conversations_user_id", table_name="rag_conversations")
    op.drop_table("rag_conversations")
