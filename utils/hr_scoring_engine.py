import json
import os
from typing import List, Dict, Any

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "hr_scoring_config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    # Default configuration
    CONFIG = {
        "weights": {
            "relevance": 0.4,
            "communication": 0.2,
            "confidence": 0.2,
            "consistency": 0.2
        },
        "normalize_by_length": True,
        "relevance": {
            "use_ats": True
        }
    }

WEIGHTS = CONFIG.get("weights", {})
NORMALIZE = CONFIG.get("normalize_by_length", True)
USE_ATS = CONFIG.get("relevance", {}).get("use_ats", True)

def _normalize_score(score: float, length: int) -> float:
    """Optional length‑based normalization. Currently uses simple linear scaling:
    score = score * (1 + 0.1 * (length - 3))  # assume 3‑question baseline
    """
    if not NORMALIZE:
        return score
    # Prevent division by zero
    factor = 1 + 0.1 * max(0, length - 3)
    return min(score * factor, 100.0)

class HRScoringEngine:
    """Engine to compute an overall HR interview score.

    The engine expects four sub‑metrics:
    * relevance (0‑1)
    * communication (0‑1) – from utils.communication_scoring
    * confidence (0‑1) – from utils.confidence_analyzer
    * consistency (0‑1)
    It combines them using configurable weights and optionally normalises
    the final score based on interview length.
    """

    def __init__(self):
        self.weights = WEIGHTS
        self.normalize = NORMALIZE
        self.use_ats = USE_ATS
        # Placeholder for ATS relevance logic – can be extended later
        self.ats_keywords = []
        if self.use_ats:
            # Load ATS keyword list if exists
            ats_path = os.path.join(os.path.dirname(__file__), "..", "config", "ats_keywords.json")
            if os.path.exists(ats_path):
                with open(ats_path, "r", encoding="utf-8") as f:
                    self.ats_keywords = json.load(f).get("keywords", [])

    def compute_relevance(self, answer_obj: Dict[str, Any]) -> float:
        """Calculate relevance of an answer.
        If ATS mode is on, naive keyword overlap is used; otherwise a neutral 0.5.
        Returns a value in the 0‑1 range.
        """
        if not self.use_ats or not self.ats_keywords:
            return 0.5
        text = answer_obj.get("answer", {}).get("raw_text", "")
        
        # Import dynamically to avoid circular dependencies if any
        from utils.text_cleaner import clean_text
        text = clean_text(text)
        
        if not text:
            return 0.0
            
        matches = sum(1 for kw in self.ats_keywords if kw.lower() in text)
        return max(0.0, min(matches / len(self.ats_keywords), 1.0)) if self.ats_keywords else 0.5

    def compute_consistency(self, current_answer: str, history: List[Dict[str, Any]]) -> float:
        """Very simple consistency check.
        If the current answer repeats content from previous answers, penalise.
        Returns 0‑1 where 1 is fully consistent (no contradictions).
        """
        if not history:
            return 1.0
            
        from utils.text_cleaner import clean_text
        current_answer = clean_text(current_answer)
        if not current_answer:
            return 0.5 # Neutral for empty
            
        curr_words = set(current_answer.split())
        if not curr_words:
            return 0.5
            
        overlap = 0
        for entry in history:
            prev = clean_text(entry.get("answer", {}).get("raw_text", ""))
            overlap += len(curr_words & set(prev.split()))
            
        # Normalize overlap: more overlap -> lower consistency
        max_possible = len(curr_words) * len(history)
        if max_possible == 0:
            return 1.0
        ratio = overlap / max_possible
        return max(0.0, min(1.0 - ratio, 1.0))

    def aggregate_score(self, metrics: Dict[str, float]) -> float:
        """Weighted sum of sub‑metrics (each 0‑1) → 0‑100.
        Missing metrics default to 0.5.
        Clamps the final output to 0-100.
        """
        total = 0.0
        weight_sum = sum(self.weights.values()) or 1.0
        for key, weight in self.weights.items():
            val = metrics.get(key, 0.5)
            # Ensure sub-metric is clamped 0-1 before weighting
            val = max(0.0, min(val, 1.0))
            total += weight * val
            
        normalized = total / weight_sum
        return max(0.0, min(round(normalized * 100, 2), 100.0))

    def generate_report(self, candidate_id: str, metrics: Dict[str, float], final_score: float = None, interview_length: int = None) -> Dict[str, Any]:
        """Return a structured report.
        If `final_score` is None, it will be computed from `metrics`.
        """
        if final_score is None:
            final_score = self.aggregate_score(metrics)
            if interview_length is not None:
                final_score = _normalize_score(final_score, interview_length)
                
        # Explainability: Determine which metric had the strongest positive/negative impact
        strongest = max(metrics, key=metrics.get) if metrics else "none"
        weakest = min(metrics, key=metrics.get) if metrics else "none"
        explain_note = (f"Scores are weighted according to configuration and normalized for interview length. "
                        f"Strongest indicator: {strongest}. Weakest indicator: {weakest}.")
                        
        report = {
            "candidate_id": candidate_id,
            "final_score": final_score,
            "breakdown": {
                "relevance": round(metrics.get("relevance", 0.5) * 100, 2),
                "communication": round(metrics.get("communication", 0.5) * 100, 2),
                "confidence": round(metrics.get("confidence", 0.5) * 100, 2),
                "consistency": round(metrics.get("consistency", 0.5) * 100, 2)
            },
            "explainability_note": explain_note
        }
        return report

__all__ = ["HRScoringEngine"]
