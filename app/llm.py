from __future__ import annotations

import os
from typing import List

from .schemas import Source


class AnswerGenerator:
    def generate(self, question: str, sources: List[Source]) -> str:
        raise NotImplementedError


class SimpleExtractiveAnswerGenerator(AnswerGenerator):
    def generate(self, question: str, sources: List[Source]) -> str:
        # Very simple heuristic: echo question and list key snippets
        lines = [
            f"Query: {question}",
            "Top findings (from similar tickets/documents):",
        ]
        for i, s in enumerate(sources, start=1):
            label = s.title or s.name or f"{s.type} {s.id}"
            snippet = (s.snippet or "").strip().replace("\n", " ")
            snippet = snippet[:300] + ("…" if len(snippet) > 300 else "")
            lines.append(f"{i}. {label} — score {s.score:.2f}: {snippet}")
        lines.append(
            "Note: Configure an LLM provider to synthesize richer answers."
        )
        return "\n".join(lines)


def get_answer_generator() -> AnswerGenerator:
    # Placeholder for future pluggable providers (e.g., OpenAI, Azure, etc.)
    # For now, always return the simple extractive generator.
    # To integrate a real LLM, implement a new AnswerGenerator and select via env vars.
    _provider = os.getenv("LLM_PROVIDER", "simple").lower()
    return SimpleExtractiveAnswerGenerator()

