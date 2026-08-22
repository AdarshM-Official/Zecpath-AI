# Request / Response JSON Schemas

This document defines the core data contracts between the Core Backend and the Zecpath-AI Microservices.

## 1. Resume Parsing & ATS Scoring API (Async)

### Request: `POST /api/v1/resume/parse`
```json
{
  "candidate_id": "c_12345",
  "job_role": "senior_backend",
  "resume_url": "s3://bucket/resumes/c_12345.pdf"
}
```

### Response: `202 Accepted`
```json
{
  "status": "processing",
  "job_id": "job_9876",
  "webhook_url": "/api/v1/webhooks/ats_complete"
}
```

## 2. Interview Message API (Sync)

### Request: `POST /api/v1/interview/<session_id>/message`
```json
{
  "event_type": "answer_received",
  "payload": {
    "raw_text": "I utilized a Redis cache to reduce database load by 40%.",
    "audio_duration_ms": 12500
  },
  "behavioral_context": {
    "gaze_deviations": 0,
    "tab_switches": 0
  }
}
```

### Response: `200 OK`
```json
{
  "state": "WAITING_FOR_ANSWER",
  "action": "speak",
  "message": "That's an excellent approach. What eviction policy did you configure for Redis, and why?",
  "metrics": {
    "communication_score": 0.85,
    "tech_depth_score": 0.70
  }
}
```

## 3. Final Decision API (Async Trigger)

### Request: `POST /api/v1/interview/<session_id>/finalize`
```json
{
  "candidate_id": "c_12345",
  "role": "senior_backend",
  "override_weights": null
}
```

### Response (Webhook Payload upon completion):
```json
{
  "candidate_id": "c_12345",
  "final_decision": "SELECTED",
  "hiring_fit_percent": 88.5,
  "confidence_score": 92.0,
  "risk_factors": [],
  "report_url": "s3://bucket/reports/c_12345_evaluation_report.md"
}
```
