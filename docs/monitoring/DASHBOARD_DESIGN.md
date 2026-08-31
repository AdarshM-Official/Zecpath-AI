# Monitoring Dashboard Design

This document outlines the proposed layout for the primary Grafana/Datadog dashboards used by SREs and AI Operations teams.

## Dashboard 1: System Health & Performance (SRE View)

**Target Audience:** Site Reliability Engineers, DevOps

| Panel Name | Type | Metric/Source | Description |
|---|---|---|---|
| **Global API Latency** | Line Chart | `p50, p95, p99` of `latency_ms` | Tracks responsiveness of the interview messaging endpoints. |
| **Error Rate (5xx)** | Time Series | `rate(http_5xx)` | Monitors unhandled exceptions in the API gateways. |
| **Queue Depths** | Gauge / Graph | Redis/Celery Queue Sizes | Shows backlog for async tasks (Resume Parsing, Machine Tests, Report Generation). |
| **Resource Utilization** | Time Series | CPU & Mem per Pod | Tracks hardware load, triggering auto-scaling events. |
| **Degraded Executions** | Bar Chart | Count of `ERROR` logs for missing dependencies | Shows how often the system is relying on fallback logic (e.g., VADER offline). |

## Dashboard 2: AI Operations & Funnel (Data Science View)

**Target Audience:** AI Product Managers, Data Scientists, Talent Ops

| Panel Name | Type | Metric/Source | Description |
|---|---|---|---|
| **Active Interviews** | Stat / Number | Count of active `SESSIONS` | Real-time tracking of candidate concurrency. |
| **Decision Funnel** | Funnel Chart | % Selected / Hold / Rejected | Tracks the ultimate outcomes. Sudden shifts indicate algorithmic drift. |
| **Fallback Trigger Rate** | Line Chart | % of turns hitting `FALLBACK` state | Measures the health of the conversational NLP model. High rates mean candidates are confused or the AI is stuck. |
| **Average Hiring Fit Score** | Histogram | Distribution of `hiring_fit_percent` | Ensures scores are normally distributed and not heavily skewed. |
| **Integrity Risk Distribution** | Pie Chart | % CLEAN / LOW / MEDIUM / HIGH | Tracks the frequency of malpractice flags across the platform. |

## Dashboard 3: Human vs AI Alignment (Audit View)

**Target Audience:** HR Leadership, Compliance Officers

| Panel Name | Type | Metric/Source | Description |
|---|---|---|---|
| **AI vs Human Agreement** | Gauge | % Match between AI decision and final recruiter decision | The ultimate metric of AI accuracy. |
| **Override Sources** | Bar Chart | Reasons recruiters override the AI | E.g., "AI was too strict on Tech", "AI missed a behavioral cue". |
| **Bias Tracking** | Bar Chart | Approval rates segmented by anonymized demographic proxies (if available) | Monitors algorithmic fairness across different cohorts. |
