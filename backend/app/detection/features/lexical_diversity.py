from ..preprocessor import tokenize_words, extract_ngrams
import math


def type_token_ratio(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def lexical_diversity_score(text: str) -> dict:
    tokens = tokenize_words(text)
    if len(tokens) < 10:
        return {"ttr": 0.5, "maas_ttr": 0.5, "honore_stat": 0.5, "ai_pattern_score": 0.5}

    ttr = type_token_ratio(tokens)
    maas = (math.log(len(tokens)) - math.log(len(set(tokens)))) / (math.log(len(tokens)) ** 2) if len(tokens) > 1 else 0.5

    hapax = sum(1 for t in tokens if tokens.count(t) == 1)
    honore = (100 * math.log(len(tokens))) / (1 - hapax / len(tokens)) if hapax < len(tokens) else 0

    bigram_set = extract_ngrams(tokens, 2)
    trigram_set = extract_ngrams(tokens, 3)
    bigram_ttr = len(bigram_set) / max(len(tokens) - 1, 1)
    trigram_ttr = len(trigram_set) / max(len(tokens) - 2, 1)

    ai_pattern_score = 0.5

    if ttr < 0.35:
        ai_pattern_score += 0.20
    elif ttr < 0.45:
        ai_pattern_score += 0.10
    elif ttr > 0.65:
        ai_pattern_score -= 0.10

    if bigram_ttr < 0.15:
        ai_pattern_score += 0.10
    if trigram_ttr < 0.05:
        ai_pattern_score += 0.05

    if maas > 0.8:
        ai_pattern_score += 0.10

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "ttr": round(ttr, 3),
        "maas_ttr": round(maas, 3),
        "honore_stat": round(honore, 2),
        "bigram_ttr": round(bigram_ttr, 3),
        "trigram_ttr": round(trigram_ttr, 3),
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_lexical_diversity(text: str) -> float:
    return lexical_diversity_score(text)["ai_pattern_score"]
