# Integrity & Malpractice Detection Framework
**Module:** `utils/malpractice_detector.py`

Zecpath-AI utilizes a zero-tolerance, multi-modal integrity evaluation system designed to catch candidates using unauthorized assistance (e.g., ChatGPT, dual monitors, or interviewing proxies). 

## 1. Detection Vectors

The system continuously analyzes three distinct vectors in real-time during the `InterviewConversationFlow`:

1. **Browser Events (Tab Switching):** The frontend strictly monitors window focus.
2. **Vision/Gaze Analysis:** Using webcam feeds, the system measures the angle of the candidate's gaze.
3. **Audio Signatures:** Tracks the number of distinct voices detected in the background.

## 2. Thresholds & Heuristics
The core logic relies on hard thresholds which trigger severity flags. If a severity flag reaches `CRITICAL`, the Final Recommendation Engine will automatically override any high test scores and issue a `REJECTED` decision.

- **Tab Switches:**
  - `<= 2`: Ignored (Accidental clicks)
  - `3 - 5`: `WARNING` (Candidate is warned)
  - `>= 6`: `CRITICAL` (Candidate is flagged for possible lookup behavior)
  
- **Gaze Deviation:**
  - The system checks for repeated off-screen gaze. If a candidate exhibits `> 3` distinct reading patterns (e.g., staring at a second monitor for > 5 seconds while answering), a `WARNING` or `CRITICAL` flag is generated.

## 3. Data Integration
The `MalpracticeDetector` does not just spit out raw logs; it generates a structured `integrity_report` dictionary which is injected directly into the `master_data` payload for the `HiringReportGenerator`.

```json
{
  "integrity_risk_tag": "HIGH",
  "flags": [
    {"severity": "CRITICAL", "description": "Tab switch count reached 12. Possible lookup behavior."},
    {"severity": "WARNING", "description": "Repeated off-screen gaze detected."}
  ]
}
```
*If no flags are triggered, the `integrity_risk_tag` remains `LOW` and the candidate is marked as CLEAN.*
