import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure vader_lexicon is downloaded silently
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

class SentimentGate:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        
    def check_despair(self, user_text: str) -> tuple[bool, float]:
        """
        Analyzes the user's text for despair or acceptance of futility.
        Returns (is_despair, compound_score).
        """
        scores = self.analyzer.polarity_scores(user_text)
        
        # 'compound' is a normalized, weighted composite score between -1 and +1
        score = scores['compound']
        return score <= -0.4, score
