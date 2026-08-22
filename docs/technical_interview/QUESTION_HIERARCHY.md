# Question Hierarchy & Experience Logic

## 1. Experience-Based Difficulty Tiers
The system initializes the question difficulty based on the candidate's Years of Experience (YoE). 

### Tier 1: Junior (0–2 Years)
*   **Focus:** Core syntax, basic concepts, tool familiarity, and execution under guidance.
*   **Question Examples:**
    *   *Conceptual:* "What is the difference between `let`, `const`, and `var` in JavaScript?"
    *   *Scenario:* "You encounter a NullPointerException. How do you find the cause?"
*   **Expectation:** Accurate textbook definitions and basic debugging skills.

### Tier 2: Intermediate (3–5 Years)
*   **Focus:** Framework internals, performance optimization, design patterns, and independent problem-solving.
*   **Question Examples:**
    *   *Conceptual:* "Explain how the Virtual DOM works in React and how it optimizes rendering."
    *   *Scenario:* "Your API endpoint is taking 5 seconds to respond. Walk me through your optimization strategy."
*   **Expectation:** Understanding of "under-the-hood" mechanics and ability to identify bottlenecks.

### Tier 3: Senior/Lead (5+ Years)
*   **Focus:** System design, architectural trade-offs, scalability, security, and mentoring.
*   **Question Examples:**
    *   *Conceptual:* "Compare the trade-offs between a monolithic architecture and microservices for a rapidly scaling startup."
    *   *Scenario:* "Design a URL shortener service that must handle 10,000 requests per second. How do you partition the database?"
*   **Expectation:** Ability to discuss pros/cons, handle ambiguity, and design for scale and resilience.

## 2. Dynamic Progression Logic
While YoE sets the *initial* tier, the AI adapts in real-time. If a 2-year junior perfectly answers Tier 1 and Tier 2 questions, the AI will introduce a Tier 3 question to test their ceiling. Conversely, if a 6-year senior struggles with Tier 3 architectural concepts, the AI will drop to Tier 2 to establish their actual competency level.

## 3. Question Bank JSON Schema (Proposed)
```json
{
  "domain": "java_backend",
  "tier": 2,
  "type": "scenario",
  "tags": ["performance", "database"],
  "question": "Your Spring Boot application is throwing OutOfMemory errors during peak load. How do you investigate?",
  "evaluation_criteria": {
    "required_concepts": ["Heap dump analysis", "Garbage collection logs", "Memory profiling tools"],
    "bonus_concepts": ["Thread contention", "Connection pool tuning"]
  }
}
```
