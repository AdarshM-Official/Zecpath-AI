"""
risk_scoring.py – Utility for aggregating integrity flags into a risk score and tag.

The `MalpracticeDetector` (utils/malpractice_detector.py) records individual
`IntegrityFlag` objects.  This module provides a lightweight, reusable class that
takes those flags (or any dict with the same shape) and produces a numeric risk
score, a human‑readable risk tag, and an optional recruiter note.

The logic mirrors the one used inside `MalpracticeDetector.compute_risk_report`
but is isolated so other components (e.g., batch processing, dashboard
generation) can reuse it without depending on the full detector implementation.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class IntegrityFlag:
    """Simple representation of a single integrity anomaly.

    Attributes
    ----------
    rule_id: str
        Identifier of the rule (e.g., "INT-01", "PAT-A").
    description: str
        Human‑readable description of the anomaly.
    severity: str
        One of "LOW", "MEDIUM", "HIGH".
    confidence: float
        Confidence in the detection, 0.0 – 1.0.
    event_count: int
        How many events contributed to the flag.
    """

    rule_id: str
    description: str
    severity: str
    confidence: float
    event_count: int


# ---------------------------------------------------------------------------
# Scorer implementation
# ---------------------------------------------------------------------------

class RiskScorer:
    """Aggregates a collection of :class:`IntegrityFlag` objects into a risk score.

    The scoring system is deliberately simple and deterministic so it can be
    reproduced across services (API, batch jobs, UI).  The core idea is to weight
    each flag by a severity multiplier and its confidence, then sum the weighted
    values.

    Example
    -------
    >>> from utils.risk_scoring import RiskScorer, IntegrityFlag
    >>> flags = [
    ...     IntegrityFlag('INT-02', '7 tab switches', 'HIGH', 1.0, 7),
    ...     IntegrityFlag('INT-06', '5 gaze deviations', 'MEDIUM', 0.9, 5),
    ... ]
    >>> scorer = RiskScorer()
    >>> scorer.add_flags(flags)
    >>> report = scorer.compute_report()
    >>> report['risk_tag']
    'HIGH_RISK'
    """

    # Severity → weight mapping (same as in the detector)
    SEVERITY_WEIGHTS = {"LOW": 1, "MEDIUM": 3, "HIGH": 8}

    def __init__(self) -> None:
        self.flags: List[IntegrityFlag] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_flag(self, flag: IntegrityFlag) -> None:
        """Add a single flag (replaces any existing flag with the same rule_id)."""
        # Ensure we only keep the latest flag for each rule_id
        self.flags = [f for f in self.flags if f.rule_id != flag.rule_id]
        self.flags.append(flag)

    def add_flags(self, flags: List[IntegrityFlag]) -> None:
        """Add a batch of flags."""
        for f in flags:
            self.add_flag(f)

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _weighted_contribution(flag: IntegrityFlag) -> float:
        weight = RiskScorer.SEVERITY_WEIGHTS.get(flag.severity.upper(), 0)
        return weight * max(0.0, min(flag.confidence, 1.0))

    def compute_score(self) -> float:
        """Return the summed weighted score (rounded to two decimals)."""
        total = sum(self._weighted_contribution(f) for f in self.flags)
        return round(total, 2)

    def _determine_tag(self, score: float) -> str:
        """Map a numeric score to a risk tag.

        Mapping mirrors the logic in ``MalpracticeDetector.compute_risk_report``:
        * 0 → CLEAN
        * 0 < score ≤ 5 → LOW_RISK
        * 5 < score ≤ 15 → MEDIUM_RISK
        * score > 15 → HIGH_RISK
        """
        if score == 0:
            return "CLEAN"
        if score <= 5:
            return "LOW_RISK"
        if score <= 15:
            return "MEDIUM_RISK"
        return "HIGH_RISK"

    def _recommendation_note(self, tag: str) -> str:
        notes = {
            "CLEAN": "No integrity anomalies detected.",
            "LOW_RISK": "Minor anomalies – likely environmental; no action required.",
            "MEDIUM_RISK": "Moderate anomalies – recommend recruiter review of flagged timestamps.",
            "HIGH_RISK": "Significant anomalies – strong recommendation for an in‑person follow‑up.",
        }
        return notes.get(tag, "")

    # ------------------------------------------------------------------
    # Final report
    # ------------------------------------------------------------------
    def compute_report(self, candidate_id: str = "", session_id: str = "") -> Dict[str, Any]:
        """Generate a full JSON‑serialisable report.

        Parameters
        ----------
        candidate_id: str, optional
            Identifier of the candidate.
        session_id: str, optional
            Identifier of the interview session.
        """
        score = self.compute_score()
        tag = self._determine_tag(score)
        note = self._recommendation_note(tag)

        return {
            "candidate_id": candidate_id,
            "session_id": session_id,
            "integrity_risk_tag": tag,
            "risk_score": score,
            "flags": [
                {
                    "rule_id": f.rule_id,
                    "description": f.description,
                    "severity": f.severity,
                    "confidence": f.confidence,
                    "event_count": f.event_count,
                }
                for f in self.flags
            ],
            "recruiter_note": note,
        }


__all__ = ["IntegrityFlag", "RiskScorer"]
