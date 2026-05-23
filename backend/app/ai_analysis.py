import os
import json
import httpx
from typing import Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL

_SECOND_OPINION_SYSTEM_PROMPT = """You are an expert in computational linguistics and AI-generated text detection. Your job is to analyze essays and provide a second opinion on whether they were written by a human or an AI.

Analyze the provided essay text and return a JSON object with these fields:
- "ai_likelihood": float between 0.0 (definitely human) and 1.0 (definitely AI)
- "confidence": "High", "Medium", or "Low" describing your certainty
- "reasoning": a paragraph explaining your assessment, citing specific textual evidence
- "strengths": list of features that make the text seem human-written
- "weaknesses": list of features that make the text seem AI-written
- "verdict": a one-sentence summary

Be balanced, fair, and consider false positives. Many well-written formal essays look AI-like. Never make a definitive claim of authorship. Frame everything as likelihood and pattern-matching."""

_IMPROVEMENT_SYSTEM_PROMPT = """You are a professional writing coach specializing in making text sound more natural and human-like. Given an essay and specific sections that were flagged as potentially AI-generated, provide concrete rewrite suggestions.

Return a JSON object with:
- "suggestions": array of objects, each with:
  - "original_snippet": the flagged text (max 200 chars)
  - "issue": what makes it sound AI-like
  - "rewritten": a more natural, human-sounding version
  - "explanation": why the rewrite is more natural
- "general_tips": array of general writing tips to avoid AI-like patterns
- "overall_style_shift": a brief description of what the writer should adjust overall"""

_REPORT_SYSTEM_PROMPT = """You are a technical report writer. Generate a clear, professional AI detection report in natural language based on the provided analysis data. Write in plain English paragraphs (not JSON). Include:
1. Executive summary
2. Score interpretation
3. Key linguistic findings
4. Specific flagged patterns
5. Limitations disclaimer
6. Recommendations

Make it sound like a human expert wrote it, not a template."""


def _sanitize_text(text: str) -> str:
    """Replace Unicode line separators and other problematic chars with plain newline."""
    return text.replace("\u2028", "\n").replace("\u2029", "\n")


async def _call_openrouter(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    response_format: Optional[dict] = None,
    api_key: Optional[str] = None,
) -> str:
    key = api_key or OPENROUTER_API_KEY
    if not key or not key.strip():
        return json.dumps({"error": "No OpenRouter API key provided. Enter your key in the AI Enhancement panel or set OPENROUTER_API_KEY."})

    # Sanitize inputs to prevent Unicode encoding issues in Lambda environments
    system_prompt = _sanitize_text(system_prompt)
    user_message = _sanitize_text(user_message)

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ai-essay-detector",
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": 2000,
    }

    if response_format:
        body["response_format"] = response_format

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            detail = f"OpenRouter API error: {e.response.status_code}"
            try:
                detail += f" - {e.response.json().get('error', {}).get('message', '')}"
            except Exception:
                err_text = e.response.text[:500]
                detail += f" - {err_text}"
            return json.dumps({"error": detail})
        except (httpx.RequestError, json.JSONDecodeError, KeyError, IndexError, UnicodeEncodeError) as e:
            return json.dumps({"error": f"API request failed: {type(e).__name__}: {e}"})


async def second_opinion(text: str, word_count: int, api_key: Optional[str] = None) -> dict:
    msg = (
        f"Please analyze this essay for AI vs human authorship.\n\n"
        f"--- ESSAY TEXT ({word_count} words) ---\n{text[:8000]}"
    )
    raw = await _call_openrouter(
        _SECOND_OPINION_SYSTEM_PROMPT,
        msg,
        temperature=0.2,
        response_format={"type": "json_object"},
        api_key=api_key,
    )
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"error": "Failed to parse AI response", "raw": raw}


async def improvement_suggestions(text: str, highlighted_sections: list, api_key: Optional[str] = None) -> dict:
    flagged = []
    for h in highlighted_sections[:8]:
        flagged.append({
            "snippet": h.get("snippet", "")[:300],
            "reasons": h.get("reasons", []),
        })

    msg = (
        f"Here is an essay with flagged sections that may sound AI-generated. "
        f"Provide rewrite suggestions to make each flagged section sound more natural and human.\n\n"
        f"--- FULL ESSAY TEXT ---\n{text[:4000]}\n\n"
        f"--- FLAGGED SECTIONS ---\n{json.dumps(flagged, indent=2)}"
    )
    raw = await _call_openrouter(
        _IMPROVEMENT_SYSTEM_PROMPT,
        msg,
        temperature=0.4,
        response_format={"type": "json_object"},
        api_key=api_key,
    )
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"error": "Failed to parse AI response", "raw": raw}


async def generate_ai_report(
    text: str,
    ai_score: float,
    human_score: float,
    mixed_score: float,
    confidence: str,
    category_breakdown: dict,
    highlighted_sections: list,
    summary: str,
    api_key: Optional[str] = None,
) -> str:
    categories = {}
    for k, v in category_breakdown.items():
        score_val = v.get("score", v if isinstance(v, float) else 0)
        weight_val = v.get("weight", 0.07)
        categories[k] = {"score": score_val, "weight": weight_val}

    msg = (
        f"Generate an AI detection report in natural language prose based on this analysis:\n\n"
        f"AI Score: {ai_score:.1%}\n"
        f"Human Score: {human_score:.1%}\n"
        f"Mixed Score: {mixed_score:.1%}\n"
        f"Confidence: {confidence}\n"
        f"Summary: {summary}\n\n"
        f"Categories:\n{json.dumps(categories, indent=2)}\n\n"
        f"Flagged Sections: {len(highlighted_sections)}\n\n"
        f"Text snippet: {text[:2000]}"
    )
    return await _call_openrouter(
        _REPORT_SYSTEM_PROMPT,
        msg,
        temperature=0.5,
        api_key=api_key,
    )
