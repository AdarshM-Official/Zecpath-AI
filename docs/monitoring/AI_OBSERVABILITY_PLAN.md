# AI Observability & Monitoring Plan

## 1. Overview
This document outlines the strategy for tracking the health, performance, and accuracy of Zecpath-AI in production. An effective observability strategy ensures we can quickly detect system degradation, algorithmic drift, and infrastructure bottlenecks.

## 2. Key Metrics & Service Level Indicators (SLIs)

### A. Performance & Latency
- **API Response Time (p95, p99):** Time taken to respond to candidate messages (Target: < 1.0s for text, < 2.0s for audio transcription + NLP).
- **Batch Processing Throughput:** Resumes parsed per minute or background scoring jobs completed per second.
- **Cold Start Times:** Time taken to spin up Machine Test Docker containers (Target: < 3.0s).

### B. AI Accuracy & Efficacy
- **AI-Human Agreement Rate:** Percentage of AI "Selected" or "Rejected" decisions that are upheld by human recruiters during manual audits (Target: > 90%).
- **Fallback Trigger Rate:** Percentage of candidate interactions that trigger the conversational fallback state due to confusion/looping (Target: < 5%).
- **Score Variance:** Standard deviation of scores across evaluation rounds. Drastic spikes in variance may indicate an issue with a specific engine.

### C. Reliability & Failures
- **Error Rate (HTTP 5xx):** Unhandled exceptions in the API (Target: < 0.1%).
- **Degraded Execution Rate:** Percentage of requests where an optional dependency (like VADER sentiment analysis) failed and a fallback was used.
- **Queue Backpressure:** Number of pending items in the async processing queues (Resume parsing, Machine tests).

## 3. Alerting Rules (PagerDuty / Slack Integrations)

Alerts are categorized by severity to prevent alert fatigue.

### Critical Alerts (P1 - Immediate Page)
- **High API Error Rate:** `rate(http_500_errors) > 1%` over a 5-minute window.
- **System Halting Latency:** `p99(interview_message_latency) > 5.0s` for > 3 minutes.
- **Queue Stalling:** Machine Test queue depth > 1000 items and processing rate is 0.

### Warning Alerts (P2 - Slack Notification)
- **High Fallback Rate:** `fallback_state_triggers > 10%` of total conversational turns in a 1-hour window. Indicates a prompt or NLP intent detection degradation.
- **Degraded Service:** `vader_fallback_rate > 5%`. Indicates the NLP service is struggling to initialize or connect.
- **Elevated Integrity Flags:** `high_risk_flags > 20%` of total candidates in a 4-hour window. May indicate an overly sensitive malpractice threshold or a coordinated cheating attempt.
