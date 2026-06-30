from __future__ import annotations

from .environment import CampusWorld
from .llm import BaseLLM
from .memory import MemoryStream
from .models import Memory, StepLog


class GenerativeAgent:
    def __init__(
        self,
        *,
        name: str,
        summary: str,
        memory: MemoryStream,
        llm: BaseLLM,
        reflection_interval: int = 20,
        reflection_threshold: float = 999.0,
        top_k: int = 6,
    ) -> None:
        self.name = name
        self.summary = summary
        self.memory = memory
        self.llm = llm
        self.reflection_interval = reflection_interval
        self.reflection_threshold = reflection_threshold
        self.top_k = top_k
        self.importance_since_reflection = 0.0

    def seed_memories(self) -> None:
        seeds = [
            "Maya Chen is a student researcher building a small generative-agent sandbox.",
            "Maya wants the project to show memory, retrieval, and reflection rather than a flashy visual world.",
            "Maya tends to work best when she alternates focused library sessions with short reset breaks.",
            "Maya is worried that the final writeup needs concrete surprises from an actual run.",
        ]
        for text in seeds:
            self.memory.add(
                step=0,
                kind="observation",
                text=text,
                importance=self.llm.rate_importance(text, kind="observation"),
                location="Dorm",
                tags=["seed"],
            )

    def step(self, world: CampusWorld, step: int) -> StepLog:
        snapshot = world.snapshot(step)
        location_before = snapshot.location
        observation_text = world.observe(step)
        observation = self._remember(
            step=step,
            kind="observation",
            text=observation_text,
            location=location_before,
        )

        query = (
            f"{snapshot.describe()} Current observation: {observation_text}. "
            "What past experience should influence Maya's next action?"
        )
        retrieved = self.memory.retrieve(query, step=step, top_k=self.top_k)

        decision = self.llm.choose_action(
            agent_summary=self.summary,
            world_state=snapshot.describe(),
            observation=observation_text,
            retrieved=retrieved,
        )
        outcome_text = world.apply_decision(decision, step)
        outcome = self._remember(
            step=step,
            kind="action",
            text=f"Maya chose to {decision.action} at the {decision.destination}. {outcome_text}",
            location=world.location,
        )

        reflection = self._maybe_reflect(step=step, location=world.location)
        world.tick()

        return StepLog(
            step=step,
            time_label=snapshot.time_label,
            location_before=location_before,
            observation=observation,
            retrieved=retrieved,
            decision=decision,
            outcome=outcome,
            location_after=world.location,
            reflection=reflection,
        )

    def _remember(self, *, step: int, kind: str, text: str, location: str) -> Memory:
        importance = self.llm.rate_importance(text, kind=kind)
        memory = self.memory.add(
            step=step,
            kind=kind,
            text=text,
            importance=importance,
            location=location,
        )
        if kind != "reflection":
            self.importance_since_reflection += importance
        return memory

    def _maybe_reflect(self, *, step: int, location: str) -> list[Memory]:
        should_reflect = False
        if self.reflection_interval > 0 and step % self.reflection_interval == 0:
            should_reflect = True
        if self.importance_since_reflection >= self.reflection_threshold:
            should_reflect = True
        if not should_reflect:
            return []

        recent = self.memory.recent(24)
        drafts = self.llm.reflect(recent_memories=recent)
        reflections: list[Memory] = []
        existing_reflections = {
            memory.text.lower()
            for memory in self.memory.memories
            if memory.kind == "reflection"
        }
        for draft in drafts:
            if draft.text.lower() in existing_reflections:
                continue
            reflections.append(
                self.memory.add(
                    step=step,
                    kind="reflection",
                    text=draft.text,
                    importance=draft.importance,
                    location=location,
                    evidence_ids=draft.evidence_ids,
                )
            )
        self.importance_since_reflection = 0.0
        return reflections
