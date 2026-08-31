# Zecpath-AI API Specification

## Overview
The Zecpath-AI API is a RESTful service powered by a Waitress WSGI server, designed to handle high-concurrency interview interactions. All data is exchanged in `application/json` format. 

## Standardized Error Handling
As of Day 65, all API endpoints are guaranteed to return a standardized JSON error schema upon failure. The system traps `Internal Server Errors` natively, preventing connection drops.

**Error Response Schema:**
```json
{
  "error": true,
  "code": 400,
  "message": "Invalid input data",
  "details": "candidate_id is required"
}
```

---

## 1. Start Interview Session

**Endpoint:** `POST /api/v1/interview/start`
**Description:** Initializes a new finite state machine instance for the candidate.

### Request Body
```json
{
  "candidate_id": "c_12345",
  "role": "senior_developer",
  "ats_score": 0.85,
  "screening_score": 0.90
}
```
*Note: `ats_score` and `screening_score` must be float values between `0.0` and `1.0`.*

### Success Response (200 OK)
```json
{
  "session_id": "sess_8f3a9b1-...",
  "state": "GREETING",
  "message": "Hello! Thank you for joining. Let's get started. Could you briefly introduce yourself and your background?"
}
```

---

## 2. Process Interview Message

**Endpoint:** `POST /api/v1/interview/<session_id>/message`
**Description:** Submits a candidate's response to the AI. The NLP engine evaluates the text, updates the behavioral metrics, and responds.

### Request Body
```json
{
  "raw_text": "I have 5 years of experience building microservices with Python and Kubernetes."
}
```
*Alternatively, nested JSON is supported: `{"answer": {"raw_text": "..."}}`*

### Success Response (200 OK)
```json
{
  "state": "ASKING",
  "message": "Great. Next question: Can you describe a time you had to optimize a slow database query?"
}
```

### Error Responses
- **404 Not Found:** If `session_id` does not exist or has expired.
- **400 Bad Request:** If `raw_text` is empty, or if the interview state is `CLOSING` or `TERMINATED`.

---

## 3. Retrieve Hiring Report

**Endpoint:** `GET /api/v1/interview/<session_id>/report`
**Description:** Fetches the finalized scoring breakdown once the interview reaches the `CLOSING` state.

### Success Response (200 OK)
```json
{
  "candidate_id": "c_12345",
  "role": "senior_developer",
  "hiring_fit_percent": 84.5,
  "breakdown": {
    "ats": 0.85,
    "screening": 0.90,
    "hr": 0.82,
    "technical": 0.0,
    "machine_test": 0.0
  },
  "unified_score": {
    "hiring_fit_percent": 84.5,
    "transparency_log": "ATS (15% weight): provided ... Final Score"
  }
}
```

### Error Responses
- **400 Bad Request:** `"Interview is still in progress."` (Returned if the state machine has not concluded).
- **404 Not Found:** `"Report not found."`

---

## 4. Purge Candidate Data (GDPR Compliance)

**Endpoint:** `DELETE /api/v1/candidate/<candidate_id>`
**Description:** Purges all session memory, reports, and persistent data related to the candidate to comply with data retention policies.

### Success Response (204 No Content)
*(No body returned)*
