import sys
import os

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app
from mangum import Mangum

_mangum = Mangum(app, lifespan="off")


def handler(event, context):
    # Strip /api prefix so FastAPI routes match
    path = event.get("rawPath") or event.get("path", "")
    if path.startswith("/api/"):
        event["rawPath"] = path[4:]
        if "path" in event:
            event["path"] = path[4:]
    return _mangum(event, context)
