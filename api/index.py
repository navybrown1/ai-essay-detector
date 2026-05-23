import sys
import os

# Force UTF-8 encoding for stdout/stderr on Lambda (prevents ASCII codec errors)
os.environ["PYTHONIOENCODING"] = "utf-8"

# NLTK must download data to /tmp on Lambda's read-only filesystem
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

# Monkey-patch nltk.download to default to /tmp
import nltk
_original_download = nltk.download

def _patched_download(info_or_id, download_dir="/tmp/nltk_data", quiet=False, force=False, raise_on_error=True, prefix=""):
    os.makedirs(download_dir, exist_ok=True)
    return _original_download(info_or_id, download_dir=download_dir, quiet=quiet, force=force, raise_on_error=raise_on_error, prefix=prefix)

nltk.download = _patched_download

# Eagerly pre-download required NLTK data during cold-start initialization
# so the first request doesn't pay the download penalty.
try:
    for _pkg in ("punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{_pkg}", paths=["/tmp/nltk_data"])
        except LookupError:
            nltk.download(_pkg, quiet=True, download_dir="/tmp/nltk_data")
except Exception:
    # Don't fail startup if NLTK servers are unreachable; it'll retry on first use.
    pass

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
