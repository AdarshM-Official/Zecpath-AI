import os
import sys

# Ensure project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.hr_scoring_engine import HRScoringEngine
from utils.communication_scoring import score_text
from utils.confidence_analyzer import analyze_response


def main():
    candidate_id = "candidate_001"
    answers = [
        "I have five years of experience in software development.",
        "I think I am a good fit, but I'm not entirely sure.",
        "My biggest strength is teamwork."
    ]
    engine = HRScoringEngine()
    history = []
    # Process each answer and collect metrics
    for ans in answers:
        # Communication score (0-1)
        comm = score_text(ans)
        comm_score = comm.get('final_score', 0) / 100.0
        # Confidence score (0-1)
        conf_res = analyze_response(ans, history=history)
        conf_score = conf_res.get('final_score', 0) / 100.0
        # Relevance (0-1) – using naive ATS keyword fallback
        relevance_score = engine.compute_relevance({"answer": {"raw_text": ans}})
        # Consistency (0-1)
        consistency_score = engine.compute_consistency(ans, history)
        metrics = {
            "relevance": relevance_score,
            "communication": comm_score,
            "confidence": conf_score,
            "consistency": consistency_score
        }
        # Generate per‑answer report (optional)
        report = engine.generate_report(candidate_id, metrics, interview_length=len(answers))
        print(json.dumps(report, indent=2))
        # Update history for next iteration
        history.append({"answer": ans})

if __name__ == "__main__":
    import json
    main()
