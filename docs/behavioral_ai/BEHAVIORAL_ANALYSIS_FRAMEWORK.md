# Behavioral Analysis Framework

## 1. Architecture Overview
The Behavioral Analysis Framework is a modular, plug-in component of Zecpath-AI. It is designed to run **in parallel** with the interview conversation flow and produces an independent behavioral context report at the end of the session.

```
InterviewConversationFlow  ──────────────────────────────────► HR Score
                 |
                 |── [Parallel Thread] ──► BehavioralAnalyzer ──► Behavioral Context Report
```

---

## 2. Module Structure

| Module | Responsibility |
|---|---|
| `behavioral_ai/gaze_tracker.py` | Processes webcam frames, calculates gaze_on_screen_pct and deviation events |
| `behavioral_ai/head_pose_estimator.py` | Estimates yaw/pitch/roll, detects looking-away events |
| `behavioral_ai/expression_detector.py` | Detects smiles and micro-expressions |
| `behavioral_ai/behavioral_scoring_engine.py` | Aggregates signals into Focus, Confidence, Stress scores |

---

## 3. Framework Rules

### 3.1 Sampling Rate
- Process every **5th frame** (at 30fps, this gives 6 evaluations/second) to reduce CPU load.

### 3.2 Windowed Aggregation
- Signals are aggregated over **30-second windows** to smooth out momentary noise (e.g., a sneeze should not permanently mark a candidate as "distracted").

### 3.3 Per-Question Timestamping
- Behavioral signals are aligned to each interview question by timestamp. This lets the recruiter review: *"During Question 3 (System Design), the candidate's focus score dropped to 45."*

### 3.4 Privacy & Consent Guard
```python
class BehavioralAnalyzer:
    def __init__(self, consent_given: bool):
        if not consent_given:
            self.enabled = False
            return
        self.enabled = True
        # ... initialize detectors
```
If `consent_given=False`, the analyzer is completely disabled and returns an empty context report.

---

## 4. Output: Behavioral Context Report (JSON)
```json
{
  "candidate_id": "c_12345",
  "behavioral_context": {
    "focus_score": 74.5,
    "confidence_score": 81.0,
    "stress_indicator": 32.0,
    "per_question_behavior": [
      {
        "question_index": 1,
        "focus": 88.0,
        "confidence": 85.0,
        "stress": 20.0,
        "flag": null
      },
      {
        "question_index": 3,
        "focus": 45.0,
        "confidence": 72.0,
        "stress": 55.0,
        "flag": "Low focus detected. Candidate may have been distracted or anxious on this question."
      }
    ],
    "recruiter_note": "Overall behavioral profile is strong. Minor stress spike on system design question — recommend a brief verbal follow-up."
  }
}
```

---

## 5. Implementation Readiness
> [!NOTE]
> Day 48 is a **design phase**. The modules listed in Section 2 are stubs pending computer vision dependency setup (OpenCV, MediaPipe). Implementation is scheduled for a future sprint.

**Dependencies to install before implementing:**
```bash
pip install opencv-python mediapipe dlib numpy
```
