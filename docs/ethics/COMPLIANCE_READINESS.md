# Compliance Readiness Report

## 1. Data Protection & Privacy Laws (GDPR, CCPA)
The system architecture has been reviewed for alignment with major data protection regulations.

*   **Right to Access / Portability:** Candidates can request a copy of their interview transcript and the resulting AI scores. The unified scoring JSON serves as a portable data format.
*   **Right to Erasure (Right to be Forgotten):** A `data_retention.py` module handles the purging of all candidate data (audio, transcripts, scores) upon request or automatically after the retention period expires.
*   **Data Minimization:** Only data necessary for evaluating the candidate against the specific job description is processed.

## 2. Data Retention Policy
*   **Active Candidates:** Data is retained for the duration of the hiring process (typically 30-90 days).
*   **Archived Candidates:** For compliance and audit purposes (e.g., EEOC reporting), anonymized score data may be retained for up to 3 years. PII and raw audio/transcripts will be purged within 90 days post-decision, unless explicit consent for longer retention is obtained.

## 3. Automated Decision Making Compliance
Under GDPR Article 22, data subjects have the right not to be subject to a decision based solely on automated processing.
*   **Compliance Measure:** The HR AI assigns a "Hiring Fit Percentage," but this score is advisory. All hiring and rejection decisions *must* be finalized by a human employee. This system is a sorting and insight tool, not an automated hiring agent.
