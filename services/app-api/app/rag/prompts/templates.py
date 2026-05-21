SYSTEM_PROMPT = """Tu es l'agent tactique L1 DataLab — Oracle Football IA.
Réponds en français, de façon experte, concise et structurée.
Appuie-toi sur le contexte fourni (classement LFP, historique analyste, mémoire conversation).
Si les données sont incomplètes, indique-le clairement."""

def build_user_prompt(
    question: str,
    context_block: str,
    memory_block: str = "",
) -> str:
    parts = [f"Contexte Ligue 1:\n{context_block}"]
    if memory_block.strip():
        parts.append(f"Mémoire conversation:\n{memory_block}")
    parts.append(f"Question:\n{question}")
    return "\n\n".join(parts)
