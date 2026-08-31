# Zecpath-AI Flowcharts & Diagrams

These diagrams provide a visual overview of the Zecpath-AI architecture and hiring pipeline.

## 1. The 5-Stage Hiring Pipeline

This flowchart illustrates the end-to-end journey of a candidate from resume upload to the final decision.

```mermaid
graph LR
    %% Nodes
    A[ATS Resume Parsing] -->|Async| B[AI Chat Screening]
    B -->|Sync| C[HR Conversational Interview]
    C -->|Sync| D[Technical Deep-Dive]
    D -->|Sync| E[Docker Machine Test]
    E -->|Async| F((Final Recommendation Engine))
    
    %% Styling
    style A fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style B fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style C fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style D fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style E fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style F fill:#4CAF50,stroke:#1b5e20,stroke-width:3px,color:#fff
```

---

## 2. AI Module Integration & Data Flow

This diagram details how raw candidate inputs (Audio, Video, Code) are processed by specialized AI modules and aggregated into the Unified Scoring Engine.

```mermaid
graph TD
    %% Inputs
    subgraph Candidate Interface
        Audio[Audio Stream]
        Video[Video Stream]
        IDE[Code Editor]
        Chat[Text Input]
    end

    %% Processors
    subgraph AI Processing Layer
        STT[Speech-to-Text]
        NLP[NLP Scorer: Fluency, Clarity]
        TechScorer[Tech Scorer: Logic, Accuracy]
        Vision[Behavioral Vision Model]
        Integrity[Malpractice Detector]
        Sandbox[Docker Sandbox Execution]
    end

    %% Aggregation
    subgraph Decision Layer
        Unified[Unified Scoring Engine]
        Report[Hiring Report Generator]
    end

    %% Routing
    Audio --> STT
    STT --> NLP
    STT --> TechScorer
    Chat --> NLP
    Chat --> TechScorer
    
    Video --> Vision
    Vision --> Integrity
    
    IDE --> Sandbox
    
    %% To Unified
    NLP -->|HR Score| Unified
    TechScorer -->|Tech Score| Unified
    Sandbox -->|Code Score| Unified
    Integrity -->|Risk Flags| Unified
    
    %% Final Output
    Unified --> Report
```

---

## 3. The Malpractice Detection Logic

This flowchart shows how the system evaluates behavioral signals to catch cheating in real-time.

```mermaid
stateDiagram-v2
    [*] --> Monitoring

    state Monitoring {
        [*] --> TrackEvents
        TrackEvents --> GazeDeviation: Candidate looks off-screen
        TrackEvents --> TabSwitch: Candidate leaves browser
        TrackEvents --> AudioMatch: Second voice detected
    }
    
    Monitoring --> Evaluation: End of Answer
    
    state Evaluation {
        CheckLimits: Threshold Check
        CheckLimits --> Clean: Events < Threshold
        CheckLimits --> Flagged: Events >= Threshold
    }
    
    Clean --> Monitoring: Next Question
    Flagged --> Override: Trigger High Risk Flag
    
    Override --> [*]: Auto-Reject Candidate
```
