from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Ticket, Document


@dataclass
class RetrievedItem:
    type: str  # 'ticket' or 'document'
    id: int
    text: str
    title: str | None = None
    name: str | None = None
    score: float = 0.0


class Retriever:
    def __init__(self) -> None:
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._items: list[RetrievedItem] = []
        self._dirty = True

    def mark_dirty(self):
        self._dirty = True

    def _load_items(self, db: Session):
        items: list[RetrievedItem] = []
        # Load tickets
        tickets = db.scalars(select(Ticket)).all()
        for t in tickets:
            text = (t.title or "") + "\n" + (t.body or "")
            items.append(RetrievedItem(type="ticket", id=t.id, text=text, title=t.title))
        # Load documents
        docs = db.scalars(select(Document)).all()
        for d in docs:
            items.append(RetrievedItem(type="document", id=d.id, text=d.content or "", name=d.name))
        self._items = items

    def _ensure_index(self, db: Session):
        if not self._dirty and self._vectorizer is not None and self._matrix is not None:
            return
        self._load_items(db)
        corpus = [it.text for it in self._items]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        if corpus:
            self._matrix = self._vectorizer.fit_transform(corpus)
        else:
            self._matrix = None
        self._dirty = False

    def query(self, db: Session, text: str, top_k: int = 5) -> List[RetrievedItem]:
        self._ensure_index(db)
        if self._matrix is None or self._vectorizer is None or not self._items:
            return []
        q_vec = self._vectorizer.transform([text])
        sims = cosine_similarity(q_vec, self._matrix).flatten()
        idxs = np.argsort(-sims)[:top_k]
        results: list[RetrievedItem] = []
        for idx in idxs:
            item = self._items[int(idx)]
            score = float(sims[int(idx)])
            results.append(RetrievedItem(
                type=item.type,
                id=item.id,
                text=item.text,
                title=item.title,
                name=item.name,
                score=score,
            ))
        return results

