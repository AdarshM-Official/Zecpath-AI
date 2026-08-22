import json
import os

class FollowUpEngine:
    """Engine that provides adaptive follow‑up prompts based on candidate answers.

    It loads a JSON configuration (config/followup_config.json) describing per‑question
    follow‑up templates and global settings such as confidence thresholds and maximum
    follow‑up depth.
    """

    def __init__(self, config_path: str = "config/followup_config.json"):
        self.config_path = config_path
        self.cfg = self._load_config()
        # Ensure optimal threshold based on Day 54 optimization (was 0.7)
        self.cfg["confidence_threshold"] = self.cfg.get("confidence_threshold", 0.6)
        self.asked_questions = set()
        self.follow_up_counts = {}
        self.max_per_question = self.cfg.get('max_follow_up_per_question', 2)

    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # Fallback to minimal defaults if the file is missing
            return {
                "confidence_threshold": 0.7,
                "max_follow_up_per_question": 2,
                "questions": {}
            }
        self.asked_questions = set()
        self.follow_up_counts = {}
        self.max_per_question = self.cfg.get('max_follow_up_per_question', 2)

    def _track(self, q_id: str):
        """Increment follow‑up count for a question and record that we have asked it."""
        self.asked_questions.add(q_id)
        self.follow_up_counts[q_id] = self.follow_up_counts.get(q_id, 0) + 1

    def _can_ask(self, q_id: str) -> bool:
        return self.follow_up_counts.get(q_id, 0) < self.max_per_question

    def _template(self, q_id: str, kind: str) -> str:
        """Return the template for a given question id and kind (clarification, deepening, example).
        If not defined, return a generic prompt.
        """
        question_cfg = self.cfg.get('questions', {}).get(q_id, {})
        return question_cfg.get(kind, "Could you provide more detail?")

    def detect_incomplete(self, answer_obj: dict) -> bool:
        """Detect incomplete answers.
        Simple heuristic: missing_information flag or very short raw text (<3 words instead of 5).
        """
        quality = answer_obj.get('quality', {})
        if quality.get('missing_information', False):
            return True
        raw = answer_obj.get('answer', {}).get('raw_text', '')
        word_count = len(raw.split())
        return word_count > 0 and word_count < 3

    def detect_vague(self, answer_obj: dict) -> bool:
        """Detect vague answers.
        Heuristic: 'vague' flag or moderately short text (3‑6 words instead of 5-8).
        """
        quality = answer_obj.get('quality', {})
        if quality.get('vague', False):
            return True
        raw = answer_obj.get('answer', {}).get('raw_text', '')
        word_count = len(raw.split())
        return 3 <= word_count <= 6

    def select_clarification(self, q_id: str) -> str:
        if not self._can_ask(q_id):
            return None
        self._track(q_id)
        return self._template(q_id, 'clarification')

    def select_deepening(self, q_id: str) -> str:
        if not self._can_ask(q_id):
            return None
        self._track(q_id)
        return self._template(q_id, 'deepening')

    def select_example(self, q_id: str) -> str:
        if not self._can_ask(q_id):
            return None
        self._track(q_id)
        return self._template(q_id, 'example')
