import sys
import os
import json

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app
from mangum import Mangum

_mangum = Mangum(app, lifespan="off")


def handler(event, context):
    # Debug: log what we receive
    print(f"DEBUG EVENT PATHS: rawPath={event.get('rawPath')}, path={event.get('path')}, requestContext={event.get('requestContext', {}).get('http', {}).get('path')}")
    
    # Strip /api prefix so FastAPI routes match
    path = event.get("rawPath") or event.get("path", "")
    if path.startswith("/api/"):
        new_path = path[4:]
        event["rawPath"] = new_path
        if "path" in event:
            event["path"] = new_path
        print(f"DEBUG REWRITTEN: {path} -> {new_path}")
    
    return _mangum(event, context)
