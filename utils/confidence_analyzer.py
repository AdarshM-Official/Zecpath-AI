import os
import json
import re
from collections import Counter
from typing import List, Dict, Any

# Sentiment – VADER (NLTK)
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except ImportError:
    # Fallback: neutral sentiment if nltk not installed
    SentimentIntensityAnalyzer = None

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "confidence_config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        "weights": {
            "hesitation": 0.25,
            "sentiment": 0.30,
            "contradiction": 0.20,
            "stress": 0.25
        },
        "hesitation": {
            "long_pause_ms": 2000,
            "repeat_word_threshold": 2,
            "uncertainty_phrases": ["I think", "maybe", "perhaps", "not sure", "I'm not certain"]
        },
        "stress": {
            "excess_punct": ["!", "..."],
            "caps_threshold": 0.6,
            "filler_word_ratio": 0.1
        }
    }

WEIGHTS = CONFIG.get("weights", {})
HESITATION_CFG = CONFIG.get("hesitation", {})
STRESS_CFG = CONFIG.get("stress", {})

# Helper to load filler words from existing communication config if present
FILLER_SET = set()
comm_cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "communication_config.json")
if os.path.exists(comm_cfg_path):
    with open(comm_cfg_path, "r", encoding="utf-8") as f:
        comm_cfg = json.load(f)
    FILLER_SET.update(word.lower() for word in comm_cfg.get("filler_words", []))

# Sentiment analyzer (initialize lazily, optional dependency)
_SENTIMENT_ANALYZER = None
_VADER_AVAILABLE = None  # None = not yet checked

def _get_sentiment_analyzer():
    global _SENTIMENT_ANALYZER, _VADER_AVAILABLE
    if _VADER_AVAILABLE is False:
        return None  # already determined unavailable
    if _SENTIMENT_ANALYZER is None:
        if SentimentIntensityAnalyzer is None:
            _VADER_AVAILABLE = False
            return None
        try:
            _SENTIMENT_ANALYZER = SentimentIntensityAnalyzer()
            _VADER_AVAILABLE = True
        except Exception:
            _VADER_AVAILABLE = False
            return None
    return _SENTIMENT_ANALYZER

# Pre-compile Regex Patterns (Day 60 Optimization)
_WORD_REGEX = re.compile(r"\b\w+\b")
_NEGATION_REGEX = re.compile(r"\b(not|no|never|none)\b")

def detect_hesitation(text: str, timestamps: List[int] = None) -> Dict[str, int]:
    """Detect hesitation cues.
    Returns a dict with counts for long pauses, repeated words, and uncertainty phrases.
    """
    long_pauses = 0
    if timestamps and len(timestamps) > 1:
        # timestamps are assumed cumulative ms for each token
        diffs = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
        long_pauses = sum(1 for d in diffs if d > HESITATION_CFG.get("long_pause_ms", 2000))
    # repeated words (consecutive) using pre-compiled regex
    tokens = _WORD_REGEX.findall(text.lower())
    repeated = sum(1 for i in range(1, len(tokens)) if tokens[i] == tokens[i-1])
    # uncertainty phrases
    uncertainty = 0
    lower = text.lower()
    for phrase in HESITATION_CFG.get("uncertainty_phrases", []):
        if phrase.lower() in lower:
            uncertainty += 1
    return {"long_pauses": long_pauses, "repeated_words": repeated, "uncertainty_phrases": uncertainty}

def sentiment_score(text: str) -> float:
    """Return normalized sentiment polarity (0-1). Returns 0.5 (neutral) when VADER is unavailable."""
    analyzer = _get_sentiment_analyzer()
    if analyzer is None:
        return 0.5  # neutral fallback — no crash
    polarity = analyzer.polarity_scores(text)["compound"]  # -1 to 1
    return (polarity + 1) / 2

def detect_contradiction(text: str, history: List[Dict[str, Any]]) -> bool:
    """Very simple contradiction check: if a negation word appears and the same keyword was affirmed earlier.
    This is a placeholder; can be replaced with an entailment model later.
    """
    if not history:
        return False
    # extract keywords from current text using pre-compiled regex
    current_words = set(_WORD_REGEX.findall(text.lower()))
    
    # Pre-check negation in current text to avoid unnecessary history loops
    if not _NEGATION_REGEX.search(text.lower()):
        return False

    for entry in history:
        raw = entry.get("answer", "")
        # answer may be a nested dict {"raw_text": "..."} or a plain string
        if isinstance(raw, dict):
            raw = raw.get("raw_text", "")
        prev_words = set(_WORD_REGEX.findall(str(raw).lower()))
        if current_words & prev_words:
            return True
    return False

def stress_indicators(text: str) -> Dict[str, float]:
    """Detect stress cues and return normalized ratios."""
    # excess punctuation
    excess = sum(text.count(p) for p in STRESS_CFG.get("excess_punct", []))
    # caps ratio
    caps_chars = sum(1 for c in text if c.isupper())
    total_alpha = sum(1 for c in text if c.isalpha())
    caps_ratio = caps_chars / total_alpha if total_alpha else 0.0
    # filler word ratio
    tokens = _WORD_REGEX.findall(text.lower())
    filler_cnt = sum(1 for t in tokens if t in FILLER_SET)
    filler_ratio = filler_cnt / len(tokens) if tokens else 0.0
    return {"excess_punct": min(excess / 5, 1.0), "caps_ratio": caps_ratio, "filler_ratio": filler_ratio}

def compute_behavioral_score(metrics: Dict[str, Any]) -> float:
    """Combine sub‑metrics using configured weights and output a 0‑100 score.
    Expected keys in metrics: hesitation (dict), sentiment (float), contradiction (bool), stress (dict).
    """
    # Convert hesitation dict to a single score: lower counts -> higher score
    hes = metrics.get("hesitation", {})
    hes_score = 1.0 - min((hes.get("long_pauses", 0) + hes.get("repeated_words", 0) + hes.get("uncertainty_phrases", 0)) / 5.0, 1.0)
    # Sentiment already 0‑1
    sent_score = metrics.get("sentiment", 0.5)
    # Contradiction: no contradiction = 1, contradiction = 0
    contr_score = 0.0 if metrics.get("contradiction", False) else 1.0
    # Stress: lower ratios -> higher score
    stress = metrics.get("stress", {})
    stress_score = 1.0 - min((stress.get("excess_punct", 0) + stress.get("caps_ratio", 0) + stress.get("filler_ratio", 0)) / 3.0, 1.0)
    # Weighted sum
    total = (
        WEIGHTS.get("hesitation", 0) * hes_score +
        WEIGHTS.get("sentiment", 0) * sent_score +
        WEIGHTS.get("contradiction", 0) * contr_score +
        WEIGHTS.get("stress", 0) * stress_score
    )
    weight_sum = sum(WEIGHTS.values()) or 1.0
    normalized = total / weight_sum
    return round(normalized * 100, 2)

def analyze_response(text: str, timestamps: List[int] = None, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run the full confidence analysis pipeline and return a dict with breakdown and final score."""
    hes = detect_hesitation(text, timestamps)
    sent = sentiment_score(text)
    contr = detect_contradiction(text, history or [])
    stress = stress_indicators(text)
    breakdown = {
        "hesitation": hes,
        "sentiment": sent,
        "contradiction": contr,
        "stress": stress
    }
    final = compute_behavioral_score({
        "hesitation": hes,
        "sentiment": sent,
        "contradiction": contr,
        "stress": stress
    })
    return {"final_score": final, "breakdown": breakdown}

__all__ = [
    "detect_hesitation",
    "sentiment_score",
    "detect_contradiction",
    "stress_indicators",
    "compute_behavioral_score",
    "analyze_response",
]
