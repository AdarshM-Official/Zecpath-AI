# Technical Interview AI Blueprint

## 1. System Overview
The Technical Interview AI is a specialized module of Zecpath-AI designed to evaluate a candidate's hard skills, architectural thinking, and problem-solving abilities. Unlike the HR module (which focuses on behavioral traits), this system is highly dynamic, adjusting question difficulty and domain focus based on the candidate's real-time performance and stated experience level.

## 2. Interview Structure
The technical interview is conducted across four distinct phases:

1.  **Introduction & Profiling (2-3 mins):**
    *   Verifies the candidate's stated role and primary tech stack.
    *   Calibrates the initial difficulty based on their resume/experience level.
2.  **Experience-Based Questions (5-10 mins):**
    *   Questions derived directly from the candidate's past projects.
    *   *Goal:* Validate that the candidate actually performed the work they claimed.
3.  **Conceptual Questions (10-15 mins):**
    *   Rapid-fire knowledge checks on core languages, frameworks, and computer science fundamentals.
    *   *Goal:* Assess breadth and depth of theoretical knowledge.
4.  **Scenario-Based Problems (15-20 mins):**
    *   Open-ended architectural, debugging, or system design scenarios (e.g., "Our database is experiencing high latency during peak hours. How do you troubleshoot this?").
    *   *Goal:* Assess problem-solving methodology, trade-off analysis, and practical application.

## 3. Role-to-Domain Mapping
The AI pulls questions from specialized skill domains based on the applied role.

| Job Role | Primary Skill Domains | Secondary Skill Domains |
| :--- | :--- | :--- |
| **MERN Fullstack** | React, Node.js, Express, MongoDB | REST APIs, JWT Auth, Webpack |
| **Backend (Java)** | Java 11/17, Spring Boot, Hibernate | Microservices, SQL/NoSQL, Kafka |
| **DevOps Engineer** | Docker, Kubernetes, CI/CD (Jenkins/GitLab) | AWS/GCP/Azure, Terraform, Linux OS |
| **Data Scientist** | Python, Pandas, Scikit-Learn, SQL | Deep Learning, MLOps, Data Visualization |

## 4. Adaptive Difficulty Progression
The AI employs an Elo-like rating system under the hood to manage difficulty progression:
*   **Correct/Deep Answer:** The AI increments the difficulty tier for the next question.
*   **Vague/Incorrect Answer:** The AI asks a follow-up hint. If still incorrect, the AI lowers the difficulty tier for the next question to find the candidate's "baseline".
