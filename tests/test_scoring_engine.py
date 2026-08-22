from screening_ai.scoring_engine import evaluate_screening
sample_answers = [
    {
        "question_id": "Q1",
        "original_text": "I am a Python developer with 3 years experience",
        "intent": "experience",
        "skills": ["python"],
        "experience_years": 3,
        "is_vague": False,
        "off_topic": False
    },
    {
        "question_id": "Q2",
        "original_text": "I worked in Django and React projects",
        "intent": "skills",
        "skills": ["django", "react"],
        "experience_years": 2,
        "is_vague": False,
        "off_topic": False
    }
]
result = evaluate_screening(sample_answers)
print(result)
