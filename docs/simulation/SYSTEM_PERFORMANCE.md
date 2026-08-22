# System Performance Analysis

## 1. Latency & Processing Speed
A critical component of the simulation was monitoring the latency between the candidate providing an answer and the AI generating the next prompt.

| Stage | Average Processing Time | Goal | Status |
|---|---|---|---|
| **ATS Parsing** | 1.2s per resume | < 2.0s | PASS |
| **Screening Chatbot** | 450ms per reply | < 800ms | PASS |
| **HR / Tech NLP Analysis** | 1.1s per answer | < 1.5s | PASS |
| **Behavioral Video Processing** | Real-time (30fps sample) | Real-time | PASS |
| **Machine Test Execution** | 2.4s (Docker spin-up + run) | < 3.0s | PASS |
| **Final Aggregation & Decision** | 150ms | < 500ms | PASS |

## 2. Bottlenecks Identified
- **Audio Transcription:** While the NLP analysis is fast (1.1s), the initial Speech-to-Text (STT) layer occasionally experienced latency spikes up to 3.5s during the HR interview, leading to unnatural conversational pauses.
- **Machine Test Cold Starts:** The secure Docker sandbox executor experiences a ~1.5s "cold start" delay when spinning up an environment for the first time.

## 3. Resource Utilization
- **Memory:** Peaked during concurrent video behavioral tracking (Gaze/Head Pose estimation).
- **CPU:** The heaviest load occurs during the `FinalRecommendationEngine` variance calculations when processing hundreds of batch candidates simultaneously. The Day 54 caching optimizations successfully prevented I/O bottlenecks.
