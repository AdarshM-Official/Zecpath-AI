# AI Integration & Architecture Plan

## 1. Overview
This document defines how the Zecpath-AI modules interact with the broader enterprise backend, detailing the transition between synchronous and asynchronous processing, error handling, and security protocols.

## 2. Processing Models: Async vs Sync

To ensure high availability and prevent HTTP timeouts, the AI system utilizes a hybrid processing model.

### A. Asynchronous Processing (Message Queue)
Heavy computational tasks that do not require an immediate candidate-facing response are pushed to a background queue (e.g., Celery/Redis or RabbitMQ).
- **Resume Parsing & ATS Scoring:** Candidate uploads a PDF. The API immediately returns a `202 Accepted` with a `job_id`. A background worker extracts text, scores the ATS match, and writes to the DB.
- **Machine Test Evaluation:** Execution of untrusted code in a Docker sandbox.
- **Final Hiring Intelligence Report Generation:** Compiling the markdown/PDF summary.

### B. Synchronous Processing (Real-Time)
Tasks requiring conversational flow and immediate feedback execute synchronously.
- **Screening Chatbot:** Instant text replies.
- **Interview AI (HR & Tech):** Rapid NLP analysis of spoken/typed answers, triggering real-time follow-up logic.
- **Real-Time Behavioral Flags:** Gaze tracking and integrity monitoring (streamed via WebSockets).

## 3. Backend → AI → Database Interaction Flow

1. **Client Tier:** Web/Mobile app interacts with the API Gateway.
2. **API Gateway:** Handles JWT authentication, rate limiting, and routes requests.
3. **Zecpath-AI Microservices:** 
   - Receives sanitized JSON payloads.
   - Loads models/configs from memory.
   - Computes scores.
4. **Data Tier:** 
   - **PostgreSQL:** Stores candidate metadata, final scores, and decisions.
   - **MongoDB:** Stores flexible JSON structures (e.g., unstructured answer history, raw behavioral logs).
   - **AWS S3:** Stores encrypted audio/video transcripts and resume files.

## 4. Error Handling & Retry Mechanisms

- **Idempotency:** All state-changing endpoints (e.g., submitting an answer) require an idempotency key to prevent duplicate scoring in the event of network retries.
- **Graceful Degradation:** If an optional service (e.g., VADER Sentiment Analysis) fails, the system defaults to a neutral score (0.5) and proceeds, logging a warning rather than crashing the interview.
- **Exponential Backoff:** If the backend database is unreachable, the AI service queues the final report in memory/Redis and retries with exponential backoff (up to 3 times) before raising a critical alert.

## 5. API Authentication & Security

- **Authentication:** All API calls require a Bearer Token (JWT). Short-lived tokens (1 hour) are issued for active candidate sessions.
- **Service-to-Service Security:** The Core Backend communicates with the AI Microservices via mutual TLS (mTLS) or internal VPC routing.
- **Payload Validation:** All incoming JSON payloads are strictly validated using Pydantic models (or similar) to prevent injection attacks or type mismatch errors (as stabilized on Day 57).
