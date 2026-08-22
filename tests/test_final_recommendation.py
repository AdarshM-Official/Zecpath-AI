import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.final_recommendation_engine import FinalRecommendationEngine

def run_tests():
    engine = FinalRecommendationEngine()

    print("=== TEST 1: Ideal Candidate (High Score, Clean) ===")
    agg1 = {"candidate_id": "c_1", "hiring_fit_percent": 92.0, "breakdown": {"ats":0.9, "hr":0.95, "tech":0.91}}
    res1 = engine.generate_decision(agg1)
    print(json.dumps(res1, indent=2))

    print("\n=== TEST 2: High Score, but HIGH Integrity Risk ===")
    agg2 = {"candidate_id": "c_2", "hiring_fit_percent": 95.0, "breakdown": {"ats":0.95, "hr":0.95, "tech":0.95}}
    int2 = {"integrity_risk_tag": "HIGH_RISK"}
    res2 = engine.generate_decision(agg2, integrity_report=int2)
    print(json.dumps(res2, indent=2))

    print("\n=== TEST 3: High Score, but High Variance (Low Confidence) ===")
    # Terrible ATS, perfect HR, perfect Tech = High variance
    agg3 = {"candidate_id": "c_3", "hiring_fit_percent": 82.0, "breakdown": {"ats":0.1, "hr":1.0, "tech":1.0}}
    res3 = engine.generate_decision(agg3)
    print(json.dumps(res3, indent=2))
    
    print("\n=== TEST 4: Borderline Score ===")
    agg4 = {"candidate_id": "c_4", "hiring_fit_percent": 72.0, "breakdown": {"ats":0.7, "hr":0.7, "tech":0.75}}
    res4 = engine.generate_decision(agg4)
    print(json.dumps(res4, indent=2))

if __name__ == "__main__":
    run_tests()
