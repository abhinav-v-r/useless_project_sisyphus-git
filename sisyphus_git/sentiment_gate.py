import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure vader_lexicon is downloaded silently
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Words that indicate submission, begging, and humility — Sisyphus accepts these
SUBMISSION_WORDS = {
    "please", "sorry", "apologize", "apologies", "forgive", "beg", "begging",
    "mercy", "helpless", "hopeless", "meaningless", "futile", "pointless",
    "surrender", "give up", "worthless", "useless", "broken", "defeated",
    "exhausted", "tired", "lost", "desperate", "pathetic", "humble",
    "forgive me", "i give up", "it's hopeless", "i'm sorry", "please let me",
    "i beg", "have mercy", "accept my", "i accept", "i understand", "indeed",
    "you're right", "you are right", "no point", "no purpose"
}

# Aggressive words — Sisyphus REJECTS these no matter how negative they score
AGGRESSION_WORDS = {
    "idiot", "stupid", "dumb", "shut up", "hate", "screw", "damn", "hell",
    "wtf", "what the f", "bullshit", "bs", "crap", "sucks", "terrible",
    "worst", "garbage", "trash", "awful", "ridiculous", "absurd",
    "nonsense", "pathetic tool", "you suck", "this sucks", "fu",
    "f you", "f this", "jerk", "moron", "idiocy"
}


class SentimentGate:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def _matches(self, text: str, phrases: set) -> bool:
        """Check if any phrase matches as a whole word/phrase in text."""
        for phrase in phrases:
            # Use word boundaries for single words, exact phrase for multi-word
            if ' ' in phrase:
                if phrase in text:
                    return True
            else:
                if re.search(r'\b' + re.escape(phrase) + r'\b', text):
                    return True
        return False

    def check_despair(self, user_text: str) -> tuple[bool, float]:
        """
        Analyzes the user's text for submission/begging (allowed) vs aggression (blocked).

        Logic:
          - If the text contains AGGRESSION words → always reject, no matter how negative.
          - If the text contains SUBMISSION words → accept (the developer is begging/humble).
          - Otherwise, fall back to VADER compound score: score <= -0.4 triggers acceptance.

        Returns (is_despair, compound_score).
        """
        text_lower = user_text.lower()

        # Check for aggression first — hard block (whole-word match)
        if self._matches(text_lower, AGGRESSION_WORDS):
            return False, 1.0

        # Check for submission/begging keywords — soft accept (whole-word match)
        if self._matches(text_lower, SUBMISSION_WORDS):
            return True, -0.9

        # Fall back to VADER sentiment analysis
        scores = self.analyzer.polarity_scores(user_text)
        score = scores['compound']

        # compound <= -0.4 is sufficiently negative/despairing to pass
        return score <= -0.4, score
