from ..config import SCORING_WEIGHTS
from .preprocessor import segment_sentences, segment_paragraphs, tokenize_words
from .features import (
    readability, lexical_diversity, sentence_variation, repetition,
    transitions, structure, personal_voice, specificity,
    semantic_similarity, citation_analysis,
)


def compute_all_features(text: str) -> dict:
    return {
        "predictability": repetition.score_repetition(text),
        "sentence_variation": sentence_variation.score_sentence_variation(text),
        "paragraph_rhythm": structure.score_structure(text),
        "repetitive_phrasing": repetition.score_repetition(text),
        "generic_filler": specificity.score_specificity(text),
        "transition_patterns": transitions.score_transitions(text),
        "evidence_specificity": specificity.score_specificity(text),
        "personal_voice": personal_voice.score_personal_voice(text),
        "natural_imperfection": 1.0 - sentence_variation.score_sentence_variation(text),
        "citation_behavior": citation_analysis.score_citations(text),
        "readability_profile": readability.score_readability(text),
        "topic_depth": specificity.score_specificity(text),
        "structural_symmetry": structure.score_structure(text),
        "lexical_diversity": lexical_diversity.score_lexical_diversity(text),
    }


def compute_detailed_features(text: str) -> dict:
    return {
        "readability": readability.compute_readability_scores(text),
        "lexical_diversity": lexical_diversity.lexical_diversity_score(text),
        "sentence_variation": sentence_variation.analyze_sentence_variation(text),
        "repetition": repetition.analyze_repetition(text),
        "transitions": transitions.analyze_transitions(text),
        "structure": structure.analyze_structure(text),
        "personal_voice": personal_voice.analyze_personal_voice(text),
        "specificity": specificity.analyze_specificity(text),
        "semantic_similarity": semantic_similarity.analyze_semantic_similarity(text),
        "citations": citation_analysis.analyze_citations(text),
    }


def compute_ai_score(features: dict) -> float:
    weighted = 0.0
    total_weight = 0.0
    for key, weight in SCORING_WEIGHTS.items():
        if key in features:
            weighted += features[key] * weight
            total_weight += weight

    if total_weight == 0:
        return 0.5

    raw_score = weighted / total_weight

    return max(0.05, min(0.95, raw_score))


def compute_human_score(ai_score: float, mixed_score: float) -> float:
    remaining = 1.0 - max(ai_score, mixed_score)
    return round(remaining, 3)


def compute_mixed_score(features: dict) -> float:
    contradictory_signals = 0
    total_signals = 0

    for key in ["sentence_variation", "personal_voice", "natural_imperfection"]:
        val = features.get(key, 0.5)
        if 0.35 <= val <= 0.65:
            contradictory_signals += 1
        total_signals += 1

    for key in ["predictability", "repetitive_phrasing", "lexical_diversity"]:
        val = features.get(key, 0.5)
        if key in ["lexical_diversity"]:
            comp = 1.0 - val
            if 0.35 <= comp <= 0.65:
                contradictory_signals += 1
        elif val > 0.3:
            contradictory_signals += 1
        total_signals += 1

    mixed_ratio = contradictory_signals / max(total_signals, 1)

    return round(mixed_ratio * 0.6, 3)


def determine_confidence(features: dict) -> str:
    ai_score = compute_ai_score(features)
    mixed_score = compute_mixed_score(features)

    scores = list(features.values())
    variance = (
        sum((s - 0.5) ** 2 for s in scores) / max(len(scores), 1)
    )

    if variance > 0.10 and mixed_score < 0.15:
        return "High"
    elif variance > 0.05 or mixed_score < 0.25:
        return "Medium"
    else:
        return "Low"


def compute_sentence_scores(text: str) -> list[dict]:
    sentences = segment_sentences(text)
    results = []
    for i, sent in enumerate(sentences):
        words = tokenize_words(sent)
        word_count = len(words)
        if word_count == 0:
            continue

        upper_ratio = sum(1 for c in sent if c.isupper()) / max(len(sent.strip()), 1)
        exclamation = sent.count("!") > 0
        question = sent.count("?") > 0
        sent_len = len(sent)

        if word_count < 5:
            ai_indicators = 0.1
        elif word_count > 40:
            ai_indicators = 0.3
        else:
            ai_indicators = 0.5

        penalty = 0.0
        if upper_ratio > 0.3:
            penalty += 0.1  # all caps not typical
        if exclamation:
            penalty -= 0.1
        if question:
            penalty -= 0.05

        score = min(0.95, max(0.05, ai_indicators + penalty))

        results.append({
            "index": i,
            "text": sent[:200],
            "word_count": word_count,
            "ai_score": round(score, 3),
            "char_length": sent_len,
        })

    return results


def compute_paragraph_scores(text: str) -> list[dict]:
    paragraphs = segment_paragraphs(text)
    results = []
    for i, para in enumerate(paragraphs):
        words = tokenize_words(para)
        word_count = len(words)
        sentences = segment_sentences(para)
        sent_count = len(sentences)

        if word_count < 10:
            depth = "shallow"
        elif word_count > 150:
            depth = "deep"
        else:
            depth = "moderate"

        avg_sent_len = word_count / max(sent_count, 1)
        if avg_sent_len > 30:
            synthents = "complex"
        elif avg_sent_len > 18:
            synthents = "moderate"
        else:
            synthents = "simple"

        results.append({
            "index": i,
            "word_count": word_count,
            "sentence_count": sent_count,
            "depth": depth,
            "syntax": synthents,
        })

    return results


def determine_summary(
    ai_score: float, human_score: float, mixed_score: float, confidence: str
) -> str:
    if confidence == "Low":
        return (
            "This essay shows mixed or inconclusive signals. "
            "The linguistic patterns do not strongly favor either human or AI authorship. "
            "Human review is recommended before drawing any conclusions."
        )

    if ai_score > 0.7 and mixed_score < 0.2:
        return (
            "This essay exhibits many patterns commonly found in AI-generated text, "
            "including consistent sentence structure, formulaic transitions, "
            "and low lexical variation. However, this does not prove AI authorship. "
            "False positives are possible, especially with well-structured formal writing."
        )

    if human_score > 0.6 and mixed_score < 0.15:
        return (
            "This essay shows patterns consistent with human writing, "
            "including natural variation in sentence length, personal voice markers, "
            "and uneven paragraph structure. AI assistance cannot be ruled out entirely."
        )

    if mixed_score > 0.2:
        return (
            "This essay contains a mix of human and AI-like patterns. "
            "Some sections read naturally while others show characteristics "
            "associated with AI-generated text. This could indicate AI-assisted writing, "
            "or a writer who naturally uses a structured, formal style."
        )

    return (
        f"Based on analysis, this essay has a {confidence.lower()} confidence "
        f"indication. The linguistic features analyzed show some patterns "
        f"consistent with {'AI' if ai_score > human_score else 'human'} writing, "
        f"but the signals are not definitive."
    )
