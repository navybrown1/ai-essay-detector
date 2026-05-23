# AI Essay Detector

An evidence-based tool that analyzes writing patterns to estimate whether a text was written by AI, a human, or a mixture of both. Built with transparent scoring, clear uncertainty communication, and ethical guardrails.

**This tool is probabilistic, not conclusive.** It identifies patterns correlated with AI-generated text but does not prove authorship. Never use it as the sole basis for academic or disciplinary decisions.

## Research Foundation

The detector evaluates 14 linguistic indicators based on peer-reviewed research:

| Indicator | Research Basis | Type |
|---|---|---|
| Sentence variation | Mitchell et al. 2023; Guo et al. 2023 | Research-supported |
| Lexical diversity | Uchendu et al. 2020; Tulchinskii et al. 2023 | Research-supported |
| Repetition patterns | Kobak et al. 2024; Sadasivan et al. 2023 | Research-supported |
| Transition choices | Liang et al. 2024 | Research-supported |
| Personal voice | Herbold et al. 2023 | Research-supported |
| Specificity | Wen & Wang 2024 | Heuristic |
| Readability profile | General stylometry | Heuristic |
| Semantic similarity | sentence-transformers | Heuristic/experimental |
| Citation behavior | Walters & Wilder 2023 | Heuristic |
| Paragraph structure | Clark et al. 2021 | Heuristic |
| Natural imperfection | Inversion of AI-smoothness | Experimental |
| Topic depth | Specificity analysis | Heuristic |
| Structural symmetry | Essay structure analysis | Heuristic |
| Predictability | Entropy-based analysis | Research-supported |

**Key references:**
- Guo, B. et al. (2023). "How Close is ChatGPT to Human Experts?" — arXiv:2301.07597
- Mitchell, E. et al. (2023). "DetectGPT: Zero-Shot Machine-Generated Text Detection" — arXiv:2301.11305
- Tulchinskii, A. et al. (2023). "AI-generated Text Detection via Language Model Perplexity" — arXiv:2306.01921
- Sadasivan, V. et al. (2023). "Can AI-Generated Text be Reliably Detected?" — arXiv:2303.11156
- Liang, W. et al. (2024). "Mapping the Increasing Use of LLMs in Scientific Papers" — arXiv:2404.01268

## Features

- **Paste or upload**: Text input or file upload (.txt, .docx, .pdf)
- **Three scores**: AI-likelihood, human-likelihood, mixed-writing probability
- **Confidence level**: Low / Medium / High indication
- **Category breakdown**: 14 linguistic indicators scored individually
- **Highlighted sections**: Paragraphs flagged for AI-like patterns
- **Sentence analysis**: Per-sentence AI pattern scoring
- **Paragraph analysis**: Depth and syntax assessment per paragraph
- **PDF export**: Full downloadable report
- **History**: Previous scans stored and viewable
- **Dark mode**: Light/dark theme toggle
- **Responsive**: Works on desktop and mobile

## Architecture

```
ai-essay-detector/
  backend/
    app/
      main.py                 # FastAPI server and API routes
      config.py               # Configuration and scoring weights
      database/
        models.py             # SQLAlchemy scan record model
        crud.py               # Database operations
      parsers/
        document_parser.py    # TXT/DOCX/PDF parsing
      detection/
        preprocessor.py       # Text cleaning, sentence/paragraph segmentation
        analyzer.py           # Main analysis orchestrator
        scoring.py            # Score computation and aggregation
        report.py             # PDF report generation (ReportLab)
        features/
          readability.py      # Flesch scores and readability patterns
          lexical_diversity.py # TTR, Maas, bigram/trigram diversity
          sentence_variation.py # Length CV, burstiness, consecutive similarity
          repetition.py       # Bigram/trigram/sentence-start repetition
          transitions.py      # AI vs human transition word analysis
          structure.py        # Paragraph length CV, intro/conclusion detection
          personal_voice.py   # First-person, hedging, contraction, colloquial markers
          specificity.py      # Vague vs concrete language ratio
          semantic_similarity.py # Cross-paragraph embedding similarity
          citation_analysis.py    # Citation presence and density
      schemas/
        schemas.py           # Pydantic request/response models
    data/sample_essays/       # Example texts for testing
  frontend/
    src/
      App.jsx                # Main app with tabs and state
      components/
        Dashboard.jsx         # Landing page with explanation
        InputPanel.jsx        # Text input and file upload
        ResultsPanel.jsx      # Scores, categories, highlights
        ScoreGauge.jsx        # Visual score display
        CategoryBreakdown.jsx # 14-category grid
        HighlightedText.jsx   # Flagged paragraph display
        HistoryPanel.jsx      # Past scan table
        ReportExport.jsx      # PDF download trigger
      styles/globals.css      # Complete styling with dark mode
      utils/api.js            # API client functions
  run.sh                     # One-command launcher
  README.md
```

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Quick start

```bash
git clone <repo-url>
cd ai-essay-detector
chmod +x run.sh
./run.sh
```

This will:
1. Create a Python venv and install dependencies
2. Install npm packages
3. Start the backend on port 8000
4. Start the frontend on port 3000

### Manual setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /analyze | Analyze essay text or file |
| GET | /history | Recent scan history |
| GET | /scan/{id} | Get scan by ID |
| DELETE | /scan/{id} | Delete a scan |
| GET | /author/{id} | Scans by author ID |
| GET | /compare?ids=1,2,3 | Compare multiple scans |
| GET | /report/{id} | Download PDF report |
| GET | /health | Health check |

## Scoring Methodology

The final AI-likelihood score is a weighted composite of 14 linguistic indicators. Each indicator produces a 0-1 score where higher values suggest AI-writing patterns. The weighted sum is calibrated to avoid extreme scores (range: 0.05-0.95).

**Scoring weights:**
- Personal voice: 10% (highest weight — strong research basis)
- Sentence variation: 9%
- Evidence specificity: 9%
- Lexical diversity: 8%
- Predictability: 8%
- Repetitive phrasing: 8%
- Natural imperfection: 8%
- Paragraph rhythm: 7%
- Generic filler: 6%
- Transition patterns: 6%
- Topic depth: 6%
- Citation behavior: 5%
- Readability profile: 5%
- Structural symmetry: 5%

The mixed-writing score measures how many indicators produce contradictory signals (some highly AI-like, others highly human-like). A high mixed score does not mean "definitely mixed" — it means the text has internally inconsistent linguistic patterns.

Confidence is determined by the variance across category scores. High variance = high confidence in the classification; low variance = mixed signals = low confidence.

## Limitations

1. **No detection is perfect.** All AI text detectors have measurable false positive and false negative rates.
2. **Formal/academic writing** naturally exhibits low variation, formulaic structure, and careful transitions — the same patterns AI text shows. Expect higher false positives for these genres.
3. **Non-native English** can trigger false positives due to reduced lexical diversity and simpler sentence structures.
4. **Short texts** (< 100 words) lack sufficient data for reliable analysis.
5. **AI-assisted editing** (Grammarly, ChatGPT polish, AI rewriting tools) is substantially indistinguishable from AI generation.
6. **Adversarial evasion** — someone who knows these indicators can deliberately modify AI text to reduce detection scores.
7. **Calibration drift** — as language models evolve, the statistical fingerprints of AI text change.
8. **The tool is text-only** — it does not analyze metadata, writing process data, or version history.

## Sample Essays

Three sample essays are included in `backend/data/sample_essays/`:
- `human_sample.txt` — A personally-written essay with natural voice and variation
- `ai_sample.txt` — An AI-generated essay with formulaic structure and transitions
- `mixed_sample.txt` — A hybrid combining human voice with AI-polished sections

## Future Improvements

- **ML classifier integration**: Train a classifier on known human/AI corpora and calibrate against the heuristic features
- **Perplexity scoring**: Integrate with GPT-2 output detection or similar perplexity-based approaches
- **Stylometric fingerprinting**: Analyze writing style consistency against known author samples
- **Adversarial robustness testing**: Systematically test against evasion techniques
- **Batch analysis**: Compare multiple essays simultaneously
- **API rate limiting and authentication**: Production hardening
- **More file formats**: Support for .md, .rtf, .odt
- **User accounts**: Persistent history per user with authentication

## License

MIT
