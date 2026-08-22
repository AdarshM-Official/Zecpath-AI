import re
from typing import Dict, Any, List

class SentimentScorer:
    def __init__(self):
        # Basic lexicons for sentiment scoring
        self.positive_words = {
            'great': 1.0, 'excellent': 1.0, 'good': 0.5, 'love': 1.0, 
            'amazing': 1.0, 'happy': 0.8, 'confident': 0.8, 'success': 1.0, 
            'achieve': 0.8, 'strong': 0.7, 'passionate': 0.9, 'excited': 0.9
        }
        self.negative_words = {
            'bad': -1.0, 'poor': -1.0, 'terrible': -1.0, 'hate': -1.0, 
            'fail': -1.0, 'worried': -0.8, 'nervous': -0.7, 'weak': -0.7, 
            'difficult': -0.5, 'struggle': -0.6, 'anxious': -0.8, 'confused': -0.6
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Identify positive/negative sentiment from text.
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        pos_score = 0.0
        neg_score = 0.0
        pos_markers = []
        neg_markers = []
        
        for word in words:
            if word in self.positive_words:
                pos_score += self.positive_words[word]
                pos_markers.append(word)
            elif word in self.negative_words:
                neg_score += abs(self.negative_words[word])
                neg_markers.append(word)
                
        total_score = pos_score - neg_score
        
        # Normalize score between -1 and 1 approximately
        intensity = pos_score + neg_score
        normalized_score = total_score / intensity if intensity > 0 else 0.0
        
        sentiment_label = "neutral"
        if normalized_score > 0.2:
            sentiment_label = "positive"
        elif normalized_score < -0.2:
            sentiment_label = "negative"
            
        return {
            "score": normalized_score,
            "label": sentiment_label,
            "positive_markers": pos_markers,
            "negative_markers": neg_markers,
            "intensity": intensity
        }
