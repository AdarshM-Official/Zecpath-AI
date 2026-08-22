# Fairness Review Notes

## Objective
To ensure that the Zecpath-AI HR Interview system evaluates all candidates fairly, without regard to race, gender, age, disability, or other protected characteristics.

## 1. Removing Demographic Bias Signals
*   **PII Scrubbing:** The `text_cleaner.py` module includes mechanisms to redact identifiable information before analysis. This ensures that the scoring engine cannot be inadvertently biased by names or cultural markers.
*   **Language Models:** The underlying natural language processing relies on structural analysis (e.g., word count, repetition) and exact keyword matching (ATS score), which are less susceptible to the biases often found in large language models.

## 2. Fairness of Scoring Algorithms
*   **Relevance Scoring:** Based entirely on overlap with the provided job description/ATS keywords. This is an objective metric.
*   **Communication Scoring:** Evaluated on clarity, lack of filler words, and sentence structure. *Note: We must monitor this metric to ensure it does not unfairly penalize non-native speakers or neurodivergent candidates. The "Confidence" and "Communication" thresholds are configurable and should be adjusted to be inclusive.*
*   **Consistency Scoring:** Measures internal contradiction within the candidate's own answers. This is a purely logical check, independent of demographic traits.

## 3. Continuous Monitoring
*   HR teams must conduct quarterly reviews comparing AI scoring distributions across different demographic groups.
*   If a statistical disparity is detected (e.g., the system consistently scores older candidates lower on "confidence"), the underlying weights and algorithms must be paused and audited.
