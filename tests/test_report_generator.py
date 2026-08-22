import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.hiring_report_generator import HiringReportGenerator

def test_report_generation():
    # Mock data assembled from the various AI engines
    master_data = {
        "final_decision": {
            "final_decision": "SELECTED",
            "decision_confidence": {"score": 85.0},
            "hiring_fit_score": 82.5,
            "explanation": [
                "Final Hiring Fit Score: 82.5%.",
                "Decision confidence: 85.0%.",
                "Candidate achieved a strong overall hiring-fit score.",
                "No blocking review conditions were identified."
            ]
        },
        "integrity_report": {
            "integrity_risk_tag": "CLEAN",
            "flags": []
        },
        "behavioral_report": {
            "behavioral_context": {
                "stress_indicator": 22.0,
                "recruiter_note": "Overall behavioral profile is strong. Recovered quickly from minor distraction."
            }
        },
        "round_scores": {
            "ats": 82.0,
            "screening": 78.0,
            "hr_interview": 80.0,
            "technical_interview": 85.0,
            "machine_test": 83.0
        },
        "strengths": [
            "Deep understanding of JVM tuning and memory management.",
            "Excellent communication and structured problem-solving (STAR method used effectively)."
        ],
        "weaknesses": [
            "Slightly vague when discussing CI/CD pipeline setups (DevOps domain)."
        ]
    }

    generator = HiringReportGenerator(output_dir="reports")
    
    # Generate the markdown string
    md_content = generator.generate_report(
        candidate_id="c_test_001", 
        role="Senior Backend Engineer", 
        master_data=master_data
    )
    
    # Save it to disk
    filepath = generator.export_report("c_test_001", md_content)
    
    print(f"Test Report successfully generated at: {filepath}")
    print("\n--- REPORT PREVIEW ---\n")
    print(md_content)

if __name__ == "__main__":
    test_report_generation()
