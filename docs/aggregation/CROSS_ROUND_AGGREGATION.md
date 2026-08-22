# Cross-Round Aggregation Engine

## 1. Objective
Combine evaluation signals from all phases of the interview process (ATS, Screening, HR, Technical, Machine Test) into a single, transparent, unified **Hiring Fit Score**.

## 2. Dynamic Role-Based Weightage
Different job roles require different weightings for technical vs behavioral skills.

| Role Profile | ATS | Screening | HR | Technical | Machine Test | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Junior Developer** | 15% | 15% | 20% | 30% | 20% | Emphasizes technical knowledge (conceptual) over complex real-world architecture. |
| **Senior Developer** | 10% | 10% | 20% | 25% | 35% | Heavy emphasis on the Machine Test to prove real-world execution and system design. |
| **Manager** | 20% | 20% | 40% | 20% | 0% | Heavy behavioral/HR emphasis; Machine test is skipped entirely. |

*Weights are automatically normalized to 100% at runtime if any stages are skipped or modified.*

## 3. Transparency & Normalization
To ensure explainable AI compliance, the aggregation engine exposes a `transparency_log` detailing exactly how the final score was computed.

**Example Output:**
```json
{
  "candidate_id": "c_999",
  "hiring_fit_percent": 82.35,
  "breakdown": {
    "ats": 0.80,
    "screening": 0.85,
    "hr": 0.90,
    "technical": 0.75,
    "machine_test": 0.85
  },
  "weighting_applied": {
    "role": "senior_developer",
    "normalized_weights": {
      "ats": 0.1,
      "screening": 0.1,
      "hr": 0.2,
      "technical": 0.25,
      "machine_test": 0.35
    }
  },
  "transparency_log": "ATS (10% weight): provided 8.0 pts + SCREENING (10% weight): provided 8.5 pts + HR (20% weight): provided 18.0 pts + TECHNICAL (25% weight): provided 18.8 pts + MACHINE_TEST (35% weight): provided 29.8 pts = 82.4 Final Score"
}
```

## 4. Integration
The `UnifiedScoringEngine` resides in `utils/unified_scoring_engine.py` and is called at the very end of the candidate lifecycle, merging the final output artifacts of all sub-systems into the final Candidate Report.
