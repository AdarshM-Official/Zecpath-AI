import json
import os
from typing import Dict, Optional


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value to [lo, hi], coercing None/non-numeric to lo."""
    try:
        return max(lo, min(float(value), hi))
    except (TypeError, ValueError):
        return lo


class UnifiedScoringEngine:
    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_path = os.path.join(base_dir, "config", "unified_scoring_config.json")
        else:
            self.config_path = config_path

        self.config = self._load_config()

    def _load_config(self) -> Dict:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[UnifiedScoringEngine] Warning: could not load config ({e}). Using defaults.")
        return {
            "default_weights": {
                "ats": 0.15,
                "screening": 0.15,
                "hr": 0.20,
                "technical": 0.25,
                "machine_test": 0.25
            },
            "role_weights": {}
        }

    def compute_score(
        self,
        ats: float,
        screening: float,
        hr: float,
        technical: float = 0.0,
        machine_test: float = 0.0,
        candidate_id: str = "candidate_001",
        role: Optional[str] = None
    ) -> Dict:
        """
        Aggregates scores from all 5 evaluation stages into a unified hiring fit score.
        All inputs are clamped to [0.0, 1.0] before processing.
        """
        # 1. Clamp all inputs to 0-1 range regardless of what was passed in
        scores = {
            "ats":          _clamp(ats),
            "screening":    _clamp(screening),
            "hr":           _clamp(hr),
            "technical":    _clamp(technical),
            "machine_test": _clamp(machine_test),
        }

        # 2. Determine weights based on role
        weights = self.config.get("default_weights", {})
        if role and role in self.config.get("role_weights", {}):
            weights = self.config["role_weights"][role]

        # 3. Filter out stages with zero weight
        active_weights = {k: v for k, v in weights.items() if v > 0}

        # 4. Normalize weights to exactly 1.0
        total_weight = sum(active_weights.values())
        if total_weight == 0:
            active_weights = {k: 1 / len(scores) for k in scores}
            total_weight = 1.0
        norm_weights = {k: v / total_weight for k, v in active_weights.items()}

        # 5. Weighted sum (clamped to 0-100 final range)
        hiring_fit = _clamp(
            sum(scores[stage] * norm_weights.get(stage, 0) for stage in scores),
            0.0, 1.0
        )

        # 6. Transparency log
        explanation_parts = [
            f"{stage.upper()} ({w*100:.0f}% weight): provided {scores[stage] * w * 100:.1f} pts"
            for stage, w in norm_weights.items()
        ]
        explanation = " + ".join(explanation_parts) + f" = {hiring_fit*100:.1f} Final Score"

        return {
            "candidate_id": candidate_id,
            "hiring_fit_percent": round(hiring_fit * 100, 2),
            "breakdown": scores,
            "weighting_applied": {
                "role": role or "default",
                "normalized_weights": {k: round(v, 3) for k, v in norm_weights.items()}
            },
            "transparency_log": explanation
        }
