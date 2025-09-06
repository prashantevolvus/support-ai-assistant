#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
Bootstrap Flux Support AI Assistant

Usage:
  scripts/bootstrap.sh [--force-venv] [--no-test] [--python <version>]

Options:
  --force-venv       Recreate .venv even if it exists
  --no-test          Skip running pytest after install
  --python <version> Use a specific Python version for venv (e.g., 3.12)

This script uses 'uv' to create a virtual environment, install dependencies
from requirements.txt, and run the test suite. It does not modify your shell;
you can activate the venv with: source .venv/bin/activate
USAGE
}

FORCE_VENV=0
RUN_TESTS=1
PY_VER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force-venv)
      FORCE_VENV=1
      shift
      ;;
    --no-test)
      RUN_TESTS=0
      shift
      ;;
    --python)
      PY_VER="$2"
      shift 2
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage
      exit 1
      ;;
  esac
done

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: 'uv' not found. Install uv first (e.g., 'brew install uv' or see https://docs.astral.sh/uv/)." >&2
  exit 1
fi

echo "[1/3] Setting up virtual environment (.venv)"
if [[ $FORCE_VENV -eq 1 && -d .venv ]]; then
  rm -rf .venv
fi

if [[ ! -d .venv ]]; then
  if [[ -n "$PY_VER" ]]; then
    uv venv --python "$PY_VER" .venv
  else
    uv venv .venv
  fi
else
  echo ".venv already exists; reuse (use --force-venv to recreate)"
fi

echo "[2/3] Installing dependencies from requirements.txt"
uv pip install -r requirements.txt

if [[ $RUN_TESTS -eq 1 ]]; then
  echo "[3/3] Running test suite"
  uv run pytest -q
else
  echo "[3/3] Skipping tests (per --no-test)"
fi

echo
echo "Done. Next steps:"
echo "  - Activate venv:   source .venv/bin/activate"
echo "  - Run API:         uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
if command -v just >/dev/null 2>&1; then
  echo "  - Or with Just:    just run"
else
  echo "  - (Optional) Install 'just' for shortcuts: brew install just"
fi

