# Technical Evaluation Report Format

## JSON Structure
When the Technical Interview reaches CLOSING, the scoring engine generates the following report object:

```json
{
  "candidate_id": "c_12345",
  "role": "Backend Engineer (Java)",
  "experience_tier": 2,
  "overall_technical_score": 78.5,
  "skill_breakdown": {
    "java_backend": 82.0,
    "system_design": 65.0,
    "problem_solving": 88.0
  },
  "per_question_scores": [
    {
      "question_id": "q_001",
      "domain": "java_backend",
      "difficulty_tier": 2,
      "answer_depth": "deep",
      "scores": {
        "accuracy": 90.0,
        "depth": 85.0,
        "logic": 80.0,
        "applicability": 70.0
      },
      "weighted_score": 84.5,
      "normalized_score": 76.0,
      "explainability_note": "Candidate demonstrated understanding of heap dumps and GC logs (required concepts hit). Mentioned JVM tuning as a bonus concept, indicating practical depth."
    }
  ],
  "hiring_recommendation": "STRONG HIRE",
  "strengths": ["Deep Java internals knowledge", "Structured debugging methodology"],
  "gaps": ["Limited exposure to distributed system design patterns"]
}
```

## Markdown Report Format
The report is also rendered as a human-readable markdown file for recruiter review:

```markdown
# Technical Evaluation Report: John Doe

**Role:** Backend Engineer | **Tier:** Intermediate | **Score:** 78.5 / 100

## Skill Breakdown
| Skill Domain | Score |
|---|---|
| Java Backend | 82.0 |
| System Design | 65.0 |
| Problem Solving | 88.0 |

## Recommendation
**STRONG HIRE** – Candidate demonstrated deep technical understanding of core Java
concepts and problem-solving. Recommend final interview with system design focus.
```
