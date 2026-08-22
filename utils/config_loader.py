import json
import os
import functools

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'screening_config.json'))

@functools.lru_cache(maxsize=32)
def load_config(config_path: str = CONFIG_PATH):
    """Load JSON configuration for screening thresholds and settings. Cached in-memory."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        # Fallback to defaults if config missing
        return {
            "overall_score_thresholds": {"strong": 80, "weak": 60},
            "question_score_thresholds": {"excellent": 85, "poor": 50},
            "max_retries": 2,
            "use_ml_intent": False
        }

