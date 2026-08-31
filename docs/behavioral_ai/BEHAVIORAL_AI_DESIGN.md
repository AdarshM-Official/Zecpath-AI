# Behavioral AI & Communication Scoring Design
**Module:** `utils/communication_scoring.py`

Zecpath-AI does not just evaluate *what* a candidate says, but *how* they say it. The Behavioral AI layer analyzes textual responses and audio transcriptions to gauge fluency, confidence, and stress levels.

## 1. NLP Tooling & Fallbacks
The system uses heavy NLP libraries for behavioral analysis:
- **NLTK (VADER):** Used for fast, rule-based sentiment analysis to detect frustration or extreme negativity.
- **spaCy (`en_core_web_sm`):** Used for advanced Part-of-Speech (POS) tagging and grammatical complexity analysis.

### The Windows / CI Fallback Pattern
Due to Windows Application Control restrictions and container limitations, `spaCy` DLLs can sometimes fail to load. The `communication_scoring.py` module is wrapped in a fail-safe soft-dependency loader. If `spaCy` fails, the system automatically falls back to lightweight, regex-based heuristic parsing without crashing the interview.

## 2. Core Metrics Evaluated

The scoring engine calculates three primary sub-scores:

### A. Fluency & Clarity (0-100)
- Analyzes the structure of the sentences.
- **Penalties:** Frequent use of filler words ("um", "uh", "like") or run-on sentences with poor punctuation lowers the score.
- **Bias Mitigation:** A configurable `language_proficiency` toggle can reduce grammar penalties for non-native English speakers.

### B. Confidence & Sentiment (0-100)
- NLTK VADER assigns a compound polarity score `[-1.0, 1.0]`. 
- High positive sentiment (e.g., "I successfully optimized...", "I am confident...") boosts the score.
- Defensive or highly negative language (e.g., "I don't know why you are asking this") drops the score.

### C. Stress & Consistency (0-100)
- The system checks for semantic contradictions across the interview timeline (e.g., claiming 10 years of Python experience in Question 1, but failing basic Python syntax in Question 3).

## 3. Output Schema
The generated HR scores are injected into the Unified Engine as follows:
```json
{
  "relevance": 50.0,
  "communication": 64.82,
  "confidence": 84.67,
  "consistency": 59.72
}
```
