import sys
import os
import traceback

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

try:
    from app.main import app
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except Exception:
    from fastapi import FastAPI
    from mangum import Mangum
    app = FastAPI()

    @app.get("/api/health")
    def health():
        return {"status": "error", "detail": traceback.format_exc()}

    handler = Mangum(app, lifespan="off")
