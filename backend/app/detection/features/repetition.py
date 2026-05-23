from ..preprocessor import tokenize_words, extract_ngrams, segment_sentences
from collections import Counter


def analyze_repetition(text: str) -> dict:
    tokens = tokenize_words(text)
    sentences = segment_sentences(text)
    if len(tokens) < 10:
        return {
            "top_repeated_bigrams": [],
            "top_repeated_trigrams": [],
            "repeated_sentence_starts": [],
            "self_similarity": 0.5,
            "ai_pattern_score": 0.5,
        }

    bigrams = list(zip(tokens, tokens[1:]))
    trigrams = list(zip(tokens, tokens[2:], tokens[3:]))
    bigram_freq = Counter(bigrams)
    trigram_freq = Counter(trigrams)

    total_bigrams = len(bigrams)
    total_trigrams = len(trigrams)

    repeated_bigram_count = sum(c for c in bigram_freq.values() if c > 1)
    repeated_trigram_count = sum(c for c in trigram_freq.values() if c > 1)

    bigram_repeat_ratio = repeated_bigram_count / max(total_bigrams, 1)
    trigram_repeat_ratio = repeated_trigram_count / max(total_trigrams, 1)

    sentence_starts = []
    for s in sentences:
        words = s.split()
        if len(words) >= 2:
            sentence_starts.append((words[0].lower(), words[1].lower()))
    start_freq = Counter(sentence_starts)
    repeated_starts = sum(c - 1 for c in start_freq.values() if c > 1)
    start_repeat_ratio = repeated_starts / max(len(sentence_starts), 1)

    top_repeated_bigrams = [{"phrase": " ".join(b), "count": c}
                            for b, c in bigram_freq.most_common(10) if c > 1]
    top_repeated_trigrams = [{"phrase": " ".join(t), "count": c}
                             for t, c in trigram_freq.most_common(10) if c > 2]
    top_repeated_starts = [{"phrase": " ".join(s), "count": c}
                           for s, c in start_freq.most_common(10) if c > 1]

    ai_pattern_score = 0.5

    if bigram_repeat_ratio > 0.15:
        ai_pattern_score += 0.15
    elif bigram_repeat_ratio > 0.10:
        ai_pattern_score += 0.08

    if trigram_repeat_ratio > 0.04:
        ai_pattern_score += 0.10
    elif trigram_repeat_ratio > 0.02:
        ai_pattern_score += 0.05

    if start_repeat_ratio > 0.15:
        ai_pattern_score += 0.10
    elif start_repeat_ratio < 0.03:
        ai_pattern_score -= 0.05

    if len(tokens) > 200:
        unique_ratio = len(set(tokens)) / len(tokens)
        if unique_ratio < 0.25:
            ai_pattern_score += 0.10
        elif unique_ratio > 0.40:
            ai_pattern_score -= 0.05

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "bigram_repeat_ratio": round(bigram_repeat_ratio, 3),
        "trigram_repeat_ratio": round(trigram_repeat_ratio, 3),
        "start_repeat_ratio": round(start_repeat_ratio, 3),
        "top_repeated_bigrams": top_repeated_bigrams[:5],
        "top_repeated_trigrams": top_repeated_trigrams[:5],
        "top_repeated_starts": top_repeated_starts[:5],
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_repetition(text: str) -> float:
    return analyze_repetition(text)["ai_pattern_score"]
