import sys
import os

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
