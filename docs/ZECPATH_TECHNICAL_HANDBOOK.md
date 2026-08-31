# Zecpath-AI Technical Handbook
**Version:** 2.0 (Production Release)

Welcome to the **Zecpath-AI Technical Handbook**. This master document serves as the central index and architectural overview for the entire AI system, linking to all specialized documentation created over the development lifecycle.

The Zecpath-AI pipeline is designed to evaluate candidates seamlessly from resume upload to a final hiring recommendation, utilizing specialized engines for ATS screening, conversational HR assessment, technical depth evaluation, and behavioral analysis.

## 1. System Overview & Architecture
Zecpath-AI has evolved from a monolithic Flask application into a production-ready, stateless microservice architecture powered by Waitress. It processes candidate interactions via a robust 5-stage pipeline, ensuring both asynchronous (resume parsing, machine tests) and synchronous (chat/audio) workflows are handled gracefully.

- **[Master System Architecture](architecture/SYSTEM_ARCHITECTURE.md)**: Deep dive into the core pipeline design, workflows, Docker containerization for untrusted code execution, and our Mermaid-based processing models.
- **[Future Architecture & Roadmap](roadmap/FUTURE_ARCHITECTURE.md)**: Plans for v2.0, including LLM-based technical judges (e.g., Llama-3 8B integration) and further microservice decomposition.
- **[Scalability Strategy](scalability/SCALABILITY_STRATEGY.md)**: Details on horizontal scaling, load balancing via Nginx, and Kubernetes HPA design.

## 2. API & Integrations
The AI system is exposed via a highly resilient REST API. On Day 65, all endpoints were standardized to emit a uniform JSON error schema (`{"error": true, "code": HTTP_STATUS, "message": "..."}`), preventing dropped connections and making downstream integration bulletproof.

- **[API Specification](api/API_SPECIFICATION.md)**: Comprehensive endpoint details, rate limiting, and HTTP status code documentation.
- **[AI Integration Plan](integration/AI_INTEGRATION_PLAN.md)**: Orchestration logic detailing Async vs Sync processing models.
- **[Request/Response Schemas](integration/API_SCHEMAS.md)**: Exact JSON payloads for all AI endpoints.
- **[API Mapping Diagram](integration/API_MAPPING_DIAGRAM.md)**: Visual sequence diagrams illustrating how the Zecpath Core Backend interacts with the AI services.

## 3. Scoring Engines & Logic
The heart of Zecpath-AI is its multi-stage scoring pipeline. Each module computes a localized score which is mathematically clamped (`max(0.0, min(score, 1.0))`) to ensure absolute consistency before being aggregated by the Unified Engine.

- **[Unified Scoring Engine & Cross-Round Aggregation](aggregation/CROSS_ROUND_AGGREGATION.md)**: Explains the dynamic weighting system (e.g., Senior vs Junior role weights) and the bounds-checking logic.
- **[Technical Scoring Logic](technical_interview/BLUEPRINT.md)**: Evaluation of accuracy, depth, logic, and applicability using our proprietary regex/NLP logic.
- **[Behavioral AI & Stress Mapping](behavioral_ai/BEHAVIORAL_AI_DESIGN.md)**: Calculation of sentiment, hesitation (filler words), and contradiction using NLTK VADER and spaCy (with soft-dependency fallbacks).
- **[Final Recommendation Engine](aggregation/DECISION_OUTPUT_FORMAT.md)**: The hybrid rule-based system that outputs `SELECTED`, `HOLD_REVIEW`, or `REJECTED`, complete with confidence intervals.

## 4. Integrity, Compliance, & Observability
Enterprise software requires rigorous auditing, malpractice detection, and monitoring. Zecpath-AI includes a zero-tolerance integrity layer that evaluates gaze deviation, tab switching, and audio mismatches in real-time.

- **[Malpractice & Integrity Detection](integrity/INTEGRITY_DETECTION_FRAMEWORK.md)**: The threshold-based detection system (e.g., >= 3 reading patterns, >= 12 tab switches).
- **[AI Ethics & Fairness Policy](ethics/AI_ETHICS_POLICY.md)**: Guidelines on bias mitigation, including the non-native English speaker proficiency toggles.
- **[Security & Governance Framework](governance/SECURITY_FRAMEWORK.md)**: Data retention, encryption in transit, and role-based access control (RBAC).
- **[AI Observability & Monitoring Plan](monitoring/AI_OBSERVABILITY_PLAN.md)**: SLIs, alerting rules (P1/P2), and Grafana dashboard designs.
- **[Logging Structure & Audit Trails](monitoring/LOGGING_STRUCTURE.md)**: JSON schemas for the immutable decision audit logs required for enterprise compliance.

## 5. Developer Guides
For engineers, SREs, and data scientists contributing to the Zecpath-AI codebase:

- **[Developer Onboarding Guide](DEVELOPER_HANDBOOK.md)**: Setup, local execution, environment dependencies, and running the `production_server.py`.
- **[Performance Benchmark Report](scalability/PERFORMANCE_BENCHMARK.md)**: Details on config caching (`lru_cache`) and regex pre-compilation optimizations.
- **[Debugging & Stabilization History](stabilization/DEBUGGING_REPORT_DAY_57.md)**: History of edge-case stabilization and crash-prevention architecture.
