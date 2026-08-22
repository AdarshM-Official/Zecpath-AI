import json
import sys
import os
import time

# Ensure we can import from utils and interview_ai
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from interview_ai.conversation_flow import InterviewConversationFlow, ConversationState

def run_simulation(candidate_profile):
    print("="*60)
    print(f"STARTING DEMO INTERVIEW FOR: {candidate_profile['name']} ({candidate_profile['role']})")
    print("="*60)
    
    # Initialize the flow
    flow = InterviewConversationFlow()
    # Inject initial scores from previous rounds
    flow.ats_score = candidate_profile.get("ats_score", 0.5)
    flow.screening_score = candidate_profile.get("screening_score", 0.5)
    flow.candidate_role = candidate_profile.get("role", "junior")
    
    answers = candidate_profile["answers"].copy()
    
    # Start interview
    response = flow.process_event("start")
    print(f"\n[AI]: {response['message']}")
    
    # Loop through the conversation state machine
    while flow.state not in [ConversationState.CLOSING, ConversationState.TERMINATED]:
        if not answers:
            print("\n[SYSTEM]: Candidate ran out of answers in the demo script!")
            break
            
        candidate_text = answers.pop(0)
        time.sleep(1) # Slight pause for effect
        print(f"\n[CANDIDATE]: {candidate_text}")
        
        # Send the answer to the AI
        response = flow.process_event("answer", payload=candidate_text)
        print(f"\n[AI]: {response['message']}")
        
    if flow.unified_score:
        print("\n" + "="*60)
        print("FINAL HIRING RECOMMENDATION")
        print("="*60)
        fit = flow.unified_score.get("hiring_fit_percent", 0)
        print(f"Candidate: {candidate_profile['name']}")
        print(f"Role: {candidate_profile['role']}")
        print(f"Overall Hiring Fit: {fit}%")
        
        if fit >= 80:
            print("Recommendation: STRONG HIRE - Proceed to offer.")
        elif fit >= 65:
            print("Recommendation: HIRE - Suitable fit.")
        else:
            print("Recommendation: REJECT - Does not meet thresholds.")
            
        print("\n--- Detailed Scoring Object ---")
        print(json.dumps(flow.unified_score, indent=2))
        
    print("\n[DEMO COMPLETE]\n")

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "samples", "demo_candidates.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for candidate in data.get("candidates", []):
        run_simulation(candidate)
        time.sleep(2)
