from typing import Dict, Any
from scoring.confidence_analysis import ConfidenceAnalyzer
from scoring.sentiment_scoring import SentimentScorer

class BehavioralReporter:
    def __init__(self):
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.sentiment_scorer = SentimentScorer()

    def measure_pace_and_length(self, text: str, duration_seconds: float) -> Dict[str, Any]:
        """Measure response length and pace (WPM)."""
        words = text.split()
        word_count = len(words)
        pace_wpm = (word_count / duration_seconds) * 60 if duration_seconds > 0 else 0
        
        pace_evaluation = "Optimal"
        if pace_wpm < 100:
            pace_evaluation = "Too Slow"
        elif pace_wpm > 160:
            pace_evaluation = "Too Fast"
            
        return {
            "word_count": word_count,
            "duration_seconds": duration_seconds,
            "pace_wpm": round(pace_wpm, 2),
            "pace_evaluation": pace_evaluation
        }

    def determine_communication_strength(self, confidence_score: float, pace_wpm: float, sentiment_score: float) -> str:
        """Create communication strength indicators."""
        if confidence_score > 0.8 and 100 <= pace_wpm <= 160 and sentiment_score >= 0:
            return "Strong"
        elif confidence_score < 0.5 or pace_wpm < 80 or pace_wpm > 180:
            return "Needs Improvement"
        else:
            return "Average"

    def generate_report(self, text: str, duration_seconds: float) -> Dict[str, Any]:
        """Generate behavioral indicators report."""
        # 1. Detect hesitation patterns & uncertainty (Confidence)
        hesitation_data = self.confidence_analyzer.detect_hesitation(text)
        uncertainty_data = self.confidence_analyzer.detect_uncertainty(text)
        confidence_score = self.confidence_analyzer.calculate_confidence_score(text)
        
        # 2. Measure response length and pace
        pace_data = self.measure_pace_and_length(text, duration_seconds)
        
        # 3. Identify positive/negative sentiment
        sentiment_data = self.sentiment_scorer.analyze_sentiment(text)
        
        # 4. Create communication strength indicators
        strength_indicator = self.determine_communication_strength(
            confidence_score, 
            pace_data["pace_wpm"], 
            sentiment_data["score"]
        )
        
        report = {
            "overall_communication_strength": strength_indicator,
            "confidence_score": confidence_score,
            "sentiment_label": sentiment_data["label"],
            "detailed_metrics": {
                "hesitation": hesitation_data,
                "uncertainty_and_contradictions": uncertainty_data,
                "pace_and_length": pace_data,
                "sentiment": sentiment_data
            }
        }
        return report
