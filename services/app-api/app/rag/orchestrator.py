import os
from typing import AsyncIterator, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.prediction_repository import PredictionRepository
from app.rag.generation.fallback import build_fallback_stream
from app.rag.generation.ollama import OLLAMA_MODEL, generate_ollama_once, stream_ollama
from app.rag.generation.streaming import sse_event
from app.rag.memory.repository import RagMemoryRepository
from app.rag.prompts.templates import SYSTEM_PROMPT, build_user_prompt
from app.rag.ranking.mood import compute_entity_mood, estimate_confidence_from_predictions
from app.rag.retrieval.context_builder import build_retrieval_context, build_fallback_answer, format_predictions_summary

OLLAMA_URL = os.getenv("OLLAMA_URL", "").rstrip("/")

class RagOrchestrator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.memory = RagMemoryRepository(session)
        self.pred_repo = PredictionRepository(session)

    async def _predictions_summary(self, user_id: int) -> str:
        predictions = await self.pred_repo.get_user_predictions(user_id)
        lines = []
        for p in predictions[:5]:
            try:
                m = p.match
                home, away = getattr(m, "home_team", None), getattr(m, "away_team", None)
                if home and away:
                    lines.append(
                        f"- {home.name} vs {away.name} → {p.predicted_result} "
                        f"(H:{p.prob_h:.0%} D:{p.prob_d:.0%} A:{p.prob_a:.0%})"
                    )
            except Exception:
                continue
        return format_predictions_summary(lines)

    async def prepare_turn(self, user_id: int, question: str, conversation_id: Optional[int] = None) -> dict:
        conv = await self.memory.get_or_create_conversation(user_id, conversation_id)
        await self.memory.add_message(conv.id, "user", question)
        predictions = await self.pred_repo.get_user_predictions(user_id)
        conf_est, max_prob = estimate_confidence_from_predictions(predictions)
        pred_summary = await self._predictions_summary(user_id)
        relevant = await self.memory.retrieve_relevant_memory(conv.id, question)
        recent = await self.memory.get_recent_messages(conv.id, limit=6)
        memory_snippets = [f"[{m.role}] {m.content[:200]}" for m in relevant if m.content]
        recent_turns = [f"{m.role}: {m.content[:150]}" for m in recent[-4:]]
        context_block, data_complete = await build_retrieval_context(
            question, pred_summary, conv.summary or "", memory_snippets, recent_turns
        )
        mood, confidence = compute_entity_mood(
            confidence=conf_est, data_complete=data_complete, question=question, max_prediction_prob=max_prob
        )
        return {
            "conversation_id": conv.id,
            "prompt": build_user_prompt(question, context_block, conv.summary or ""),
            "context_block": context_block,
            "pred_summary": pred_summary,
            "mood": mood,
            "confidence": round(confidence, 3),
            "question": question,
        }

    async def stream_answer(
        self, user_id: int, question: str, conversation_id: Optional[int] = None
    ) -> AsyncIterator[str]:
        prep = await self.prepare_turn(user_id, question, conversation_id)
        sources = (
            ["LFP live data", "Ollama LLM", "conversation memory"]
            if OLLAMA_URL
            else ["LFP standings API", "L1 contextual RAG", "conversation memory"]
        )
        model = OLLAMA_MODEL if OLLAMA_URL else "l1-rag-contextual-v1"
        meta = {
            "conversation_id": prep["conversation_id"],
            "mood": prep["mood"],
            "confidence": prep["confidence"],
            "sources": sources,
            "model": model,
        }
        yield sse_event("meta", meta)
        buffer: List[str] = []
        if OLLAMA_URL:
            token_iter = stream_ollama(prep["prompt"], SYSTEM_PROMPT)
        else:
            token_iter = build_fallback_stream(question, prep["context_block"], prep["pred_summary"])
        async for token in token_iter:
            buffer.append(token)
            yield sse_event("token", {"t": token, "full": "".join(buffer), "mood": prep["mood"]})
        answer = "".join(buffer)
        conv = await self.memory.get_or_create_conversation(user_id, prep["conversation_id"])
        await self.memory.add_message(conv.id, "assistant", answer, metadata={"mood": prep["mood"], "model": model})
        await self.memory.update_conversation_summary(conv, f"Q: {question[:200]}\nR: {answer[:400]}")
        yield sse_event("done", {**meta, "answer": answer})

    async def answer_once(self, user_id: int, question: str, conversation_id: Optional[int] = None) -> dict:
        prep = await self.prepare_turn(user_id, question, conversation_id)
        if OLLAMA_URL:
            text = await generate_ollama_once(prep["prompt"], SYSTEM_PROMPT)
            answer = text or build_fallback_answer(question, prep["context_block"], prep["pred_summary"])
            model = OLLAMA_MODEL if text else "l1-rag-contextual-v1"
            sources = ["LFP live data", "Ollama LLM", "conversation memory"] if text else ["L1 contextual RAG", "conversation memory"]
        else:
            answer = build_fallback_answer(question, prep["context_block"], prep["pred_summary"])
            model = "l1-rag-contextual-v1"
            sources = ["LFP standings API", "L1 DataLab knowledge base", "conversation memory"]
        conv = await self.memory.get_or_create_conversation(user_id, prep["conversation_id"])
        await self.memory.add_message(conv.id, "assistant", answer, metadata={"mood": prep["mood"], "model": model})
        await self.memory.update_conversation_summary(conv, f"Q: {question[:200]}\nR: {answer[:400]}")
        return {
            "answer": answer,
            "sources": sources,
            "model": model,
            "conversation_id": prep["conversation_id"],
            "mood": prep["mood"],
            "confidence": prep["confidence"],
        }
