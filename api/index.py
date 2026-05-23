import sys
import os

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from fastapi import FastAPI
from app.main import app
from mangum import Mangum

# Vercel routes /api/* to this handler, so mount app at /api prefix
wrapper = FastAPI()
wrapper.mount("/api", app)

handler = Mangum(wrapper, lifespan="off")
