import os
import json
import datetime
import hashlib
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .config import DATABASE_URL
from .database.models import init_db, ScanRecord
from .database.crud import save_scan, get_scan, get_recent_scans, \
    get_scans_by_author, delete_scan, hash_text
from .parsers.document_parser import parse_file
from .detection.analyzer import EssayAnalyzer
from .detection.report import generate_pdf_report
from .schemas.schemas import (
    ScanResponse, HistoryItem,
    AIAnalysisRequest, AIAnalysisResponse,
    AIImprovementRequest, AIImprovementResponse,
    AIImprovementSuggestion, AIReportRequest,
)
from .ai_analysis import second_opinion, improvement_suggestions, generate_ai_report

app = FastAPI(title="AI Essay Detector", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        },
    )

_SessionLocal = None
analyzer = EssayAnalyzer()


def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = init_db(DATABASE_URL)
    return _SessionLocal


def get_db():
    db = _get_session_local()()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}


@app.get("/api/health")
def api_health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}


@app.post("/analyze", response_model=ScanResponse)
def analyze_essay(
    text: str = Form(""),
    title: str = Form("Untitled"),
    filename: str = Form("pasted_text"),
    author_id: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    if file and file.filename:
        content = file.file.read()
        try:
            text = parse_file(file.filename, content)
        except ValueError as e:
            raise HTTPException(400, str(e))
        filename = file.filename

    if not text or len(text.strip()) < 20:
        raise HTTPException(400, "Text must be at least 20 characters.")

    result = analyzer.analyze(text)

    th = hash_text(text)
    record = ScanRecord(
        filename=filename,
        essay_title=title,
        text_hash=th,
        word_count=result["word_count"],
        ai_score=result["ai_score"],
        human_score=result["human_score"],
        mixed_score=result["mixed_score"],
        confidence=result["confidence"],
        category_scores=result["category_breakdown"],
        highlighted_sections=result["highlighted_sections"],
        sentence_scores=result["sentence_analysis"],
        paragraph_scores=result["paragraph_analysis"],
        full_report=result,
        author_id=author_id,
    )
    scan_id = save_scan(db, record)

    return ScanResponse(
        id=scan_id,
        ai_score=result["ai_score"],
        human_score=result["human_score"],
        mixed_score=result["mixed_score"],
        confidence=result["confidence"],
        category_breakdown=result["category_breakdown"],
        highlighted_sections=result["highlighted_sections"],
        sentence_analysis=result["sentence_analysis"],
        paragraph_analysis=result["paragraph_analysis"],
        summary=result["summary"],
        disclaimer=result["disclaimer"],
    )


@app.get("/history", response_model=list[HistoryItem])
def history(limit: int = 20, db: Session = Depends(get_db)):
    scans = get_recent_scans(db, limit)
    return [
        HistoryItem(
            id=s.id,
            filename=s.filename,
            title=s.essay_title,
            created_at=s.created_at.isoformat(),
            ai_score=s.ai_score,
            human_score=s.human_score,
            mixed_score=s.mixed_score,
            confidence=s.confidence,
            word_count=s.word_count,
        )
        for s in scans
    ]


@app.get("/scan/{scan_id}", response_model=ScanResponse)
def get_scan_result(scan_id: int, db: Session = Depends(get_db)):
    record = get_scan(db, scan_id)
    if not record:
        raise HTTPException(404, "Scan not found.")
    r = record.full_report
    return ScanResponse(
        id=record.id,
        ai_score=r["ai_score"],
        human_score=r["human_score"],
        mixed_score=r["mixed_score"],
        confidence=r["confidence"],
        category_breakdown=r["category_breakdown"],
        highlighted_sections=r["highlighted_sections"],
        sentence_analysis=r["sentence_analysis"],
        paragraph_analysis=r["paragraph_analysis"],
        summary=r["summary"],
        disclaimer=r["disclaimer"],
    )


@app.delete("/scan/{scan_id}")
def delete_scan_result(scan_id: int, db: Session = Depends(get_db)):
    if not delete_scan(db, scan_id):
        raise HTTPException(404, "Scan not found.")
    return {"ok": True}


@app.get("/author/{author_id}")
def get_author_scans(author_id: str, db: Session = Depends(get_db)):
    scans = get_scans_by_author(db, author_id)
    return [
        HistoryItem(
            id=s.id,
            filename=s.filename,
            title=s.essay_title,
            created_at=s.created_at.isoformat(),
            ai_score=s.ai_score,
            human_score=s.human_score,
            mixed_score=s.mixed_score,
            confidence=s.confidence,
            word_count=s.word_count,
        )
        for s in scans
    ]


@app.get("/compare")
def compare_scans(ids: str, db: Session = Depends(get_db)):
    id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    if len(id_list) < 2:
        raise HTTPException(400, "Provide at least 2 scan IDs.")

    scans = []
    for sid in id_list:
        record = get_scan(db, sid)
        if record and record.full_report:
            scans.append(record.full_report)

    if len(scans) < 2:
        raise HTTPException(404, "Could not retrieve all scans.")

    ai_scores = [s["ai_score"] for s in scans]
    human_scores = [s["human_score"] for s in scans]

    return {
        "scan_count": len(scans),
        "ai_scores": [round(s, 3) for s in ai_scores],
        "human_scores": [round(s, 3) for s in human_scores],
        "ai_range": round(max(ai_scores) - min(ai_scores), 3),
        "consistency": "Consistent" if max(ai_scores) - min(ai_scores) < 0.15 else "Variable",
        "scans": scans,
    }


@app.post("/ai-analyze", response_model=AIAnalysisResponse)
async def ai_analyze(req: AIAnalysisRequest):
    text = req.text.strip()
    if len(text) < 50:
        raise HTTPException(400, "Text must be at least 50 characters for AI analysis.")

    try:
        word_count = len(text.split())
        result = await second_opinion(text, word_count, api_key=req.api_key)
        return AIAnalysisResponse(**result)
    except Exception as e:
        return AIAnalysisResponse(error=f"Analysis failed: {type(e).__name__}: {e}")


@app.post("/ai-improve", response_model=AIImprovementResponse)
async def ai_improve(req: AIImprovementRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Text is required.")

    try:
        result = await improvement_suggestions(text, req.highlighted_sections, api_key=req.api_key)
        if "error" in result:
            return AIImprovementResponse(error=result["error"])

        suggestions_raw = result.get("suggestions", [])
        suggestions = []
        for s in suggestions_raw:
            if isinstance(s, dict):
                suggestions.append(AIImprovementSuggestion(
                    original_snippet=s.get("original_snippet", "")[:300],
                    issue=s.get("issue", ""),
                    rewritten=s.get("rewritten", ""),
                    explanation=s.get("explanation", ""),
                ))

        return AIImprovementResponse(
            suggestions=suggestions[:8],
            general_tips=result.get("general_tips", []),
            overall_style_shift=result.get("overall_style_shift"),
        )
    except Exception as e:
        return AIImprovementResponse(error=f"Improvement failed: {type(e).__name__}: {e}")


@app.post("/ai-report/{scan_id}")
async def ai_download_report(scan_id: int, req: AIReportRequest, db: Session = Depends(get_db)):
    record = get_scan(db, scan_id)
    if not record:
        raise HTTPException(404, "Scan not found.")

    try:
        report_text = await generate_ai_report(
            text=req.text,
            ai_score=req.ai_score,
            human_score=req.human_score,
            mixed_score=req.mixed_score,
            confidence=req.confidence,
            category_breakdown=req.category_breakdown,
            highlighted_sections=req.highlighted_sections,
            summary=req.summary,
            api_key=req.api_key,
        )
        return {"report": report_text}
    except Exception as e:
        return {"report": f"Report generation failed: {type(e).__name__}: {e}"}


@app.get("/report/{scan_id}")
def download_report(scan_id: int, db: Session = Depends(get_db)):
    record = get_scan(db, scan_id)
    if not record or not record.full_report:
        raise HTTPException(404, "Scan not found.")

    r = record.full_report
    pdf_bytes = generate_pdf_report(
        text=record.full_report.get("_raw_text", ""),
        ai_score=r["ai_score"],
        human_score=r["human_score"],
        mixed_score=r["mixed_score"],
        confidence=r["confidence"],
        category_breakdown=r["category_breakdown"],
        highlighted_sections=r["highlighted_sections"],
        summary=r["summary"],
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="essay_report_{scan_id}.pdf"'
        },
    )


# Also register /api/ prefixed versions for Vercel routing
for route in list(app.routes):
    if hasattr(route, "path") and not route.path.startswith("/api/"):
        api_path = "/api" + route.path
        for method in route.methods or []:
            if method == "GET":
                app.get(api_path, response_model=getattr(route, "response_model", None))(route.endpoint)
            elif method == "POST":
                app.post(api_path, response_model=getattr(route, "response_model", None))(route.endpoint)
            elif method == "DELETE":
                app.delete(api_path, response_model=getattr(route, "response_model", None))(route.endpoint)
            elif method == "PUT":
                app.put(api_path, response_model=getattr(route, "response_model", None))(route.endpoint)
