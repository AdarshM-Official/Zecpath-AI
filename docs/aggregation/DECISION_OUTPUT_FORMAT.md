# Final Candidate Decision Output Format

The `FinalRecommendationEngine` produces a definitive JSON object representing the end of the AI-driven interview pipeline. This object is consumed by the Applicant Tracking System (ATS) dashboard.

## JSON Schema

```json
{
  "candidate_id": "c_999",
  "decision": "Hold / Review",
  "confidence_score": 58.4,
  "hiring_fit_percent": 88.5,
  "risk_factors": [
    "Integrity: HIGH_RISK"
  ],
  "explanation": "Forced HOLD due to HIGH_RISK integrity flag."
}
```

### Fields

- `decision`: Must be exactly one of `"Selected"`, `"Hold / Review"`, or `"Rejected"`.
- `confidence_score`: A percentage (0-100) indicating the AI's confidence in its decision. Low confidence usually triggers a downgrade from `Selected` to `Hold / Review`.
- `hiring_fit_percent`: The aggregated score from the `CrossRoundAggregator` (0-100).
- `risk_factors`: An array of strings highlighting specific concerns (e.g., Integrity flags, High stress indicators).
- `explanation`: A human-readable, explainable AI string detailing the logical path taken to reach the final `decision`.

## Decision Logic (Rule + Score Hybrid)

1. **Integrity Override**: Any `HIGH_RISK` integrity flag bypasses the score and forces a `Hold / Review`.
2. **Score Thresholds**: 
   - `Selected`: >= 80%
   - `Hold / Review`: 65% - 79%
   - `Rejected`: < 65%
3. **Confidence Override**: If a candidate meets the `Selected` score threshold but the `confidence_score` drops below 70% (due to inconsistent scores across rounds, or moderate behavioral penalties), the decision is downgraded to `Hold / Review`.
