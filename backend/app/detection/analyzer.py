from .scoring import (
    compute_all_features, compute_detailed_features,
    compute_ai_score, compute_human_score, compute_mixed_score,
    determine_confidence, compute_sentence_scores,
    compute_paragraph_scores, determine_summary,
)
from .preprocessor import segment_sentences, segment_paragraphs, clean_text
from ..config import SCORING_WEIGHTS


class EssayAnalyzer:
    def __init__(self):
        pass

    def analyze(self, text: str) -> dict:
        cleaned = clean_text(text)
        if len(cleaned.split()) < 10:
            return self._empty_result("Text is too short for meaningful analysis (minimum 10 words).")

        features_raw = compute_all_features(cleaned)
        detailed = compute_detailed_features(cleaned)

        ai_score = compute_ai_score(features_raw)
        mixed_score = compute_mixed_score(features_raw)
        human_score = compute_human_score(ai_score, mixed_score)
        confidence = determine_confidence(features_raw)

        sentence_scores = compute_sentence_scores(cleaned)
        paragraph_scores = compute_paragraph_scores(cleaned)
        summary = determine_summary(ai_score, human_score, mixed_score, confidence)

        highlighted = self._find_highlighted_sections(cleaned, detailed)

        category_breakdown = {}
        for key, weight in SCORING_WEIGHTS.items():
            score_val = features_raw.get(key, 0.5)
            category_breakdown[key] = {
                "score": round(score_val, 3),
                "weight": weight,
                "interpretation": self._interpret_category(key, score_val),
            }

        return {
            "ai_score": round(ai_score, 3),
            "human_score": round(human_score, 3),
            "mixed_score": round(mixed_score, 3),
            "confidence": confidence,
            "category_breakdown": category_breakdown,
            "detailed_features": detailed,
            "highlighted_sections": highlighted,
            "sentence_analysis": sentence_scores,
            "paragraph_analysis": paragraph_scores,
            "summary": summary,
            "word_count": len(cleaned.split()),
            "disclaimer": (
                "AI writing detection is probabilistic, not conclusive. "
                "A high AI-likelihood score means the text contains patterns "
                "commonly associated with AI-generated writing, but it does not "
                "prove authorship. False positives are possible, especially with "
                "well-structured formal writing, non-native English, or writing "
                "in certain academic genres. This analysis should never be used "
                "as the sole basis for academic or disciplinary decisions."
            ),
        }

    def _empty_result(self, message: str) -> dict:
        return {
            "ai_score": 0.5,
            "human_score": 0.5,
            "mixed_score": 0.0,
            "confidence": "Low",
            "category_breakdown": {},
            "detailed_features": {},
            "highlighted_sections": [],
            "sentence_analysis": [],
            "paragraph_analysis": [],
            "summary": message,
            "word_count": 0,
            "disclaimer": message,
        }

    def _find_highlighted_sections(
        self, text: str, detailed: dict
    ) -> list[dict]:
        paragraphs = segment_paragraphs(text)
        highlighted = []

        for i, para in enumerate(paragraphs):
            words = para.split()
            if len(words) < 5:
                continue

            signals = []

            if detailed.get("sentence_variation", {}).get("ai_pattern_score", 0.5) > 0.6:
                from .preprocessor import segment_sentences
                sents = segment_sentences(para)
                if len(sents) > 1:
                    lengths = [len(s.split()) for s in sents]
                    avg_len = sum(lengths) / len(lengths)
                    if all(abs(l - avg_len) / max(avg_len, 1) < 0.3 for l in lengths):
                        signals.append("Uniform sentence lengths")

            para_lower = para.lower()
            import re
            formulaic_starts = ["furthermore", "moreover", "additionally",
                                "consequently", "nevertheless", "in conclusion",
                                "in summary", "firstly", "secondly", "thirdly"]
            for word in formulaic_starts:
                if re.match(r'\b' + word + r'\b', para_lower):
                    signals.append(f"Formulaic transition: '{word.title()}'")
                    break

            if detailed.get("specificity", {}).get("vague_per_sentence", 0) > 1.0:
                signals.append("High density of vague/generic language")

            if detailed.get("repetition", {}).get("bigram_repeat_ratio", 0) > 0.12:
                signals.append("Repetitive phrasing patterns")

            if signals:
                highlighted.append({
                    "paragraph_index": i,
                    "snippet": para[:300],
                    "reasons": signals[:3],
                    "ai_score": min(0.9, 0.5 + 0.1 * len(signals)),
                })

        highlighted.sort(key=lambda x: x["ai_score"], reverse=True)
        return highlighted[:15]

    def _interpret_category(self, key: str, score: float) -> str:
        interpretations = {
            "predictability": (
                "Low lexical surprise; text follows expected patterns closely"
                if score > 0.6 else
                "Moderate lexical predictability"
                if score > 0.35 else
                "Natural lexical variation"
            ),
            "sentence_variation": (
                "Low variation in sentence length and structure"
                if score > 0.6 else
                "Moderate variation" if score > 0.35 else
                "High natural sentence variation"
            ),
            "paragraph_rhythm": (
                "Uniform paragraph lengths and consistent structure"
                if score > 0.6 else
                "Moderate paragraph variation"
                if score > 0.35 else
                "Natural paragraph rhythm"
            ),
            "repetitive_phrasing": (
                "Noticeable repetition of phrases and patterns"
                if score > 0.6 else
                "Moderate repetition" if score > 0.35 else
                "Low repetition, natural variation"
            ),
            "generic_filler": (
                "High use of vague/generic language without specifics"
                if score > 0.6 else
                "Moderate use of generic language"
                if score > 0.35 else
                "Specific, concrete language"
            ),
            "transition_patterns": (
                "Heavy use of formal, formulaic transitions"
                if score > 0.6 else
                "Moderate transition formality"
                if score > 0.35 else
                "Natural, varied transitions"
            ),
            "evidence_specificity": (
                "Low specificity in claims and examples"
                if score > 0.6 else
                "Moderate specificity" if score > 0.35 else
                "Strong specific evidence and examples"
            ),
            "personal_voice": (
                "Weak or absent personal voice markers"
                if score > 0.6 else
                "Moderate personal voice" if score > 0.35 else
                "Strong personal voice and perspective"
            ),
            "natural_imperfection": (
                "Low natural imperfection; text feels overly polished"
                if score < 0.35 else
                "Moderate natural imperfection"
                if score < 0.65 else
                "Natural unevenness and informality"
            ),
            "citation_behavior": (
                "Few or no citations in a text that would typically require them"
                if score > 0.6 else
                "Moderate citation presence" if score > 0.35 else
                "Appropriate citation behavior"
            ),
            "readability_profile": (
                "Readability metrics consistent with AI-generated text patterns"
                if score > 0.6 else
                "Moderate readability pattern match"
                if score > 0.35 else
                "Readability matches human writing patterns"
            ),
            "topic_depth": (
                "Shallow or superficial treatment of topic"
                if score > 0.6 else
                "Moderate topic depth" if score > 0.35 else
                "Deep, nuanced topic coverage"
            ),
            "structural_symmetry": (
                "Overly symmetrical, formulaic essay structure"
                if score > 0.6 else
                "Moderate structural formality"
                if score > 0.35 else
                "Natural structural variation"
            ),
            "lexical_diversity": (
                "Low lexical diversity; limited vocabulary range"
                if score > 0.6 else
                "Moderate lexical diversity"
                if score > 0.35 else
                "Rich, varied vocabulary"
            ),
        }
        return interpretations.get(key, f"Score: {score:.2f}")
