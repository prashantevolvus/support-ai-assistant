from __future__ import annotations

import json
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, get_engine, get_session_factory, session_scope
from .llm import get_answer_generator
from .models import Document, Ticket
from .retrieval import Retriever
from .schemas import (
    DocumentCreate,
    DocumentRead,
    QueryRequest,
    QueryResponse,
    Source,
    TicketCreate,
    TicketRead,
)
from . import ingest


app = FastAPI(title="Flux Support AI Assistant", version="0.1.0")

# CORS: loosen for local dev; adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database init
engine = get_engine()
Base.metadata.create_all(bind=engine)
SessionLocal = get_session_factory()


# Global singleton retriever
retriever = Retriever()


def get_db() -> Session:
    with session_scope(SessionLocal) as session:
        yield session


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    t = Ticket(
        external_id=payload.external_id,
        title=payload.title,
        body=payload.body,
        metadata_json=json.dumps(payload.metadata) if payload.metadata else None,
    )
    db.add(t)
    db.flush()  # get ID
    retriever.mark_dirty()
    return TicketRead(
        id=t.id,
        external_id=t.external_id,
        title=t.title,
        body=t.body,
        metadata=json.loads(t.metadata_json) if t.metadata_json else None,
    )


@app.post("/tickets/upload", response_model=dict)
async def upload_tickets(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    created = 0
    try:
        if file.filename.endswith(".json"):
            items = ingest.parse_json_tickets(content)
        elif file.filename.endswith(".csv"):
            items = ingest.parse_csv_tickets(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format; use .json or .csv")
        for ext_id, title, body, meta in items:
            t = Ticket(
                external_id=ext_id,
                title=title,
                body=body,
                metadata_json=json.dumps(meta) if meta else None,
            )
            db.add(t)
            created += 1
    finally:
        retriever.mark_dirty()
    return {"created": created}


@app.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    d = Document(name=payload.name, content=payload.content, metadata_json=json.dumps(payload.metadata) if payload.metadata else None)
    db.add(d)
    db.flush()
    retriever.mark_dirty()
    return DocumentRead(id=d.id, name=d.name, content=d.content, metadata=json.loads(d.metadata_json) if d.metadata_json else None)


@app.post("/documents/upload", response_model=dict)
async def upload_documents(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    created = 0
    for f in files:
        content = await f.read()
        text = ingest.parse_text_file(content)
        d = Document(name=f.filename, content=text)
        db.add(d)
        created += 1
    retriever.mark_dirty()
    return {"created": created}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, db: Session = Depends(get_db)):
    results = retriever.query(db=db, text=req.query, top_k=req.top_k)
    sources: list[Source] = []
    for r in results:
        # simple snippet: first 500 chars
        snippet = r.text[:500]
        sources.append(
            Source(type=r.type, id=r.id, score=r.score, title=r.title, name=r.name, snippet=snippet)
        )
    generator = get_answer_generator()
    answer = generator.generate(req.query, sources)
    return QueryResponse(answer=answer, sources=sources)


# Convenience root
@app.get("/")
def root():
    return {"name": "Flux Support AI Assistant", "version": "0.1.0"}


def main():
    # Console entrypoint: run the API via uvicorn
    import os
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
