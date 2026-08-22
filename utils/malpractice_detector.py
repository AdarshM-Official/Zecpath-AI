import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class IntegrityFlag:
    rule_id: str
    description: str
    severity: str          # LOW | MEDIUM | HIGH
    confidence: float      # 0.0 – 1.0
    event_count: int
    timestamp_first_event: Optional[str] = None


# ---------------------------------------------------------------------------
# Core detector
# ---------------------------------------------------------------------------

class MalpracticeDetector:
    """
    Detects and flags malpractice signals during an AI-conducted interview.

    Usage
    -----
    detector = MalpracticeDetector(consent_given=True)

    # Call event hooks as they arrive from the frontend / audio pipeline
    detector.on_tab_switch()
    detector.on_focus_loss(duration_seconds=6)
    detector.on_paste_event()
    detector.on_multi_voice_detected()
    detector.on_looking_away()
    detector.on_reading_pattern_detected()
    detector.on_answer_scored(accuracy=0.9, pause_before_answer=18, logic_score=15)

    report = detector.compute_risk_report(candidate_id="c_001", session_id="sess_001")
    """

    SEVERITY_WEIGHTS = {"LOW": 1, "MEDIUM": 3, "HIGH": 8}

    def __init__(self, consent_given: bool = True):
        self.enabled = consent_given
        self.flags: List[IntegrityFlag] = []
        self.alerts: List[Dict[str, Any]] = []   # real-time alert log

        # Raw counters
        self._tab_switch_count: int = 0
        self._focus_loss_events: List[float] = []   # durations in seconds
        self._paste_detected: bool = False
        self._multi_voice_count: int = 0
        self._looking_away_count: int = 0
        self._reading_pattern_count: int = 0

        # Per-answer tracking for pattern detection
        self._answer_records: List[Dict[str, Any]] = []

        self._start_time: float = time.time()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _elapsed(self) -> str:
        """Return HH:MM:SS string since session start."""
        elapsed = int(time.time() - self._start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _add_flag(
        self,
        rule_id: str,
        description: str,
        severity: str,
        confidence: float,
        event_count: int,
    ) -> None:
        """Add an integrity flag, replacing any existing flag for the same rule_id."""
        # Remove existing flag for same rule so we always have the latest
        self.flags = [f for f in self.flags if f.rule_id != rule_id]
        flag = IntegrityFlag(
            rule_id=rule_id,
            description=description,
            severity=severity,
            confidence=max(0.0, min(confidence, 1.0)),
            event_count=event_count,
            timestamp_first_event=self._elapsed(),
        )
        self.flags.append(flag)

    def _emit_alert(self, level: str, message: str) -> None:
        """Emit a real-time alert to the recruiter monitoring panel."""
        alert = {
            "level": level,          # INFO | WARNING | CRITICAL
            "message": message,
            "timestamp": self._elapsed(),
        }
        self.alerts.append(alert)
        # In production this would push via WebSocket; for now just print
        print(f"[ALERT][{level}] {self._elapsed()} – {message}")

    @staticmethod
    def _compute_confidence(event_count: int, max_expected: int,
                            duration_weight: float = 1.0) -> float:
        ratio = event_count / max(max_expected, 1)
        return round(min(ratio * duration_weight, 1.0), 2)

    # ------------------------------------------------------------------
    # Event hooks (called by the frontend or audio pipeline)
    # ------------------------------------------------------------------

    def on_tab_switch(self) -> None:
        """Called each time the candidate switches away from the interview tab."""
        if not self.enabled:
            return
        self._tab_switch_count += 1
        n = self._tab_switch_count

        # INT-01: ≥3 switches → MEDIUM
        if n == 3:
            conf = self._compute_confidence(n, 3)
            self._add_flag(
                "INT-01",
                f"{n} tab switches detected during interview.",
                "MEDIUM", conf, n,
            )
            self._emit_alert("WARNING", f"Tab switch count reached {n}.")

        # INT-02: ≥6 switches → HIGH
        if n >= 6:
            conf = self._compute_confidence(n, 6)
            self._add_flag(
                "INT-02",
                f"{n} tab switches detected during interview.",
                "HIGH", conf, n,
            )
            self._emit_alert("CRITICAL", f"Tab switch count reached {n}. Possible lookup behavior.")

    def on_focus_loss(self, duration_seconds: float) -> None:
        """Called when the browser window loses focus. Pass duration in seconds."""
        if not self.enabled:
            return
        if duration_seconds >= 5:
            self._focus_loss_events.append(duration_seconds)
            count = len(self._focus_loss_events)

            # INT-03: ≥2 focus-loss events >5s each → MEDIUM
            if count >= 2:
                conf = self._compute_confidence(count, 2, duration_weight=1.1)
                self._add_flag(
                    "INT-03",
                    f"{count} screen focus-loss events (each >5s) detected.",
                    "MEDIUM", conf, count,
                )
                self._emit_alert("WARNING", "Repeated screen focus loss detected.")

    def on_paste_event(self) -> None:
        """Called when a paste action is detected in the answer input field."""
        if not self.enabled:
            return
        self._paste_detected = True
        self._add_flag(
            "INT-04",
            "Paste event detected in candidate answer field.",
            "HIGH", 1.0, 1,
        )
        self._emit_alert("CRITICAL", "Copy-paste detected in answer field!")

    def on_multi_voice_detected(self) -> None:
        """Called when the audio pipeline detects a second speaker voice."""
        if not self.enabled:
            return
        self._multi_voice_count += 1
        count = self._multi_voice_count

        # INT-05: ≥2 multi-voice events → HIGH
        if count >= 2:
            conf = self._compute_confidence(count, 2)
            self._add_flag(
                "INT-05",
                f"Multiple voices detected {count} times during interview.",
                "HIGH", conf, count,
            )
            self._emit_alert("CRITICAL", "Possible external coaching: second voice detected.")

    def on_looking_away(self) -> None:
        """Called by BehavioralAnalyzer when a large gaze deviation (>30°) occurs."""
        if not self.enabled:
            return
        self._looking_away_count += 1

        # INT-06: ≥5 looking-away events per question → MEDIUM
        if self._looking_away_count >= 5:
            conf = self._compute_confidence(self._looking_away_count, 5)
            self._add_flag(
                "INT-06",
                f"{self._looking_away_count} large gaze deviations detected.",
                "MEDIUM", conf, self._looking_away_count,
            )
            self._emit_alert("WARNING", "Repeated off-screen gaze detected.")

    def on_reading_pattern_detected(self) -> None:
        """Called by BehavioralAnalyzer when a horizontal reading eye-scan is detected."""
        if not self.enabled:
            return
        self._reading_pattern_count += 1

        # INT-07: ≥3 reading pattern clusters → MEDIUM
        if self._reading_pattern_count >= 3:
            conf = self._compute_confidence(self._reading_pattern_count, 3)
            self._add_flag(
                "INT-07",
                f"Reading-pattern eye movement detected {self._reading_pattern_count} times.",
                "MEDIUM", conf, self._reading_pattern_count,
            )
            self._emit_alert("WARNING", "Reading eye-movement pattern detected.")

    def on_answer_scored(
        self,
        accuracy: float,      # 0.0 – 1.0
        pause_before_answer: float,  # seconds
        logic_score: float,   # 0–100 from TechScoringEngine
    ) -> None:
        """
        Called after each answer is evaluated by TechScoringEngine.
        Records the answer for pattern analysis (INT-08 / Pattern C).
        """
        if not self.enabled:
            return

        record = {
            "accuracy": accuracy,
            "pause": pause_before_answer,
            "logic": logic_score,
        }
        self._answer_records.append(record)
        self._evaluate_patterns(record)

    # ------------------------------------------------------------------
    # Pattern recognition
    # ------------------------------------------------------------------

    def _evaluate_patterns(self, latest: Dict[str, Any]) -> None:
        """Run multi-signal pattern checks after each new answer record."""
        records = self._answer_records

        # Pattern A – Lookup Pattern
        # Long pauses + reading pattern + high accuracy on hard questions
        avg_pause = sum(r["pause"] for r in records) / len(records)
        if (
            avg_pause > 15
            and self._reading_pattern_count >= 3
            and latest["accuracy"] > 0.85
        ):
            self._add_flag(
                "PAT-A",
                "Likely External Reference: consistent long pauses + reading pattern + high accuracy.",
                "HIGH", 0.80, len(records),
            )
            self._emit_alert("CRITICAL", "Lookup pattern detected (long pause + reading eye movement + high accuracy).")

        # Pattern B – External Coaching
        # ≥2 multi-voice events (already handled in INT-05, reinforcing here)
        if self._multi_voice_count >= 2:
            self._add_flag(
                "PAT-B",
                "Possible Coaching: second voice detected in multiple answers.",
                "HIGH", min(self._multi_voice_count / 2, 1.0), self._multi_voice_count,
            )

        # Pattern C – Assisted Answer (paste + low logic + high accuracy)
        if (
            self._paste_detected
            and latest["logic"] < 20
            and latest["accuracy"] > 0.80
        ):
            self._add_flag(
                "PAT-C",
                "Possible Pasted Answer: paste event + polished accuracy with minimal logical reasoning.",
                "HIGH", 0.90, 1,
            )
            self._emit_alert("CRITICAL", "Pasted answer pattern detected.")

    # ------------------------------------------------------------------
    # Risk report generation
    # ------------------------------------------------------------------

    def compute_risk_report(
        self, candidate_id: str, session_id: str
    ) -> Dict[str, Any]:
        """
        Compute the final integrity risk report.
        Returns a structured dict suitable for JSON serialization.
        """
        if not self.enabled:
            return {
                "candidate_id": candidate_id,
                "session_id": session_id,
                "integrity_risk_tag": "SKIPPED",
                "note": "Candidate did not consent to behavioral monitoring.",
            }

        # Weighted risk score
        risk_score = sum(
            self.SEVERITY_WEIGHTS.get(f.severity, 0) * f.confidence
            for f in self.flags
        )
        risk_score = round(risk_score, 2)

        if risk_score == 0:
            tag = "CLEAN"
            note = "No integrity anomalies detected."
        elif risk_score <= 5:
            tag = "LOW_RISK"
            note = "Minor anomalies detected — likely environmental. No action required."
        elif risk_score <= 15:
            tag = "MEDIUM_RISK"
            note = "Moderate anomalies detected. Recommend recruiter review of flagged timestamps."
        else:
            tag = "HIGH_RISK"
            note = "Significant anomalies detected. Strong recommendation to schedule a follow-up in-person round."

        return {
            "candidate_id": candidate_id,
            "session_id": session_id,
            "integrity_risk_tag": tag,
            "risk_score": risk_score,
            "flags": [
                {
                    "rule_id": f.rule_id,
                    "description": f.description,
                    "severity": f.severity,
                    "confidence": f.confidence,
                    "event_count": f.event_count,
                    "timestamp_first_event": f.timestamp_first_event,
                }
                for f in self.flags
            ],
            "alerts_issued": len(self.alerts),
            "recruiter_note": note,
        }

    def reset_looking_away_count(self) -> None:
        """Call between questions to reset per-question looking-away counter."""
        self._looking_away_count = 0


__all__ = ["MalpracticeDetector", "IntegrityFlag"]
