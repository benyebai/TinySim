from __future__ import annotations

import math
import re
from collections import Counter

from .models import Memory, RetrievalResult


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z']+")


class MemoryStream:
    """Chronological natural-language memory stream with simple retrieval."""

    def __init__(self) -> None:
        self.memories: list[Memory] = []
        self._next_id = 1

    def add(
        self,
        *,
        step: int,
        kind: str,
        text: str,
        importance: float,
        location: str,
        evidence_ids: list[int] | None = None,
        tags: list[str] | None = None,
    ) -> Memory:
        memory = Memory(
            id=self._next_id,
            step=step,
            kind=kind,
            text=text,
            importance=max(1.0, min(10.0, float(importance))),
            location=location,
            created_at=step,
            last_accessed=step,
            evidence_ids=evidence_ids or [],
            tags=tags or [],
        )
        self._next_id += 1
        self.memories.append(memory)
        return memory

    def recent(self, count: int = 20) -> list[Memory]:
        return self.memories[-count:]

    def retrieve(self, query: str, *, step: int, top_k: int = 5) -> list[RetrievalResult]:
        if not self.memories:
            return []

        scored: list[RetrievalResult] = []
        for memory in self.memories:
            recency = self._recency_score(memory, step)
            importance = memory.importance / 10.0
            relevance = self._relevance_score(query, memory)
            score = recency + importance + relevance
            scored.append(
                RetrievalResult(
                    memory=memory,
                    score=score,
                    recency=recency,
                    importance=importance,
                    relevance=relevance,
                )
            )

        scored.sort(key=lambda result: result.score, reverse=True)
        selected = scored[:top_k]
        for result in selected:
            result.memory.last_accessed = step
        return selected

    def to_dicts(self) -> list[dict]:
        return [memory.to_dict() for memory in self.memories]

    @staticmethod
    def _recency_score(memory: Memory, step: int) -> float:
        age = max(0, step - memory.created_at)
        return math.pow(0.93, age)

    @staticmethod
    def _relevance_score(query: str, memory: Memory) -> float:
        query_tokens = _token_counts(query)
        memory_tokens = _token_counts(
            " ".join([memory.kind, memory.location, memory.text, *memory.tags])
        )
        if not query_tokens or not memory_tokens:
            return 0.0

        dot = sum(query_tokens[token] * memory_tokens[token] for token in query_tokens)
        query_norm = math.sqrt(sum(value * value for value in query_tokens.values()))
        memory_norm = math.sqrt(sum(value * value for value in memory_tokens.values()))
        if query_norm == 0 or memory_norm == 0:
            return 0.0
        return dot / (query_norm * memory_norm)


def _token_counts(text: str) -> Counter[str]:
    stopwords = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "into",
        "about",
        "maya",
        "chen",
        "she",
        "her",
        "hers",
        "was",
        "were",
        "has",
        "had",
        "will",
        "would",
        "could",
        "should",
        "step",
    }
    tokens = TOKEN_RE.findall(text.lower())
    return Counter(token for token in tokens if token not in stopwords)
