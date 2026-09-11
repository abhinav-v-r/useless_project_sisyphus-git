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
        
    def check_despair(self, user_text: str) -> bool:
        """
        Analyzes the user's text for despair or acceptance of futility.
        Returns True if the compound score is <= -0.4.
        """
        scores = self.analyzer.polarity_scores(user_text)
        
        # 'compound' is a normalized, weighted composite score between -1 and +1
        return scores['compound'] <= -0.4
