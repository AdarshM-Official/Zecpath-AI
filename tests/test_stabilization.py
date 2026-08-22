"""
Stabilization test suite (Day 57).
Feeds intentionally malformed or edge-case inputs to the scoring engines
and conversation flow to verify robust error handling.
"""
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.unified_scoring_engine import UnifiedScoringEngine
from interview_ai.conversation_flow import InterviewConversationFlow, ConversationState


def test_unified_engine_bad_inputs():
    """Scores outside 0-1, None values, and string inputs must be clamped gracefully."""
    engine = UnifiedScoringEngine()

    result = engine.compute_score(
        ats=1.5,          # over-range
        screening=-0.3,   # under-range (negative)
        hr=None,          # None
        technical="abc",  # non-numeric string
        machine_test=0.7,
        candidate_id="edge_case_01",
        role="junior_developer"
    )
    fit = result["hiring_fit_percent"]
    assert 0 <= fit <= 100, f"Fit out of bounds: {fit}"
    bd = result["breakdown"]
    assert bd["ats"] == 1.0,       f"Expected clamped ats=1.0, got {bd['ats']}"
    assert bd["screening"] == 0.0, f"Expected clamped screening=0.0, got {bd['screening']}"
    assert bd["hr"] == 0.0,        f"Expected clamped hr=0.0 (None), got {bd['hr']}"
    assert bd["technical"] == 0.0, f"Expected clamped technical=0.0 (str), got {bd['technical']}"
    print("[PASS] test_unified_engine_bad_inputs")
    return result


def test_conversation_double_submit():
    """Submitting an answer after CLOSING must return a no_op, not crash."""
    flow = InterviewConversationFlow()
    flow.process_event("start")  # GREETING -> WAITING_FOR_ANSWER

    # Answer all questions
    for _ in range(len(flow.questions)):
        if flow.state in [ConversationState.CLOSING, ConversationState.TERMINATED]:
            break
        flow.process_event("answer", payload="This is my answer with enough detail.")

    assert flow.state == ConversationState.CLOSING, f"Expected CLOSING, got {flow.state}"

    # Now try to double-submit – must not crash
    double_result = flow.process_event("answer", payload="Extra answer after close")
    assert double_result["action"] == "no_op", f"Expected no_op, got {double_result['action']}"
    print("[PASS] test_conversation_double_submit")


def test_conversation_fallback_bounds():
    """Fallback state with current_question_index beyond list length must not raise IndexError."""
    flow = InterviewConversationFlow()
    flow.state = ConversationState.FALLBACK
    flow.current_question_index = 9999  # Way beyond list length

    result = flow.process_event("some_event")
    assert "message" in result, "Expected message key in fallback response"
    print("[PASS] test_conversation_fallback_bounds")


def test_unified_engine_missing_config():
    """Engine with a bad config path must fall back to defaults gracefully."""
    engine = UnifiedScoringEngine(config_path="nonexistent_path/config.json")
    result = engine.compute_score(ats=0.8, screening=0.7, hr=0.75)
    assert result["hiring_fit_percent"] > 0, "Expected non-zero score with defaults"
    print("[PASS] test_unified_engine_missing_config")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Day 57 Stabilization Tests")
    print("=" * 60)

    r = test_unified_engine_bad_inputs()
    print(f"  -> Hiring fit from bad inputs: {r['hiring_fit_percent']}%")
    test_conversation_double_submit()
    test_conversation_fallback_bounds()
    test_unified_engine_missing_config()

    print("\nAll stabilization tests passed.")
