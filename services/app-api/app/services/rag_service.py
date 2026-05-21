"""Compat — délégué au package app.rag."""
from app.rag.orchestrator import RagOrchestrator

async def answer_question(question: str, *, user_id: int = 0, conversation_id=None, db=None, user_predictions_summary: str = "") -> dict:
    if db is None or not user_id:
        from app.rag.retrieval.context_builder import build_retrieval_context, build_fallback_answer
        ctx, _ = await build_retrieval_context(question, user_predictions_summary)
        return {"answer": build_fallback_answer(question, ctx, user_predictions_summary), "sources": ["LFP"], "model": "l1-rag-contextual-v1"}
    return await RagOrchestrator(db).answer_once(user_id, question, conversation_id)
