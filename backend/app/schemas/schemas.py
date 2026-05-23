from pydantic import BaseModel
from typing import Optional


class ScanRequest(BaseModel):
    text: str
    title: Optional[str] = "Untitled"
    author_id: Optional[str] = None
    filename: Optional[str] = "pasted_text"


class ScanResponse(BaseModel):
    id: int
    ai_score: float
    human_score: float
    mixed_score: float
    confidence: str
    category_breakdown: dict
    highlighted_sections: list
    sentence_analysis: list
    paragraph_analysis: list
    summary: str
    disclaimer: str
    raw_text: Optional[str] = None


class HistoryItem(BaseModel):
    id: int
    filename: str
    title: str
    created_at: str
    ai_score: float
    human_score: float
    mixed_score: float
    confidence: str
    word_count: int


class ComparisonRequest(BaseModel):
    scan_ids: list[int]


class ComparisonResponse(BaseModel):
    scans: list[ScanResponse]
    similarity_analysis: Optional[dict] = None


class AIAnalysisRequest(BaseModel):
    text: str
    api_key: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    ai_likelihood: Optional[float] = None
    confidence: Optional[str] = None
    reasoning: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    verdict: Optional[str] = None
    error: Optional[str] = None


class AIImprovementRequest(BaseModel):
    text: str
    highlighted_sections: list
    api_key: Optional[str] = None


class AIImprovementSuggestion(BaseModel):
    original_snippet: str
    issue: str
    rewritten: str
    explanation: str


class AIImprovementResponse(BaseModel):
    suggestions: list[AIImprovementSuggestion] = []
    general_tips: list[str] = []
    overall_style_shift: Optional[str] = None
    error: Optional[str] = None


class AIReportRequest(BaseModel):
    text: str
    ai_score: float
    human_score: float
    mixed_score: float
    confidence: str
    category_breakdown: dict
    highlighted_sections: list
    summary: str
    api_key: Optional[str] = None
