import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interview_ai.conversation_flow import InterviewConversationFlow

def main():
    flow = InterviewConversationFlow()
    
    # Simulate a realistic conversation
    events = [
        {"type": "start", "payload": ""},                                                        # Triggers greeting
        {"type": "silence", "payload": ""},                                                      # Handles silence
        {"type": "confusion", "payload": ""},                                                    # Handles confusion (retry 2)
        {"type": "confusion", "payload": ""},                                                    # Max retries hit -> fallback
        {"type": "answer_received", "payload": "I am great at python and django."},              # Good answer from fallback
        {"type": "answer_received", "payload": "Yes."},                                          # Short answer -> follow up
        {"type": "answer_received", "payload": "I know Python, Django, React, and SQL well."},   # Proper answer after follow-up
        {"type": "repeated_answer", "payload": ""},                                              # Repeated answer handled
        {"type": "answer_received", "payload": "I built a microservices platform on AWS."},      # Final answer -> closing
    ]

    print("=" * 60)
    print("    AI Conversation Flow Simulation")
    print("=" * 60)

    for i, event in enumerate(events, 1):
        print(f"\n--- Step {i} ---")
        print(f"[Event]: {event['type']} | Payload: '{event['payload']}'")
        response = flow.process_event(event["type"], event["payload"])
        
        # If the state machine transitions internally (fallback/follow-up),
        # auto-trigger the next state's speech immediately.
        while response["action"] in ["transition", "trigger"]:
            print(f"  [State Shift]: {response['message']}")
            response = flow.process_event("auto_continue")
            
        print(f"  [AI -> {response['state']}]: {response['action'].upper()}")
        if response["message"]:
            print(f"  [AI Says]: \"{response['message']}\"")

    print("\n" + "=" * 60)
    print(f"  Final State: {flow.state}")
    print("=" * 60)

if __name__ == "__main__":
    main()
