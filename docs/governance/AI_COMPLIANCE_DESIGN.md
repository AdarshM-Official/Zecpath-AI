# AI Compliance & Audit Design

## 1. Objective
Ensure Zecpath-AI complies with international data protection laws (GDPR, CCPA) and algorithmic fairness standards (such as the EU AI Act). The system must maintain an immutable audit trail for all AI-driven decisions to allow for human appeal and review.

## 2. Audit Trail System
Every major action taken by the AI is logged with a cryptographic hash to prevent tampering.

### A. Score Logs
Every intermediate score (ATS, Screening, HR, Tech, Machine Test) is logged to `logs/audit_scores.jsonl`.
**Schema:**
```json
{
  "timestamp": "2026-08-21T12:00:00Z",
  "candidate_id": "c_001",
  "stage": "TECHNICAL_INTERVIEW",
  "raw_score": 85.0,
  "engine_version": "v1.2.4",
  "transparency_note": "Required concepts covered: heap dump, garbage collection."
}
```

### B. Decision Logs
The final recommendation (Selected, Hold, Rejected) is logged to `logs/audit_decisions.jsonl`.
**Schema:**
```json
{
  "timestamp": "2026-08-21T12:30:00Z",
  "candidate_id": "c_001",
  "decision": "SELECTED",
  "confidence": 85.0,
  "human_reviewer": null,
  "appeal_status": "NONE",
  "hash": "a1b2c3d4e5f6..."
}
```

## 3. Consent-Based Data Usage
- **Explicit Opt-In:** Candidates must click an explicit "I Agree" button before the interview starts.
- **Granular Consent:** Candidates can opt out of Behavioral Tracking (webcam analysis) while still proceeding with the text/audio interview.
- **Right to Explanation:** The `FinalRecommendationEngine` exposes the `explanation` field directly to the recruiter, which can be provided to the candidate upon request.

## 4. Algorithmic Fairness & Bias Mitigation
- The HR and Technical scoring engines explicitly ignore demographic data (name, age, gender) during NLP analysis.
- The Behavioral engine does not classify emotion (which is prone to cultural bias), but rather physical engagement metrics (gaze stability).
