# AI Essay Detector - Comprehensive Handoff Document

## Project Overview
AI-powered essay detection web application with heuristic analysis + DeepSeek V4 Flash AI analysis via OpenRouter. Deployed to Vercel with GitHub integration.

**Production URL:** https://ai-essay-detector-henna.vercel.app
**GitHub Repo:** https://github.com/navybrown1/ai-essay-detector

## Architecture

```
ai-essay-detector/
├── api/index.py              # Vercel entry point (mangum handler)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app with 11 endpoints
│   │   ├── config.py         # Configuration (DB, API keys, weights)
│   │   ├── ai_analysis.py    # OpenRouter/DeepSeek integration
│   │   ├── schemas/          # Pydantic models
│   │   ├── detection/        # Heuristic analysis engine
│   │   │   ├── analyzer.py   # Main EssayAnalyzer class
│   │   │   ├── scoring.py    # Feature computation
│   │   │   ├── preprocessor.py # Text preprocessing (NLTK)
│   │   │   ├── features/     # Individual feature detectors
│   │   │   └── report.py     # PDF report generation
│   │   ├── database/         # SQLite + SQLAlchemy
│   │   └── parsers/          # File parsers (PDF, DOCX, TXT)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React app
│   │   ├── main.jsx          # React entry point
│   │   ├── components/       # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── InputPanel.jsx
│   │   │   ├── ResultsPanel.jsx
│   │   │   ├── HistoryPanel.jsx
│   │   │   ├── ScoreGauge.jsx
│   │   │   ├── CategoryBreakdown.jsx
│   │   │   ├── HighlightedText.jsx
│   │   │   └── ReportExport.jsx
│   │   ├── utils/api.js      # API client
│   │   └── styles/globals.css
│   ├── index.html
│   └── vite.config.js
├── vercel.json               # Vercel config (Python + static builds)
├── pyproject.toml            # Python dependencies for Vercel
├── requirements.txt          # Root requirements (Vercel)
└── package.json              # Frontend dependencies
```

## What's Implemented

### Backend (FastAPI)
- **14-feature heuristic analysis** scoring AI vs human likelihood
- **SQLite database** with scan history, author tracking, comparisons
- **File parsing**: PDF (pdfplumber), DOCX (python-docx), TXT
- **PDF report generation** (reportlab)
- **3 AI endpoints** via OpenRouter:
  - `POST /ai-analyze` - Second opinion from DeepSeek
  - `POST /ai-improve` - Writing improvement suggestions
  - `POST /ai-report/{scan_id}` - AI-powered detailed report
- **Lazy imports** for heavy packages (numpy, textstat, reportlab) to fix Lambda cold start
- **Lambda-specific fixes**:
  - SQLite DB path: `/tmp/essay_detector.db` (read-only filesystem)
  - NLTK data downloads to `/tmp/nltk_data` via monkey-patched `nltk.download`
  - Auto-generated `/api/` prefixed routes for Vercel routing

### Frontend (React + Vite)
- Tabbed interface: Analyze, Results, History
- Text input + file upload (drag & drop)
- Real-time analysis with visual gauges
- Category breakdown with interpretations
- Highlighted sections showing AI patterns
- Sentence-by-sentence and paragraph analysis
- History panel with scan management
- Dark/light theme toggle
- **AI Enhancement panel** (collapsible):
  - OpenRouter API key input (stored in localStorage)
  - "Run DeepSeek Analysis" button
  - AI opinion gauge + strengths/weaknesses + verdict
  - Rewrite suggestions with before/after
  - AI-powered report generation

### Deployment
- **GitHub**: `navybrown1/ai-essay-detector`
- **Vercel**: Auto-deploys on push to main
- **Environment**: `OPENROUTER_API_KEY` (optional, can be provided via frontend)

## Current Status

### ✅ Working
- Backend builds and deploys successfully
- All API endpoints respond correctly
- Heuristic analysis returns full results
- Database operations work
- AI endpoints work (when API key provided)

### ❌ Not Working
**FRONTEND DISPLAYS BLANK WHITE PAGE**
- HTML loads correctly
- JS/CSS assets return 200
- React app likely has runtime error causing blank screen
- **This is the #1 priority fix needed**

## Known Issues

1. **Blank Frontend (CRITICAL)**
   - Browser shows white screen
   - Tab title "AI Essay Detector" loads
   - Need to check browser console for React runtime errors
   - Possible causes:
     - Missing polyfill or import error
     - React StrictMode double-render issue
     - CSS causing invisible content
     - JavaScript exception before render

2. **Vercel Routing**
   - Vercel routes `/api/*` to Python handler
   - FastAPI routes duplicated with `/api/` prefix at runtime
   - This is working but could be cleaner

3. **Lambda Cold Start**
   - First request after deploy takes 5-10s
   - Subsequent requests are fast
   - Heavy package imports deferred via lazy loading

4. **NLTK Data**
   - Downloads on first use (after each cold start)
   - Stored in `/tmp/nltk_data`
   - Adds ~2-3s to first analysis

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/analyze` | POST | Analyze essay text/file |
| `/api/history` | GET | Get scan history |
| `/api/scan/{id}` | GET | Get specific scan |
| `/api/scan/{id}` | DELETE | Delete scan |
| `/api/author/{id}` | GET | Get scans by author |
| `/api/compare?ids=1,2` | GET | Compare multiple scans |
| `/api/report/{id}` | GET | Download PDF report |
| `/api/ai-analyze` | POST | AI second opinion |
| `/api/ai-improve` | POST | AI writing suggestions |
| `/api/ai-report/{id}` | POST | AI detailed report |

## Environment Variables

```bash
# Required for AI features (optional - can use frontend input)
OPENROUTER_API_KEY=sk-or-v1-...

# Optional overrides
OPENROUTER_MODEL=openrouter/free  # default
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DATABASE_URL=sqlite:////tmp/essay_detector.db  # default for Lambda
```

## Configuration (`backend/app/config.py`)

- **SCORING_WEIGHTS**: 14 features with weights summing to 1.0
- **MAX_TEXT_LENGTH**: 50000 characters
- **Model**: `openrouter/free` (generic free router, auto-selects from 25 free models)

## Key Files to Review

1. **`frontend/src/main.jsx`** - React entry point (check for errors)
2. **`frontend/src/App.jsx`** - Main app component
3. **`frontend/src/utils/api.js`** - API client (`API_BASE = "/api"`)
4. **`api/index.py`** - Vercel handler with mangum
5. **`backend/app/main.py`** - FastAPI routes + global exception handler
6. **`vercel.json`** - Build config

## How to Fix the Blank Page

1. Check browser console for JavaScript errors
2. Check if React is mounting properly:
   ```jsx
   // In main.jsx, add error boundary or try/catch
   ```
3. Verify all imports resolve correctly
4. Check if CSS is hiding content (`display: none`, `visibility: hidden`)
5. Test locally with `npm run dev` in `frontend/` directory
6. Check Vite build output for errors

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Deployment Commands

```bash
# Deploy to Vercel
vercel --prod --yes

# Or push to GitHub (auto-deploys)
git push origin main
```

## Testing the API

```bash
# Health check
curl https://ai-essay-detector-henna.vercel.app/api/health

# Analyze text
curl -X POST https://ai-essay-detector-henna.vercel.app/api/analyze \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Your essay text here..."

# AI analysis (requires API key)
curl -X POST https://ai-essay-detector-henna.vercel.app/api/ai-analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your essay...", "api_key": "sk-or-v1-..."}'
```

## Next Steps for Kimi

1. **FIX BLANK FRONTEND** (Priority #1)
   - Debug React runtime errors
   - Check browser console
   - Verify build output
   - Test locally

2. **Clean up `/api/` route duplication**
   - Currently auto-generates `/api/` prefixed copies
   - Should use FastAPI APIRouter with prefix instead

3. **Add loading states**
   - Better UX during Lambda cold starts
   - Show "Warming up..." message

4. **Error handling**
   - Frontend error boundaries
   - Better error messages for users

5. **Performance**
   - Pre-download NLTK data during build
   - Bundle size optimization
   - Consider CDN for assets

6. **Features**
   - Batch analysis (multiple files)
   - Export results as JSON/CSV
   - User accounts/authentication
   - Comparison visualization

## Contact/Resources

- **GitHub Issues**: https://github.com/navybrown1/ai-essay-detector/issues
- **Vercel Dashboard**: https://vercel.com/edwin-browns-projects/ai-essay-detector
- **OpenRouter**: https://openrouter.ai/docs

---

**Last Updated:** 2026-05-23
**Status:** Backend fully functional, frontend blank page needs fixing
