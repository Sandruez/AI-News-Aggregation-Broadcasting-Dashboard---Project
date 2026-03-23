#!/bin/sh
# Startup script for Railway deployment
# Ensure PORT is set, fallback to 8000 for local development
PORT=${PORT:-8000}
exec uvicorn main:app --host 0.0.0.0 --port $PORT
