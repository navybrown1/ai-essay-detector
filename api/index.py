import sys
import os

# NLTK must download data to /tmp on Lambda's read-only filesystem
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

# Monkey-patch nltk.download to default to /tmp
import nltk
_original_download = nltk.download

def _patched_download(info_or_id, download_dir="/tmp/nltk_data", quiet=False, force=False, raise_on_error=True, prefix=""):
    os.makedirs(download_dir, exist_ok=True)
    return _original_download(info_or_id, download_dir=download_dir, quiet=quiet, force=force, raise_on_error=raise_on_error, prefix=prefix)

nltk.download = _patched_download

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
