import hashlib
import math
from typing import List

EMBED_DIM = 64

def embed_text(text: str) -> List[float]:
    vec = [0.0] * EMBED_DIM
    if not text:
        return vec
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).hexdigest()
        idx = int(digest[:8], 16) % EMBED_DIM
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)
