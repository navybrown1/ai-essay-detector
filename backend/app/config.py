import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/essay_detector.db")

MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/tmp/essay_models")

SPACY_MODEL = "en_core_web_sm"

SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"

MAX_TEXT_LENGTH = 50000

UPLOAD_DIR = "/tmp/essay_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

REPORT_DIR = "/tmp/essay_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

SCORING_WEIGHTS = {
    "predictability": 0.08,
    "sentence_variation": 0.09,
    "paragraph_rhythm": 0.07,
    "repetitive_phrasing": 0.08,
    "generic_filler": 0.06,
    "transition_patterns": 0.06,
    "evidence_specificity": 0.09,
    "personal_voice": 0.10,
    "natural_imperfection": 0.08,
    "citation_behavior": 0.05,
    "readability_profile": 0.05,
    "topic_depth": 0.06,
    "structural_symmetry": 0.05,
    "lexical_diversity": 0.08,
}
