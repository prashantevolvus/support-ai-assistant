from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    external_id: Optional[str] = None
    title: str
    body: str
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Arbitrary metadata")


class TicketRead(BaseModel):
    id: int
    external_id: Optional[str] = None
    title: str
    body: str
    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    name: str
    content: str
    metadata: Optional[dict[str, Any]] = None


class DocumentRead(BaseModel):
    id: int
    name: str
    content: str
    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    use_llm: bool = False


class Source(BaseModel):
    type: str
    id: int
    score: float
    title: Optional[str] = None
    name: Optional[str] = None
    snippet: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]

