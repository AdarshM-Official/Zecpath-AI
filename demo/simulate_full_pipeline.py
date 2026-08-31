import os
import json
import sys

# Ensure imports work regardless of execution directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from interview_ai.conversation_flow import InterviewConversationFlow, ConversationState
from utils.final_recommendation_engine import FinalRecommendationEngine
from utils.malpractice_detector import MalpracticeDetector
from utils.hiring_report_generator import HiringReportGenerator

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "demo_dataset")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

def load_json(filename):
    with open(os.path.join(DATASET_DIR, filename), 'r') as f:
        return json.load(f)

def run_simulation():
    print("=" * 60)
    print("ZECPATH-AI END-TO-END PIPELINE SIMULATION")
    print("=" * 60)
    
    candidates = load_json("candidates.json")
    jds = load_json("job_descriptions.json")
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    for candidate in candidates:
        name = candidate["name"]
        role_key = candidate["role_key"]
        jd = jds.get(role_key, {})
        role_type = jd.get("role_type", "junior_developer")
        
        print(f"\n--- PROCESSING CANDIDATE: {name} ({role_type.upper()}) ---")
        
        # 1. Initialize Conversation Flow (Sync Interview)
        flow = InterviewConversationFlow()
        flow.candidate_role = role_type
        flow.ats_score = candidate["mock_async_results"]["ats_score"]
        flow.screening_score = candidate["mock_async_results"]["screening_score"]
        
        # Trigger Start
        resp = flow.process_event("start")
        print(f"[AI]: {resp.get('message')}")
        
        # Feed predefined answers
        for answer in candidate["interview_responses"]:
            if flow.state in [ConversationState.CLOSING, ConversationState.TERMINATED]:
                break
            
            print(f"[CANDIDATE]: {answer}")
            
            # Send plain string payload
            resp = flow.process_event("answer", payload=answer)
            if resp.get('message'):
                print(f"[AI]: {resp.get('message')}")
        
        # If not closed yet, send a closing event (mocking time up)
        if flow.state not in [ConversationState.CLOSING, ConversationState.TERMINATED]:
            flow.state = ConversationState.CLOSING
            flow.unified_score = flow.unified_engine.compute_score(
                ats=flow.ats_score,
                screening=flow.screening_score,
                hr=flow.hr_engine.evaluate_candidate(flow.answer_history)["final_score"] / 100,
                technical=0.0, # Handled downstream
                machine_test=candidate["mock_async_results"]["machine_test_score"],
                role=flow.candidate_role
            )
            
        print("\n[SYSTEM] Interview Concluded. Generating Final Decision...")
        
        # 2. Run Integrity/Malpractice Check
        detector = MalpracticeDetector()
        
        # Trigger hooks based on mock behavioral context
        for _ in range(candidate.get("behavioral_context", {}).get("tab_switches", 0)):
            detector.on_tab_switch()
            
        for _ in range(candidate.get("behavioral_context", {}).get("gaze_deviations", 0)):
            detector.on_looking_away()
            
        integrity_report = detector.compute_risk_report(
            candidate_id=candidate["candidate_id"], 
            session_id="sim_session"
        )
        integrity_flags = integrity_report.get("flags", [])
        
        # 3. Final Recommendation Engine
        decision_engine = FinalRecommendationEngine(
            candidate_id=candidate["candidate_id"],
            job_id=role_key
        )
        unified_breakdown = flow.unified_score.get("breakdown", {})
        
        decision = decision_engine.generate_decision(
            hiring_fit_score=flow.unified_score.get("hiring_fit_percent", 0.0),
            round_scores={
                "ats": flow.ats_score * 100,
                "screening": flow.screening_score * 100,
                "hr": unified_breakdown.get("hr", 0) * 100,
                "technical": 75.0, # Mocking technical score for demo
                "machine_test": candidate["mock_async_results"]["machine_test_score"] * 100
            },
            integrity_data={"flags": integrity_flags}
        )
        
        print(f"[DECISION ENGINE] Final Decision: {decision.get('final_decision')}")
        print(f"[DECISION ENGINE] Hiring Fit: {decision.get('hiring_fit_score')}%")
        
        # 4. Generate Markdown Report
        report_gen = HiringReportGenerator()
        
        master_data = {
            "final_decision": decision,
            "integrity_report": integrity_report,
            "behavioral_report": {},
            "round_scores": decision.get("round_scores", {}),
            "strengths": ["Good communication structure", "Answered questions confidently"],
            "weaknesses": ["Needs deeper technical explanation"]
        }
        
        report_content = report_gen.generate_report(
            candidate_id=candidate["candidate_id"],
            role=role_type,
            master_data=master_data
        )
        
        report_path = os.path.join(REPORTS_DIR, f"{candidate['candidate_id']}_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        print(f"[REPORT] Saved to: {report_path}")
        print("-" * 60)

if __name__ == "__main__":
    run_simulation()
