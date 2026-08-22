# Malpractice Detection Logic

## 1. Threshold-Based Flag Rules
Each rule produces a flag with a **severity** (LOW / MEDIUM / HIGH) and a **confidence** (0.0–1.0).

### Rule Table
| Rule ID | Signal | Condition | Severity | Confidence Basis |
|---|---|---|---|---|
| `INT-01` | Tab switch | ≥3 tab switches during interview | MEDIUM | Event count / total time |
| `INT-02` | Tab switch | ≥6 tab switches during interview | HIGH | Event count |
| `INT-03` | Screen focus loss | ≥2 focus-loss events >5 seconds each | MEDIUM | Duration × count |
| `INT-04` | Copy-paste | Any paste event into answer field | HIGH | Binary — event detected |
| `INT-05` | Multiple voices | Second voice detected >2× | HIGH | Audio source separation confidence |
| `INT-06` | Looking away | ≥5 large gaze deviations per question | MEDIUM | Gaze deviation count |
| `INT-07` | Reading pattern | ≥3 horizontal scan clusters per answer | MEDIUM | Eye movement cluster count |
| `INT-08` | Sudden performance spike | Answer accuracy jumps >40% after a >15s pause | MEDIUM | Score delta + pause duration |

---

## 2. Pattern Recognition Logic
Threshold rules catch isolated events, but **pattern analysis** detects coordinated cheating strategies.

### Pattern A: Lookup Pattern
- **Definition:** Candidate shows consistent long pauses (>15s) before answers, combined with reading-eye-movement clusters and near-perfect accuracy on harder questions.
- **Logic:**
  ```
  IF avg_pause_before_answer > 15s
  AND reading_pattern_detected == True
  AND accuracy_on_tier_3_questions > 85%
  THEN flag as "Likely External Reference" (HIGH severity)
  ```

### Pattern B: External Coaching Pattern
- **Definition:** A second voice is detected in ≥2 separate answers, or a whisper-level audio signal overlaps with the candidate's answer turns.
- **Logic:**
  ```
  IF multi_voice_events >= 2
  OR background_voice_overlap_detected == True
  THEN flag as "Possible Coaching" (HIGH severity)
  ```

### Pattern C: Assisted Answer Pattern
- **Definition:** Candidate pastes into the text field AND immediately produces a highly accurate, deep answer with no logical reasoning markers (i.e., the phrasing is too polished — no connectors, no personal framing).
- **Logic:**
  ```
  IF paste_event_detected == True
  AND logic_score < 20
  AND accuracy_score > 80
  THEN flag as "Possible Pasted Answer" (HIGH severity)
  ```

---

## 3. Confidence Scoring for Flags
Every flag carries a `confidence` value:

```python
def compute_flag_confidence(event_count: int, max_expected: int, duration_weight: float = 1.0) -> float:
    """
    Returns a 0.0-1.0 confidence for a flag based on how far
    the observed count exceeds the expected normal range.
    """
    ratio = event_count / max(max_expected, 1)
    return max(0.0, min(round(ratio * duration_weight, 2), 1.0))
```

Flags with `confidence < 0.4` are downgraded to LOW and labelled as *"Possible environmental issue — verify with recruiter."*
