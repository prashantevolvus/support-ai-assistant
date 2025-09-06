# Flux Support AI Assistant (API)

FastAPI service that lets Flux support teams upload historical tickets and documents, then answer troubleshooting questions using retrieval over stored data with an optional LLM.

See also SERVICE.md for a concise API reference.

## Features

- Upload support tickets (single or bulk CSV/JSON)
- Upload relevant documents (text/markdown files)
- Retrieval‑augmented answering using TF‑IDF + cosine similarity
- SQLite persistence via SQLAlchemy
- Pluggable LLM stub for future synthesis

## Installation

- Prerequisites:
  - Python 3.9+
  - astral/uv (package manager)
    - macOS (Homebrew): `brew install uv`
    - macOS/Linux (script): `curl -LsSf https://astral.sh/uv/install.sh | sh`
    - Windows: see uv install options at https://docs.astral.sh/uv/
  - Optional: `just` command runner
    - macOS (Homebrew): `brew install just`
    - Debian/Ubuntu: `sudo apt-get install just` (or `cargo install just`)

- Setup in this repo:
  - Create venv: `uv venv .venv`
  - Activate: `source .venv/bin/activate`
  - Install deps: `uv pip install -r requirements.txt`

### Bootstrap script

Alternatively, run the bootstrap script (creates venv, installs deps, runs tests):

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh            # default: runs tests
./scripts/bootstrap.sh --no-test  # skip tests
./scripts/bootstrap.sh --force-venv --python 3.12  # recreate venv with Python 3.12
```

## Quickstart (uv)

Prereq: Install astral/uv (https://github.com/astral-sh/uv)

```bash
# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run tests
uv run pytest -q

# Start the API
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open interactive docs at http://localhost:8000/docs

## With Just

```bash
just venv        # create .venv with uv
just install     # install dependencies
just test        # run pytest
just run         # start the API (port 8000)
```

## API Endpoints (summary)

- GET `/health` — health check
- POST `/tickets` — create a ticket (JSON)
- POST `/tickets/upload` — bulk upload tickets (`.json` or `.csv`)
- POST `/documents` — create a document (JSON)
- POST `/documents/upload` — upload one or more text files
- POST `/query` — ask a question; returns an answer and ranked sources

Details and payload formats are documented in the OpenAPI docs and SERVICE.md.

## Configuration

- `DATABASE_URL` — SQLAlchemy URL (default: `sqlite:///./data.db`)
- `LLM_PROVIDER` — reserved for future LLM integration (default: simple)

## Project Structure

```
app/
  main.py        # FastAPI app and routes
  db.py          # DB engine and session helpers
  models.py      # SQLAlchemy models (Ticket, Document)
  schemas.py     # Pydantic request/response models
  retrieval.py   # TF‑IDF retriever
  ingest.py      # Parsers for JSON/CSV/text uploads
  llm.py         # Simple extractive answer generator
tests/
  test_app.py    # Smoke tests
requirements.txt
SERVICE.md
```

## Notes

- The retriever caches an index and reindexes after uploads.
- For a production LLM, implement a provider in `app/llm.py` and select via `LLM_PROVIDER`.

## GitHub Packages: Publish & Install

This repo includes a GitHub Actions workflow to build the package on tag pushes and optionally publish to GitHub Packages (Python registry).

### Publishing

1. Create a repository secret named `TWINE_REPOSITORY_URL` with your GitHub Packages Python upload endpoint.
   - Example (org-level): `https://upload.pypi.org/legacy/` (placeholder — replace with the GitHub Packages Python upload URL as per GitHub docs).
   - The workflow uses `GITHUB_TOKEN` for authentication; ensure workflow permissions include `packages: write` (already set).
2. Push a tag to trigger the workflow:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The workflow builds wheels/sdist and publishes using Twine.

### Installing from GitHub Packages

You need a token with `read:packages` scope. For local use, a classic PAT works.

- pip (one-off):

  ```bash
  export GITHUB_USER=<your-username>
  export GITHUB_TOKEN=<token-with-read:packages>
  pip install \
    --index-url https://${GITHUB_USER}:${GITHUB_TOKEN}@pip.pkg.github.com/<OWNER> \
    --extra-index-url https://pypi.org/simple \
    flux-support-ai-assistant
  ```

- uv:

  ```bash
  export GITHUB_USER=<your-username>
  export GITHUB_TOKEN=<token-with-read:packages>
  uv pip install \
    --index-url https://${GITHUB_USER}:${GITHUB_TOKEN}@pip.pkg.github.com/<OWNER> \
    --extra-index-url https://pypi.org/simple \
    flux-support-ai-assistant
  ```

Replace `<OWNER>` with your org or user that owns the repository.

After installing, you can run the server via the console script:

```bash
flux-assistant-api  # uses HOST/PORT env or 0.0.0.0:8000 by default
```
