# Zecpath-AI Product Roadmap

## Phase 1: Current System (v1.0) – Production-Ready
*Days 1–57 | Status: Complete*

The core Zecpath-AI pipeline is feature-complete. It covers the full candidate lifecycle from resume parsing to a final hiring recommendation, with behavioral AI design, malpractice detection, and governance documentation.

**Capabilities:**
- ATS Parsing & Screening
- HR Interview AI (Conversation Flow, Follow-Up Engine)
- Technical Interview (Score-Based Depth & Logic)
- Cross-Round Score Aggregation (Unified Engine)
- Final Recommendation Engine (Hybrid Rule + Score)
- Integrity Detection (Threshold + Pattern Rules)
- Hiring Intelligence Report Generator
- AI Ethics, Compliance, and Governance Documentation

---

## Phase 2: Enhanced Intelligence (v1.5) – Q4 2026
*Target: 3 months post v1.0*

| Feature | Description | Priority |
|---|---|---|
| **Real-Time AI Coaching Panel** | A recruiter-side overlay that shows live candidate confidence signals and suggests better probing questions in real-time | HIGH |
| **Candidate Improvement Suggestions** | At end of interview, generate a personalized improvement report for the candidate (e.g., "Your communication score was strong, but your system design depth could improve") | HIGH |
| **Interview Analytics Dashboard** | Web-based recruiter dashboard showing aggregated AI decision trends, score distributions, and round-by-round performance heatmaps | MEDIUM |
| **Multi-Language Support** | Extend the NLP pipeline to support Hindi, Arabic, and Spanish interviews | MEDIUM |

---

## Phase 3: Deep AI Integration (v2.0) – Q2 2027
*Target: 9 months post v1.0*

| Feature | Description | Priority |
|---|---|---|
| **AI Video Analysis (Computer Vision)** | Implement the behavioral AI modules designed on Day 48 using MediaPipe FaceMesh for real gaze and head pose estimation | HIGH |
| **Emotion Detection (Valence-Only)** | Detect valence (positive/neutral/negative affect) using micro-expression analysis — explicitly excluding emotion labeling to avoid cultural bias | MEDIUM |
| **LLM-Powered Answer Evaluation** | Replace heuristic concept-matching in the Technical Scoring Engine with an LLM judge that can evaluate semantic correctness | HIGH |
| **Adaptive Question Generation** | Use an LLM to dynamically generate new technical questions based on the candidate's last answer, rather than pulling from a static bank | HIGH |

---

## Phase 4: Scaling & Enterprise (v3.0) – 2028
*Target: 18 months post v1.0*

| Feature | Description | Priority |
|---|---|---|
| **Multi-Tenant SaaS Architecture** | Deploy as an isolated multi-tenant service supporting hundreds of companies with dedicated data partitions | HIGH |
| **Continuous Learning Loop** | Integrate recruiter feedback on AI decisions to fine-tune scoring weights over time using RLHF techniques | HIGH |
| **Structured Hiring Graph** | Build a knowledge graph connecting candidates, roles, skills, and outcomes to surface non-obvious matches | MEDIUM |
