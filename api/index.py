import sys
import os
import json

here = os.path.dirname(__file__)
backend_dir = os.path.join(here, "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

entrypoint = None


def handler(event, context):
    global entrypoint
    if entrypoint is None:
        try:
            from app.main import app
            from mangum import Mangum
            entrypoint = Mangum(app, lifespan="off")
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"content-type": "application/json"},
                "body": json.dumps({"error": str(e), "type": type(e).__name__}),
            }
    try:
        return entrypoint(event, context)
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": str(e), "type": type(e).__name__}),
        }
