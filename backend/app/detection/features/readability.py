import textstat
from ..preprocessor import segment_sentences, tokenize_words, count_syllables


def compute_readability_scores(text: str) -> dict:
    sentences = segment_sentences(text)
    words = tokenize_words(text)

    if not words or len(sentences) < 2:
        return {
            "flesch_reading_ease": 50.0,
            "flesch_kincaid_grade": 10.0,
            "gunning_fog": 12.0,
            "avg_sentence_length": 20.0,
            "avg_syllables_per_word": 1.5,
            "ai_pattern_score": 0.5,
        }

    fre = textstat.flesch_reading_ease(text)
    fk = textstat.flesch_kincaid_grade(text)
    fog = textstat.gunning_fog(text)
    avg_sent_len = len(words) / len(sentences) if sentences else 20
    avg_syl = sum(count_syllables(w) for w in words) / len(words) if words else 1.5

    sentence_lengths = [len(w.split()) for w in sentences]

    variation = (
        max(sentence_lengths) - min(sentence_lengths)
    ) / max(sum(sentence_lengths) / len(sentence_lengths), 1)

    ai_pattern_score = 0.5

    if fre < 30 and avg_sent_len > 25:
        ai_pattern_score += 0.15
    if abs(fre - 45) < 10:
        ai_pattern_score += 0.10
    if variation < 1.5:
        ai_pattern_score += 0.10
    if avg_syl < 1.4:
        ai_pattern_score += 0.05

    ai_pattern_score = min(ai_pattern_score, 0.95)

    return {
        "flesch_reading_ease": fre,
        "flesch_kincaid_grade": fk,
        "gunning_fog": fog,
        "avg_sentence_length": avg_sent_len,
        "avg_syllables_per_word": avg_syl,
        "sentence_length_variation": round(variation, 2),
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_readability(text: str) -> float:
    scores = compute_readability_scores(text)
    return scores["ai_pattern_score"]
