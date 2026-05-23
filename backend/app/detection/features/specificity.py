from ..preprocessor import segment_sentences, tokenize_words
import re

VAGUE_WORDS = {
    "very", "really", "quite", "somewhat", "rather", "fairly",
    "pretty", "highly", "extremely", "incredibly", "absolutely",
    "things", "stuff", "something", "someone", "somewhere",
    "many", "numerous", "various", "multiple", "countless",
    "significant", "substantial", "considerable", "notable",
    "certain", "specific", "particular", "various",
    "good", "bad", "nice", "great", "wonderful",
    "important", "crucial", "critical", "essential", "key",
    "overall", "general", "broad", "wide-ranging",
    "in recent years", "in today's world", "in modern society",
    "in today's society", "throughout history",
    "it is widely believed", "it is commonly thought",
    "as is well known", "it goes without saying",
}

CONCRETE_INDICATORS = [
    "percent", "percentage", "statistic", "data", "study",
    "research", "survey", "experiment", "analysis", "finding",
    "according to", "reported", "demonstrated", "shown",
    "measured", "calculated", "estimated", "observed",
    "specifically", "for example", "for instance",
    "such as", "e.g.", "i.e.",
    "in 20", "between 20", "from 20",
    "figure", "table", "chart", "graph",
    "source", "reference", "citation",
]


def analyze_specificity(text: str) -> dict:
    sentences = segment_sentences(text)
    tokens = tokenize_words(text)
    text_lower = text.lower()

    if len(tokens) < 10:
        return {"ai_pattern_score": 0.5}

    total_sentences = len(sentences)
    total_words = len(tokens)

    vague_count = 0
    for v in VAGUE_WORDS:
        vague_count += len(re.findall(r'\b' + re.escape(v) + r'\b', text_lower))

    concrete_count = 0
    for c in CONCRETE_INDICATORS:
        concrete_count += len(re.findall(r'\b' + re.escape(c) + r'\b', text_lower))

    number_pattern = r'\b\d+\b'
    number_count = len(re.findall(number_pattern, text))

    vague_per_sentence = vague_count / max(total_sentences, 1)
    concrete_per_sentence = concrete_count / max(total_sentences, 1)
    numbers_per_sentence = number_count / max(total_sentences, 1)
    specificity_ratio = concrete_count / max(vague_count + concrete_count, 1)

    sentences_with_examples = 0
    for s in sentences:
        s_lower = s.lower()
        if any(ex in s_lower for ex in ["for example", "for instance",
                                          "such as", "e.g.", "specifically",
                                          "in particular"]):
            sentences_with_examples += 1

    example_ratio = sentences_with_examples / max(total_sentences, 1)

    avg_vague_per_para = vague_count / max(len(set(s[0] for s in sentences)), 1)

    ai_pattern_score = 0.5

    if vague_per_sentence > 1.5:
        ai_pattern_score += 0.20
    elif vague_per_sentence > 0.8:
        ai_pattern_score += 0.10
    elif vague_per_sentence < 0.3:
        ai_pattern_score -= 0.10

    if specificity_ratio < 0.3:
        ai_pattern_score += 0.15
    elif specificity_ratio < 0.5:
        ai_pattern_score += 0.08
    elif specificity_ratio > 0.7:
        ai_pattern_score -= 0.10

    if numbers_per_sentence < 0.1 and total_sentences > 5:
        ai_pattern_score += 0.10
    elif numbers_per_sentence > 0.5:
        ai_pattern_score -= 0.05

    if example_ratio < 0.05:
        ai_pattern_score += 0.05
    elif example_ratio > 0.15:
        ai_pattern_score -= 0.05

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "vague_count": vague_count,
        "concrete_count": concrete_count,
        "number_count": number_count,
        "vague_per_sentence": round(vague_per_sentence, 3),
        "concrete_per_sentence": round(concrete_per_sentence, 3),
        "numbers_per_sentence": round(numbers_per_sentence, 3),
        "specificity_ratio": round(specificity_ratio, 3),
        "example_sentence_ratio": round(example_ratio, 3),
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_specificity(text: str) -> float:
    return analyze_specificity(text)["ai_pattern_score"]
