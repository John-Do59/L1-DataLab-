import re
from typing import List, Optional
from app.services.lfp_client import lfp_client

def format_standings(standings: list) -> str:
    if not standings:
        return ""
    lines = []
    for i, row in enumerate(standings[:10], 1):
        name = row.get("club_name") or row.get("name") or row.get("team") or "?"
        pts = row.get("points") or row.get("pts") or "—"
        lines.append(f"{i}. {name} ({pts} pts)")
    return "\n".join(lines)

def format_predictions_summary(lines: List[str]) -> str:
    return "\n".join(lines) if lines else "Aucune prédiction enregistrée pour cet analyste."

def format_memory_block(summary: str, relevant_snippets: List[str], recent_turns: List[str]) -> str:
    parts = []
    if summary.strip():
        parts.append(f"Résumé session:\n{summary.strip()}")
    if relevant_snippets:
        parts.append("Extraits pertinents:\n" + "\n".join(relevant_snippets))
    if recent_turns:
        parts.append("Derniers échanges:\n" + "\n".join(recent_turns))
    return "\n\n".join(parts)

async def build_retrieval_context(
    question: str,
    user_predictions_summary: str,
    memory_summary: str = "",
    memory_snippets: Optional[List[str]] = None,
    recent_turns: Optional[List[str]] = None,
) -> tuple[str, bool]:
    standings = await lfp_client.get_standings() or []
    standings_text = format_standings(standings)
    data_complete = bool(standings)
    memory_block = format_memory_block(memory_summary, memory_snippets or [], recent_turns or [])
    blocks = []
    if standings_text:
        blocks.append(f"Classement LFP:\n{standings_text}")
    else:
        blocks.append("Classement LFP: indisponible (signal dégradé).")
    if user_predictions_summary:
        blocks.append(f"Prédictions analyste:\n{user_predictions_summary}")
    if memory_block:
        blocks.append(memory_block)
    return "\n\n".join(blocks), data_complete

def build_fallback_answer(question: str, context_block: str, hint: str) -> str:
    q = question.lower()
    if any(w in q for w in ("classement", "standings", "leader", "premier")):
        return f"Voici le contexte classement indexé:\n{context_block}\n\nSynthèse LFP L1 DataLab."
    if any(w in q for w in ("prédit", "prediction", "pronostic", "risque", "confiance")):
        return f"{hint}\n\n{context_block}\n\nUtilisez l'onglet Prédictions pour les probabilités H/D/A."
    team_match = re.search(r"(psg|paris|marseille|om|lyon|lille|monaco|rennes|nice|lens)", q)
    if team_match:
        return f"Analyse {team_match.group(1).upper()}:\n\n{context_block}"
    return f"Oracle L1 DataLab:\n\n{context_block}\n\nAffinez avec une équipe ou un angle tactique."
