from ..preprocessor import segment_paragraphs, segment_sentences
import numpy as np


def analyze_semantic_similarity(text: str) -> dict:
    paragraphs = segment_paragraphs(text)
    if len(paragraphs) < 2:
        return {
            "mean_similarity": 0.5,
            "max_similarity": 0.5,
            "min_similarity": 0.5,
            "overly_similar_pairs": 0,
            "ai_pattern_score": 0.5,
        }

    try:
        from sentence_transformers import SentenceTransformer
        from ..config import SENTENCE_TRANSFORMER_MODEL

        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        para_embeddings = model.encode([p[:512] for p in paragraphs])

        similarities = []
        for i in range(len(para_embeddings)):
            for j in range(i + 1, len(para_embeddings)):
                cos_sim = np.dot(para_embeddings[i], para_embeddings[j]) / (
                    np.linalg.norm(para_embeddings[i]) *
                    np.linalg.norm(para_embeddings[j]) + 1e-10
                )
                similarities.append(float(cos_sim))

        if not similarities:
            return {"ai_pattern_score": 0.5}

        mean_sim = np.mean(similarities)
        max_sim = max(similarities)
        min_sim = min(similarities)
        overly_similar = sum(1 for s in similarities if s > 0.85)

        ai_pattern_score = 0.5

        if mean_sim > 0.75:
            ai_pattern_score += 0.20
        elif mean_sim > 0.6:
            ai_pattern_score += 0.10

        if overly_similar / max(len(similarities), 1) > 0.3:
            ai_pattern_score += 0.10

        if max_sim - min_sim < 0.2:
            ai_pattern_score += 0.10

        ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

        return {
            "mean_similarity": round(mean_sim, 3),
            "max_similarity": round(max_sim, 3),
            "min_similarity": round(min_sim, 3),
            "similarity_range": round(max_sim - min_sim, 3),
            "overly_similar_pairs": overly_similar,
            "total_pairs": len(similarities),
            "overly_similar_ratio": round(overly_similar / max(len(similarities), 1), 3),
            "ai_pattern_score": round(ai_pattern_score, 3),
        }

    except Exception:
        return {"mean_similarity": 0.5, "max_similarity": 0.5,
                "min_similarity": 0.5, "overly_similar_pairs": 0,
                "total_pairs": 0, "ai_pattern_score": 0.5}


def score_semantic_similarity(text: str) -> float:
    return analyze_semantic_similarity(text)["ai_pattern_score"]
