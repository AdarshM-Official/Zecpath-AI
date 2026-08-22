import json
from report_generator import ScreeningReportGenerator

def main():
    # Mock raw evaluation data coming from ATS/Screening engines
    mock_raw_data = {
        "overall_score": 82.5,
        "recommendation": "Shortlist",
        "qa_sessions": [
            {
                "question": "What are your strongest technical skills?",
                "intent": "skills",
                "answer": {"raw_text": "I am strongest in Python, Django, React and SQL."},
                "score": 95,
                "extracted_entities": {
                    "skills": ["python", "django", "react", "sql"]
                },
                "quality": {"missing_information": False}
            },
            {
                "question": "How many years of experience do you have?",
                "intent": "experience",
                "answer": {"raw_text": "I have three years of experience in software development."},
                "score": 90,
                "extracted_entities": {
                    "experience": {"years": 3.0}
                },
                "quality": {"missing_information": False}
            },
            {
                "question": "What are your salary expectations?",
                "intent": "salary",
                "answer": {"raw_text": "I am expecting around 6 LPA."},
                "score": 85,
                "extracted_entities": {
                    "salary": {"amount": 6.0, "unit": "LPA"}
                },
                "quality": {"missing_information": False}
            },
            {
                "question": "What is your notice period?",
                "intent": "availability",
                "answer": {"raw_text": "I can join immediately."},
                "score": 90,
                "extracted_entities": {
                    "availability": {"immediate": True, "start_time": "immediate"}
                },
                "quality": {"missing_information": False}
            },
            {
                "question": "Have you worked with Docker and Kubernetes?",
                "intent": "skills_specific",
                "answer": {"raw_text": "No, I haven't used them in production, only learning."},
                "score": 45,
                "extracted_entities": {
                    "skills": []
                },
                "quality": {"missing_information": True, "missing_reason": "Missing production experience for Docker/K8s"}
            }
        ]
    }

    generator = ScreeningReportGenerator()
    
    # Generate the structured report
    report = generator.generate_report(
        candidate_id="C999", 
        job_role="Backend Developer", 
        raw_evaluation=mock_raw_data
    )
    
    # Save the sample
    sample_path = "aiproject/screening_ai/sample_screening_report.json"
    generator.export_report(report, sample_path)
    print(f"Sample report successfully exported to {sample_path}")
    
    # Print it out
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()
