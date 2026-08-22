# Future Architecture Ideas

## 1. From Heuristics to a Neural Scoring Pipeline

### Current (v1.0)
The current scoring engines (Technical, HR, Behavioral) are heuristic-based. They use keyword matching, word count thresholds, and regex pattern matching for logic/depth evaluation.

**Limitations:** Cannot handle semantic equivalence (e.g., "uses a hash map" vs "implements an O(1) lookup structure"), and is brittle to paraphrasing.

### Proposed (v2.0)
Replace the concept-matching layer in `TechScoringEngine` with a **small LLM-as-judge** approach:

```
Candidate Answer → [Embedding Model] → Similarity Score vs Expected Concepts
                                     +
Candidate Answer → [LLM Judge] → {"accuracy": 8/10, "depth": 7/10, "reasoning": "..."}
```

**Target models:** A fine-tuned `gemma-2-9b-it` or `Mistral-7B-Instruct` served via local inference (Ollama) to maintain data privacy.

---

## 2. Distributed Pipeline Architecture

### Current (v1.0)
All processing runs within a single Python process / Flask API server. Fine for development, but not scalable beyond a few concurrent interviews.

### Proposed (v2.0)
A microservices architecture with an asynchronous event bus:

```
[API Gateway]
     |
     +─── [Interview Session Service]  ─── Redis (session state)
     |
     +─── [Scoring Service]            ─── Kafka (score events)
     |
     +─── [Behavioral Service]         ─── WebRTC → Frame Processor
     |
     +─── [Reporting Service]          ─── PostgreSQL + S3
     |
     +─── [Decision Service]           ─── Final Recommendation Engine
```

**Benefits:** Each service scales independently. A surge in machine tests doesn't affect HR interview throughput.

---

## 3. Continuous Learning via Recruiter Feedback

### Design
When a recruiter overrides an AI decision (e.g., AI says "HOLD", recruiter converts to "SELECTED"), this feedback event is captured:

```json
{
  "session_id": "sess_001",
  "ai_decision": "HOLD / REVIEW",
  "recruiter_decision": "SELECTED",
  "recruiter_note": "Strong cultural fit despite low tech score."
}
```

These override events are stored in a feedback log. Periodically, a **weight calibration job** analyzes override patterns and adjusts the `unified_scoring_config.json` role weights accordingly.

This creates a **Reinforcement Learning from Human Feedback (RLHF)** loop without requiring model retraining.

---

## 4. Privacy-Preserving Federated Scoring
For enterprise clients with strict data locality requirements (e.g., EU companies governed by GDPR), deploy the scoring engines **locally on the client's infrastructure**. Only anonymized, aggregated metrics are sent back to the Zecpath platform for analytics and model improvement — never raw candidate data.
