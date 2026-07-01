from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionSpec:
    id: str
    label: str
    destination: str
    description: str


ACTION_SPECS: tuple[ActionSpec, ...] = (
    ActionSpec(
        id="go_to_library",
        label="go to the library",
        destination="Library",
        description="Move to the library without doing focused project work yet.",
    ),
    ActionSpec(
        id="go_to_cafe",
        label="go to the cafe",
        destination="Cafe",
        description="Move to the cafe without eating yet.",
    ),
    ActionSpec(
        id="go_to_dorm",
        label="go to the dorm",
        destination="Dorm",
        description="Move to the dorm without resting yet.",
    ),
    ActionSpec(
        id="eat_meal",
        label="eat a meal",
        destination="Cafe",
        description="Eat food to reduce hunger and recover a little energy and focus.",
    ),
    ActionSpec(
        id="rest",
        label="rest",
        destination="Dorm",
        description="Rest to recover energy and focus.",
    ),
    ActionSpec(
        id="work_on_project",
        label="work on the project",
        destination="Library",
        description="Do focused implementation or writing work for the project.",
    ),
    ActionSpec(
        id="review_notes",
        label="review the run notes",
        destination="Dorm",
        description="Review logs and preserve evidence for the assignment writeup.",
    ),
    ActionSpec(
        id="write_evidence_section",
        label="write the evidence section",
        destination="Dorm",
        description="Write the final evidence section using remembered assignment requirements and run notes.",
    ),
    ActionSpec(
        id="attend_discussion",
        label="attend the behavioral modeling discussion",
        destination="Classroom",
        description="Attend class discussion to improve project ideas.",
    ),
    ActionSpec(
        id="take_break",
        label="take a reset break",
        destination="Park",
        description="Take a short break to recover focus.",
    ),
    ActionSpec(
        id="organize_notes",
        label="organize project notes",
        destination="Dorm",
        description="Turn scattered notes into a clearer implementation plan.",
    ),
    ActionSpec(
        id="buy_snack",
        label="buy a snack",
        destination="Store",
        description="Buy and eat a small snack when hunger is rising.",
    ),
)

ACTION_BY_ID = {spec.id: spec for spec in ACTION_SPECS}

ACTION_ALIASES = {
    "go": "go_to_library",
    "go_library": "go_to_library",
    "library": "go_to_library",
    "go_cafe": "go_to_cafe",
    "cafe": "go_to_cafe",
    "go_dorm": "go_to_dorm",
    "dorm": "go_to_dorm",
    "eat": "eat_meal",
    "eat_a_meal": "eat_meal",
    "eat_food": "eat_meal",
    "meal": "eat_meal",
    "snack": "buy_snack",
    "buy_a_snack": "buy_snack",
    "sleep": "rest",
    "nap": "rest",
    "work": "work_on_project",
    "work_on_the_project": "work_on_project",
    "study": "work_on_project",
    "write": "work_on_project",
    "review": "review_notes",
    "review_log": "review_notes",
    "review_the_run_notes": "review_notes",
    "evidence": "write_evidence_section",
    "write_evidence": "write_evidence_section",
    "write_evidence_section": "write_evidence_section",
    "write_the_evidence_section": "write_evidence_section",
    "writeup": "write_evidence_section",
    "class": "attend_discussion",
    "discussion": "attend_discussion",
    "attend_the_behavioral_modeling_discussion": "attend_discussion",
    "break": "take_break",
    "reset_break": "take_break",
    "take_a_reset_break": "take_break",
    "walk": "take_break",
    "organize": "organize_notes",
    "organize_project_notes": "organize_notes",
    "plan": "organize_notes",
}


def action_schema_text() -> str:
    return "\n".join(
        f"- {spec.id}: {spec.description} Destination: {spec.destination}."
        for spec in ACTION_SPECS
    )


def normalize_action_id(raw: str) -> str | None:
    normalized = raw.strip().lower()
    normalized = normalized.replace("-", "_").replace(" ", "_")
    normalized = "".join(char for char in normalized if char.isalnum() or char == "_")
    normalized = normalized.replace("go_to_the_", "go_to_")

    if normalized in ACTION_BY_ID:
        return normalized
    if normalized in ACTION_ALIASES:
        return ACTION_ALIASES[normalized]
    return None


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
    action_id: str
    action: str
    destination: str
    reason: str

    @classmethod
    def from_action_id(cls, action_id: str, *, reason: str) -> "Decision":
        spec = ACTION_BY_ID[action_id]
        return cls(
            action_id=spec.id,
            action=spec.label,
            destination=spec.destination,
            reason=reason,
        )

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
