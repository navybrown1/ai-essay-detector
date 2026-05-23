import re


def analyze_citations(text: str) -> dict:
    patterns = {
        "apa_inline": r'\([^)]*\d{4}[^)]*\)',
        "mla_author_page": r'\b\w+\s+\d+\b',
        "numeric_bracket": r'\[\d+(?:[-,]\s*\d+)*\]',
        "footnote_marker": r'\[\d+\]',
        "et_al": r'\bet al\.?\b',
        "doi_url": r'doi\.org/\S+',
        "url_http": r'https?://\S+',
        "quote_citation": r'"[^"]{20,}"\s*\([^)]*\d{4}',
    }

    results = {}
    total_matches = 0
    for name, pat in patterns.items():
        matches = re.findall(pat, text)
        results[name] = len(matches)
        total_matches += len(matches)

    references_section = False
    ref_lines = 0
    for line in text.split("\n"):
        if re.search(r'\b(?:references|bibliography|works cited|sources)\b', line, re.IGNORECASE):
            references_section = True
        if references_section:
            ref_lines += 1

    has_references = references_section and ref_lines > 2

    reference_density = total_matches / max(len(text.split("\n")), 1)

    words = text.split()
    total_words = len(words)
    citation_per_1000 = total_matches / max(total_words / 1000, 1)

    ai_pattern_score = 0.5

    if citation_per_1000 < 0.5 and total_words > 300:
        ai_pattern_score += 0.10

    if total_matches == 0 and total_words > 500:
        ai_pattern_score += 0.15

    if not has_references and total_words > 500:
        ai_pattern_score += 0.05

    reference_quality = ""
    if has_references:
        reference_quality = "present"
        ai_pattern_score -= 0.05

    ai_pattern_score = max(0.05, min(ai_pattern_score, 0.95))

    return {
        "apa_inline_count": results.get("apa_inline", 0),
        "numeric_citation_count": results.get("numeric_bracket", 0),
        "total_citations": total_matches,
        "citations_per_1000_words": round(citation_per_1000, 2),
        "has_references_section": has_references,
        "reference_quality": reference_quality,
        "ai_pattern_score": round(ai_pattern_score, 3),
    }


def score_citations(text: str) -> float:
    return analyze_citations(text)["ai_pattern_score"]
