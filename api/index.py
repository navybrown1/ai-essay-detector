import sys
import os

# NLTK must download data to /tmp on Lambda's read-only filesystem
os.environ["NLTK_DATA"] = "/tmp/nltk_data"

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
