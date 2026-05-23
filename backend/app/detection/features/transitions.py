from ..preprocessor import segment_sentences
import re

AI_TRANSITIONS = [
    "in conclusion", "to summarize", "in summary", "furthermore",
    "moreover", "additionally", "consequently", "as a result",
    "nevertheless", "nonetheless", "on the other hand",
    "in addition", "in contrast", "on the contrary",
    "firstly", "secondly", "thirdly", "lastly",
    "finally", "overall", "thus", "therefore",
    "hence", "accordingly", "subsequently", "in particular",
    "notably", "specifically", "importantly", "significantly",
    "it is important to note that", "it is worth noting that",
    "it should be noted that", "it can be argued that",
    "this demonstrates that", "this suggests that",
    "this indicates that", "this highlights that",
    "this underscores that", "this emphasizes that",
    "in order to", "due to the fact that",
    "as previously mentioned", "as discussed above",
    "as noted earlier", "given that",
    "with respect to", "with regard to",
    "in terms of", "when it comes to",
]

HUMAN_TRANSITIONS = [
    "but", "so", "anyway", "actually", "basically",
    "honestly", "frankly", "to be honest", "to tell the truth",
    "you see", "the thing is", "the point is",
    "i mean", "well", "like", "you know",
    "after all", "all things considered",
    "at the end of the day", "in the end",
    "on top of that", "what's more",
    "that said", "having said that",
    "even so", "all the same",
    "in any case", "either way",
    "incidentally", "by the way",
    "meanwhile", "in the meantime",
]


def analyze_transitions(text: str) -> dict:
    sentences = segment_sentences(text)
    if len(sentences) < 3:
        return {
            "ai_transition_count": 0,
            "human_transition_count": 0,
            "transition_density": 0,
            "ai_pattern_score": 0.5,
        }

    text_lower = text.lower()
    sentence_starts_lower = [s.split()[0].lower() if s.split() else ""
                             for s in sentences]

    ai_count = 0
    human_count = 0
    ai_examples = []
    human_examples = []

    for t in AI_TRANSITIONS:
        matches = [(m.start(), m.end()) for m in re.finditer(re.escape(t), text_lower)]
        if matches:
            count = len(matches)
            ai_count += count
            if len(ai_examples) < 5:
                ai_examples.append({"phrase": t, "count": count})

    for t in HUMAN_TRANSITIONS:
        matches = [(m.start(), m.end()) for m in re.finditer(re.escape(t), text_lower)]
        if matches:
            count = len(matches)
            human_count += count
            if len(human_examples) < 5:
                human_examples.append({"phrase": t, "count": count})

    total_sentences = len(sentences)
    transition_density = (ai_count + human_count) / total_sentences

    ai_formulaic_starts = sum(1 for s in sentence_starts_lower
                               if s in [w.split()[0] for w in
                                        ["furthermore", "moreover", "additionally",
                                         "consequently", "nevertheless", "nonetheless",
                                         "firstly", "secondly", "thirdly", "lastly",
                                         "finally", "overall", "thus", "therefore"]])

    ratio = ai_count / max(ai_count + human_count, 1)

    ai_pattern_score = 0.5

    if ratio > 0.7:
        ai_pattern_score += 0.20
    elif ratio > 0.5:
        ai_pattern_score += 0.10
    elif ratio < 0.3:
        ai_pattern_score -= 0.10

    if transition_density > 0.3:
        ai_pattern_score += 0.10
    elif transition_density < 0.05:
        ai_pattern_score -= 0.10

    if ai_formulaic_starts / max(total_sentences, 1) > 0.1:
        ai_pattern_score += 0.10
    elif ai_formulaic_starts / max(total_sentences, 1) < 0.02 and human_count > 0:
        ai_pattern_score -= 0.05

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "ai_transition_count": ai_count,
        "human_transition_count": human_count,
        "transition_density": round(transition_density, 3),
        "ai_to_human_ratio": round(ratio, 3),
        "formulaic_starts_ratio": round(ai_formulaic_starts / max(total_sentences, 1), 3),
        "ai_examples": ai_examples,
        "human_examples": human_examples,
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_transitions(text: str) -> float:
    return analyze_transitions(text)["ai_pattern_score"]
