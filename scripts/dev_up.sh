#!/usr/bin/env bash
set -euo pipefail

# Determine project root (one level up from this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

cd "${PROJECT_ROOT}"
echo "[dev_up] Project root: ${PROJECT_ROOT}"

# Start Postgres container
echo "[dev_up] Starting Postgres container (if not already running)..."
docker compose up -d db

# Initialize database schema
echo "[dev_up] Initializing database schema (if needed)..."
PYTHONPATH="${PROJECT_ROOT}" python scripts/init_db.py

echo "[dev_up] Done."
echo "[dev_up] You can now run the API with:"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"