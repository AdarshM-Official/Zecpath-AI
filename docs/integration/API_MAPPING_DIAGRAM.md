# API Mapping Diagram

This diagram visualizes the flow of data between the candidate frontend, the core backend, and the Zecpath-AI microservices.

```mermaid
sequenceDiagram
    participant C as Candidate (Frontend)
    participant GW as API Gateway / Core Backend
    participant MQ as Message Queue (Redis/Celery)
    participant AI as Zecpath-AI Engines
    participant DB as Database (Postgres/Mongo)

    %% Asynchronous Flow (Resume Upload)
    rect rgb(240, 248, 255)
        note right of C: 1. Async Flow: Resume Parsing
        C->>GW: POST /upload-resume (PDF)
        GW->>MQ: Enqueue Parse Job
        GW-->>C: 202 Accepted (job_id)
        MQ->>AI: Extract Text & Score ATS
        AI->>DB: Save ATS Score
    end

    %% Synchronous Flow (Interview)
    rect rgb(255, 245, 238)
        note right of C: 2. Sync Flow: Live Interview
        C->>GW: POST /interview/start
        GW->>AI: Initialize Session (Role, ID)
        AI->>DB: Create Session Record
        AI-->>GW: Return Question 1
        GW-->>C: Display Question 1
        
        C->>GW: POST /interview/message (Answer)
        GW->>AI: Analyze Answer (NLP, Logic)
        AI-->>GW: Next Question / Follow-Up
        GW-->>C: Display Next Prompt
    end

    %% Asynchronous Flow (Final Decision)
    rect rgb(240, 255, 240)
        note right of C: 3. Final Aggregation & Decision
        C->>GW: POST /interview/complete
        GW->>MQ: Enqueue Final Scoring Job
        GW-->>C: 200 OK (Session Ended)
        
        MQ->>AI: Trigger Unified Scoring Engine
        AI->>AI: FinalRecommendationEngine
        AI->>AI: HiringReportGenerator
        AI->>DB: Save Final Decision & Markdown Report
    end
```

### Module-to-Endpoint Mapping

| AI Module | Primary API Endpoint | Processing Model |
|---|---|---|
| **Resume Parser & ATS** | `POST /api/v1/resume/parse` | Asynchronous |
| **Screening Chatbot** | `POST /api/v1/screening/message` | Synchronous |
| **HR / Tech Interview** | `POST /api/v1/interview/<session_id>/message` | Synchronous |
| **Behavioral Monitor** | `WS /api/v1/behavioral/stream` | WebSocket (Sync) |
| **Machine Test Evaluator** | `POST /api/v1/machine-test/evaluate` | Asynchronous |
| **Decision & Reporting** | `POST /api/v1/interview/<session_id>/finalize` | Asynchronous |
