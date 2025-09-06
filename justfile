# Justfile for common development tasks

uv := "uv"
app := "app.main:app"
port := "8000"

default:
    @just --list

# Create a virtual environment using uv
venv:
    {{uv}} venv .venv

# Install dependencies into the venv
install: venv
    . .venv/bin/activate && {{uv}} pip install -r requirements.txt

# Run tests via uv
test:
    {{uv}} run pytest

# Start the FastAPI server
run:
    {{uv}} run uvicorn {{app}} --reload --host 0.0.0.0 --port {{port}}

# Clean Python caches
clean:
    find . -name '__pycache__' -type d -prune -exec rm -rf {} +
    find . -name '*.py[co]' -delete

