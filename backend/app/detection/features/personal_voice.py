from ..preprocessor import segment_sentences, tokenize_words
import re

FIRST_PERSON_PRONOUNS = {"i", "me", "my", "mine", "myself",
                         "we", "us", "our", "ours", "ourselves"}

SECOND_PERSON_PRONOUNS = {"you", "your", "yours", "yourself", "yourselves"}

HEDGING_WORDS = {"might", "maybe", "perhaps", "possibly", "probably",
                 "likely", "seems", "appears", "tends", "suggests",
                 "could", "would", "somewhat", "rather", "quite",
                 "sort of", "kind of", "i think", "i believe",
                 "i feel", "in my opinion", "in my view",
                 "it seems that", "it appears that"}

CONFIDENT_WORDS = {"always", "never", "undoubtedly", "certainly",
                   "definitely", "absolutely", "obviously", "clearly",
                   "without doubt", "unquestionably", "undeniably",
                   "everyone knows", "it is clear that",
                   "there is no doubt that", "it is obvious that"}

CONTRACTIONS = {"don't", "doesn't", "didn't", "won't", "wouldn't",
                "can't", "couldn't", "shouldn't", "isn't", "aren't",
                "wasn't", "weren't", "haven't", "hasn't", "hadn't",
                "it's", "i'm", "i've", "i'll", "i'd",
                "you're", "you've", "you'll", "you'd",
                "they're", "they've", "they'll", "they'd",
                "we're", "we've", "we'll", "we'd",
                "that's", "there's", "here's", "what's"}

COLLOQUIAL_MARKERS = {"gonna", "wanna", "gotta", "kinda", "sorta",
                      "lots of", "stuff", "things", "really",
                      "pretty good", "a bit", "a lot", "bunch of"}


def analyze_personal_voice(text: str) -> dict:
    sentences = segment_sentences(text)
    tokens = tokenize_words(text)
    text_lower = text.lower()

    if len(tokens) < 10:
        return {"ai_pattern_score": 0.5}

    total_words = len(tokens)

    first_person_count = sum(1 for t in tokens if t in FIRST_PERSON_PRONOUNS)
    second_person_count = sum(1 for t in tokens if t in SECOND_PERSON_PRONOUNS)
    contraction_count = sum(1 for c in CONTRACTIONS
                            if re.search(r'\b' + re.escape(c) + r'\b', text_lower))

    hedging_count = 0
    for h in HEDGING_WORDS:
        hedging_count += len(re.findall(r'\b' + re.escape(h) + r'\b', text_lower))

    confident_count = 0
    for c in CONFIDENT_WORDS:
        confident_count += len(re.findall(r'\b' + re.escape(c) + r'\b', text_lower))

    colloquial_count = 0
    for c in COLLOQUIAL_MARKERS:
        colloquial_count += len(re.findall(r'\b' + re.escape(c) + r'\b', text_lower))

    first_person_ratio = first_person_count / max(total_words, 1) * 100
    contraction_ratio = contraction_count / max(total_words, 1) * 100
    hedging_ratio = hedging_count / max(len(sentences), 1)
    confident_ratio = confident_count / max(len(sentences), 1)

    sentence_starts = []
    for s in sentences:
        words = s.split()
        if words:
            sentence_starts.append(words[0].lower())

    varied_starts = len(set(sentence_starts)) / max(len(sentence_starts), 1)

    ai_pattern_score = 0.5

    if first_person_ratio < 0.1:
        ai_pattern_score += 0.15
    elif first_person_ratio < 0.3:
        ai_pattern_score += 0.05
    elif first_person_ratio > 1.5:
        ai_pattern_score -= 0.15
    elif first_person_ratio > 0.5:
        ai_pattern_score -= 0.05

    if contraction_ratio < 0.02:
        ai_pattern_score += 0.10
    elif contraction_ratio > 0.5:
        ai_pattern_score -= 0.10

    if hedging_ratio < 0.05:
        ai_pattern_score += 0.05
    elif hedging_ratio > 0.3:
        ai_pattern_score -= 0.05

    if confident_ratio > 0.3:
        ai_pattern_score += 0.10

    if colloquial_count == 0 and len(tokens) > 200:
        ai_pattern_score += 0.10
    elif colloquial_count > 2:
        ai_pattern_score -= 0.05

    if varied_starts < 0.4:
        ai_pattern_score += 0.10
    elif varied_starts > 0.6:
        ai_pattern_score -= 0.10

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "first_person_ratio": round(first_person_ratio, 3),
        "contraction_ratio": round(contraction_ratio, 3),
        "hedging_per_sentence": round(hedging_ratio, 3),
        "confident_per_sentence": round(confident_ratio, 3),
        "colloquial_count": colloquial_count,
        "sentence_starter_variety": round(varied_starts, 3),
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_personal_voice(text: str) -> float:
    return analyze_personal_voice(text)["ai_pattern_score"]
