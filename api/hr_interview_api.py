from flask import Flask, request, jsonify
import uuid
import sys
import os

# Add parent directory to path to allow importing our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from interview_ai.conversation_flow import InterviewConversationFlow, ConversationState
from utils.data_retention import DataRetentionManager

app = Flask(__name__)

# In-memory storage for active sessions
# Keys are session_ids, values are InterviewConversationFlow instances
SESSIONS = {}

# In-memory storage for completed reports
REPORTS = {}

retention_manager = DataRetentionManager(storage_dir="candidates")


def _error_response(code: int, message: str, details: str = None):
    resp = {"error": True, "code": code, "message": message}
    if details:
        resp["details"] = details
    return jsonify(resp), code

@app.route("/api/v1/interview/start", methods=["POST"])
def start_interview():
    try:
        data = request.get_json(silent=True) or {}

        candidate_id = data.get("candidate_id")
        role = data.get("role", "junior")
        ats_score = float(data.get("ats_score", 0.5))
        screening_score = float(data.get("screening_score", 0.5))

        if not candidate_id:
            return _error_response(400, "candidate_id is required")

        session_id = "sess_" + str(uuid.uuid4())

        flow = InterviewConversationFlow()
        flow.candidate_role = role
        flow.ats_score = ats_score
        flow.screening_score = screening_score

        response = flow.process_event("start")

        SESSIONS[session_id] = {
            "flow": flow,
            "candidate_id": candidate_id
        }

        return jsonify({
            "session_id": session_id,
            "state": flow.state,
            "message": response.get("message", "")
        }), 200

    except (ValueError, TypeError) as e:
        return _error_response(400, "Invalid input data", str(e))
    except Exception as e:
        return _error_response(500, "Internal server error", str(e))


@app.route("/api/v1/interview/<session_id>/message", methods=["POST"])
def process_message(session_id):
    try:
        if session_id not in SESSIONS:
            return _error_response(404, "Invalid session_id")

        data = request.get_json(silent=True) or {}
        # Support both flat {"raw_text": "..."} and nested {"answer": {"raw_text": "..."}}
        raw_text = data.get("raw_text") or data.get("answer", {}).get("raw_text", "")

        if not str(raw_text).strip():
            return _error_response(400, "Response text is required")

        session = SESSIONS[session_id]
        flow = session["flow"]

        if flow.state in [ConversationState.CLOSING, ConversationState.TERMINATED]:
            return _error_response(400, "Interview is already complete")

        response = flow.process_event("answer", payload=raw_text)

        if flow.state == ConversationState.CLOSING:
            REPORTS[session_id] = {
                "candidate_id": session["candidate_id"],
                "role": flow.candidate_role,
                "unified_score": flow.unified_score
            }

        return jsonify({
            "state": flow.state,
            "message": response.get("message", "")
        }), 200

    except Exception as e:
        return _error_response(500, "Internal server error", str(e))


@app.route("/api/v1/interview/<session_id>/report", methods=["GET"])
def get_report(session_id):
    if session_id in REPORTS:
        report = REPORTS[session_id]
        return jsonify({
            "candidate_id": report["candidate_id"],
            "role": report["role"],
            "hiring_fit_percent": report["unified_score"].get("hiring_fit_percent", 0),
            "breakdown": report["unified_score"].get("breakdown", {}),
            "unified_score": report["unified_score"]
        }), 200
        
    if session_id in SESSIONS:
        return _error_response(400, "Interview is still in progress.")
        
    return _error_response(404, "Report not found")


@app.route("/api/v1/candidate/<candidate_id>", methods=["DELETE"])
def delete_candidate(candidate_id):
    success = retention_manager.purge_candidate_data(candidate_id)
    # Also clean up memory structures for the demo
    keys_to_delete = []
    for sid, s in SESSIONS.items():
        if s.get("candidate_id") == candidate_id:
            keys_to_delete.append(sid)
    for k in keys_to_delete:
        del SESSIONS[k]
        
    keys_to_delete = []
    for sid, r in REPORTS.items():
        if r.get("candidate_id") == candidate_id:
            keys_to_delete.append(sid)
    for k in keys_to_delete:
        del REPORTS[k]
        
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)