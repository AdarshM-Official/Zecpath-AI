# Cross-Round Aggregation & Unified Scoring
**Module:** `utils/unified_scoring_engine.py`

Zecpath-AI aggregates scores from five disparate modules into a single, reliable metric: the `hiring_fit_percent`.

## 1. The Clamping Mechanism
A critical stabilization feature implemented in V2 is strict mathematical clamping. 
Because the AI modules use different heuristics (Regex vs NLP vs Docker execution), it is possible for an edge case to return a score like `1.2` or `-0.05`.

Before any weighting is applied, every input is clamped using:
```python
def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(float(value), hi))
    except (TypeError, ValueError):
        return lo
```
This guarantees absolute consistency; a broken sub-module cannot corrupt the overall system average.

## 2. Dynamic Role Weighting
The system dynamically loads weights from `config/unified_scoring_config.json`. Different engineering levels require different evaluation criteria.

### Junior Developer Weights
Focuses heavily on raw technical ability and ATS screening, rather than deep system design (HR).
- ATS: 15%
- Screening: 15%
- HR / Behavioral: 20%
- Technical: 30%
- Machine Test: 20%

### Senior Developer Weights
Focuses heavily on communication, architecture, and practical machine tests.
- ATS: 10%
- Screening: 10%
- HR / Behavioral: 20%
- Technical: 25%
- Machine Test: 35%

## 3. Transparency Logs
To build trust with recruiters, the engine outputs a human-readable `transparency_log` explaining exactly how the math was computed:
> *"ATS (15% weight): provided 9.8 pts + SCREENING (15% weight): provided 8.2 pts + HR (20% weight): provided 11.9 pts + TECHNICAL (30% weight): provided 0.0 pts + MACHINE_TEST (20% weight): provided 0.0 pts = 29.9 Final Score"*
