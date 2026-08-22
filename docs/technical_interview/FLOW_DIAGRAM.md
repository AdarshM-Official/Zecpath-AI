# Technical Interview Flow Design

This diagram illustrates the state machine for the Technical Interview AI.

```mermaid
stateDiagram-v2
    [*] --> INITIALIZE
    
    INITIALIZE --> GREETING: Load Candidate Profile & YoE
    GREETING --> EXP_PHASE: Verify Resume Details
    
    state EXP_PHASE {
        [*] --> AskPastProject
        AskPastProject --> EvaluateExp: Candidate Answers
        EvaluateExp --> AskPastProject: Loop (2-3 questions)
        EvaluateExp --> CONCEPTUAL_PHASE: Phase Complete
    }
    
    state CONCEPTUAL_PHASE {
        [*] --> SelectConceptQ: Filter by Role & Tier
        SelectConceptQ --> WaitConceptAns
        WaitConceptAns --> EvaluateConcept: Candidate Answers
        
        EvaluateConcept --> IncreaseTier: Answer is Excellent
        EvaluateConcept --> MaintainTier: Answer is Adequate
        EvaluateConcept --> ProvideHint_DecreaseTier: Answer is Poor
        
        IncreaseTier --> SelectConceptQ
        MaintainTier --> SelectConceptQ
        ProvideHint_DecreaseTier --> SelectConceptQ
        
        EvaluateConcept --> SCENARIO_PHASE: Phase Complete (Time/Limit reached)
    }
    
    state SCENARIO_PHASE {
        [*] --> PresentScenario: Present System/Debug Problem
        PresentScenario --> WaitScenarioAns
        WaitScenarioAns --> EvaluateScenario: Candidate Explains Approach
        
        EvaluateScenario --> AskFollowUp: Drill down on specific technical choice
        AskFollowUp --> WaitScenarioAns
        
        EvaluateScenario --> AGGREGATE_SCORES: Phase Complete
    }
    
    AGGREGATE_SCORES --> CLOSING: Generate Tech Score & Feedback
    CLOSING --> [*]
```

## State Descriptions
*   **INITIALIZE:** System loads ATS parsing data to know the candidate's stack and sets the initial difficulty tier.
*   **CONCEPTUAL_PHASE:** The engine loops through rapid-fire knowledge questions, actively adjusting the `Tier` up or down based on the `EvaluateConcept` heuristic.
*   **SCENARIO_PHASE:** Focuses on a single, long-form question. The AI acts as a collaborative partner, asking probing follow-ups (e.g., "Why did you choose Redis over Memcached for that layer?").
*   **AGGREGATE_SCORES:** The Technical Scoring Engine computes metrics for *Accuracy*, *Problem Solving*, *Depth of Knowledge*, and *Communication of Technical Concepts*.
