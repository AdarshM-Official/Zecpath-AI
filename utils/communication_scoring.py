import json
import os
import re
from typing import Dict, List, Any

# Optional spacy import
try:
    import spacy
    from spacy.lang.en import English
    from spacy.tokens import Doc
    _SPACY_AVAILABLE = True
except ImportError:
    _SPACY_AVAILABLE = False
    spacy = None
    English = None
    Doc = Any

# Load spaCy model lazily
_nlp = None

def get_nlp() -> Any:
    global _nlp
    if not _SPACY_AVAILABLE:
        return None
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not installed, fall back to blank English pipeline
            _nlp = English()
            _nlp.add_pipe("sentencizer")
    return _nlp


# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "communication_config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        "weights": {
            "fluency": 0.15,
            "grammar": 0.20,
            "vocabulary": 0.15,
            "clarity": 0.20,
            "filler": 0.10,
            "structure": 0.20,
        },
        "filler_words": ["um", "uh", "like", "you know", "actually", "basically"],
        "readability": {"target_score": 70},
    }

FILLER_SET = set(word.lower() for word in CONFIG.get("filler_words", []))
WEIGHTS = CONFIG.get("weights", {})

# Helper utilities
def _sentences(text: str) -> List[Any]:
    nlp = get_nlp()
    if nlp is None:
        return [s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    return list(nlp(text).sents)

def _tokenize(text: str) -> List[str]:
    nlp = get_nlp()
    if nlp is None:
        return re.findall(r"\b\w+\b", text)
    return [t.text for t in nlp(text)]

# Metric implementations
def measure_fluency(text: str) -> float:
    """Estimate fluency via average sentence length and transition word count."""
    nlp = get_nlp()
    if nlp is None:
        return 0.5 # Neutral fallback
    doc = nlp(text)
    sentences = list(doc.sents)
    if not sentences:
        return 0.0
    avg_len = sum(len(sent) for sent in sentences) / len(sentences)
    transitions = {"however", "therefore", "moreover", "thus", "consequently"}
    transition_hits = sum(1 for token in doc if token.text.lower() in transitions)
    score = (avg_len / 20) * 0.7 + (transition_hits / len(doc)) * 0.3
    return min(max(score, 0.0), 1.0)

def measure_grammar(text: str) -> float:
    """Very light grammar check."""
    nlp = get_nlp()
    if nlp is None:
        return 0.5 # Neutral fallback
    doc = nlp(text)
    if not doc:
        return 0.0
    grammatical = sum(1 for token in doc if token.pos_ not in {"PUNCT", "SPACE"})
    score = grammatical / len(doc)
    return min(max(score, 0.0), 1.0)

def measure_vocabulary(text: str) -> float:
    """Lexical diversity: type-token ratio adjusted for rare word frequency."""
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    types = set(tok.lower() for tok in tokens)
    ttr = len(types) / len(tokens)
    rare = sum(1 for tok in tokens if len(tok) > 7)
    score = ttr * 0.7 + (rare / len(tokens)) * 0.3
    return min(max(score, 0.0), 1.0)

def measure_clarity(text: str) -> float:
    """Readability via Flesch-Kincaid grade level and active-voice proportion."""
    nlp = get_nlp()
    if nlp is None:
        return 0.5 # Neutral fallback
    doc = nlp(text)
    sentences = list(doc.sents)
    if not sentences:
        return 0.0
    words = [token.text for token in doc if token.is_alpha]
    syllables = sum(_count_syllables(word) for word in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = syllables / max(len(words), 1)
    fk_grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    readability_score = max(0.0, 1.0 - (fk_grade - 5) / 10)
    passive_hits = sum(1 for token in doc if token.lemma_ == "be" and token.tag_ in {"VBN", "VBD"})
    passive_ratio = passive_hits / max(len(doc), 1)
    active_score = 1.0 - passive_ratio
    final = 0.7 * readability_score + 0.3 * active_score
    return min(max(final, 0.0), 1.0)

def _count_syllables(word: str) -> int:
    # Very naive syllable count based on vowel groups
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)

def detect_filler_words(text: str) -> int:
    tokens = _tokenize(text)
    return sum(1 for tok in tokens if tok.lower() in FILLER_SET)

def measure_structure(text: str) -> float:
    """Heuristic detection of intro/body/conclusion markers.
    Returns 0‑1.
    """
    lower = text.lower()
    markers = 0
    if any(kw in lower for kw in ["introduction", "i would like to start", "first"]):
        markers += 1
    if any(kw in lower for kw in ["in conclusion", "to sum up", "overall"]):
        markers += 1
    if any(kw in lower for kw in ["therefore", "as a result", "so"]):
        markers += 1
    return markers / 3.0

def compute_communication_score(metrics: Dict[str, float]) -> float:
    """Combine sub‑metrics using configured weights and normalize to 0‑100.
    Missing metrics are treated as 0.
    """
    total = 0.0
    weight_sum = 0.0
    for key, weight in WEIGHTS.items():
        value = metrics.get(key, 0.0)
        total += value * weight
        weight_sum += weight
    if weight_sum == 0:
        return 0.0
    normalized = total / weight_sum
    return round(normalized * 100, 2)

def score_text(text: str) -> Dict[str, any]:
    """Run all metrics and return a dictionary with the final score and a breakdown.
    Example output:
    {
        "final_score": 78.5,
        "breakdown": {
            "fluency": 0.82,
            "grammar": 0.91,
            ...
        }
    }
    """
    fluency = measure_fluency(text)
    grammar = measure_grammar(text)
    vocab = measure_vocabulary(text)
    clarity = measure_clarity(text)
    filler = detect_filler_words(text)
    # Convert filler count to a penalty (more filler = lower score)
    filler_score = 1.0 - min(filler / 5, 1.0)
    structure = measure_structure(text)

    breakdown = {
        "fluency": fluency,
        "grammar": grammar,
        "vocabulary": vocab,
        "clarity": clarity,
        "filler": filler_score,
        "structure": structure,
    }
    final = compute_communication_score(breakdown)
    return {"final_score": final, "breakdown": breakdown}

# Exported symbols
__all__ = [
    "measure_fluency",
    "measure_grammar",
    "measure_vocabulary",
    "measure_clarity",
    "detect_filler_words",
    "measure_structure",
    "compute_communication_score",
    "score_text",
]
