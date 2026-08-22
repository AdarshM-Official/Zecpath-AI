# API Specification

This document outlines the proposed RESTful API endpoints for integrating the Zecpath-AI HR Interview engine with external applications (e.g., a web frontend or ATS platform).

## Base URL
`POST /api/v1/interview`

---

### 1. Start Interview
Initializes a new interview session and retrieves the first question.

*   **Endpoint:** `POST /start`
*   **Payload:**
    ```json
    {
      "candidate_id": "c_12345",
      "role": "senior_developer",
      "ats_score": 0.85,
      "screening_score": 0.90
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "session_id": "sess_9876",
      "state": "WAITING_FOR_ANSWER",
      "message": "Tell me about a time you faced a difficult challenge at work."
    }
    ```

---

### 2. Process Candidate Message
Submits a candidate's answer and receives the AI's next prompt (either a follow-up or the next question).

*   **Endpoint:** `POST /{session_id}/message`
*   **Payload:**
    ```json
    {
      "answer": {
        "raw_text": "We had a production outage and I fixed it by reverting the database."
      }
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "state": "FOLLOW_UP",
      "message": "Could you provide more detail on how you coordinated with your team during that outage?"
    }
    ```
*   **Response (Interview Complete):**
    ```json
    {
      "state": "CLOSING",
      "message": "That covers all my questions. Thank you for your time!"
    }
    ```

---

### 3. Fetch Final Report
Retrieves the aggregated scores and explanation notes after the interview reaches the `CLOSING` state.

*   **Endpoint:** `GET /{session_id}/report`
*   **Response (200 OK):**
    ```json
    {
      "candidate_id": "c_12345",
      "role": "senior_developer",
      "hiring_fit_percent": 88.5,
      "breakdown": {
        "ats": 0.85,
        "screening": 0.90,
        "hr_interview": 0.92
      },
      "hr_details": {
        "relevance": 95.0,
        "consistency": 100.0,
        "explainability_note": "Strongest indicator: consistency. Weakest indicator: communication."
      }
    }
    ```

---

### 4. Delete Candidate Data (GDPR/CCPA)
Purges all PII, transcripts, and scores for a given candidate.

*   **Endpoint:** `DELETE /candidate/{candidate_id}`
*   **Response (204 No Content)**
