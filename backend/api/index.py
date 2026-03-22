import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import and run the FastAPI app
from main import app

# Vercel serverless handler
def handler(request):
    return app(request.scope, request.receive, request.send)
