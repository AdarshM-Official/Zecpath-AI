# Zecpath-AI: Automated Technical Hiring Pipeline
**Version:** 2.0 (Production Release)

![Zecpath-AI Banner](https://via.placeholder.com/1000x200.png?text=Zecpath-AI+Hiring+Pipeline)

Zecpath-AI is an end-to-end, stateless microservice platform designed to fully automate the technical hiring process. It evaluates candidates across 5 distinct stages—from resume parsing to a final hiring recommendation—using multi-modal AI analysis (NLP, Regex Heuristics, and Vision/Audio Integrity Monitoring).

---

## 🌟 Key Features
- **5-Stage Pipeline:** ATS Parsing ➔ Chat Screening ➔ Conversational HR Interview ➔ Technical Depth ➔ Machine Code Test.
- **Behavioral Analysis:** Uses NLTK and spaCy to gauge fluency, sentiment, and stress in real-time.
- **Enterprise Integrity:** Built-in `MalpracticeDetector` traps tab-switching, gaze deviation, and external assistance (e.g., ChatGPT).
- **Stateless Concurrency:** Built on a Domain-Driven Design (DDD) architecture, powered by a high-throughput `waitress` WSGI server.
- **Fairness Toggles:** Dynamic configuration to mitigate bias against non-native English speakers.

---

## 📚 Comprehensive Documentation
The `docs/` folder contains exhaustive documentation of the system. 
**Start here:** [Zecpath Technical Handbook](docs/ZECPATH_TECHNICAL_HANDBOOK.md)

Other critical documents:
- [Developer Onboarding & Architecture](docs/DEVELOPER_HANDBOOK.md)
- [API Specifications](docs/api/API_SPECIFICATION.md)
- [Malpractice & Integrity Logic](docs/integrity/MALPRACTICE_DETECTION_LOGIC.md)
- [Future AI Roadmap](docs/roadmap/AI_ROADMAP.md)

---

## ⚙️ Quick Start (Local Setup)

### 1. Requirements
- Python 3.10+
- Git
- Windows/Linux OS

### 2. Installation
Clone the repository and spin up a virtual environment:
```bash
git clone https://github.com/Zecpath-AI/aiproject.git
cd aiproject
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate
```

Install dependencies and NLP corpora:
```bash
pip install -r requirements.txt
pip install waitress

python -m nltk.downloader vader_lexicon
python -m spacy download en_core_web_sm
```
*(Note: If spaCy fails to load due to Windows Application Control, the system will automatically fall back to regex heuristics without crashing).*

---

## 🚀 Running the System

Zecpath-AI is bundled with a master CLI control script: `release_ready_system.py`.

### 1. Check System Status
Verify that the AI modules and scoring engines are online and bounds-clamping is active.
```bash
python release_ready_system.py status
```

### 2. Run the End-to-End Simulation
To test the core algorithms without a frontend UI, run the simulation script. It will evaluate 3 mock candidate personas (A Strong Senior, a Weak Junior, and a Suspicious Cheater) and generate Markdown reports in the `reports/` folder.
```bash
python release_ready_system.py simulate
```

### 3. Start the Production API Server
Boot the `waitress` server to listen for live HTTP requests on `0.0.0.0:8080`.
```bash
python release_ready_system.py serve
```

---
*Developed during the Zecpath-AI Internship Program.*
