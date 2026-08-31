# Zecpath-AI Future Roadmap & Innovation Proposal
**Target Audience:** Engineering Leadership, Product Management
**Current Status:** V2.0 (Production API Released)

## Overview
Over the past 69 days, the foundation for Zecpath-AI was laid, transitioning the product from concept to a hardened, stateless microservice pipeline. This document outlines the strategic innovation roadmap for V3.0 and beyond, focusing on integrating deeper LLM capabilities, real-time analytics, and candidate coaching.

---

## Phase 1 (Q3): Large Language Model (LLM) Integration

### The Goal
Upgrade the `TechScoringEngine` and `InterviewConversationFlow`.
Currently, the system relies on regex heuristics and NLTK/spaCy sentiment analysis. While highly performant and predictable, it struggles to evaluate highly nuanced, open-ended system design questions.

### Execution Strategy
1. **Local Quantized Models:** Integrate a locally hosted model like `Llama-3 8B-Instruct` using `llama.cpp` or `vLLM` to maintain the current $0.05/eval cost structure while avoiding OpenAI API latency and data-privacy concerns.
2. **Context-Aware Follow-Ups:** Replace the finite state machine with an LLM Agent capable of asking dynamic, probing follow-up questions based on the candidate's previous response.

---

## Phase 2 (Q4): The Recruiter Dashboard & WebSocket Streaming

### The Goal
Move recruiters out of Markdown files and into a rich, interactive web portal.

### Execution Strategy
1. **Next.js Frontend:** Build the visual dashboard designed in `docs/monitoring/DASHBOARD_DESIGN.md`. 
2. **WebSocket API:** Refactor `hr_interview_api.py` from synchronous HTTP REST to WebSockets. This will eliminate UI latency ("dead air") for candidates during the interview, allowing the AI to stream its conversational text chunks in real-time.
3. **Live Telemetry:** Stream `MalpracticeDetector` events to the recruiter dashboard so human reviewers can intervene in a live interview if a candidate triggers a `CRITICAL` tab-switch threshold.

---

## Phase 3 (Next Year): The AI Coaching Ecosystem

### The Goal
Transform Zecpath-AI from just an evaluation tool into a candidate enablement platform. Candidate rejection is currently a negative UX. We can monetize and improve UX by offering feedback.

### Execution Strategy
1. **Actionable Improvement Reports:** Instead of just sending a rejection email, the `HiringReportGenerator` will generate a secondary "Candidate Facing" report.
2. **Skill Gap Analysis:** "You were rejected because your understanding of Kafka consumer groups was weak. Here are 3 resources to study."
3. **Mock Interview Subscriptions:** Candidates can pay to practice against the Zecpath-AI system in "Coaching Mode" to improve their communication and technical delivery before applying to actual enterprise roles.

---
*Roadmap Authored at the conclusion of the Zecpath-AI Internship Program.*
