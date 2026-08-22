# AI Governance & Data Retention Policy

## 1. Overview
This document outlines the operational governance of Zecpath-AI, defining how data is retained, purged, and how the AI models are maintained.

## 2. Data Retention Policies

| Data Type | Retention Period | Action Post-Retention |
|---|---|---|
| **Interview Transcripts** | 30 Days (if rejected) / 1 Year (if hired) | Hard delete |
| **Video/Audio Recordings**| 7 Days | Hard delete |
| **Behavioral Signals** | 30 Days | Aggregated & Anonymized |
| **Final AI Report** | 1 Year | Anonymized for model training |
| **Audit Logs** | 3 Years | Archived to cold storage |

### The Right to be Forgotten (GDPR)
Upon receiving a candidate deletion request, the `DataRetentionManager` (developed on Day 43) executes a cascading delete across the transcript DB, the report DB, and the active session memory. Anonymized audit logs mapping to the candidate hash are preserved for compliance.

## 3. AI Model Governance

### A. Model Versioning
- All NLP prompts, scoring weights, and ML models are strictly versioned.
- The exact version of the scoring engine used is stamped into the `audit_scores.jsonl` file. This prevents retroactive disputes if a candidate was evaluated under an older, stricter model.

### B. Human-in-the-Loop (HITL) Requirement
- **No Automatic Rejection:** If a candidate triggers a HIGH_RISK integrity flag, the AI transitions to `Hold / Review`, forcing a human recruiter to verify the anomaly.
- **Model Auditing:** Every quarter, 5% of randomly selected "Rejected" AI decisions are audited by senior recruiters to detect potential algorithmic drift or emerging biases.
