from typing import Literal, Optional

EntityMood = Literal["stable", "risky", "uncertain", "glitch"]

def compute_entity_mood(
    *,
    confidence: float,
    data_complete: bool,
    question: str,
    max_prediction_prob: Optional[float] = None,
) -> tuple[EntityMood, float]:
    if not data_complete:
        return "glitch", min(confidence, 0.35)
    q = question.lower()
    if any(k in q for k in ("risque", "incertain", "surprise", "upset", "piège", "danger")):
        return "risky", max(0.25, min(confidence, 0.55))
    if max_prediction_prob is not None:
        if max_prediction_prob >= 0.72:
            return "stable", max_prediction_prob
        if max_prediction_prob <= 0.45:
            return "risky", max_prediction_prob
        return "uncertain", max_prediction_prob
    if confidence >= 0.72:
        return "stable", confidence
    if confidence <= 0.42:
        return "risky", confidence
    return "uncertain", confidence

def estimate_confidence_from_predictions(predictions: list) -> tuple[float, Optional[float]]:
    if not predictions:
        return 0.5, None
    max_probs = [max(p.prob_h, p.prob_d, p.prob_a) for p in predictions[:5]]
    if not max_probs:
        return 0.5, None
    return sum(max_probs) / len(max_probs), max(max_probs)
