import json
import os
import sys
# Ensure project root is on PYTHONPATH for utils and other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.config_loader import load_config
from interview_ai.conversation_flow import InterviewConversationFlow
from screening_ai.report_generator import ScreeningReportGenerator

def simulate_candidate(candidate_id: str, job_role: str, raw_evaluation: dict) -> dict:
    """Run the full pipeline for a single candidate and return the report dict."""
    generator = ScreeningReportGenerator()
    report = generator.generate_report(candidate_id, job_role, raw_evaluation)
    return report

def main():
    config = load_config()
    print("Loaded config:", config)

    # Mock candidate data – in a real setup this would be produced by ATS/answer_understanding pipelines
    mock_candidates = [
        {
            "candidate_id": "C001",
            "job_role": "Backend Developer",
            "raw_evaluation": {
                "overall_score": 85,
                "recommendation": "Shortlist",
                "qa_sessions": [
                    {
                        "question": "What are your strongest technical skills?",
                        "intent": "skills",
                        "answer": {"raw_text": "Python, Django, Flask"},
                        "score": 92,
                        "extracted_entities": {"skills": ["python", "django", "flask"]},
                        "quality": {"missing_information": False}
                    },
                    {
                        "question": "How many years of experience do you have?",
                        "intent": "experience",
                        "answer": {"raw_text": "I have four years of experience."},
                        "score": 88,
                        "extracted_entities": {"experience": {"years": 4}},
                        "quality": {"missing_information": False}
                    }
                ]
            }
        },
        {
            "candidate_id": "C002",
            "job_role": "Data Scientist",
            "raw_evaluation": {
                "overall_score": 58,
                "recommendation": "Reject",
                "qa_sessions": [
                    {
                        "question": "What are your strongest technical skills?",
                        "intent": "skills",
                        "answer": {"raw_text": "I know Excel."},
                        "score": 45,
                        "extracted_entities": {"skills": []},
                        "quality": {"missing_information": true, "missing_reason": "Missing core ML skills"}
                    },
                    {
                        "question": "How many years of experience do you have?",
                        "intent": "experience",
                        "answer": {"raw_text": "I am a fresher."},
                        "score": 50,
                        "extracted_entities": {"experience": {"years": 0}},
                        "quality": {"missing_information": False}
                    }
                ]
            }
        }
    ]

    reports = []
    for cand in mock_candidates:
        report = simulate_candidate(cand["candidate_id"], cand["job_role"], cand["raw_evaluation"])
        reports.append(report)
        # Export each report for later comparison
        out_path = f"screening_ai/{cand['candidate_id']}_report.json"
        with open(out_path, "w") as f:
            json.dump(report, f, indent=4)
        print(f"Report for {cand['candidate_id']} written to {out_path}")

    # Save aggregated reports for analysis
    aggregated_path = "screening_ai/aggregated_reports.json"
    with open(aggregated_path, "w") as f:
        json.dump(reports, f, indent=4)
    print(f"All reports aggregated at {aggregated_path}")

if __name__ == "__main__":
    main()
