# Developer Handbook & Integration Guide

Welcome to the Zecpath-AI HR Interview engine. This guide explains how to set up the project, extend its features, and troubleshoot common issues.

## 1. Getting Started

### Prerequisites
*   Python 3.8+
*   Virtual environment (recommended)

### Running a Demo
To see the interview flow and scoring engines in action without spinning up an API, run the provided demo scripts:
```bash
# Run the unified scoring demo
python demo/run_unified_demo.py
```

## 2. Extending the System

### Modifying Scoring Weights
All scoring weights are centralized in the `config/` directory. You do not need to alter code to change how candidates are evaluated.
*   **HR Scores:** Edit `config/hr_scoring_config.json` to adjust the weight of `relevance`, `consistency`, etc.
*   **Unified Scores:** Edit `config/unified_scoring_config.json` to adjust role-based weights (e.g., making ATS matter less for senior roles).

### Adding a New Evaluation Metric
1.  Open `utils/hr_scoring_engine.py`.
2.  Add a new method (e.g., `compute_technical_jargon(self, text)`).
3.  Ensure the method returns a clamped float between `0.0` and `1.0`.
4.  Call the method inside the metrics dictionary before `generate_report` is invoked in `conversation_flow.py`.
5.  Add the new metric to `config/hr_scoring_config.json` with a designated weight.

## 3. Troubleshooting

### Issue: The AI asks infinite follow-up questions.
*   **Cause:** The candidate's answer is repeatedly triggering the `detect_vague` or `detect_incomplete` heuristics.
*   **Fix:** Ensure `max_follow_up_per_question` is set (e.g., to 2) in `config/followup_config.json`. Check `utils/followup_engine.py` to ensure `_can_ask()` is properly gating requests.

### Issue: HR Sub-Scores are > 100 or negative.
*   **Cause:** A custom metric calculation is returning an out-of-bounds float.
*   **Fix:** Wrap the return statement of your custom metric in a clamp: `max(0.0, min(your_value, 1.0))`. The `aggregate_score` function acts as a secondary safety net.

### Issue: Legitimate answers are being flagged as "Vague".
*   **Cause:** The word-count threshold in `followup_engine.py` might be too aggressive for the specific role being interviewed.
*   **Fix:** Lower the word-count threshold in `detect_vague()` (currently looks for 3-6 words).

### Issue: Division by Zero Errors in Scoring.
*   **Cause:** Empty transcripts bypassing the text cleaner.
*   **Fix:** Ensure `clean_text()` in `utils/text_cleaner.py` handles `None` and empty strings gracefully, returning `""`. The scoring engines have fallbacks to return `0.0` or `0.5` if the text is empty.
