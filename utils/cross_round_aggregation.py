import json
import os
from typing import Dict, Optional, Any

class CrossRoundAggregator:
    """
    Combines evaluation signals from all phases of the Zecpath-AI interview process
    (ATS, Screening, HR, Technical, Machine Test) into a single, unified Hiring Fit Score.
    """
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Resolve relative to the current file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_path = os.path.join(base_dir, "config", "unified_scoring_config.json")
        else:
            self.config_path = config_path
            
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
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

    def aggregate(
        self, 
        candidate_id: str,
        role: str,
        ats_score: float, 
        screening_score: float, 
        hr_score: float, 
        technical_score: float = 0.0,
        machine_test_score: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Aggregates scores from all 5 evaluation stages into a unified hiring fit score.
        Inputs should be in the range 0.0 - 1.0 (or 0 - 100, as long as they are consistent).
        If inputs are 0-1, the final percentage is multiplied by 100.
        """
        
        # 1. Determine weights based on role
        weights = self.config.get("default_weights", {})
        if role and role in self.config.get("role_weights", {}):
            weights = self.config["role_weights"][role]

        # 2. Filter out stages that are entirely skipped/not applicable for this role
        # (e.g., if machine_test weight is 0 in config, we ignore it)
        active_weights = {k: v for k, v in weights.items() if v > 0}
        
        # 3. Normalize weights to ensure they sum to exactly 1.0
        total_weight = sum(active_weights.values())
        if total_weight == 0:
            total_weight = 1.0
            active_weights = {"ats": 0.2, "screening": 0.2, "hr": 0.2, "technical": 0.2, "machine_test": 0.2}
            
        norm_weights = {k: v / total_weight for k, v in active_weights.items()}

        # 4. Calculate weighted sum
        scores = {
            "ats": ats_score,
            "screening": screening_score,
            "hr": hr_score,
            "technical": technical_score,
            "machine_test": machine_test_score
        }
        
        hiring_fit = sum(scores[stage] * norm_weights.get(stage, 0) for stage in scores)

        # 5. Format explanation string for transparency
        explanation_parts = []
        for stage, w in norm_weights.items():
            contribution = scores[stage] * w * 100
            explanation_parts.append(f"{stage.upper()} ({w*100:.0f}% weight): provided {contribution:.1f} pts")
            
        explanation = " + ".join(explanation_parts) + f" = {hiring_fit*100:.1f} Final Score"

        # 6. Build unified candidate score object
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

if __name__ == "__main__":
    aggregator = CrossRoundAggregator()
    
    # Example execution for a Senior Developer
    result = aggregator.aggregate(
        candidate_id="cand_888",
        role="senior_developer",
        ats_score=0.90,
        screening_score=0.85,
        hr_score=0.88,
        technical_score=0.92,
        machine_test_score=0.95
    )
    print(json.dumps(result, indent=2))
