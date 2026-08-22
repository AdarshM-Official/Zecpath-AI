# Debugging Report – Day 57 Stabilization

## 1. Issues Found & Fixed

### A. Scoring Engine – Input Injection & Clamping
**File:** `utils/unified_scoring_engine.py`

| Issue | Fix |
|---|---|
| Scores above 1.0 (e.g., 1.5) produced hiring_fit > 100% | Added `_clamp()` helper, all inputs strictly bounded to [0.0, 1.0] |
| `None` values caused `TypeError` in arithmetic | `_clamp()` coerces `None` to `0.0` |
| Non-numeric strings (e.g., `"abc"`) caused `ValueError` | `_clamp()` catches `TypeError/ValueError` and defaults to `0.0` |
| Corrupted JSON config caused uncaught `json.JSONDecodeError` | `_load_config()` now wraps parsing in `try/except` and falls back to hardcoded defaults |

### B. Conversation Flow – Double-Submit & IndexError
**File:** `interview_ai/conversation_flow.py`

| Issue | Fix |
|---|---|
| `process_event()` accepted answers even in `CLOSING`/`TERMINATED` state, causing duplicate unified score computations | Added early-exit guard returning `{"action": "no_op"}` when state is already terminal |
| `FALLBACK` state with `current_question_index` beyond `fallback_questions` list raised `IndexError` | Index is now clamped via `min(idx, len(list)-1)` |
| `event_type == "answer"` (from the API) was silently ignored; only `"answer_received"` was handled | Both `"answer"` and `"answer_received"` now accepted in `WAITING_FOR_ANSWER` and `FOLLOW_UP` states |

### C. API – Unhandled Exceptions & Input Normalization
**File:** `api/hr_interview_api.py`

| Issue | Fix |
|---|---|
| Unhandled exceptions caused the Flask server to return an HTML error traceback instead of JSON | Wrapped all endpoints in `try/except`, returning `{"error": "..."}` with 400/500 status codes |
| Only `{"answer": {"raw_text": "..."}}` payload format was accepted; flat `{"raw_text": "..."}` was silently dropped | `process_message` now checks both payload shapes |
| `ats_score` / `screening_score` passed as strings from JSON were not cast to `float`, causing downstream type errors | Explicit `float()` cast added with `ValueError` handling |

## 2. Verification
All fixes verified via `tests/test_stabilization.py`, which purposely feeds malformed inputs, double-submits, and out-of-bounds indices to confirm graceful handling.

**All 4 stabilization tests passed.**
