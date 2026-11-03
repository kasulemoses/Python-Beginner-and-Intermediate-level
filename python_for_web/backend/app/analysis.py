import re
import unicodedata
from collections import Counter

from .schemas import AnalysisResult, WordFrequency

# Unicode letters/digits; underscores separate words. Internal apostrophes stay.
TOKEN = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)


def analyze(text: str) -> AnalysisResult:
    normalized = unicodedata.normalize("NFC", text).casefold().replace("’", "'")
    words = TOKEN.findall(normalized)
    counts = Counter(words)
    most_common = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:10]
    return AnalysisResult(
        character_count=len(text),
        word_count=len(words),
        unique_word_count=len(counts),
        frequent_words=[WordFrequency(word=word, count=count) for word, count in most_common],
    )
