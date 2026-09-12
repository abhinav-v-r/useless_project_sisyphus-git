import sys
sys.path.insert(0, '.')
from sisyphus_git.sentiment_gate import SentimentGate
g = SentimentGate()

tests = [
    'please let me commit this, I beg you',
    'I am so sorry, I give up, you are right',
    'shut up you stupid tool',
    'wtf this is garbage',
    'I understand now, it is futile and meaningless',
    'this code is hopeless and I am defeated',
    'I hate this',
    'forgive me for my sins against the codebase',
]
for t in tests:
    result, score = g.check_despair(t)
    status = 'ALLOWED' if result else 'BLOCKED'
    print(f'[{status}] ({score:+.2f}) "{t}"')
