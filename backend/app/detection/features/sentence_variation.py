from ..preprocessor import segment_sentences, tokenize_words
import statistics


def analyze_sentence_variation(text: str) -> dict:
    sentences = segment_sentences(text)
    if len(sentences) < 3:
        return {
            "length_mean": 20.0,
            "length_std": 5.0,
            "cv": 0.25,
            "min": 5,
            "max": 50,
            "burstiness": 0.5,
            "ai_pattern_score": 0.5,
        }

    lengths = [len(s.split()) for s in sentences]
    words = tokenize_words(text)

    mean_len = statistics.mean(lengths)
    std_len = statistics.pstdev(lengths) if len(lengths) > 1 else 0
    cv = std_len / mean_len if mean_len > 0 else 0

    diffs = [abs(lengths[i] - lengths[i - 1]) for i in range(1, len(lengths))]
    burstiness = statistics.mean(diffs) / mean_len if mean_len > 0 else 0

    ai_pattern_score = 0.5

    if cv < 0.3:
        ai_pattern_score += 0.20
    elif cv < 0.45:
        ai_pattern_score += 0.10
    elif cv > 0.7:
        ai_pattern_score -= 0.15
    elif cv > 0.55:
        ai_pattern_score -= 0.05

    if burstiness < 0.3:
        ai_pattern_score += 0.15
    elif burstiness > 0.6:
        ai_pattern_score -= 0.10

    n_short = sum(1 for l in lengths if l < 5)
    n_long = sum(1 for l in lengths if l > 40)
    short_pct = n_short / len(lengths)
    long_pct = n_long / len(lengths)

    if short_pct < 0.05 and long_pct < 0.05:
        ai_pattern_score += 0.10
    if short_pct < 0.02:
        ai_pattern_score += 0.05

    consecutive_similar = sum(
        1 for i in range(1, len(lengths))
        if abs(lengths[i] - lengths[i - 1]) / max(lengths[i], lengths[i - 1], 1) < 0.15
    )
    similar_ratio = consecutive_similar / max(len(lengths) - 1, 1)
    if similar_ratio > 0.4:
        ai_pattern_score += 0.10

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "length_mean": round(mean_len, 1),
        "length_std": round(std_len, 1),
        "cv": round(cv, 3),
        "burstiness": round(burstiness, 3),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "short_sentence_pct": round(short_pct, 3),
        "long_sentence_pct": round(long_pct, 3),
        "consecutive_similar_ratio": round(similar_ratio, 3),
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_sentence_variation(text: str) -> float:
    return analyze_sentence_variation(text)["ai_pattern_score"]
