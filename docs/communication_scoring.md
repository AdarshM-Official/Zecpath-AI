# Communication Scoring

This document explains the communication skill evaluation model added in **Day 35**.

## Overview
The model evaluates a candidate’s answer based on six sub‑metrics and combines them into a final score (0‑100).

| Sub‑metric   | Description | How it is measured |
|--------------|-------------|--------------------|
| **Fluency** | Sentence continuity and use of transition words. | Average sentence length (target ~20 words) and count of transition words (`however`, `therefore`, …). |
| **Grammar** | Basic grammatical correctness. | Ratio of tokens that have a POS tag other than `PUNCT`/`SPACE`. |
| **Vocabulary** | Lexical richness and use of rare words. | Type‑token ratio plus proportion of words longer than 7 characters. |
| **Clarity** | How clear the explanation is. | Readability via Flesch‑Kincaid grade and a rough active‑voice estimate. |
| **Filler** | Presence of filler words that reduce professionalism. | Count of filler words (configurable list). |
| **Structure** | Presence of an introduction, body and conclusion. | Keyword heuristics for intro, transition, and concluding markers. |

## Configuration (`config/communication_config.json`)
```json
{
  "weights": {
    "fluency": 0.15,
    "grammar": 0.20,
    "vocabulary": 0.15,
    "clarity": 0.20,
    "filler": 0.10,
    "structure": 0.20
  },
  "filler_words": ["um", "uh", "like", "you know", "actually", "basically"],
  "readability": {"target_score": 70}
}
```
* **weights** – relative importance of each sub‑metric. Adjust to match your hiring priorities.
* **filler_words** – list of tokens that are counted as fillers. Extend as needed.
* **readability.target_score** – desired Flesch‑Kincaid score; the implementation uses it to map readability to a 0‑1 range.

## Scoring Formula
The utility `utils.communication_scoring.score_text` returns a dict:
```json
{
  "final_score": 82.5,
  "breakdown": {
    "fluency": 0.84,
    "grammar": 0.92,
    "vocabulary": 0.78,
    "clarity": 0.80,
    "filler": 0.90,
    "structure": 0.85
  }
}
```
1. Each sub‑metric produces a value in the range **0‑1**.
2. The **filler** count is transformed into a score where more filler reduces the value.
3. The weighted sum of all sub‑metrics is computed:
   ```
   weighted_sum = Σ(weight_i * metric_i)
   normalized = weighted_sum / Σ(weights)
   final_score = round(normalized * 100, 2)
   ```

## Bias Mitigation
* **Normalization** – All metrics are scaled to 0‑1 before weighting, which removes absolute magnitude bias.
* **Weight tuning** – You can lower the impact of vocabulary or fluency to reduce language‑centric bias.
* **Percentile‑based scaling** (future work) – Replace the simple min‑max scaling with a percentile lookup across a candidate pool for finer fairness.

## Usage Example
```python
from utils.communication_scoring import score_text

answer = "Um, I think I ... actually built a system that improves performance."
result = score_text(answer)
print(f"Score: {result['final_score']} (breakdown: {result['breakdown']})")
```
The script prints a numeric score and the individual metric contributions.

## Integration
* The scoring module is **stand‑alone** – you can call it from any part of the pipeline (e.g., after each answer in `InterviewConversationFlow`).
* To automatically score each answer, import `score_text` and store the result alongside the existing ATS score.

---

**Next steps**
1. Add `spacy` to `requirement.txt`.
2. Run `python -m spacy download en_core_web_sm` to install the model.
3. Execute the demo script `demo/run_communication_demo.py` to see the model in action.
4. Add unit tests (`tests/test_communication_scoring.py`).
