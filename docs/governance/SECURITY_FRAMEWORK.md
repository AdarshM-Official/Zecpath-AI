# Security Framework

## 1. Secure Storage Architecture
Zecpath-AI handles highly sensitive Personally Identifiable Information (PII). Storage architecture is segmented by sensitivity.

### A. Transcripts & Resumes (High Sensitivity)
- **Encryption at Rest:** AES-256 encryption.
- **Masking:** PII (emails, phone numbers, addresses) are masked by the `TextCleaner` utility *before* being saved to the transcript database.
- **Location:** Dedicated isolated bucket (e.g., AWS S3 with strict IAM roles).

### B. Reports & Scores (Medium Sensitivity)
- **Encryption at Rest:** AES-256 encryption.
- **Anonymization:** Candidate IDs are hashed using a one-way function for analytics purposes.
- **Location:** Relational database (e.g., PostgreSQL).

## 2. Access Control Logic (RBAC)
Access to candidate data is strictly controlled via Role-Based Access Control.

| Role | Access Level | Data Visibility |
|---|---|---|
| **Candidate** | Own Data Only | Can view final decision and generic feedback. |
| **Recruiter** | Assigned Jobs | Can view unified reports, risk flags, and transcripts. Cannot view raw algorithmic weights. |
| **Hiring Manager** | Assigned Jobs | Can view strengths/weaknesses and technical score breakdowns. Cannot view behavioral risk flags (preventing unconscious bias). |
| **Auditor / Admin** | All Data | Can view immutable audit logs, algorithmic weights, and raw system data. |

## 3. Machine Test Sandbox Security
- **Isolation:** Machine tests (coding challenges) execute in tightly constrained Docker containers.
- **Resource Limits:** Max execution time: 10s. Max Memory: 512MB. No network access.
- **Syscall Blocking:** Seccomp profiles block dangerous system calls (e.g., `execve`, file system writes outside the `/tmp` directory).
