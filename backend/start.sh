#!/usr/bin/env bash
set -euo pipefail
# Simple runner for Railway
export PYTHONUNBUFFERED=1
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
