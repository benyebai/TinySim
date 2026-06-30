from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Memory:
    id: int
    step: int
    kind: str
    text: str
    importance: float
    location: str
    created_at: int
    last_accessed: int
    evidence_ids: list[int] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalResult:
    memory: Memory
    score: float
    recency: float
    importance: float
    relevance: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory": self.memory.to_dict(),
            "score": round(self.score, 4),
            "recency": round(self.recency, 4),
            "importance": round(self.importance, 4),
            "relevance": round(self.relevance, 4),
        }


@dataclass
class Decision:
    action: str
    destination: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class ReflectionDraft:
    text: str
    evidence_ids: list[int]
    importance: float = 8.0


@dataclass
class StepLog:
    step: int
    time_label: str
    location_before: str
    observation: Memory
    retrieved: list[RetrievalResult]
    decision: Decision
    outcome: Memory
    location_after: str
    reflection: list[Memory] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "time_label": self.time_label,
            "location_before": self.location_before,
            "observation": self.observation.to_dict(),
            "retrieved": [result.to_dict() for result in self.retrieved],
            "decision": self.decision.to_dict(),
            "outcome": self.outcome.to_dict(),
            "location_after": self.location_after,
            "reflection": [memory.to_dict() for memory in self.reflection],
        }
