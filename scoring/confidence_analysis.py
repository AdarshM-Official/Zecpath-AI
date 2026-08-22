import re
from typing import Dict, Any, List

class ConfidenceAnalyzer:
    def __init__(self):
        # Hesitation and uncertainty markers
        self.hesitation_words = ['uh', 'um', 'like', 'you know', 'i mean', 'well', 'ah', 'sort of', 'kind of']
        self.uncertainty_words = ['maybe', 'probably', 'perhaps', 'i think', 'not sure', 'possibly', 'might', 'could', 'guess', 'somewhat']
        self.contradiction_words = ['but', 'however', 'although', 'even though', 'on the other hand', 'despite', 'yet']

    def detect_hesitation(self, text: str) -> Dict[str, Any]:
        """Detect hesitation patterns."""
        text_lower = text.lower()
        hesitations = []
        for word in self.hesitation_words:
            matches = re.findall(r'\b' + re.escape(word) + r'\b', text_lower)
            hesitations.extend(matches)
        
        ellipses_count = len(re.findall(r'\.\.\.', text))
        total_hesitations = len(hesitations) + ellipses_count
        
        return {
            "count": total_hesitations,
            "markers": list(set(hesitations)),
            "ellipses": ellipses_count
        }

    def detect_uncertainty(self, text: str) -> Dict[str, Any]:
        """Detect uncertainty and contradictions."""
        text_lower = text.lower()
        uncertainties = []
        for word in self.uncertainty_words:
            matches = re.findall(r'\b' + re.escape(word) + r'\b', text_lower)
            uncertainties.extend(matches)
            
        contradictions = []
        for word in self.contradiction_words:
            matches = re.findall(r'\b' + re.escape(word) + r'\b', text_lower)
            contradictions.extend(matches)
            
        return {
            "uncertainty_count": len(uncertainties),
            "contradiction_count": len(contradictions),
            "uncertainty_markers": list(set(uncertainties)),
            "contradiction_markers": list(set(contradictions))
        }

    def calculate_confidence_score(self, text: str) -> float:
        """Calculate overall confidence logic score."""
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
            
        hesitation_data = self.detect_hesitation(text)
        uncertainty_data = self.detect_uncertainty(text)
        
        hesitation_ratio = hesitation_data["count"] / word_count
        uncertainty_ratio = uncertainty_data["uncertainty_count"] / word_count
        
        # Base confidence 1.0, penalties applied based on occurrences per word
        hesitation_penalty = min(0.4, hesitation_ratio * 4) 
        uncertainty_penalty = min(0.4, uncertainty_ratio * 3)
        
        score = max(0.0, 1.0 - hesitation_penalty - uncertainty_penalty)
        return round(score, 2)
