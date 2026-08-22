import json
import os
import re
from typing import Dict, List, Optional, Any

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'tech_scoring_config.json')


def _load_config() -> Dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "weights": {"accuracy": 0.40, "depth": 0.30, "logic": 0.20, "applicability": 0.10},
        "difficulty_multipliers": {"1": 1.0, "2": 1.2, "3": 1.5},
        "shallow_answer_threshold": 15,
        "deep_answer_threshold": 60,
        "logic_markers": ["because", "therefore", "however", "as a result", "for example"]
    }


class TechScoringEngine:
    """
    Evaluates the depth, accuracy, logic, and real-world applicability
    of technical interview answers.
    """

    def __init__(self):
        self.config = _load_config()
        self.weights = self.config.get("weights", {})
        self.multipliers = {
            int(k): v for k, v in self.config.get("difficulty_multipliers", {}).items()
        }
        self.shallow_threshold = self.config.get("shallow_answer_threshold", 15)
        self.deep_threshold = self.config.get("deep_answer_threshold", 60)
        self.logic_markers = self.config.get("logic_markers", [])
        self._question_scores: List[Dict] = []

    # ------------------------------------------------------------------
    # Sub-metric evaluators
    # ------------------------------------------------------------------

    def evaluate_accuracy(self, answer: str, required_concepts: List[str]) -> float:
        """
        Checks how many of the required concepts appear in the answer.
        Returns 0.0 – 1.0.
        """
        if not required_concepts:
            return 0.5  # No criteria → neutral
        answer_lower = answer.lower()
        hits = sum(1 for c in required_concepts if c.lower() in answer_lower)
        return max(0.0, min(hits / len(required_concepts), 1.0))

    def evaluate_depth(self, answer: str, bonus_concepts: Optional[List[str]] = None) -> float:
        """
        Detects deep answers via:
        - Word count (short answers are penalized)
        - Presence of bonus/advanced concepts
        Returns 0.0 – 1.0.
        """
        word_count = len(answer.split())
        bonus_concepts = bonus_concepts or []

        # Base depth from length
        if word_count < self.shallow_threshold:
            length_score = 0.2
        elif word_count >= self.deep_threshold:
            length_score = 1.0
        else:
            # Linear scale between shallow and deep thresholds
            length_score = (word_count - self.shallow_threshold) / (
                self.deep_threshold - self.shallow_threshold
            )

        # Bonus concept score
        answer_lower = answer.lower()
        bonus_hits = sum(1 for c in bonus_concepts if c.lower() in answer_lower)
        bonus_score = min(bonus_hits / max(len(bonus_concepts), 1), 1.0) if bonus_concepts else 0.0

        # Combine: 70% length signal, 30% bonus signal
        depth = 0.70 * length_score + 0.30 * bonus_score
        return max(0.0, min(depth, 1.0))

    def evaluate_logic(self, answer: str) -> float:
        """
        Checks for logical connective phrases that indicate structured reasoning.
        Returns 0.0 – 1.0.
        """
        answer_lower = answer.lower()
        markers_found = sum(1 for m in self.logic_markers if m in answer_lower)
        # Saturates at 5 markers → 1.0
        return max(0.0, min(markers_found / 5.0, 1.0))

    def evaluate_applicability(self, answer: str) -> float:
        """
        Checks for real-world signals: tool names, numbers, percentages,
        or phrases like "in production", "at scale", "our team".
        Returns 0.0 – 1.0.
        """
        signals = [
            r'\b(in production|at scale|our team|we used|we built|real-world|'
            r'deployed|shipped|end-to-end)\b',
            r'\d+\s?(ms|ms\b|seconds|requests|users|GB|TB|nodes)',  # metrics
            r'\b(AWS|GCP|Azure|Kubernetes|Docker|Redis|Kafka|Postgres|MySQL|MongoDB)\b',
        ]
        score = 0.0
        for pattern in signals:
            if re.search(pattern, answer, re.IGNORECASE):
                score += 1.0
        # 3 signal types → max 1.0
        return max(0.0, min(score / 3.0, 1.0))

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def classify_depth(self, depth_score: float) -> str:
        if depth_score < 0.35:
            return "shallow"
        elif depth_score < 0.70:
            return "moderate"
        return "deep"

    def aggregate_score(self, metrics: Dict[str, float], difficulty_tier: int = 1) -> float:
        """
        Computes weighted score (0–100) and applies difficulty multiplier,
        clamped to 100.
        """
        w = self.weights
        raw = (
            metrics.get("accuracy", 0) * w.get("accuracy", 0.4)
            + metrics.get("depth", 0) * w.get("depth", 0.3)
            + metrics.get("logic", 0) * w.get("logic", 0.2)
            + metrics.get("applicability", 0) * w.get("applicability", 0.1)
        )
        multiplier = self.multipliers.get(difficulty_tier, 1.0)
        final = raw * multiplier * 100
        return max(0.0, min(round(final, 2), 100.0))

    # ------------------------------------------------------------------
    # Main evaluation method
    # ------------------------------------------------------------------

    def evaluate_answer(
        self,
        question_id: str,
        answer: str,
        required_concepts: List[str],
        bonus_concepts: Optional[List[str]] = None,
        difficulty_tier: int = 1,
        domain: str = "general",
    ) -> Dict[str, Any]:
        """
        Full evaluation of a single answer. Returns a structured score object.
        """
        accuracy = self.evaluate_accuracy(answer, required_concepts)
        depth = self.evaluate_depth(answer, bonus_concepts)
        logic = self.evaluate_logic(answer)
        applicability = self.evaluate_applicability(answer)

        metrics = {
            "accuracy": accuracy,
            "depth": depth,
            "logic": logic,
            "applicability": applicability,
        }
        weighted = self.aggregate_score(metrics, difficulty_tier)
        depth_label = self.classify_depth(depth)

        # Build explainability note
        hit_concepts = [c for c in required_concepts if c.lower() in answer.lower()]
        hit_bonus = [c for c in (bonus_concepts or []) if c.lower() in answer.lower()]
        note_parts = []
        if hit_concepts:
            note_parts.append(f"Required concepts covered: {', '.join(hit_concepts)}.")
        if hit_bonus:
            note_parts.append(f"Advanced concepts mentioned: {', '.join(hit_bonus)}.")
        if depth_label == "shallow":
            note_parts.append("Answer appears shallow; consider probing further.")
        explainability_note = " ".join(note_parts) or "No specific concepts detected."

        result = {
            "question_id": question_id,
            "domain": domain,
            "difficulty_tier": difficulty_tier,
            "answer_depth": depth_label,
            "scores": {
                "accuracy": round(accuracy * 100, 2),
                "depth": round(depth * 100, 2),
                "logic": round(logic * 100, 2),
                "applicability": round(applicability * 100, 2),
            },
            "weighted_score": weighted,
            "explainability_note": explainability_note,
        }
        self._question_scores.append(result)
        return result

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_report(
        self,
        candidate_id: str,
        role: str,
        experience_tier: int,
    ) -> Dict[str, Any]:
        """
        Aggregates all evaluated answers into a final technical report.
        """
        if not self._question_scores:
            return {"candidate_id": candidate_id, "error": "No answers evaluated yet."}

        overall = round(
            sum(q["weighted_score"] for q in self._question_scores) / len(self._question_scores), 2
        )

        # Skill-wise breakdown (aggregate by domain)
        domain_scores: Dict[str, List[float]] = {}
        for q in self._question_scores:
            domain_scores.setdefault(q["domain"], []).append(q["weighted_score"])
        skill_breakdown = {
            d: round(sum(v) / len(v), 2) for d, v in domain_scores.items()
        }

        # Simple recommendation logic
        if overall >= 80:
            recommendation = "STRONG HIRE"
        elif overall >= 65:
            recommendation = "HIRE"
        elif overall >= 50:
            recommendation = "BORDERLINE – Needs HR review"
        else:
            recommendation = "REJECT"

        return {
            "candidate_id": candidate_id,
            "role": role,
            "experience_tier": experience_tier,
            "overall_technical_score": overall,
            "skill_breakdown": skill_breakdown,
            "per_question_scores": self._question_scores,
            "hiring_recommendation": recommendation,
        }


__all__ = ["TechScoringEngine"]
