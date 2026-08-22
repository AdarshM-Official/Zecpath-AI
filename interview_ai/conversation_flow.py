import json
from typing import Dict, Any, List
from utils.config_loader import load_config
from utils.followup_engine import FollowUpEngine
from utils.hr_scoring_engine import HRScoringEngine
from utils.communication_scoring import score_text
from utils.confidence_analyzer import analyze_response
from utils.unified_scoring_engine import UnifiedScoringEngine

class ConversationState:
    GREETING = "GREETING"
    ASKING_QUESTION = "ASKING_QUESTION"
    WAITING_FOR_ANSWER = "WAITING_FOR_ANSWER"
    ANALYZING_ANSWER = "ANALYZING_ANSWER"
    FOLLOW_UP = "FOLLOW_UP"
    FALLBACK = "FALLBACK"
    CLOSING = "CLOSING"
    TERMINATED = "TERMINATED"

class InterviewConversationFlow:
    def __init__(self):
        self.state = ConversationState.GREETING
        self.follow_up_engine = FollowUpEngine()
        self.hr_engine = HRScoringEngine()
        self.unified_engine = UnifiedScoringEngine()
        self.answer_history = []
        self.current_question_index = 0
        self.questions = [
            "Could you briefly introduce yourself and your background?",
            "What are your primary technical skills?",
            "Can you tell me about your most challenging project?"
        ]
        
        # Placeholders for screening and ats scores which would come from earlier stages
        self.screening_score = 0.85
        self.ats_score = 0.90
        self.candidate_role = "senior"
        self.unified_score = None
        self.retry_count = 0
        self.max_retries = load_config().get('max_retries', 2)  # Load from config
        self.fallback_questions = [
            "Let's simplify. What is your strongest skill?",
            "Could you just share the name of your last company and role?",
            "Take your time. Just tell me what you enjoy working on the most."
        ]
        # Track follow‑up attempts
        self.follow_up_counts = {}

    def process_event(self, event_type: str, payload: str = "") -> Dict[str, Any]:
        """State machine processor for call events."""
        response = {"state": self.state, "action": "", "message": ""}

        # Guard: if already closed/terminated, do not process further
        if self.state in [ConversationState.CLOSING, ConversationState.TERMINATED]:
            return {
                "state": self.state,
                "action": "no_op",
                "message": "Interview is already complete."
            }

        if self.state == ConversationState.GREETING:
            response["state"] = ConversationState.ASKING_QUESTION
            response["action"] = "speak"
            response["message"] = "Hello! Thank you for joining. Let's get started. " + self.questions[0]
            self.state = ConversationState.WAITING_FOR_ANSWER

        elif self.state == ConversationState.WAITING_FOR_ANSWER:
            if event_type == "silence":
                response = self._handle_silence()
            elif event_type == "confusion":
                response = self._handle_confusion()
            elif event_type == "repeated_answer":
                response = self._handle_repeated_answer()
            elif event_type in ("answer_received", "answer"):
                self.state = ConversationState.ANALYZING_ANSWER
                response = self._analyze_answer(payload)
            else:
                response["state"] = self.state
                response["action"] = "wait"
                response["message"] = ""

        elif self.state == ConversationState.FOLLOW_UP:
            # Any incoming answer after a follow-up is re-analyzed
            if event_type in ("answer_received", "answer"):
                self.state = ConversationState.ANALYZING_ANSWER
                response = self._analyze_answer(payload)
            else:
                response["state"] = ConversationState.WAITING_FOR_ANSWER
                response["action"] = "speak"
                response["message"] = "Could you elaborate a bit more on that?"
                self.state = ConversationState.WAITING_FOR_ANSWER

        elif self.state == ConversationState.FALLBACK:
            response["state"] = ConversationState.WAITING_FOR_ANSWER
            response["action"] = "speak"
            # Clamp index to avoid IndexError on fallback questions list
            idx = min(self.current_question_index, len(self.fallback_questions) - 1)
            response["message"] = self.fallback_questions[idx]
            self.state = ConversationState.WAITING_FOR_ANSWER

        return response


    def _handle_silence(self) -> Dict[str, Any]:
        self.retry_count += 1
        if self.retry_count > self.max_retries:
            return self._polite_failure("I'm having trouble hearing you. Let's try again later or switch to a text chat.")
        return {
            "state": ConversationState.WAITING_FOR_ANSWER,
            "action": "speak",
            "message": "I didn't quite catch that. Are you still there? Take your time."
        }

    def _handle_confusion(self) -> Dict[str, Any]:
        self.retry_count += 1
        if self.retry_count > self.max_retries:
            self.state = ConversationState.FALLBACK
            return {"state": ConversationState.FALLBACK, "action": "transition", "message": ""}
            
        return {
            "state": ConversationState.WAITING_FOR_ANSWER,
            "action": "speak",
            "message": "Let me rephrase the question for you. " + self.questions[self.current_question_index]
        }

    def _handle_repeated_answer(self) -> Dict[str, Any]:
        self.retry_count += 1
        if self.retry_count > self.max_retries:
            return self._polite_failure("It seems we are stuck in a loop. Let's move on to the next topic.")
            
        return {
            "state": ConversationState.WAITING_FOR_ANSWER,
            "action": "speak",
            "message": "I think you mentioned that already. Could you provide a different example or detail?"
        }

    def _analyze_answer(self, payload: Any) -> Dict[str, Any]:
        # Reset retry counter
        self.retry_count = 0
        
        # Normalize payload to an answer dict
        if isinstance(payload, dict):
            answer_obj = payload
        else:
            answer_obj = {"answer": {"raw_text": str(payload)}, "quality": {}}
            
        # Store answer for history
        self.answer_history.append(answer_obj)
        
        # Compute sub‑metrics
        comm_res = score_text(answer_obj.get('answer', {}).get('raw_text', ''))
        comm_score = comm_res.get('final_score', 0) / 100.0
        conf_res = analyze_response(answer_obj.get('answer', {}).get('raw_text', ''), history=self.answer_history)
        conf_score = conf_res.get('final_score', 0) / 100.0
        relevance_score = self.hr_engine.compute_relevance(answer_obj)
        consistency_score = self.hr_engine.compute_consistency(answer_obj.get('answer', {}).get('raw_text', ''), self.answer_history)
        
        metrics = {
            "relevance": relevance_score,
            "communication": comm_score,
            "confidence": conf_score,
            "consistency": consistency_score
        }
        report = self.hr_engine.generate_report("candidate_001", metrics, interview_length=len(self.answer_history))
        print("\n--- HR Scoring Engine Report ---")
        print(json.dumps(report, indent=2))
        
        # Prepare for follow‑up logic
        q_id = f"Q{self.current_question_index+1:03d}"  # synthetic question id
        
        # Adaptive follow‑up logic
        if self.follow_up_engine.detect_incomplete(answer_obj):
            follow_up = self.follow_up_engine.select_clarification(q_id)
            if follow_up:
                self.state = ConversationState.FOLLOW_UP
                return {"state": ConversationState.FOLLOW_UP, "action": "speak", "message": follow_up}
        elif self.follow_up_engine.detect_vague(answer_obj):
            follow_up = self.follow_up_engine.select_deepening(q_id)
            if follow_up:
                self.state = ConversationState.FOLLOW_UP
                return {"state": ConversationState.FOLLOW_UP, "action": "speak", "message": follow_up}
        else:
            # Confidence‑based adaptation (fallback to example prompt)
            confidence = answer_obj.get('intent', {}).get('confidence', 1.0)
            if confidence < self.follow_up_engine.cfg.get('confidence_threshold', 0.7):
                follow_up = self.follow_up_engine.select_example(q_id)
                if follow_up:
                    self.state = ConversationState.FOLLOW_UP
                    return {"state": ConversationState.FOLLOW_UP, "action": "speak", "message": follow_up}
                    
        # No follow‑up needed – proceed to next question
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            self.state = ConversationState.CLOSING
            
            # Generate the unified score when closing
            self.unified_score = self.unified_engine.compute_score(
                ats=self.ats_score,
                screening=self.screening_score,
                hr=report.get("final_score", 0) / 100.0,  # Normalize to 0-1 for unified engine
                role=self.candidate_role
            )
            print("\n--- FINAL UNIFIED SCORE ---")
            print(json.dumps(self.unified_score, indent=2))
            
            return {
                "state": ConversationState.CLOSING,
                "action": "speak",
                "message": "That covers all my questions. Thank you for your time!"
            }
            
        self.state = ConversationState.WAITING_FOR_ANSWER
        return {
            "state": ConversationState.WAITING_FOR_ANSWER,
            "action": "speak",
            "message": "Great. Next question: " + self.questions[self.current_question_index]
        }
        
    def _polite_failure(self, reason: str) -> Dict[str, Any]:
        self.state = ConversationState.TERMINATED
        return {
            "state": ConversationState.TERMINATED,
            "action": "end_call",
            "message": reason
        }

