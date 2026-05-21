from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import RagConversation, RagMessage
from .embeddings import embed_text, cosine_similarity

class RagMemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_conversation(
        self, user_id: int, conversation_id: Optional[int] = None
    ) -> RagConversation:
        if conversation_id:
            q = (
                select(RagConversation)
                .where(
                    RagConversation.id == conversation_id,
                    RagConversation.user_id == user_id,
                )
                .options(selectinload(RagConversation.messages))
            )
            res = await self.session.execute(q)
            conv = res.scalar_one_or_none()
            if conv:
                return conv

        conv = RagConversation(user_id=user_id, title="Nouvelle analyse", summary="")
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        *,
        metadata: Optional[dict] = None,
    ) -> RagMessage:
        msg = RagMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            embedding_json=embed_text(content),
            message_metadata=metadata or {},
        )
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def get_recent_messages(self, conversation_id: int, limit: int = 12) -> List[RagMessage]:
        q = (
            select(RagMessage)
            .where(RagMessage.conversation_id == conversation_id)
            .order_by(RagMessage.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(q)
        return list(reversed(res.scalars().all()))

    async def retrieve_relevant_memory(
        self, conversation_id: int, query: str, top_k: int = 4
    ) -> List[RagMessage]:
        q = select(RagMessage).where(RagMessage.conversation_id == conversation_id)
        res = await self.session.execute(q)
        messages = res.scalars().all()
        if not messages:
            return []
        query_emb = embed_text(query)
        scored = [
            (cosine_similarity(query_emb, m.embedding_json or []), m)
            for m in messages
            if m.role in ("user", "assistant") and m.embedding_json
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:top_k]]

    async def update_conversation_summary(
        self, conversation: RagConversation, latest_exchange: str
    ) -> None:
        prev = (conversation.summary or "").strip()
        snippet = latest_exchange[:500]
        conversation.summary = f"{prev}\n---\n{snippet}"[-2000:] if prev else snippet
        conversation.summary_embedding = embed_text(conversation.summary)
        conversation.updated_at = datetime.utcnow()
        if conversation.title == "Nouvelle analyse" and latest_exchange:
            conversation.title = latest_exchange.split("\n")[0][:80]
