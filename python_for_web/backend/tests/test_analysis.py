from app.analysis import analyze


def test_apostrophes_unicode_and_ties():
    result = analyze("Don't don’t naïve cafe\u0301 café _ hi-hi 123")
    assert result.word_count == 8
    assert result.unique_word_count == 5
    assert result.frequent_words[0].word == "café"
    assert [(w.word, w.count) for w in result.frequent_words[:3]] == [("café", 2), ("don't", 2), ("hi", 2)]


def test_punctuation_only_and_frequency_limit():
    assert analyze("!!!").word_count == 0
    result = analyze("one two three four five six seven eight nine ten eleven twelve")
    assert len(result.frequent_words) == 10
