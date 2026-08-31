# Logging Structure & Audit Trails

To support the observability plan, Zecpath-AI enforces structured JSON logging across all microservices. This allows logs to be easily ingested by log aggregators (e.g., ELK stack, Datadog, Splunk).

## 1. API & Infrastructure Logs

### Schema: `api_access_log`
Tracks HTTP requests, latencies, and status codes.
```json
{
  "timestamp": "2026-08-31T12:00:05.123Z",
  "level": "INFO",
  "service": "interview_api",
  "endpoint": "/api/v1/interview/sess_123/message",
  "method": "POST",
  "status_code": 200,
  "latency_ms": 845,
  "client_ip": "192.168.1.55",
  "session_id": "sess_123"
}
```

## 2. Model Output Logs

### Schema: `model_inference_log`
Tracks the raw outputs and intermediate scores from the AI engines. These logs are critical for debugging why a specific score was given.
```json
{
  "timestamp": "2026-08-31T12:00:06.000Z",
  "level": "DEBUG",
  "service": "tech_scoring_engine",
  "candidate_id": "c_999",
  "question_id": "Q002",
  "raw_input_length": 45,
  "inferred_depth": "deep",
  "scores": {
    "accuracy": 90.0,
    "logic": 85.0
  },
  "processing_time_ms": 320
}
```

## 3. Error & Exception Logs

### Schema: `error_trace_log`
Captures unhandled exceptions and degraded states.
```json
{
  "timestamp": "2026-08-31T12:05:10.450Z",
  "level": "ERROR",
  "service": "confidence_analyzer",
  "error_type": "DependencyError",
  "message": "NLTK VADER unavailable, falling back to neutral sentiment 0.5",
  "stack_trace": "...",
  "context": {
    "candidate_id": "c_888",
    "text_snippet": "I am not sure..."
  }
}
```

## 4. Immutable Audit Logs (Decision Tracking)

Extending the Day 55 compliance design, final decisions are logged immutably for fairness audits.

### Schema: `decision_audit_log`
```json
{
  "timestamp": "2026-08-31T12:30:00.000Z",
  "level": "AUDIT",
  "service": "final_recommendation_engine",
  "candidate_id": "c_777",
  "job_id": "job_backend_01",
  "engine_version": "v1.2.4",
  "decision": "HOLD_REVIEW",
  "hiring_fit_percent": 82.5,
  "risk_factors": ["Integrity: HIGH_RISK"],
  "decision_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
*Note: The `decision_hash` ensures that the record cannot be altered retroactively without detection, satisfying enterprise compliance requirements.*
