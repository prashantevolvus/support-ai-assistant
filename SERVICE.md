Flux Support AI Assistant API

Overview
- FastAPI service exposing endpoints to upload support tickets/documents and answer troubleshooting queries using retrieval over stored data with an optional LLM.
- Uses SQLite for storage (file: ./data.db) and a TF‑IDF retriever for semantic search. A simple extractive answer generator is provided by default.

Run Locally
- Create a virtualenv and install deps: `pip install -r requirements.txt`
- Start the API: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Open docs at: `http://localhost:8000/docs`

Environment
- `LLM_PROVIDER` (optional): set to select an LLM backend in future; defaults to the simple local generator.
- `DATABASE_URL` (optional): set a SQLAlchemy URL if not using the default SQLite file.

Endpoints
- `GET /health`: health check.
- `POST /tickets` (JSON): create one ticket. Body: `{ external_id?, title, body, metadata? }`.
- `POST /tickets/upload` (multipart file): bulk upload tickets via `.json` (array of objects) or `.csv` (columns: `external_id|id`, `title|subject`, `body|description`, other columns saved into metadata).
- `POST /documents` (JSON): create one document. Body: `{ name, content, metadata? }`.
- `POST /documents/upload` (multipart files): upload one or more text/markdown files; content is stored as plain text.
- `POST /query` (JSON): ask a question. Body: `{ query, top_k?, use_llm? }`. Returns an answer and ranked sources.

Notes
- The retriever reindexes after uploads (cached and invalidated on writes).
- For a production LLM, implement a new provider in `app/llm.py` and select via `LLM_PROVIDER`.
