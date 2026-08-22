# Risk Flagging System Design

## 1. Real-Time Alert System
During a live interview, the system emits real-time alerts to the **recruiter monitoring panel** (not the candidate). Alerts are non-disruptive — they do not interrupt the interview flow.

### Alert Levels
| Level | Color | Action Required |
|---|---|---|
| **INFO** | Blue | Log only. No action needed. |
| **WARNING** | Yellow | Recruiter is notified. They may choose to intervene or note it. |
| **CRITICAL** | Red | Recruiter is strongly prompted to review. The AI may (optionally) issue a candidate reminder. |

### Candidate-Facing Reminder (Optional)
When a CRITICAL flag fires, the AI interviewer can optionally issue a soft, neutral reminder to the candidate:
> *"Just a reminder — please ensure your attention remains on the interview screen."*
This is non-accusatory and gives the candidate a chance to correct innocent behavior (e.g., they were distracted by a notification).

---

## 2. Interview Risk Tagging
At the end of the interview, the system computes an overall **Integrity Risk Tag**:

### Risk Tag Computation
```
risk_score = Σ (severity_weight × confidence)
             for each flag in session_flags

Where severity_weights = { LOW: 1, MEDIUM: 3, HIGH: 8 }
```

| Risk Score | Risk Tag | Recruiter Action |
|---|---|---|
| 0 | `CLEAN` | No anomalies detected |
| 1–5 | `LOW_RISK` | Minor anomalies — likely environmental |
| 6–15 | `MEDIUM_RISK` | Recommend recruiter review of flagged timestamps |
| 16+ | `HIGH_RISK` | Strong recommendation to schedule a follow-up in-person round |

---

## 3. IntegrityReport JSON Schema
```json
{
  "candidate_id": "c_12345",
  "session_id": "sess_9876",
  "integrity_risk_tag": "MEDIUM_RISK",
  "risk_score": 9,
  "flags": [
    {
      "rule_id": "INT-02",
      "description": "6 or more tab switches detected during interview",
      "severity": "HIGH",
      "confidence": 0.85,
      "timestamp_first_event": "00:04:32",
      "event_count": 7
    },
    {
      "rule_id": "INT-07",
      "description": "Reading eye-movement pattern detected on Q3",
      "severity": "MEDIUM",
      "confidence": 0.55,
      "timestamp_first_event": "00:12:10",
      "event_count": 3
    }
  ],
  "recruiter_note": "Candidate switched tabs multiple times. Recommend verifying if this was due to browser/OS notifications or deliberate lookup behavior.",
  "generated_at": "2026-08-21T12:00:00Z"
}
```

---

## 4. Module Design (Stub — Implementation in future sprint)
```python
# utils/integrity_detector.py

class IntegrityDetector:
    def __init__(self, consent_given: bool):
        self.enabled = consent_given
        self.flags = []
        self.tab_switch_count = 0
        self.focus_loss_events = []
        self.paste_detected = False

    def on_tab_switch(self):
        self.tab_switch_count += 1
        self._evaluate_tab_rules()

    def on_paste_event(self):
        self.paste_detected = True
        self._add_flag("INT-04", severity="HIGH", confidence=1.0)

    def compute_risk_tag(self) -> dict:
        weights = {"LOW": 1, "MEDIUM": 3, "HIGH": 8}
        score = sum(weights[f["severity"]] * f["confidence"] for f in self.flags)
        if score == 0: tag = "CLEAN"
        elif score <= 5: tag = "LOW_RISK"
        elif score <= 15: tag = "MEDIUM_RISK"
        else: tag = "HIGH_RISK"
        return {"risk_score": round(score, 2), "integrity_risk_tag": tag, "flags": self.flags}
```
