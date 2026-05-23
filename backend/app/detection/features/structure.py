from ..preprocessor import segment_paragraphs, segment_sentences
import statistics


def analyze_structure(text: str) -> dict:
    paragraphs = segment_paragraphs(text)
    if len(paragraphs) < 2:
        return {
            "paragraph_count": 1,
            "para_length_mean": len(text),
            "para_length_cv": 0,
            "has_intro": False,
            "has_conclusion": False,
            "ai_pattern_score": 0.5,
        }

    para_lengths = [len(p.split()) for p in paragraphs]
    mean_len = statistics.mean(para_lengths)
    std_len = statistics.pstdev(para_lengths) if len(para_lengths) > 1 else 0
    cv = std_len / mean_len if mean_len > 0 else 0

    first_para = paragraphs[0].lower()
    last_para = paragraphs[-1].lower()

    intro_signals = ["introduction", "in this essay", "this essay will",
                     "purpose of this", "overview", "background",
                     "this paper", "this analysis"]
    conc_signals = ["in conclusion", "to conclude", "in summary",
                    "to summarize", "overall,", "in closing",
                    "finally,", "to sum up", "in review"]

    has_intro = any(s in first_para for s in intro_signals)
    has_conclusion = any(s in last_para for s in conc_signals)
    intro_is_short = len(paragraphs[0].split()) < len(paragraphs[-1].split()) * 0.5

    sentence_counts = []
    for p in paragraphs:
        sc = len(segment_sentences(p))
        sentence_counts.append(sc)

    sc_mean = statistics.mean(sentence_counts) if sentence_counts else 0
    sc_std = statistics.pstdev(sentence_counts) if len(sentence_counts) > 1 else 0
    sc_cv = sc_std / sc_mean if sc_mean > 0 else 0

    ai_pattern_score = 0.5

    if cv < 0.3:
        ai_pattern_score += 0.15
    elif cv < 0.5:
        ai_pattern_score += 0.08

    if sc_cv < 0.25:
        ai_pattern_score += 0.10

    if has_intro and has_conclusion:
        ai_pattern_score += 0.05

    para_lengths_norm = [l / max(para_lengths) for l in para_lengths]
    monotonic = all(para_lengths_norm[i] <= para_lengths_norm[i+1] + 0.1
                    for i in range(len(para_lengths_norm)-1))
    if not monotonic:
        ai_pattern_score -= 0.05

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "paragraph_count": len(paragraphs),
        "para_length_mean": round(mean_len, 1),
        "para_length_cv": round(cv, 3),
        "sentence_per_para_cv": round(sc_cv, 3),
        "has_intro": has_intro,
        "has_conclusion": has_conclusion,
        "intro_is_short": intro_is_short,
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_structure(text: str) -> float:
    return analyze_structure(text)["ai_pattern_score"]
